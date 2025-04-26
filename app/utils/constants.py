from enum import Enum

CONFIG_PATH = "./binary_config.json"


class ListenerEventTypes(Enum):
    AFTER_SERVER_START = "after_server_start"
    BEFORE_SERVER_START = "before_server_start"
    BEFORE_SERVER_STOP = "before_server_stop"
    AFTER_SERVER_STOP = "after_server_stop"


class Headers:
    X_CLIENT = "X-Client"
    X_Client_Version = "X-Client-Version"
    AUTHORIZATION = "Authorization"
