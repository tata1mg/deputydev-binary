import asyncio
import json
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, Optional

from deputydev_core.services.initialization.extension_initialisation_manager import ExtensionInitialisationManager
from deputydev_core.utils.config_manager import ConfigManager
from deputydev_core.utils.custom_progress_bar import CustomProgressBar

from app.clients.one_dev_client import OneDevClient
from app.models.dtos.update_vector_store_params import UpdateVectorStoreParams
from app.utils.constants import CONFIG_PATH
from app.utils.util import weaviate_connection
from app.services.shared_chunks_manager import SharedChunksManager
from sanic import Sanic


class InitializationService:
    @classmethod
    async def update_vector_store(cls, payload: UpdateVectorStoreParams, progress_callback) -> None:
        repo_path = payload.repo_path
        auth_token = payload.auth_token
        chunkable_files = payload.chunkable_files
        with ProcessPoolExecutor(
            max_workers=ConfigManager.configs["NUMBER_OF_WORKERS"]
        ) as executor:
            one_dev_client = OneDevClient()
            initialization_manager = ExtensionInitialisationManager(
                repo_path=repo_path,
                auth_token=auth_token,
                process_executor=executor,
                one_dev_client=one_dev_client
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
                progress_monitor_task = asyncio.create_task(cls._monitor_embedding_progress(progressbar, progress_callback))
            await initialization_manager.prefill_vector_store(
                chunkable_files_and_hashes,
                progressbar=progressbar
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
    async def initialization(cls, auth_token, payload):
        app = Sanic.get_app()
        print("Getting config")
        await cls.get_config(auth_token, base_config=payload.get("config"))
        if not hasattr(app.ctx, "weaviate_client"):
            weaviate_client = await ExtensionInitialisationManager().initialize_vector_db()
            app.ctx.weaviate_client = weaviate_client

    @classmethod
    async def get_config(
        cls, auth_token: str, file_path: str = CONFIG_PATH, base_config: Dict = {}
    ) -> None:
        print("Getting config 2")
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
                print("********************")
                print(ConfigManager.configs)
                print("********************")
                with open(file_path, "w") as json_file:
                    json.dump(configs, json_file, indent=4)
            except Exception as error:
                print(f"Failed to fetch configs: {error}")
                await cls.close_session_and_exit(one_dev_client)

    @staticmethod
    async def close_session_and_exit(one_dev_client):
        print("Exiting ...")
        await one_dev_client.close_session()
