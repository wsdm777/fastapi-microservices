from pydantic import BaseModel, Field


class UserInfo(BaseModel):
    id: int
    login: str
    name: str
    surname: str
    rank_id: int

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    login: str = Field(min_length=4, max_length=16)
    password: str = Field(min_length=4, max_length=50)
    name: str
    surname: str
    rank_id: int


class UserChangePasswordInfo(BaseModel):
    id: int
    login: str
    new_password: str = Field(min_length=4, max_length=50)
