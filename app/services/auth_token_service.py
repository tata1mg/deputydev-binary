from app.utils.constants import AuthTokenStorageManagers, Status
from deputydev_core.services.auth_token_storage.cli_auth_token_storage_manager import CLIAuthTokenStorageManager
from deputydev_core.services.auth_token_storage.extension_auth_token_storage_manager import ExtensionAuthTokenStorageManager
from typing import Dict, Any, Union

class AuthTokenService:
    """
    A service class for managing authentication tokens, including storing and loading tokens
    from different storage managers.
    """

    @classmethod
    def get_auth_token_storage_manager(cls, storage_manager_type: str) -> Union[CLIAuthTokenStorageManager, ExtensionAuthTokenStorageManager]:
        """
        Retrieves the appropriate authentication token storage manager based on the provided type.

        Args:
            storage_manager_type (str): The type of the storage manager ("cli" or "extension").

        Returns:
            Union[CLIAuthTokenStorageManager, ExtensionAuthTokenStorageManager]: The corresponding storage manager instance.

        Raises:
            ValueError: If the storage manager type is invalid.
        """
        if storage_manager_type == AuthTokenStorageManagers.CLI_AUTH_TOKEN_STORAGE_MANAGER.value:
            return CLIAuthTokenStorageManager
        elif storage_manager_type == AuthTokenStorageManagers.EXTENSION_AUTH_TOKEN_STORAGE_MANAGER.value:
            return ExtensionAuthTokenStorageManager
        else:
            raise ValueError("Invalid storage manager type")

    @classmethod
    async def store_token(cls, headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stores the authentication token using the specified storage manager.

        Args:
            headers (Dict[str, Any]): The request headers containing the token and storage manager type.

        Returns:
            Dict[str, Any]: A dictionary containing the result of the operation, including success or failure messages.

        Raises:
            ValueError: If the required headers are not found.
        """
        try:
            storage_manager_type = headers.get("Type")
            if not storage_manager_type:
                raise ValueError("Type header not found")
            authorization_header = headers.get("Authorization")
            if not authorization_header:
                raise ValueError("Authorization header not found")
            auth_token = authorization_header.split(" ")[1]
            storage_manager = cls.get_auth_token_storage_manager(storage_manager_type)
            storage_manager.store_auth_token(auth_token)
            return {
                "message": Status.SUCCESS.value
            }
        except ValueError as ve:
            return {
                "message": Status.FAILED.value,
                "error": f"Failed to store auth token: {ve}"
            }
        except Exception as e:
            return {
                "message": Status.FAILED.value,
                "error": f"Failed to store auth token due: {e}"
            }

    @classmethod
    async def load_token(cls, headers: Dict[str, Any]) -> Dict[str, Any]:
        """
        Loads the authentication token using the specified storage manager.

        Args:
            headers (Dict[str, Any]): The request headers containing the storage manager type.

        Returns:
            Dict[str, Any]: A dictionary containing the loaded token and success or failure messages.

        Raises:
            ValueError: If the required headers are not found.
        """
        try:
            storage_manager_type = headers.get("Type")
            if not storage_manager_type:
                raise ValueError("Type header not found")
            storage_manager = cls.get_auth_token_storage_manager(storage_manager_type)
            auth_token = storage_manager.load_auth_token()
            return {
                "message": Status.SUCCESS.value,
                "auth_token": auth_token
            }
        except ValueError as ve:
            return {
                "message": Status.FAILED.value,
                "error": f"Failed to load auth token: {ve}"
            }
        except Exception as e:
            return {
                "message": Status.FAILED.value,
                "error": f"Failed to load auth token: {e}"
            }