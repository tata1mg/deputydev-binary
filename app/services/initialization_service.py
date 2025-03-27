import asyncio
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Optional

from deputydev_core.services.auth_token_storage.auth_token_service import (
    AuthTokenService,
)
from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
)
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.constants.auth import AuthStatus
from deputydev_core.utils.constants.enums import SharedMemoryKeys
from deputydev_core.utils.context_vars import get_context_value
from deputydev_core.utils.custom_progress_bar import CustomProgressBar
from deputydev_core.utils.shared_memory import SharedMemory
from sanic import Sanic

from app.clients.one_dev_client import OneDevClient
from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from app.services.shared_chunks_manager import SharedChunksManager
from app.utils.constants import Headers
from app.utils.util import weaviate_connection


class InitializationService:
    @classmethod
    async def update_chunks(cls, payload: UpdateVectorStoreParams, progress_callback):
        task = asyncio.create_task(cls.update_vector_store(payload, progress_callback))
        if payload.sync:
            await task

    @classmethod
    async def update_vector_store(
        cls, payload: UpdateVectorStoreParams, progress_callback
    ) -> None:
        repo_path = payload.repo_path
        auth_token = SharedMemory.read(SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value)
        chunkable_files = payload.chunkable_files
        with ProcessPoolExecutor(
            max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]
        ) as executor:
            one_dev_client = OneDevClient()
            body = {
                "enable_grace_period": ConfigManager.configs[
                    "USE_GRACE_PERIOD_FOR_EMBEDDING"
                ]
            }
            headers = {"Authorization": f"Bearer {auth_token}"}
            token_data = await one_dev_client.verify_auth_token(
                headers=headers, payload=body
            )
            if token_data["status"] == AuthStatus.EXPIRED.value:
                await cls.handle_expired_token(token_data)

            initialization_manager = ExtensionInitialisationManager(
                repo_path=repo_path,
                auth_token_key=SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value,
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
            progressbar = CustomProgressBar()
            if payload.sync:
                progress_monitor_task = asyncio.create_task(
                    cls._monitor_embedding_progress(progressbar, progress_callback)
                )
            await initialization_manager.prefill_vector_store(
                chunkable_files_and_hashes,
                progressbar=progressbar,
                enable_refresh=payload.sync,
            )

    @classmethod
    async def _monitor_embedding_progress(cls, progress_bar, progress_callback):
        """A separate task that can monitor and report progress while chunking happens"""
        try:
            while True:
                if not progress_bar.is_completed():
                    await progress_callback(progress_bar.total_percentage)
                else:
                    return
                await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            return

    @classmethod
    async def handle_expired_token(cls, token_data):
        auth_token = token_data["encrypted_session_data"]
        SharedMemory.create(SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value, auth_token)
        await AuthTokenService.store_token(
            get_context_value("headers").get(Headers.X_CLIENT)
        )
        return auth_token

    @classmethod
    async def initialization(cls, payload):
        app = Sanic.get_app()
        await cls.get_config(base_config=payload.get("config"))
        if not hasattr(app.ctx, "weaviate_client"):
            weaviate_client = (
                await ExtensionInitialisationManager().initialize_vector_db()
            )
            app.ctx.weaviate_client = weaviate_client

    @classmethod
    async def get_config(cls, base_config: Dict = {}) -> None:
        if not ConfigManager.configs:
            ConfigManager.initialize(in_memory=True)
            one_dev_client = OneDevClient(base_config)
            try:
                configs: Optional[Dict[str, str]] = await one_dev_client.get_configs(
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {SharedMemory.read(SharedMemoryKeys.EXTENSION_AUTH_TOKEN.value)}",
                    }
                )
                if configs is None:
                    raise Exception("No configs fetched")
                ConfigManager.set(configs)
                # SharedMemory.create(SharedMemoryKeys.BINARY_CONFIG.value, configs)
            except Exception as error:
                print(f"Failed to fetch configs: {error}")
                await cls.close_session_and_exit(one_dev_client)

    @staticmethod
    async def close_session_and_exit(one_dev_client):
        print("Exiting ...")
        await one_dev_client.close_session()
