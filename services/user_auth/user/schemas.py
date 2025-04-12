from enum import Enum
from pydantic import BaseModel, Field


class UserRankInfo(BaseModel):
    id: int
    name: str
    level: int

    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    id: int
    login: str
    name: str
    surname: str
    rank: UserRankInfo

    class Config:
        from_attributes = True


class UserRegisterInfo(BaseModel):
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


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class UserFilterParams(BaseModel):
    rank: int | None = None
    level: int | None = None
    name: str | None = None
    surname: str | None = None
    limit: int = Field(gt=0, le=100, default=20)
    cursor: str | None = None
    sort_order: SortOrder = SortOrder.asc


class UserPaginateResponse(BaseModel):
    users: list[UserInfo] | None = None
    next_cursor: int | None = None


class ReponseOk(BaseModel):
    message: str = Field(examples=["ok"])
