from datetime import datetime, timedelta, timezone
import uuid
from fastapi import HTTPException, status
import jwt

from config import JWT_PRIVATE, JWT_PUBLIC
from database.models import ACCESS_TOKEN_MINUTES_TTL, REFRESH_TOKEN_DAY_TTL, User


def generate_refresh_token(
    user_id: int, expires_delta: timedelta = timedelta(days=REFRESH_TOKEN_DAY_TTL)
) -> tuple[str, str]:
    expire = datetime.now(timezone.utc) + expires_delta
    jti = str(uuid.uuid4())
    payload = {"exp": expire, "jti": jti, "sub": str(user_id)}
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


def decode_token(token: str, token_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_PUBLIC,
            algorithms=["RS256"],
        )
        if token_type == "access":
            if "ref_jti" not in payload:
                raise HTTPException(
                    status_code=400, detail="Access token must contain ref_jti field"
                )

        if token_type == "refresh":
            if "jti" not in payload:
                raise HTTPException(
                    status_code=400, detail="Refresh token must contain jti field"
                )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
