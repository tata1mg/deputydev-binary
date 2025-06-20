from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.utils.constant.url_constants import UrlType


class Url(BaseModel):
    name: str
    url: str


class SaveUrlParams(BaseModel):
    url_type: Optional[UrlType] = UrlType.PUBLIC_URL
    url: Url

    model_config = ConfigDict(from_attributes=True)
