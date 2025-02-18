from enum import Enum


NUMBER_OF_WORKERS = 1

class AuthTokenStorageManagers(Enum):
    CLI_AUTH_TOKEN_STORAGE_MANAGER = "cli"
    EXTENSION_AUTH_TOKEN_STORAGE_MANAGER = "extension"

class Status(Enum):
    SUCCESS = "success"
    FAILED = "failed"
