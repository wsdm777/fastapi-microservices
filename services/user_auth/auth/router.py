from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from auth.schemas import (
    AccessTokenInfo,
    LoginResponse,
    RefreshingAccess,
    UserCreadentials,
)
from auth.service import AuthService
from dependencies.dependencies import get_current_user
from user.schemas import ResponseOk


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, summary="Авторизация")
async def login(creds: UserCreadentials, service: AuthService = Depends(AuthService)):
    access, refresh = await service.login(creds)
    return LoginResponse(access_token=access, refresh_token=refresh)


@router.post("/logout", response_model=ResponseOk, summary="Удаление refresh токена")
async def logout(
    user: AccessTokenInfo = Depends(get_current_user),
    service: AuthService = Depends(AuthService),
):
    await service.logout(user.ref_jti)
    return JSONResponse(content={"message": "ok"})


@router.post(
    "/refresh", response_model=LoginResponse, summary="Обновление access токена"
)
async def refresh_access_token(
    data: RefreshingAccess, service: AuthService = Depends(AuthService)
):
    access, refresh = await service.refresh_access(data)
    return LoginResponse(access_token=access, refresh_token=refresh)
