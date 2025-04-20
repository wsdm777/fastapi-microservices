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
        return (await self.session.execute(query)).one_or_none()

    async def get_rank_info(self, id: int):
        query = select(Rank).filter(Rank.id == id)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def get_ranks(self):
        query = (
            select(
                Rank.id, Rank.name, Rank.level, func.count(User.id).label("user_count")
            )
            .join(User, Rank.users, isouter=True)
            .group_by(Rank.id)
            .order_by(Rank.id)
        )
        return (await self.session.execute(query)).all()

    async def remove_rank(self, id: int) -> int | None:
        stmt = delete(Rank).filter(Rank.id == id).returning(Rank.level)
        return (await self.session.execute(stmt)).scalar_one_or_none()
