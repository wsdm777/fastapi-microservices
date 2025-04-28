import logging
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer
import httpx
import jwt

from config import JWT_PUBLIC


security = HTTPBearer(auto_error=False)

logger = logging.getLogger(__name__)


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


async def check_user_exists(user_id: int, request: Request):
    credentials = await security(request)
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    access_token = credentials.credentials
    try:
        async with httpx.AsyncClient(
            base_url="http://user_service:8000", timeout=5.0
        ) as client:
            req_id = request.headers.get("X-Request-ID")
            if req_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
                )

            response = await client.get(
                f"/user-api/users/{user_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Request-ID": req_id,
                },
            )
            response.raise_for_status()

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        detail = e.response.json()
        logger.warning(f"An error occured from user service, {status_code=}")
        raise HTTPException(
            status_code=status_code,
            detail=detail["detail"] or "An error occurred",
        )
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        logger.error("Cannot connect to user service")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable",
        )
