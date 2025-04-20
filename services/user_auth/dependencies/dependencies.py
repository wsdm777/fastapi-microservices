import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from middleware import security
from auth.schemas import AccessTokenInfo
from redis_client.redis import RedisRepository
from middleware import get_current_user_from_ctx


logger = logging.getLogger(__name__)


async def get_current_user(
    redis: RedisRepository = Depends(RedisRepository),
    _: HTTPAuthorizationCredentials = Depends(security),
) -> AccessTokenInfo:
    user = get_current_user_from_ctx()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    timestamp = await redis.get_user_last_changes(user.id)
    if timestamp is not None and user.iat.timestamp() < float(timestamp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    return user


def require_max_level(max_level: int):
    def dependency(
        current_user: AccessTokenInfo = Depends(get_current_user),
    ) -> AccessTokenInfo:
        if current_user.level > max_level:
            logger.warning(f"Trying to access a forbidden route")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required access level {max_level} or higher",
            )
        return current_user

    return Depends(dependency)
