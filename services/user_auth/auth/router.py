from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from auth.schemas import LoginResponse, UserCreadentials
from auth.service import AuthService
from dependencies.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(creds: UserCreadentials, service: AuthService = Depends(AuthService)):
    access, refresh = await service.login(
        login=creds.login, password=creds.password, fingerprint=creds.fingerprint
    )
    return LoginResponse(access_token=access, refresh_token=refresh)


@router.post("/logout")
async def logout(
    user: dict = Depends(get_current_user), service: AuthService = Depends(AuthService)
):
    await service.logout(user["ref_jti"])
    return JSONResponse(content={"message": "ok"})
