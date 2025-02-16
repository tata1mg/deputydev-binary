from pydantic import BaseModel


class UpdateVectorStoreParams(BaseModel):
    repo_path: str
    auth_token: str
