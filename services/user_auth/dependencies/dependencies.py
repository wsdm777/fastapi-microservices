from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from auth.utils import decode_access_token
from auth.schemas import AccessTokenInfo
from redis_client.redis import RedisRepository

security = HTTPBearer()

#     max_level: int | None = Query(default=None, include_in_schema=False),


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis: RedisRepository = Depends(RedisRepository),
) -> AccessTokenInfo:
    token = credentials.credentials
    payload = decode_access_token(token)

    payload["id"] = int(payload["sub"])
    payload.pop("sub")

    timestamp = await redis.get_user(payload["id"])
    if timestamp is not None:
        if payload["iat"] < int(timestamp):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
    return AccessTokenInfo.model_validate(payload)


def require_max_level(max_level: int):
    def dependency(
        current_user: AccessTokenInfo = Depends(get_current_user),
    ) -> AccessTokenInfo:
        if current_user.level > max_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required access level {max_level} or higher",
            )
        return current_user

    return Depends(dependency)
