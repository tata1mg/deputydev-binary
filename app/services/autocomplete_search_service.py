import os

from deputydev_core.models.dto.chunk_file_dto import ChunkFileDTO
from deputydev_core.services.initialization.initialization_service import \
    InitializationManager
from deputydev_core.services.repository.chunk_files_service import \
    ChunkFilesService

from app.constants.constant import KeywordTypes, PropertyTypes
from app.models.dtos.autocomplete_search_params import AutocompleteSearchParams
from app.models.dtos.autocomplete_search_response import ChunkRange, CodeSymbol
from app.services.shared_chunks_manager import SharedChunksManager


class AutocompleteSearchService:
    VALID_TYPES = {"file", "class", "function", "directory"}
    TYPE_CONFIG = {
        "file": {
            "property": PropertyTypes.FILE.value,
            "result_type": KeywordTypes.FILE.value,
        },
        "class": {
            "property": PropertyTypes.CLASS.value,
            "result_type": KeywordTypes.CLASS.value,
        },
        "function": {
            "property": PropertyTypes.FUNCTION.value,
            "result_type": KeywordTypes.FUNCTION.value,
        },
    }

    @classmethod
    async def get_autocomplete_keyword_chunks(cls, payload: AutocompleteSearchParams):
        repo_path = payload.repo_path
        weaviate_client = None

        try:

            chunkable_files_and_hashes = await SharedChunksManager.initialize_chunks(
                payload.repo_path
            )
            weaviate_client = await InitializationManager(
                repo_path
            ).initialize_vector_db()

            keyword_chunks = await ChunkFilesService(
                weaviate_client
            ).get_autocomplete_keyword_chunks(
                payload.keyword, chunkable_files_and_hashes
            )
            sorted_chunks = cls.sort_chunks(keyword_chunks)

            chunk_map = {}
            seen_files = set()

            for chunk_obj in sorted_chunks:
                chunk_dto = ChunkFileDTO(**chunk_obj.properties, id=str(chunk_obj.uuid))
                chunk_range = ChunkRange(
                    start_line=chunk_dto.start_line, end_line=chunk_dto.end_line
                )
                score = (
                    chunk_obj.metadata.score
                    if hasattr(chunk_obj.metadata, "score")
                    else 0.0
                )

                cls.add_symbols_to_map(
                    chunk_map,
                    KeywordTypes.CLASS.value,
                    chunk_dto.classes,
                    chunk_dto.file_path,
                    chunk_range,
                    score,
                )

                cls.add_symbols_to_map(
                    chunk_map,
                    KeywordTypes.FUNCTION.value,
                    chunk_dto.functions,
                    chunk_dto.file_path,
                    chunk_range,
                    score,
                )

                if chunk_dto.file_path not in seen_files:
                    seen_files.add(chunk_dto.file_path)
                    chunk_map[
                        f"{KeywordTypes.FILE.value}_{chunk_dto.file_path}"
                    ] = CodeSymbol(
                        type=KeywordTypes.FILE.value,
                        value=os.path.basename(chunk_dto.file_path),
                        file_path=chunk_dto.file_path,
                        chunks=[],
                        score=score,
                    )

            sorted_chunks = sorted(
                chunk_map.values(), key=lambda x: x.score, reverse=True
            )
            response = [chunk.to_dict() for chunk in sorted_chunks]
            return {"response": response}
        except Exception as ex:
            raise ex
            return {"response": []}
        finally:
            if weaviate_client:
                weaviate_client.sync_client.close()
                await weaviate_client.async_client.close()

    @classmethod
    async def get_autocomplete_keyword_type_chunks(
        cls, payload: AutocompleteSearchParams
    ):
        """
        Search for code symbols by type (file, class, function, directory)

        Args:
            payload: AutocompleteSearchParams

        Returns:
            Dictionary with search results formatted according to the type
        """
        keyword_type = payload.type
        keyword = payload.keyword
        repo_path = payload.repo_path
        weaviate_client = None

        if keyword_type not in cls.VALID_TYPES:
            return {"response": []}

        try:
            chunkable_files_and_hashes = await SharedChunksManager.initialize_chunks(
                repo_path
            )

            # Initialize Weaviate client
            initialization_manager = InitializationManager(repo_path=repo_path)
            weaviate_client = await initialization_manager.initialize_vector_db()

            if keyword_type == "directory":
                result = await cls.search_directories(repo_path, keyword)
            else:
                # For file, class and function
                chunk_files_service = ChunkFilesService(weaviate_client)
                result = await cls.search_by_type(
                    chunk_files_service,
                    keyword_type,
                    keyword,
                    chunkable_files_and_hashes,
                )
            return {"response": result}
        except Exception as ex:
            raise ex
            return {"response": []}
        finally:
            if weaviate_client:
                weaviate_client.sync_client.close()
                await weaviate_client.async_client.close()

    @classmethod
    async def search_by_type(
        cls,
        chunk_files_service: ChunkFilesService,
        search_type: str,
        keyword: str,
        chunkable_files_and_hashes,
    ):
        """
        Search for code symbols by type using Weaviate

        Args:
            chunk_files_service: Service for querying chunks
            search_type: Type of search (file, class, function)
            keyword: Search keyword

        Returns:
            List of formatted search results
        """

        keyword_chunks = await chunk_files_service.get_autocomplete_keyword_type_chunks(
            keyword=keyword,
            type=search_type,
            chunkable_files_and_hashes=chunkable_files_and_hashes,
        )

        sorted_chunks = cls.sort_chunks(keyword_chunks)

        config = cls.TYPE_CONFIG.get(search_type)
        if config:
            return cls.format_results(
                sorted_chunks, config["property"], config["result_type"]
            )

        return []

    @classmethod
    def format_results(cls, chunks, property_name, symbol_type):

        chunk_map = {}
        seen_items = set()
        for chunk_obj in chunks:
            chunk_dto = ChunkFileDTO(**chunk_obj.properties, id=str(chunk_obj.uuid))
            score = getattr(chunk_obj.metadata, "score", 0.0)

            file_path = chunk_dto.file_path
            if property_name is PropertyTypes.FILE.value:
                if file_path not in seen_items:
                    seen_items.add(file_path)
                    chunk_map[file_path] = CodeSymbol(
                        type=symbol_type,
                        value=os.path.basename(file_path),
                        file_path=file_path,
                        chunks=[],
                        score=score,
                    )
            else:
                symbols = getattr(chunk_dto, property_name, [])
                chunk_range = ChunkRange(
                    start_line=chunk_dto.start_line, end_line=chunk_dto.end_line
                )
                cls.add_symbols_to_map(
                    chunk_map, symbol_type, symbols, file_path, chunk_range, score
                )

        sorted_chunks = sorted(chunk_map.values(), key=lambda x: x.score, reverse=True)
        response = [chunk.to_dict() for chunk in sorted_chunks]
        return response

    @classmethod
    def add_symbols_to_map(
        cls, chunk_map, symbol_type, symbols, file_path, chunk_range, score
    ):
        for symbol_name in symbols:
            key = f"{symbol_type}_{symbol_name}_{file_path}"
            if key not in chunk_map:

                chunk_map[key] = CodeSymbol(
                    type=symbol_type,
                    value=symbol_name,
                    file_path=file_path,
                    chunks=[],
                    score=score,
                )
            chunk_map[key].chunks.append(chunk_range)
            chunk_map[key].score = max(chunk_map[key].score, score)

    @classmethod
    async def search_directories(cls, repo_path: str, keyword: str):
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
            results = []
            seen_dirs = set()

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
                            {
                                "type": "directory",
                                "value": dir_name,
                                "path": rel_dir_path,
                            }
                        )

                        if len(results) >= max_results:
                            return results

                if root.count(os.sep) - abs_repo_path.count(os.sep) > 5:
                    dirs[:] = []

            return results

        except Exception as e:
            return []

    @staticmethod
    def sort_chunks(chunks):
        return sorted(
            chunks, key=lambda x: getattr(x.metadata, "score", 0.0), reverse=True
        )
