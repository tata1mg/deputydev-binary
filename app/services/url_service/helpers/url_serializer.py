from datetime import datetime, timedelta, timezone
from app.models.dtos.collection_dtos.urls_content_dto import UrlsContentDto


class UrlSerializer:
    default_fields = ["id", "name", "url", "last_indexed"]

    @classmethod
    def parse_url_model(cls, url_obj: UrlsContentDto, extra_fields=[]):
        data = url_obj.model_dump(include=set(cls.default_fields + extra_fields))
        data["id"] = url_obj.backend_id
        if data["last_indexed"]:
            data["last_indexed"] = data["last_indexed"].isoformat() if data["last_indexed"] else None
        return data
