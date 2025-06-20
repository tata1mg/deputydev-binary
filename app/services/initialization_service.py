import asyncio
from asyncio import Task
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Optional, Union

from deputydev_core.services.auth_token_storage.auth_token_service import (
    AuthTokenService,
)
from deputydev_core.services.initialization.extension_initialisation_manager import (
    ExtensionInitialisationManager,
    WeaviateSyncAndAsyncClients,
)
from deputydev_core.utils.app_logger import AppLogger
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.constants.auth import AuthStatus
from deputydev_core.utils.custom_progress_bar import CustomProgressBar
from deputydev_core.utils.file_indexing_monitor import FileIndexingMonitor
from deputydev_core.utils.context_vars import get_context_value
from deputydev_core.utils.constants.enums import ContextValueKeys
from deputydev_core.utils.context_value import ContextValue
from deputydev_core.utils.weaviate import weaviate_connection
from sanic import Sanic

from app.clients.one_dev_client import OneDevClient
from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from deputydev_core.services.shared_chunks.shared_chunks_manager import (
    SharedChunksManager,
)
from app.utils.constants import Headers
from app.services.url_service.url_service import UrlService


class InitializationService:
    @classmethod
    async def update_chunks(cls, payload: UpdateVectorStoreParams, indexing_progress_callback, embedding_progress_callback):
        return await cls.update_vector_store(payload, indexing_progress_callback, embedding_progress_callback)

    @classmethod
    async def update_vector_store(cls, payload: UpdateVectorStoreParams, indexing_progress_callback, embedding_progress_callback) -> tuple[Union[Task[None], None], Union[Task[None], None]]:
        repo_path = payload.repo_path
        auth_token = ContextValue.get(ContextValueKeys.EXTENSION_AUTH_TOKEN.value)
        chunkable_files = payload.chunkable_files
        with ProcessPoolExecutor(max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]) as executor:
            one_dev_client = OneDevClient()
            body = {"enable_grace_period": ConfigManager.configs["USE_GRACE_PERIOD_FOR_EMBEDDING"]}
            headers = {"Authorization": f"Bearer {auth_token}"}
            token_data = await one_dev_client.verify_auth_token(headers=headers, payload=body)
            if token_data["status"] == AuthStatus.EXPIRED.value:
                await cls.handle_expired_token(token_data)

            initialization_manager = ExtensionInitialisationManager(
                repo_path=repo_path,
                auth_token_key=ContextValueKeys.EXTENSION_AUTH_TOKEN.value,
                process_executor=executor,
                one_dev_client=one_dev_client,
            )
            local_repo = initialization_manager.get_local_repo(chunkable_files=chunkable_files)
            chunkable_files_and_hashes = await local_repo.get_chunkable_files_and_commit_hashes()
            await SharedChunksManager.update_chunks(repo_path, chunkable_files_and_hashes, chunkable_files)
            weaviate_client = await weaviate_connection()
            if weaviate_client:
                initialization_manager.weaviate_client = weaviate_client
            else:
                await initialization_manager.initialize_vector_db()
            indexing_progressbar = CustomProgressBar()
            embedding_progressbar = CustomProgressBar()
            files_with_indexing_status = {key: {"file_path": key, "status": "IN_PROGRESS"} for key in chunkable_files_and_hashes}
            file_indexing_monitor = FileIndexingMonitor(files_with_indexing_status=files_with_indexing_status)
            if payload.sync:
                _embedding_progress_monitor_task = asyncio.create_task(
                    cls._monitor_embedding_progress(embedding_progressbar, embedding_progress_callback, repo_path)
                )
            _indexing_progress_monitor_task = asyncio.create_task(
                cls._monitor_indexing_progress(indexing_progressbar, indexing_progress_callback, file_indexing_monitor)
            )
            await initialization_manager.prefill_vector_store(
                chunkable_files_and_hashes,
                indexing_progressbar=indexing_progressbar,
                embedding_progressbar=embedding_progressbar,
                file_indexing_progress_monitor=file_indexing_monitor,
                enable_refresh=payload.sync,
            )
        if payload.sync:
            return _indexing_progress_monitor_task, _embedding_progress_monitor_task
        else:
            return _indexing_progress_monitor_task, None

    @classmethod
    async def _monitor_indexing_progress(cls, progress_bar, progress_callback, file_indexing_monitor):
        """A separate task that can monitor and report progress while chunking happens"""
        try:
            while True:
                await progress_callback(progress_bar.total_percentage, file_indexing_monitor.files_with_indexing_status)
                if progress_bar.is_completed():
                    return
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            return

    @classmethod
    async def _monitor_embedding_progress(cls, progress_bar, progress_callback, repo_path):
        """A separate task that can monitor and report progress while Embedding happens"""
        try:
            while True:
                if not progress_bar.is_completed():
                    await progress_callback(progress_bar.total_percentage)
                else:
                    AppLogger.log_info(f"Embedding done for {repo_path}")
                    return
                await asyncio.sleep(2)
        except asyncio.CancelledError as error:
            return

    @classmethod
    async def handle_expired_token(cls, token_data):
        auth_token = token_data["encrypted_session_data"]
        ContextValue.set(ContextValueKeys.EXTENSION_AUTH_TOKEN.value, auth_token)
        await AuthTokenService.store_token(get_context_value("headers").get(Headers.X_CLIENT))
        return auth_token

    @classmethod
    async def is_weaviate_ready(cls) -> bool:
        app = Sanic.get_app()
        if not hasattr(app.ctx, "weaviate_client"):
            return False
        else:
            existing_client: WeaviateSyncAndAsyncClients = app.ctx.weaviate_client
            return await existing_client.is_ready()

    @classmethod
    async def maintain_weaviate_heartbeat(cls):
        while True:
            try:
                is_reachable = await cls.is_weaviate_ready()
                if not is_reachable:
                    AppLogger.log_info(f"Is Weaviate reachable: {is_reachable}")
                    app = Sanic.get_app()
                    existing_client: WeaviateSyncAndAsyncClients = app.ctx.weaviate_client
                    await existing_client.async_client.close()
                    existing_client.sync_client.close()
                    await existing_client.ensure_connected()
            except Exception:
                AppLogger.log_error("Failed to maintain weaviate heartbeat")
            await asyncio.sleep(3)

    @classmethod
    async def initialization(cls, payload):
        app = Sanic.get_app()

        class ExtentionWeaviateSyncAndAsyncClients(WeaviateSyncAndAsyncClients):
            async def ensure_connected(self):
                if not await self.is_ready():
                    await cls.get_config(base_config=payload.get("config"))
                    (
                        weaviate_client,
                        new_weaviate_process,
                        _schema_cleaned,
                    ) = await ExtensionInitialisationManager().initialize_vector_db()
                    self.sync_client = weaviate_client.sync_client
                    self.async_client = weaviate_client.async_client

                    if new_weaviate_process:  # set only in case of windows
                        app.ctx.weaviate_process = new_weaviate_process

        if not hasattr(app.ctx, "weaviate_client"):
            await cls.get_config(base_config=payload.get("config"))
            (
                weaviate_client,
                new_weaviate_process,
                schema_cleaned,
            ) = await ExtensionInitialisationManager().initialize_vector_db()
            app.ctx.weaviate_client = ExtentionWeaviateSyncAndAsyncClients(
                async_client=weaviate_client.async_client,
                sync_client=weaviate_client.sync_client,
            )

            if new_weaviate_process:  # set only in case of windows
                app.ctx.weaviate_process = new_weaviate_process
            if schema_cleaned:
                asyncio.create_task(UrlService().refill_urls_data())
            asyncio.create_task(cls.maintain_weaviate_heartbeat())

    @classmethod
    async def get_config(cls, base_config: Dict = {}) -> None:
        time_start = time.perf_counter()
        if not ConfigManager.configs:
            ConfigManager.initialize(in_memory=True)
            one_dev_client = OneDevClient(base_config)
            await one_dev_client.close_session()
            try:
                configs: Optional[Dict[str, str]] = await one_dev_client.get_configs(
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {ContextValue.get(ContextValueKeys.EXTENSION_AUTH_TOKEN.value)}",
                    }
                )
                if configs is None:
                    raise Exception("No configs fetched")
                ConfigManager.set(configs)
            except Exception as error:
                AppLogger.log_error(f"Failed to fetch configs: {error}")
                await cls.close_session_and_exit(one_dev_client)

        time_end = time.perf_counter()
        AppLogger.log_info(f"Time taken to fetch configs: {time_end - time_start}")

    @staticmethod
    async def close_session_and_exit(one_dev_client):
        AppLogger.log_info("Exiting ...")
        await one_dev_client.close_session()
