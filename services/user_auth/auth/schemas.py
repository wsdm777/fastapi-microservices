from pydantic import BaseModel, Field


class UserCreadentials(BaseModel):
    login: str = Field(min_length=4, max_length=16)
    password: str = Field(min_length=4, max_length=50)
    fingerprint: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
