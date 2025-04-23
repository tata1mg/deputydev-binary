from app.services.url_service.managers.public_url_manager import PublicUrlManager
from app.utils.constant.url_constants import UrlType
from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from app.services.url_service.managers.url_manager import UrlManager


class UrlManagerFactory:
    url_managers = {UrlType.PUBLIC_URL: PublicUrlManager}

    @classmethod
    def url_manager(cls, url_type: UrlType) -> Type["UrlManager"]:
        return cls.url_managers[url_type]
