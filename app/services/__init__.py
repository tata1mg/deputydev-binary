import json
from deputydev_core.utils.config_manager import ConfigManager

try:
    with open("../config.json", "r") as json_file:
        ConfigManager.in_memory = True
        data = json.load(json_file)
        ConfigManager.config = data
except Exception:
    pass
