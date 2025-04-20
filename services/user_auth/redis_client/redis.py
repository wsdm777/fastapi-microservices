from datetime import datetime, timezone
import logging
from redis.asyncio import Redis

from config import REDIS_HOST, REDIS_PORT
from database.models import ACCESS_TOKEN_MINUTES_TTL

logger = logging.getLogger(__name__)


class RedisRepository:
    def __init__(self):
        self.redis = Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
        )

    async def invalidate_user_tokens(self, user_id: int) -> bool:
        try:
            current_time = int(datetime.now(timezone.utc).timestamp())
            await self.redis.setex(
                name=f"user: {user_id}",
                time=ACCESS_TOKEN_MINUTES_TTL * 60,
                value=current_time,
            )
            logger.info(f"Invalidate user {user_id} tokens")
            return True
        except Exception as e:
            logger.exception(f"Exception while invalidate user {user_id} tokens")
            raise ValueError(f"Ошибка {e}")

    async def get_user_last_changes(self, user_id: int) -> str | None:
        try:
            return await self.redis.get(f"user: {user_id}")
        except Exception as e:
            logger.exception(
                f"Exception while get user {user_id} last changes from redis"
            )
            raise ValueError(f"Ошибка {e}")
