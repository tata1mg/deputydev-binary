from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.utils.constant.url_constants import UrlType


class Url(BaseModel):
    id: Optional[int]
    name: str
    url: Optional[str] = None


class UpdateUrlParams(BaseModel):
    url_type: Optional[UrlType] = UrlType.PUBLIC_URL
    url: Url

    model_config = ConfigDict(from_attributes=True)
