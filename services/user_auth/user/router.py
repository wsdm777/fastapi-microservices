from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse

from user.schemas import UserChangePasswordInfo, UserCreate, UserInfo
from auth.schemas import AccessTokenInfo
from dependencies.dependencies import get_current_user, require_max_level
from user.schemas import UserRegisterInfo
from user.service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserRegisterInfo)
async def register(
    new_user: UserCreate,
    user: AccessTokenInfo = require_max_level(2),
    service: UserService = Depends(UserService),
):
    registered_user = await service.register(new_user)
    return UserRegisterInfo.model_validate(registered_user)


@router.post("/change-password")
async def change_password(
    new_password: str = Body(min_length=4, max_length=50, embed=True),
    user: AccessTokenInfo = Depends(get_current_user),
    service: UserService = Depends(UserService),
):
    await service.change_password(
        UserChangePasswordInfo(login=user.login, id=user.id, new_password=new_password)
    )
    return JSONResponse(content={"message": "ok"})


@router.get("/{user_id}", response_model=UserInfo)
async def get_user(
    user_id: int = Path(gt=0),
    user: AccessTokenInfo = Depends(get_current_user),
    service: UserService = Depends(UserService),
):
    user_data = await service.get_user(user_id)
    return UserInfo.model_validate(user_data)
