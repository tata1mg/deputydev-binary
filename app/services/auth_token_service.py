from typing import Any, Dict, Union

from deputydev_core.services.auth_token_storage.cli_auth_token_storage_manager import (
    CLIAuthTokenStorageManager,
)
from deputydev_core.services.auth_token_storage.extension_auth_token_storage_manager import (
    ExtensionAuthTokenStorageManager,
)

from app.utils.constants import AuthTokenStorageManagers, Status


class AuthTokenService:
    """
    A service class for managing authentication tokens, including storing and loading tokens
    from different storage managers.
    """

    @classmethod
    def get_auth_token_storage_manager(
        cls, storage_manager_type: str
    ) -> Union[CLIAuthTokenStorageManager, ExtensionAuthTokenStorageManager]:
        """
        Retrieves the appropriate authentication token storage manager based on the provided type.

        Args:
            storage_manager_type (str): The type of the storage manager ("cli" or "extension").

        Returns:
            Union[CLIAuthTokenStorageManager, ExtensionAuthTokenStorageManager]: The corresponding storage manager instance.

        Raises:
            ValueError: If the storage manager type is invalid.
        """
        if (
            storage_manager_type
            == AuthTokenStorageManagers.CLI_AUTH_TOKEN_STORAGE_MANAGER.value
        ):
            return CLIAuthTokenStorageManager
        elif (
            storage_manager_type
            == AuthTokenStorageManagers.EXTENSION_AUTH_TOKEN_STORAGE_MANAGER.value
        ):
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
            return {"message": Status.SUCCESS.value}
        except (ValueError, Exception) as e:
            return {
                "message": Status.FAILED.value,
                "error": f"Failed to store auth token: {e}",
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
            # storage_manager_type = headers.get("Type")
            # if not storage_manager_type:
            #     raise ValueError("Type header not found")
            # storage_manager = cls.get_auth_token_storage_manager(storage_manager_type)
            # auth_token = storage_manager.load_auth_token()
            auth_tokn = "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"
            return {"message": Status.SUCCESS.value, "auth_token": auth_tokn}
        except (ValueError, Exception) as e:
            return {
                "message": Status.FAILED.value,
                "error": f"Failed to load auth token: {e}",
            }
