from datetime import datetime, timezone
from redis.asyncio import Redis

from config import REDIS_HOST, REDIS_PORT
from database.models import ACCESS_TOKEN_MINUTES_TTL


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
            return True
        except Exception as e:
            return False

    async def get_user(self, user_id: int):
        try:
            return await self.redis.get(f"user: {user_id}")
        except Exception as e:
            raise ValueError(f"Ошибка {e}")
