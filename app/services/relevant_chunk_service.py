from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List

from deputydev_core.services.chunking.chunking_manager import ChunkingManger
from deputydev_core.services.embedding.one_dev_embedding_manager import (
    OneDevEmbeddingManager,
)
from deputydev_core.services.initialization.initialization_service import (
    InitializationManager,
)
from deputydev_core.services.repo.local_repo.local_repo_factory import LocalRepoFactory
from deputydev_core.services.search.dataclasses.main import SearchTypes
from deputydev_core.utils.config_manager import ConfigManager

from app.utils.constants import SharedMemoryKeys
from app.clients.one_dev_client import OneDevClient
from app.models.dtos.relevant_chunks_params import RelevantChunksParams
from app.services.reranker_service import RerankerService
from app.utils.util import jsonify_chunks, weaviate_connection
from app.services.shared_chunks_manager import SharedChunksManager


class RelevantChunksService:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def get_relevant_chunks(
            self, payload: RelevantChunksParams
    ) -> List[Dict[str, dict]]:
        repo_path = payload.repo_path
        query = payload.query
        local_repo = LocalRepoFactory.get_local_repo(repo_path)
        one_dev_client = OneDevClient()
        embedding_manager = OneDevEmbeddingManager(
            auth_token_key=SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value, one_dev_client=one_dev_client
        )
        query_vector = await embedding_manager.embed_text_array(
            texts=[query], store_embeddings=False
        )
        chunkable_files_and_hashes = (
            await local_repo.get_chunkable_files_and_commit_hashes()
        )
        await SharedChunksManager.update_chunks(repo_path, chunkable_files_and_hashes)
        with ProcessPoolExecutor(max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]) as executor:
            initialization_manager = InitializationManager(
                repo_path=repo_path,
                auth_token_key=SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value,
                process_executor=executor,
                one_dev_client=one_dev_client,
            )
            weaviate_client = await weaviate_connection()
            if weaviate_client:
                weaviate_client = weaviate_client
            else:
                weaviate_client = await initialization_manager.initialize_vector_db()
            if (
                    payload.perform_chunking
                    and ConfigManager.configs["RELEVANT_CHUNKS"]["CHUNKING_ENABLED"]
            ):
                await initialization_manager.prefill_vector_store(
                    chunkable_files_and_hashes
                )
            max_relevant_chunks = ConfigManager.configs["CHUNKING"]["NUMBER_OF_CHUNKS"]
            (
                relevant_chunks,
                input_tokens,
                focus_chunks_details,
            ) = await ChunkingManger.get_relevant_chunks(
                query=query,
                local_repo=local_repo,
                embedding_manager=embedding_manager,
                process_executor=executor,
                max_chunks_to_return=max_relevant_chunks,
                focus_files=payload.focus_files,
                focus_chunks=payload.focus_chunks,
                focus_directories=payload.focus_directories,
                weaviate_client=weaviate_client,
                chunkable_files_with_hashes=chunkable_files_and_hashes,
                query_vector=query_vector[0][0],
                search_type=SearchTypes.VECTOR_DB_BASED,
            )
            reranked_chunks = await RerankerService().rerank(
                query,
                relevant_chunks=relevant_chunks,
                is_llm_reranking_enabled=ConfigManager.configs["CHUNKING"][
                    "IS_LLM_RERANKING_ENABLED"
                ],
                # is_llm_reranking_enabled=False,
                focus_chunks=focus_chunks_details,
            )

        return jsonify_chunks(reranked_chunks)
