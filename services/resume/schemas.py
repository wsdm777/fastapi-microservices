from datetime import datetime
from pydantic import BaseModel, Field


class ResponseOk(BaseModel):
    message: str = Field(examples=["ok"])


class AccessTokenInfo(BaseModel):
    id: int
    login: str
    level: int
    ref_jti: str
    exp: datetime
    iat: datetime
