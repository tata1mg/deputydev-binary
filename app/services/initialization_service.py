from concurrent.futures import ProcessPoolExecutor
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.clients.http.service_clients.one_dev_client import OneDevClient
from deputydev_core.services.initialization.initialization_service import (
    InitializationManager,
)
from typing import Optional, Dict

from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from app.utils.constants import NUMBER_OF_WORKERS
import json


class InitializationService:
    @classmethod
    async def update_vector_store(cls, repo_path: str, auth_token: str) -> None:
        with ProcessPoolExecutor(max_workers=NUMBER_OF_WORKERS) as executor:
            one_dev_client = OneDevClient()
            initialization_manager = InitializationManager(
                repo_path=repo_path,
                auth_token=auth_token,
                process_executor=executor,
                one_dev_client=one_dev_client,
            )
            local_repo = initialization_manager.get_local_repo()
            chunkable_files_and_hashes = (
                await local_repo.get_chunkable_files_and_commit_hashes()
            )
            await initialization_manager.initialize_vector_db()
            await initialization_manager.prefill_vector_store(
                chunkable_files_and_hashes
            )
            # closing weaviate clients
            await initialization_manager.weaviate_client.async_client.close()
            initialization_manager.weaviate_client.sync_client.close()

    @classmethod
    async def initialize(cls, payload: UpdateVectorStoreParams) -> None:
        await cls.get_config(auth_token=payload.auth_token)
        await cls.update_vector_store(payload.repo_path, payload.auth_token)

    @classmethod
    async def get_config(cls, auth_token: str, file_path: str = "../config.json") -> None:
        if not ConfigManager.configs:
            ConfigManager.initialize(in_memory=True)
            one_dev_client = OneDevClient()
            try:
                configs: Optional[Dict[str, str]] = await one_dev_client.get_configs(
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {auth_token}",
                    }
                )
                if configs is None:
                    raise Exception("No configs fetched")
                ConfigManager.set(configs)
                with open(file_path, "w") as json_file:
                    json.dump(configs, json_file, indent=4)
            except Exception as error:
                print(f"Failed to fetch configs: {error}")
                await cls.close_session_and_exit(one_dev_client)

    @staticmethod
    async def close_session_and_exit(one_dev_client):
        print("Exiting ...")
        await one_dev_client.close_session()
