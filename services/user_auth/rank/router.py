from fastapi import APIRouter, Depends, Path

from rank.schemas import RankInfo
from auth.schemas import AccessTokenInfo
from dependencies.dependencies import get_current_user
from rank.service import RankService


router = APIRouter(prefix="/ranks", tags=["ranks"])


@router.get("/{rank_id}", response_model=RankInfo, summary="Получение ранга")
async def get_user(
    rank_id: int = Path(gt=0),
    user: AccessTokenInfo = Depends(get_current_user),
    service: RankService = Depends(RankService),
):
    return await service.get_rank(rank_id)
