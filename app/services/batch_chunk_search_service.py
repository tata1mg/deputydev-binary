from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from deputydev_core.utils.constants.enums import ContextValueKeys

from app.clients.one_dev_client import OneDevClient
from concurrent.futures import ProcessPoolExecutor
from deputydev_core.utils.config_manager import ConfigManager

from deputydev_core.services.tools.focussed_snippet_search.focussed_snippet_search import (
    FocussedSnippetSearch,
)
from deputydev_core.services.tools.focussed_snippet_search.dataclass.main import (
    FocussedSnippetSearchParams,
)
from deputydev_core.utils.weaviate import get_weaviate_client



class BatchSearchService:
    @classmethod
    async def search_code(cls, payload: FocussedSnippetSearchParams):
        """
        Search for code based on multiple search terms.
        """
        repo_path = payload.repo_path

        one_dev_client = OneDevClient()
        with ProcessPoolExecutor(
                max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]
        ) as executor:
            initialisation_manager = ExtensionInitialisationManager(
                repo_path=repo_path,
                auth_token_key=ContextValueKeys.EXTENSION_AUTH_TOKEN.value,
                process_executor=executor,
                one_dev_client=one_dev_client,
            )
            weaviate_client = await get_weaviate_client(initialisation_manager)
            chunks = await FocussedSnippetSearch.search_code(payload, weaviate_client, initialisation_manager)
        return chunks
