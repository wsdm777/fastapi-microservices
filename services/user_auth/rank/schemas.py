from pydantic import BaseModel


class RankInfo(BaseModel):
    id: int
    name: str
    level: int

    class Config:
        from_attributes = True


class RankGetInfo(RankInfo):
    user_count: int


class RankCreate(BaseModel):
    name: str
    level: int


class RanksInfo(BaseModel):
    ranks: list[RankGetInfo]
