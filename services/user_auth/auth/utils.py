from datetime import datetime, timedelta, timezone
import uuid
import bcrypt
import jwt

from config import JWT_PRIVATE
from database.models import ACCESS_TOKEN_MINUTES_TTL, REFRESH_TOKEN_DAY_TTL, User


def generate_refresh_token(
    user_id: int, expires_delta: timedelta = timedelta(days=REFRESH_TOKEN_DAY_TTL)
) -> tuple[str, str]:
    expire = datetime.now(timezone.utc) + expires_delta
    jti = str(uuid.uuid4())
    payload = {"exp": expire, "jti": jti, "sub": user_id}
    token = jwt.encode(payload=payload, key=JWT_PRIVATE, algorithm="RS256")
    return token, jti


def generate_access_token(
    user: User,
    refresh_token_jti: str,
    expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_MINUTES_TTL),
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    issued_time = int(datetime.now(timezone.utc).timestamp())
    payload = {
        "sub": str(user.id),
        "login": user.login,
        "level": user.rank.level,
        "ref_jti": refresh_token_jti,
        "exp": expire,
        "iat": issued_time,
    }
    token = jwt.encode(payload=payload, key=JWT_PRIVATE, algorithm="RS256")
    return token
