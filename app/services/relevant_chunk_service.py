from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, List

from deputydev_core.services.embedding.extension_embedding_manager import (
    ExtensionEmbeddingManager,
)
from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from deputydev_core.services.tools.focussed_snippet_search.dataclass.main import FocusChunksParams
from deputydev_core.services.tools.relevant_chunks.dataclass.main import RelevantChunksParams
from deputydev_core.services.tools.relevant_chunks.relevant_chunk import RelevantChunks as CoreRelevantChunksService
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.constants.enums import ContextValueKeys
from deputydev_core.utils.weaviate import weaviate_connection

from app.clients.one_dev_client import OneDevClient
from app.utils.ripgrep_path import get_rg_path


class RelevantChunksService:
    def __init__(self, repo_path: str) -> None:
        self.repo_path = repo_path

    async def get_relevant_chunks(self, payload: RelevantChunksParams) -> Dict[str, Any]:
        repo_path = payload.repo_path
        one_dev_client = OneDevClient()
        ripgrep_path = get_rg_path()
        embedding_manager = ExtensionEmbeddingManager(
            auth_token_key=ContextValueKeys.EXTENSION_AUTH_TOKEN.value,
            one_dev_client=one_dev_client,
        )
        weaviate_client = await weaviate_connection()
        with ProcessPoolExecutor(max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]) as executor:
            initialization_manager = ExtensionInitialisationManager(
                repo_path=repo_path,
                auth_token_key=ContextValueKeys.EXTENSION_AUTH_TOKEN.value,
                process_executor=executor,
                one_dev_client=one_dev_client,
                weaviate_client=weaviate_client,
                ripgrep_path=ripgrep_path,
            )
            relevant_chunks = await CoreRelevantChunksService(repo_path, ripgrep_path).get_relevant_chunks(
                payload,
                one_dev_client,
                embedding_manager,
                initialization_manager,
                executor,
                ContextValueKeys.EXTENSION_AUTH_TOKEN.value,
            )
        return relevant_chunks

    async def get_focus_chunks(self, payload: FocusChunksParams) -> List[Dict[str, Any]]:
        one_dev_client = OneDevClient()
        ripgrep_path = get_rg_path()
        with ProcessPoolExecutor(max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]) as executor:
            initialisation_manager = ExtensionInitialisationManager(
                repo_path=payload.repo_path,
                auth_token_key=ContextValueKeys.EXTENSION_AUTH_TOKEN.value,
                process_executor=executor,
                one_dev_client=one_dev_client,
                ripgrep_path=ripgrep_path,
            )

            focus_chunks = await CoreRelevantChunksService(payload.repo_path, ripgrep_path).get_focus_chunks(
                payload, initialisation_manager
            )
        return focus_chunks
