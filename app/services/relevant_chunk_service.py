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
from deputydev_core.services.repository.chunk_files_service import ChunkFilesService
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
            reranked_chunks_data = await RerankerService(
                session_id=payload.session_id, session_type=payload.session_type
            ).rerank(
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

            if (
                payload.search_item_type != "directory"
                and isinstance(payload.chunks[0], ChunkDetails)
                and payload.search_item_name
                and payload.search_item_type
            ):
                revised_relevant_chunks = await ChunkFilesService(
                    weaviate_client=weaviate_client
                ).get_chunk_files_matching_exact_search_key_on_file_hash(
                    search_key=payload.search_item_name,
                    search_type=payload.search_item_type,
                    file_path=payload.chunks[0].file_path,
                    file_hash=payload.chunks[0].file_hash,
                )
                payload.chunks = [
                    ChunkDetails(
                        start_line=chunk_file_obj.start_line,
                        end_line=chunk_file_obj.end_line,
                        chunk_hash=chunk_file_obj.chunk_hash,
                        file_path=chunk_file_obj.file_path,
                        file_hash=chunk_file_obj.file_hash,
                    )
                    for chunk_file_obj in revised_relevant_chunks
                ]

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

        # Get import-only chunk files from Weaviate
        # This retrieves all chunk files that have imports
        import_only_chunk_files = await ChunkService(
            weaviate_client=weaviate_client
        ).get_import_only_chunk_files_matching_exact_search_key_on_file_hash(
            search_key=payload.search_item_name,
            search_type=payload.search_item_type,
            file_path=payload.chunks[0].file_path,
            file_hash=payload.chunks[0].file_hash,
        )

        # Extract chunk details from import-only chunk files
        # This creates a list of chunk details that have imports
        import_only_chunks_details = [
            ChunkDetails(
                start_line=chunk_file_obj.start_line,
                end_line=chunk_file_obj.end_line,
                chunk_hash=chunk_file_obj.chunk_hash,
                file_path=chunk_file_obj.file_path,
                file_hash=chunk_file_obj.file_hash,
            )
            for chunk_file_obj in import_only_chunk_files
        ]

        # This retrieves the most relevant import-only chunks based on the query
        import_only_chunks = await ChunkService(
            weaviate_client=weaviate_client
        ).get_chunks_by_chunk_hashes(
            chunk_hashes=[
                chunk.chunk_hash
                for chunk in import_only_chunks_details
            ]
        )

        # Create mapping of file paths to their import-only chunk infos and hashes
        # This creates a dictionary where each file path maps to a set of ChunkInfoAndHash objects
        # that contain import-related content
        import_only_file_path_to_chunk_info_and_hash: Dict[str, set[ChunkInfoAndHash]] = {}
        for chunk_dto, _vector in import_only_chunks:
            for chunk_file in import_only_chunks_details:
                if chunk_file.chunk_hash == chunk_dto.chunk_hash:
                    file_path = chunk_file.file_path
                    if file_path not in import_only_file_path_to_chunk_info_and_hash:
                        import_only_file_path_to_chunk_info_and_hash[file_path] = set()

                    import_only_file_path_to_chunk_info_and_hash[file_path].add(
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

        for chunk_info in chunk_info_list:
            file_path = chunk_info.chunk_info.source_details.file_path
            if file_path in import_only_file_path_to_chunk_info_and_hash:
                import_only_file_path_to_chunk_info_and_hash[file_path].add(chunk_info)

        updated_chunk_info_list: List[ChunkInfoAndHash] = []
        for chunk_info_set in import_only_file_path_to_chunk_info_and_hash.values():
            updated_chunk_info_list.extend(list(chunk_info_set))

        # sort updated_chunk_info_list based on start_line
        updated_chunk_info_list.sort(
            key=lambda x: x.chunk_info.source_details.start_line,
        )
        return [chunk_info.model_dump(mode="json") for chunk_info in updated_chunk_info_list]
