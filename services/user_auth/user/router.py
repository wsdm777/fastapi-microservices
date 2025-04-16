from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse

from user.schemas import (
    RankChangeInfo,
    ReponseOk,
    UserChangePasswordInfo,
    UserCreate,
    UserFilterParams,
    UserInfo,
    UserPaginateResponse,
)
from auth.schemas import AccessTokenInfo
from dependencies.dependencies import get_current_user, require_max_level
from user.schemas import UserRegisterInfo
from user.service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRegisterInfo, summary="Регистрация")
async def register(
    new_user: UserCreate,
    user: AccessTokenInfo = require_max_level(2),
    service: UserService = Depends(UserService),
):
    registered_user = await service.register(new_user)
    return UserRegisterInfo.model_validate(registered_user)


@router.patch("/change-password", response_model=ReponseOk, summary="Смена пароля")
async def change_password(
    new_password: str = Body(min_length=4, max_length=50, embed=True),
    user: AccessTokenInfo = Depends(get_current_user),
    service: UserService = Depends(UserService),
):
    await service.change_password(
        UserChangePasswordInfo(login=user.login, id=user.id, new_password=new_password)
    )
    return JSONResponse(content={"message": "ok"})


@router.get(
    "/list", response_model=UserPaginateResponse, summary="Список пользователей"
)
async def get_users(
    params: UserFilterParams = Query(),
    service: UserService = Depends(UserService),
    user: AccessTokenInfo = Depends(get_current_user),
):
    users_list, cursor = await service.list_users(params=params)
    return UserPaginateResponse.model_validate(
        {"users": users_list, "next_cursor": cursor}
    )


@router.get("/{user_id}", response_model=UserInfo, summary="Получение пользователя")
async def get_user(
    user_id: int = Path(gt=0),
    user: AccessTokenInfo = Depends(get_current_user),
    service: UserService = Depends(UserService),
):
    return await service.get_user(user_id)


@router.delete("/{user_id}", response_model=ReponseOk, summary="Удаление пользователя")
async def delete_user(
    user_id: int = Path(gt=0),
    user: AccessTokenInfo = require_max_level(2),
    service: UserService = Depends(UserService),
):
    if user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Can not delete yourself"
        )
    await service.remove_user(user_id, user.level)
    return JSONResponse(content={"message": "ok"})


@router.patch("/", response_model=ReponseOk, summary="Смена ранга пользователя")
async def change_user_rank(
    data: RankChangeInfo,
    user: AccessTokenInfo = require_max_level(2),
    service: UserService = Depends(UserService),
):
    if user.id == data.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Can not change yourself"
        )
    await service.change_user_rank(user.level, data.rank_id, data.user_id)
    return JSONResponse(content={"message": "ok"})
