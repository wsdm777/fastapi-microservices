from pydantic import BaseModel


class UserInfo(BaseModel):
    id: int
    login: str
    name: str
    surname: str
    rank_id: int

    class Config:
        from_attributes = True
