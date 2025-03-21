import os
from typing import Any, Dict, List, Optional, Set

from deputydev_core.models.dto.chunk_file_dto import ChunkFileDTO, ChunkFileData
from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from deputydev_core.services.repository.chunk_files_service import ChunkFilesService
from deputydev_core.services.repository.dataclasses.main import (
    WeaviateSyncAndAsyncClients,
)
from deputydev_core.utils.app_logger import AppLogger

from app.dataclasses.codebase_search.focus_items_search.focus_items_search_dataclasses import (
    SearchKeywordType,
)
from app.dataclasses.codebase_search.focus_items_search.focus_items_search_dataclasses import (
    FocusItem,
)
from app.dataclasses.codebase_search.focus_items_search.focus_items_search_dataclasses import (
    FocusSearchParams,
)
from app.services.shared_chunks_manager import SharedChunksManager
import time

from app.utils.util import weaviate_connection


class FocusSearchService:
    @classmethod
    async def initialise_weaviate_client(
        cls, repo_path: str
    ) -> WeaviateSyncAndAsyncClients:
        initialization_manager = ExtensionInitialisationManager(repo_path=repo_path)
        weaviate_client = await weaviate_connection()
        if weaviate_client:
            weaviate_client = weaviate_client
        else:
            weaviate_client = await initialization_manager.initialize_vector_db()
        return weaviate_client

    @classmethod
    async def search_directories(cls, repo_path: str, keyword: str) -> List[FocusItem]:
        """
        Search for directories matching the keyword

        Args:
            repo_path: Path to the repository
            keyword: Directory name to search for
            chunkable_files: Dictionary of chunkable files and hashes

        Returns:
            List of matching directories
        """
        try:
            results: List[FocusItem] = []
            seen_dirs: Set[str] = set()

            abs_repo_path = repo_path
            abs_text_path = os.path.join(abs_repo_path, keyword)
            last_path_component = os.path.basename(abs_text_path)

            search_dir = (
                os.path.dirname(abs_text_path) if last_path_component else abs_repo_path
            )

            if not os.path.exists(search_dir):
                search_dir = abs_repo_path

            max_results = 7

            for root, dirs, _ in os.walk(search_dir, topdown=True):
                for dir_name in dirs:
                    abs_current_dir_path = os.path.join(root, dir_name)
                    rel_dir_path = os.path.relpath(abs_current_dir_path, abs_repo_path)

                    if (
                        last_path_component.lower() in dir_name.lower()
                        and rel_dir_path not in seen_dirs
                    ):
                        seen_dirs.add(rel_dir_path)

                        results.append(
                            FocusItem(
                                type=SearchKeywordType.DIRECTORY,
                                value=dir_name,
                                path=rel_dir_path,
                                score=0.0,
                            )
                        )

                        if len(results) >= max_results:
                            return results

                if root.count(os.sep) - abs_repo_path.count(os.sep) > 5:
                    dirs[:] = []

            return results

        except Exception as ex:
            AppLogger.log_error(f"directory search failed with exception {ex}")
            return []

    @classmethod
    def add_chunk_file_to_focus_item_map(
        cls,
        focus_item_map: Dict[str, FocusItem],
        chunk_file_dto: ChunkFileDTO,
        score: float,
        search_type: Optional[SearchKeywordType] = None,
    ):

        search_types_to_consider = (
            [
                SearchKeywordType.CLASS,
                SearchKeywordType.FUNCTION,
                SearchKeywordType.FILE,
            ]
            if not search_type
            else [search_type]
        )
        search_type_to_search_property_map = {
            SearchKeywordType.CLASS: "classes",
            SearchKeywordType.FUNCTION: "functions",
        }

        for search_type in search_types_to_consider:
            property_values = (
                getattr(
                    chunk_file_dto, search_type_to_search_property_map[search_type], []
                )
                if search_type in [SearchKeywordType.CLASS, SearchKeywordType.FUNCTION]
                else [os.path.basename(chunk_file_dto.file_path)]
            )
            chunk_file_data = ChunkFileData(**chunk_file_dto.model_dump(mode="json"))
            for property_value in property_values:
                key = f"{search_type.value}_{property_value}_{chunk_file_dto.file_path}"
                if key not in focus_item_map:
                    focus_item_map[key] = FocusItem(
                        type=search_type,
                        value=property_value,
                        path=chunk_file_dto.file_path,
                        chunks=[],
                        score=score,
                    )

                # add the chunk file to the focus item
                focus_item_map[key].chunks.append(chunk_file_data)

                # update the score of the overall focus item
                focus_item_map[key].score = max(focus_item_map[key].score, score)

    @classmethod
    def get_focus_items(
        cls,
        raw_search_result: List[Any],
        search_type: Optional[SearchKeywordType] = None,
    ) -> List[FocusItem]:
        focus_items_map: Dict[str, FocusItem] = {}
        for chunk_file_properties in raw_search_result:
            chunk_file_dto = ChunkFileDTO(
                **chunk_file_properties.properties, id=str(chunk_file_properties.uuid)
            )
            score = getattr(chunk_file_properties.metadata, "score", 0.0)
            cls.add_chunk_file_to_focus_item_map(
                focus_items_map, chunk_file_dto, score, search_type
            )

        sorted_focus_items = sorted(
            focus_items_map.values(), key=lambda x: x.score, reverse=True
        )
        return sorted_focus_items

    @classmethod
    async def get_search_results(cls, payload: FocusSearchParams) -> List[FocusItem]:
        start_time = time.perf_counter()
        result: List[FocusItem] = []
        try:
            # step 1. Directory search is different, so handle it separately
            if payload.type == SearchKeywordType.DIRECTORY:
                result = await cls.search_directories(
                    payload.repo_path, payload.keyword
                )

            # step 2. For other types, search using Weaviate
            else:
                # initializations
                weaviate_client = await cls.initialise_weaviate_client(
                    payload.repo_path
                )
                chunk_files_service = ChunkFilesService(weaviate_client)
                chunkable_files_and_hashes = (
                    await SharedChunksManager.initialize_chunks(payload.repo_path)
                )

                # now, based on whether the type is defined or not, get the chunks from weaviate via specific fuctions
                raw_search_result = []
                # TODO: This is fucking ugly. Both the conditions internally share more than 90% of the code. Just passing the type as a parameter would have been better.
                if payload.type:
                    raw_search_result = (
                        await chunk_files_service.get_keyword_type_chunks(
                            keyword=payload.keyword,
                            type=payload.type.value,
                            chunkable_files_and_hashes=chunkable_files_and_hashes,
                        )
                    )
                else:
                    raw_search_result = (
                        await chunk_files_service.get_autocomplete_keyword_chunks(
                            payload.keyword, chunkable_files_and_hashes
                        )
                    )

                result = cls.get_focus_items(raw_search_result, payload.type)

            AppLogger.log_info(
                f"Total execution time: {time.perf_counter() - start_time:.6f} sec"
            )
            return result
        except Exception as ex:
            AppLogger.log_error(f"autocomplete type search failed with exception {ex}")
            return result
