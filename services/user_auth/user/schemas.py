import base64
from enum import Enum
import json
from fastapi import HTTPException, Query, status
from pydantic import BaseModel, Field

from rank.schemas import RankInfo


class RankChangeInfo(BaseModel):
    user_id: int
    rank_id: int


class UserInfo(BaseModel):
    id: int
    login: str
    name: str
    surname: str
    rank: RankInfo

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


class Cursor(BaseModel):
    surname: str
    name: str
    id: int


def cursor_validate(value: str) -> Cursor:
    try:
        decoded_bytes = base64.urlsafe_b64decode(value.encode())
        data = json.loads(decoded_bytes.decode())
        return Cursor(**data)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid base64 encoded cursor",
        )


class UserFilterParams(BaseModel):
    rank: int | None = None
    level: int | None = None
    name: str | None = None
    surname: str | None = None
    limit: int = Field(gt=0, le=100, default=20)
    cursor: str | None = Query(default=None, description="Cursor as base64 string")
    sort_order: SortOrder = SortOrder.asc

    @property
    def decoded_cursor(self) -> Cursor | None:
        if self.cursor is None:
            return None
        return cursor_validate(self.cursor)


class UserPaginateResponse(BaseModel):
    users: list[UserInfo] | None = None
    next_cursor: Cursor | None = None


class ResponseOk(BaseModel):
    message: str = Field(examples=["ok"])
