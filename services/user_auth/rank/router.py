from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse

from rank.schemas import RankCreate, RankGetInfo, RankInfo, RanksInfo
from auth.schemas import AccessTokenInfo
from dependencies.dependencies import get_current_user, require_max_level
from rank.service import RankService
from user.schemas import ResponseOk

router = APIRouter(prefix="/ranks", tags=["ranks"])


@router.get("/list", response_model=RanksInfo, summary="Список всех рангов")
async def get_ranks(
    _: AccessTokenInfo = Depends(get_current_user),
    service: RankService = Depends(RankService),
):
    return await service.get_ranks()


@router.get("/{rank_id}", response_model=RankGetInfo, summary="Получение ранга")
async def get_rank(
    rank_id: int = Path(gt=0),
    _: AccessTokenInfo = Depends(get_current_user),
    service: RankService = Depends(RankService),
):
    return await service.get_rank(rank_id)


@router.post("/", response_model=RankInfo, summary="Создание ранга")
async def add_rank(
    data: RankCreate,
    user: AccessTokenInfo = require_max_level(2),
    service: RankService = Depends(RankService),
):
    if data.level <= user.level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create rank with this level",
        )
    return await service.add_rank(data)


@router.delete("/{rank_id}", response_model=ResponseOk, summary="Удаление ранга")
async def remove_rank(
    rank_id: int,
    user: AccessTokenInfo = require_max_level(2),
    service: RankService = Depends(RankService),
):
    await service.remove_rank(rank_id, user.level)
    return JSONResponse(content={"message": "ok"})
