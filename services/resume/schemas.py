from datetime import datetime
from pydantic import BaseModel


class AccessTokenInfo(BaseModel):
    id: int
    login: str
    level: int
    ref_jti: str
    exp: datetime
    iat: datetime
