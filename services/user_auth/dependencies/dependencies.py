from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from config import JWT_PUBLIC
from database.session import get_async_session

security = HTTPBearer()


def get_current_user(
    max_level: int | None = Query(default=None, include_in_schema=False),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            JWT_PUBLIC,
            algorithms=["RS256"],
        )
        if max_level is not None:
            if payload["level"] > max_level:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
