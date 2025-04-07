from datetime import datetime
from pydantic import BaseModel, Field


class UserCreadentials(BaseModel):
    login: str = Field(min_length=4, max_length=16)
    password: str = Field(min_length=4, max_length=50)
    fingerprint: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str


class RefreshCreate(BaseModel):
    user_id: int = Field(gt=0)
    refresh_jti: str
    fingerprint: str


class AccessTokenInfo(BaseModel):
    id: int
    login: str
    level: int
    ref_jti: str
    exp: datetime
    iat: datetime
