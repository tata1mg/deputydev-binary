import os
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, List

from deputydev_core.services.chunking.chunk_info import ChunkInfo, ChunkSourceDetails
from deputydev_core.services.chunking.chunking_manager import ChunkingManger
from deputydev_core.services.embedding.extension_embedding_manager import (
    ExtensionEmbeddingManager,
)
from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from deputydev_core.services.repo.local_repo.local_repo_factory import LocalRepoFactory
from deputydev_core.services.repository.chunk_service import ChunkService
from deputydev_core.services.search.dataclasses.main import SearchTypes
from deputydev_core.utils.app_logger import AppLogger
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.constants.enums import SharedMemoryKeys

from app.clients.one_dev_client import OneDevClient
from app.models.dtos.focus_chunk_params import (
    ChunkDetails,
    ChunkInfoAndHash,
    CodeSnippetDetails,
    FocusChunksParams,
)
from app.models.dtos.relevant_chunks_params import RelevantChunksParams
from app.services.reranker_service import RerankerService
from app.services.shared_chunks_manager import SharedChunksManager
from app.utils.util import jsonify_chunks, weaviate_connection


class RelevantChunksService:
    def __init__(self, repo_path):
        self.repo_path = repo_path

    async def get_relevant_chunks(
        self, payload: RelevantChunksParams
    ) -> Dict[str, Any]:
        print(ConfigManager.configs)
        repo_path = payload.repo_path
        query = payload.query
        local_repo = LocalRepoFactory.get_local_repo(repo_path)
        one_dev_client = OneDevClient()
        embedding_manager = ExtensionEmbeddingManager(
            auth_token_key=SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value,
            one_dev_client=one_dev_client,
        )
        query_vector = await embedding_manager.embed_text_array(
            texts=[query], store_embeddings=False
        )
        chunkable_files_and_hashes = (
            await local_repo.get_chunkable_files_and_commit_hashes()
        )
        await SharedChunksManager.update_chunks(repo_path, chunkable_files_and_hashes)
        with ProcessPoolExecutor(
            max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]
        ) as executor:
            initialization_manager = ExtensionInitialisationManager(
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
            reranked_chunks_data = await RerankerService(session_id=payload.session_id, session_type=payload.session_type).rerank(
                query,
                relevant_chunks=relevant_chunks,
                is_llm_reranking_enabled=ConfigManager.configs["CHUNKING"][
                    "IS_LLM_RERANKING_ENABLED"
                ],
                # is_llm_reranking_enabled=False,
                focus_chunks=focus_chunks_details,
            )

        return {
            "relevant_chunks": jsonify_chunks(reranked_chunks_data[0]),
            "session_id": reranked_chunks_data[1],
        }

    def get_file_chunk(self, file_path: str, start_line: int, end_line: int) -> str:
        abs_file_path = os.path.join(self.repo_path, file_path)
        with open(abs_file_path, "r", encoding="utf-8", errors="ignore") as file:
            lines = file.readlines()
            return "".join(lines[start_line - 1 : end_line])

    async def get_focus_chunks(
        self, payload: FocusChunksParams
    ) -> List[Dict[str, Any]]:
        repo_path = payload.repo_path
        local_repo = LocalRepoFactory.get_local_repo(repo_path)
        one_dev_client = OneDevClient()
        chunkable_files_and_hashes = (
            await local_repo.get_chunkable_files_and_commit_hashes()
        )
        await SharedChunksManager.update_chunks(repo_path, chunkable_files_and_hashes)
        with ProcessPoolExecutor(
            max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]
        ) as executor:
            initialization_manager = ExtensionInitialisationManager(
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
            chunks = await ChunkService(
                weaviate_client=weaviate_client
            ).get_chunks_by_chunk_hashes(
                chunk_hashes=[
                    chunk.chunk_hash
                    for chunk in payload.chunks
                    if isinstance(chunk, ChunkDetails)
                ]
            )

            chunk_info_list: List[ChunkInfoAndHash] = []
            for chunk_dto, _vector in chunks:
                for chunk_file in payload.chunks:
                    if chunk_file.chunk_hash == chunk_dto.chunk_hash:
                        chunk_info_list.append(
                            ChunkInfoAndHash(
                                chunk_info=ChunkInfo(
                                    content=chunk_dto.text,
                                    source_details=ChunkSourceDetails(
                                        file_path=chunk_file.file_path,
                                        file_hash=chunk_file.file_hash,
                                        start_line=chunk_file.start_line,
                                        end_line=chunk_file.end_line,
                                    ),
                                    embedding=None,
                                    metadata=chunk_file.meta_info,
                                ),
                                chunk_hash=chunk_file.chunk_hash,
                            )
                        )
                        break

            # handle code snippets
            code_snippets = [
                chunk
                for chunk in payload.chunks
                if isinstance(chunk, CodeSnippetDetails)
            ]

            for code_snippet in code_snippets:
                file_content = ""
                try:
                    file_content = self.get_file_chunk(
                        file_path=code_snippet.file_path,
                        start_line=code_snippet.start_line,
                        end_line=code_snippet.end_line,
                    )
                    chunk_info_list.append(
                        ChunkInfoAndHash(
                            chunk_info=ChunkInfo(
                                content=file_content,
                                source_details=ChunkSourceDetails(
                                    file_path=code_snippet.file_path,
                                    file_hash=None,
                                    start_line=code_snippet.start_line,
                                    end_line=code_snippet.end_line,
                                ),
                                embedding=None,
                                metadata=None,
                            ),
                            chunk_hash=code_snippet.chunk_hash,
                        )
                    )
                except Exception as ex:
                    AppLogger.log_error(
                        f"Error occurred while fetching code snippet: {ex}"
                    )

        return [chunk_info.model_dump(mode="json") for chunk_info in chunk_info_list]
