from pydantic import BaseModel


class RankInfo(BaseModel):
    id: int
    name: str
    level: int
    user_count: int
