from enum import Enum

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
