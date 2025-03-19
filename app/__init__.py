import json

from deputydev_core.utils.config_manager import ConfigManager

from app.utils.constants import CONFIG_PATH

try:
    with open(CONFIG_PATH, "r") as json_file:
        ConfigManager.in_memory = True
        data = json.load(json_file)
        ConfigManager.set(data)
except Exception as e:
    pass
