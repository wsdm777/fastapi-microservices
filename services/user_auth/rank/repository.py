from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Rank, User
from user.repository import BaseRepository


class RankRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_rank(self, id):
        query = (
            select(
                Rank.id, Rank.name, Rank.level, func.count(User.id).label("user_count")
            )
            .join(User, Rank.users, isouter=True)
            .group_by(Rank.id)
            .filter(Rank.id == id)
        )
        rank = await self.session.execute(query)
        return rank.one_or_none()
