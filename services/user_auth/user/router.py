from fastapi import APIRouter, Depends

from auth.schemas import UserCreate
from dependencies.dependencies import get_current_user, security
from user.schemas import UserInfo
from user.service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserInfo)
async def register(
    new_user: UserCreate,
    user: dict = Depends(
        lambda creds=Depends(security): get_current_user(max_level=2, credentials=creds)
    ),
    service: UserService = Depends(UserService),
):
    registered_user = await service.register(new_user)
    return UserInfo.model_validate(registered_user)
