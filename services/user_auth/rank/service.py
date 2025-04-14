from fastapi import Depends, HTTPException, status
from database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from rank.repository import RankRepository
from rank.schemas import RankCreate, RankGetInfo, RankInfo
from database.models import Rank


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
        return RankGetInfo.model_validate(rank._asdict())

    async def add_rank(self, rank_info: RankCreate):
        rank = Rank.create_rank_obj(rank_info)
        try:
            self.rank_repository.add(rank)
            await self.session.commit()
            await self.session.refresh(rank)

        except IntegrityError as e:
            error = str(e.orig)

            if "unique constraint" in error.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this level or name already exists",
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error occurred",
            )
        return rank
