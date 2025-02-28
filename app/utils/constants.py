from enum import Enum


NUMBER_OF_WORKERS = 1
WEAVIATE_HOST = "127.0.0.1"
WEAVIATE_HTTP_PORT = 8079
WEAVIATE_GRPC_PORT = 50050
CONFIG_PATH = "./binary_config.json"


class ListenerEventTypes(Enum):
    AFTER_SERVER_START = "after_server_start"
    BEFORE_SERVER_START = "before_server_start"
    BEFORE_SERVER_STOP = "before_server_stop"
    AFTER_SERVER_STOP = "after_server_stop"

class AuthTokenStorageManagers(Enum):
    CLI_AUTH_TOKEN_STORAGE_MANAGER = "cli"
    EXTENSION_AUTH_TOKEN_STORAGE_MANAGER = "extension"

class Status(Enum):
    SUCCESS = "success"
    FAILED = "failed"
