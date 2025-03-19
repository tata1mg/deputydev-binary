from typing import List

from deputydev_core.services.chunking.chunk_info import ChunkInfo
from deputydev_core.services.chunking.chunking_manager import ChunkingManger
from app.clients.one_dev_client import OneDevClient
from app.utils.util import filter_chunks_by_denotation, jsonify_chunks
from deputydev_core.utils.shared_memory import SharedMemory
from deputydev_core.utils.constants.enums import SharedMemoryKeys
from deputydev_core.utils.config_manager import ConfigManager


class RerankerService:

    async def rerank(
            self,
            query: str,
            relevant_chunks: List[ChunkInfo],
            focus_chunks: List[ChunkInfo],
            is_llm_reranking_enabled,
    ) -> List[ChunkInfo]:
        relevant_chunks = ChunkingManger.exclude_focused_chunks(
            relevant_chunks, focus_chunks
        )
        if is_llm_reranking_enabled:
            payload = {
                "query": query,
                "relevant_chunks": jsonify_chunks(relevant_chunks),
                "focus_chunks": jsonify_chunks(focus_chunks),
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {SharedMemory.read(SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value)}",
            }
            filtered_and_ranked_chunks_denotations = await OneDevClient().llm_reranking(payload, headers=headers)
            return filter_chunks_by_denotation(
                relevant_chunks + focus_chunks, filtered_and_ranked_chunks_denotations
            )
        else:
            filtered_and_ranked_chunks = self.get_default_chunks(
                focus_chunks, relevant_chunks
            )
            return filtered_and_ranked_chunks

    @classmethod
    def get_default_chunks(
            cls, focus_chunks: List[ChunkInfo], related_codebase_chunks: List[ChunkInfo]
    ) -> List[ChunkInfo]:
        max_default_chunks_to_return = ConfigManager.config["CHUNKING"][
            "DEFAULT_MAX_CHUNKS_CODE_GENERATION"
        ]
        chunks = focus_chunks + related_codebase_chunks
        chunks.sort(key=lambda chunk: chunk.search_score, reverse=True)
        return chunks[:max_default_chunks_to_return]
