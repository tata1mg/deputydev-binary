import json

from deputydev_core.utils.config_manager import ConfigManager

from app.utils.constants import CONFIG_PATH

try:
    with open(CONFIG_PATH, "r") as json_file:
        ConfigManager.in_memory = True
        data = {
            "CHUNKING": {
                "CHARACTER_SIZE": ConfigManager.configs["CHUNKING"]["CHARACTER_SIZE"],
                "NUMBER_OF_CHUNKS": ConfigManager.configs["CHUNKING"][
                    "MAX_CHUNKS_CODE_GENERATION"
                ],
                "IS_LLM_RERANKING_ENABLED": ConfigManager.configs["CHUNKING"][
                    "IS_LLM_RERANKING_ENABLED"
                ],
            },
            "EMBEDDING": {
                "MODEL": ConfigManager.configs["EMBEDDING"]["MODEL"],
                "TOKEN_LIMIT": ConfigManager.configs["EMBEDDING"]["TOKEN_LIMIT"],
                "MAX_PARALLEL_TASKS": 60,
            },
            "RELEVANT_CHUNKS": {"CHUNKING_ENABLED": False},
            "DEPUTY_DEV": {
                "HOST": "http://localhost:8084",
                "TIMEOUT": 20,
                "LIMIT": 0,
                "LIMIT_PER_HOST": 0,
                "TTL_DNS_CACHE": 10,
            },
            "WEAVIATE_HOST": "127.0.0.1",
            "WEAVIATE_HTTP_PORT": 8079,
            "WEAVIATE_GRPC_PORT": 50050,
            "WEAVIATE_SCHEMA_VERSION": 5,
            "NUMBER_OF_WORKERS": 1,
        }
        ConfigManager.set(data)
except Exception as e:
    pass
