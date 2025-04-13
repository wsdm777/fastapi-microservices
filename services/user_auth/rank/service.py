from fastapi import Depends, HTTPException, status
from database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

from rank.repository import RankRepository
from rank.schemas import RankInfo


class RankService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.rank_repository = RankRepository(session)
        self.session = session

    async def get_rank(self, id):
        rank = await self.rank_repository.get_rank(id)
        if rank is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        return RankInfo.model_validate(rank._asdict())
