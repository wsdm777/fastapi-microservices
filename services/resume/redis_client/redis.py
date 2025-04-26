import logging
from redis.asyncio import Redis

from config import REDIS_HOST, REDIS_PORT

logger = logging.getLogger(__name__)


class RedisRepository:
    def __init__(self):
        self.redis = Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True
        )

    async def get_user_last_changes(self, user_id: int) -> str | None:
        try:
            return await self.redis.get(f"user: {user_id}")
        except Exception as e:
            logger.exception(
                f"Exception while get user {user_id} last changes from redis"
            )
            raise ValueError(f"Ошибка {e}")
