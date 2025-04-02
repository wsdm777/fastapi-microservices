from os import access
from fastapi import APIRouter, Depends

from auth.schemas import LoginResponse, UserCreadentials
from auth.service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("login", response_model=LoginResponse)
async def login(creds: UserCreadentials, service: AuthService = Depends(AuthService)):
    access, refresh = await service.login(
        login=creds.login, password=creds.password, fingerprint=creds.fingerprint
    )
    return LoginResponse(access_token=access, refresh_token=refresh)
