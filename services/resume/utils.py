from fastapi import HTTPException, status
import jwt

from config import JWT_PUBLIC


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            JWT_PUBLIC,
            algorithms=["RS256"],
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
