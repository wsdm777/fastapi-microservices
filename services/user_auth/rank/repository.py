from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Rank, User
from user.repository import BaseRepository


class RankRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_rank(self, id: int):
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

    async def get_ranks(self):
        query = (
            select(
                Rank.id, Rank.name, Rank.level, func.count(User.id).label("user_count")
            )
            .join(User, Rank.users, isouter=True)
            .group_by(Rank.id)
            .order_by(Rank.id)
        )
        rank = await self.session.execute(query)
        return rank.all()

    async def remove_rank(self, id: int) -> int:
        stmt = delete(Rank).filter(Rank.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount
