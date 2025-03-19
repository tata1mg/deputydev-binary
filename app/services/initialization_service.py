import json
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Optional
from deputydev_core.services.initialization.initialization_service import (
    InitializationManager,
)
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.constants.auth import AuthStatus

from app.clients.one_dev_client import OneDevClient
from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from app.services.auth_token_service import AuthTokenService
from app.utils.constants import CONFIG_PATH, AuthTokenStorageManagers, SharedMemoryKeys
from app.utils.util import weaviate_connection
from app.services.shared_chunks_manager import SharedChunksManager
from sanic import Sanic
from app.utils.shared_memory import SharedMemory


class InitializationService:
    @classmethod
    async def update_vector_store(cls, payload: UpdateVectorStoreParams) -> None:
        repo_path = payload.repo_path
        auth_token = payload.auth_token
        chunkable_files = payload.chunkable_files
        with ProcessPoolExecutor(max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]) as executor:
            one_dev_client = OneDevClient()
            payload = {"enable_grace_period": ConfigManager.configs["USE_GRACE_PERIOD_FOR_EMBEDDING"]}
            headers = {"Authorization": f"Bearer {auth_token}"}
            token_data = await one_dev_client.verify_auth_token(headers=headers, payload=payload)
            if token_data["status"] == AuthStatus.EXPIRED.value:
                auth_token = cls.handle_expired_token(token_data)

            initialization_manager = InitializationManager(
                repo_path=repo_path,
                auth_token=auth_token,
                process_executor=executor,
                one_dev_client=one_dev_client,
            )
            local_repo = initialization_manager.get_local_repo(
                chunkable_files=chunkable_files
            )
            chunkable_files_and_hashes = (
                await local_repo.get_chunkable_files_and_commit_hashes()
            )
            await SharedChunksManager.update_chunks(
                repo_path, chunkable_files_and_hashes, chunkable_files
            )
            weaviate_client = await weaviate_connection()
            if weaviate_client:
                initialization_manager.weaviate_client = weaviate_client
            else:
                await initialization_manager.initialize_vector_db()
            await initialization_manager.prefill_vector_store(
                chunkable_files_and_hashes
            )

    @classmethod
    async def handle_expired_token(cls, token_data):
        auth_token = token_data["encrypted_session_data"]
        # TODO: make type on the basis of client, when we start receving from extension
        # TODO: This type should not be passed through headers
        await AuthTokenService.store_token(headers={"Authorization": f"Bearer {auth_token}",
                                                    "Type": AuthTokenStorageManagers.EXTENSION_AUTH_TOKEN_STORAGE_MANAGER.value})

    @classmethod
    async def initialization(cls, auth_token, payload):
        app = Sanic.get_app()
        await cls.get_config(auth_token, base_config=payload.get("config"))
        if not hasattr(app.ctx, "weaviate_client"):
            weaviate_client = await InitializationManager().initialize_vector_db()
            app.ctx.weaviate_client = weaviate_client

    @classmethod
    async def get_config(cls, auth_token: str, base_config: Dict = {}) -> None:
        if not ConfigManager.configs:
            ConfigManager.initialize(in_memory=True)
            one_dev_client = OneDevClient(base_config)
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
                SharedMemory.create(SharedMemoryKeys.BINARY_CONFIG.value, configs)
            except Exception as error:
                print(f"Failed to fetch configs: {error}")
                await cls.close_session_and_exit(one_dev_client)

    @staticmethod
    async def close_session_and_exit(one_dev_client):
        print("Exiting ...")
        await one_dev_client.close_session()
