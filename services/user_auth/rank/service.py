import logging
from fastapi import Depends, HTTPException, status
from database.session import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from rank.repository import RankRepository
from rank.schemas import RankCreate, RankGetInfo, RanksInfo
from database.models import Rank

logger = logging.getLogger(__name__)


class RankService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.rank_repository = RankRepository(session)
        self.session = session

    async def get_rank(self, id: int) -> RankGetInfo:
        rank = await self.rank_repository.get_rank(id)
        if rank is None:
            logger.warning(f"Trying to get a non-existed rank {id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )

        logger.info(f"Get rank {id} info")
        return RankGetInfo.model_validate(rank._asdict())

    async def add_rank(self, rank_info: RankCreate) -> Rank:
        rank = Rank.create_rank_obj(rank_info)
        try:
            self.rank_repository.add(rank)
            await self.session.commit()
            await self.session.refresh(rank)

        except IntegrityError as e:
            error = str(e.orig)

            if "unique constraint" in error.lower():
                logger.warning(
                    f"Trying to create rank with an existed name {rank_info.name}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Rank with this level or name already exists",
                )
            logger.exception("Database inegrity error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error occurred",
            )
        logger.info(f"Creared rank {rank.id}")
        return rank

    async def get_ranks(self) -> RanksInfo:
        ranks = await self.rank_repository.get_ranks()
        logger.info("Get ranks info")
        return RanksInfo.model_validate(
            {"ranks": [RankGetInfo.model_validate(rank._asdict()) for rank in ranks]}
        )

    async def remove_rank(self, id: int, user_level: int):
        try:
            rank_level = await self.rank_repository.remove_rank(id)

            if rank_level is None:
                logger.warning(f"Trying to delete a non-existed rank {id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Rank not found",
                )
            if rank_level <= user_level:
                logger.warning(f"Trying to delete rank {id}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot delete this rank",
                )

        except IntegrityError as e:
            error = str(e.orig)
            if "foreign key constraint" in error.lower():
                logger.warning(f"Trying to delete not empty rank {id}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="The rank is not empty",
                )

        logger.info(f"Delete rank{id}")
        await self.session.commit()
