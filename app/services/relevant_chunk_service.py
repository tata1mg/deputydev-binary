from concurrent.futures import ProcessPoolExecutor
from deputydev_core.services.chunking.chunking_manager import ChunkingManger
from deputydev_core.services.repo.local_repo.local_repo_factory import LocalRepoFactory
from deputydev_core.services.search.dataclasses.main import SearchTypes
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.clients.http.service_clients.one_dev_client import OneDevClient
from deputydev_core.services.initialization.initialization_service import (
    InitializationManager,
)
from deputydev_core.services.embedding.one_dev_embedding_manager import (
    OneDevEmbeddingManager,
)
from app.utils.constants import NUMBER_OF_WORKERS


class RelevantChunksService:
    @classmethod
    async def get_relevant_chunks(cls, payload):
        repo_path = payload.repo_path
        auth_token = payload.auth_token
        query = payload.query
        local_repo = LocalRepoFactory.get_local_repo(repo_path)
        one_dev_client = OneDevClient()
        embedding_manager = OneDevEmbeddingManager(
            auth_token=auth_token, one_dev_client=one_dev_client
        )
        query_vector = await embedding_manager.embed_text_array(
            texts=[query], store_embeddings=False
        )
        chunkable_files_and_hashes = (
            await local_repo.get_chunkable_files_and_commit_hashes()
        )
        with ProcessPoolExecutor(max_workers=NUMBER_OF_WORKERS) as executor:
            weaviate_client = await InitializationManager(
                repo_path=repo_path,
                auth_token=auth_token,
                process_executor=executor,
                one_dev_client=one_dev_client,
            ).initialize_vector_db()
            max_relevant_chunks = ConfigManager.configs["CHUNKING"]["NUMBER_OF_CHUNKS"]
            reranked_chunks, input_tokens, focus_chunks_details = (
                await ChunkingManger.get_relevant_chunks(
                    query=query,
                    local_repo=local_repo,
                    embedding_manager=embedding_manager,
                    process_executor=executor,
                    max_chunks_to_return=max_relevant_chunks,
                    focus_files=payload.focus_files,
                    focus_chunks=payload.focus_chunks,
                    weaviate_client=weaviate_client,
                    chunkable_files_with_hashes=chunkable_files_and_hashes,
                    query_vector=query_vector[0][0],
                    search_type=SearchTypes.VECTOR_DB_BASED,
                )
            )
            final_chunks = cls.handle_relevant_chunks(reranked_chunks)
        return final_chunks

    @classmethod
    def handle_relevant_chunks(cls, chunks):
        dumped_chunks = [chunk.model_dump(mode="json") for chunk in chunks]
        return dumped_chunks
