from deputydev_core.utils.config_manager import ConfigManager
from app.utils.constants import CONFIG_PATH
from app.utils.shared_memory import SharedMemory
from app.utils.constants import SharedMemoryKeys

config = SharedMemory.read(SharedMemoryKeys.BINARY_CONFIG.value)
if config:
    ConfigManager.in_memory = True
    ConfigManager.set(config)
