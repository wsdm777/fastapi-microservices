from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.session import get_async_session
from database.models import User
from redis_client.redis import RedisRepository
from user.schemas import UserCreate, UserFilterParams, UserInfo
from user.schemas import UserChangePasswordInfo
from user.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.user_repository = UserRepository(session)
        self.redis = RedisRepository()
        self.session = session

    async def register(self, new_user: UserCreate) -> User:
        user = User.create_user_obj(new_user)
        try:
            self.user_repository.add(user)
            await self.session.commit()
            await self.session.refresh(user)

        except IntegrityError as e:
            error = str(e.orig)

            if "unique constraint" in error.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this login already exists",
                )
            elif "foreign key constraint" in error.lower():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified rank does not exist",
                )

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error occurred",
            )
        return user

    async def change_password(self, user_data: UserChangePasswordInfo):
        password = User.hash_password(user_data.new_password)
        res = await self.user_repository.update_user_password(user_data.login, password)
        if res != 1:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )

        await self.session.commit()

        await self.redis.invalidate_user_tokens(user_data.id)

        return True

    async def get_user(self, user_id: int):
        user = await self.user_repository.get_user(user_id, load_related=True)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        return {
            "id": user.id,
            "login": user.login,
            "name": user.name,
            "surname": user.surname,
            "rank_name": user.rank.name,
            "rank_level": user.rank.level,
        }

    async def list_users(self, params: UserFilterParams):
        users = await self.user_repository.get_users(params=params)
        users_list = []

        for user in users:
            users_list.append(
                UserInfo.model_validate(
                    {
                        "id": user.id,
                        "login": user.login,
                        "name": user.name,
                        "surname": user.surname,
                        "rank_name": user.rank.name,
                        "rank_level": user.rank.level,
                    }
                )
            )

        next_cursor = users_list[-1].id if len(users) == params.limit else None

        return users_list, next_cursor

    async def remove_user(self, user_id: int) -> UserInfo:
        rowcount = await self.user_repository.remove_user_by_id(user_id)
        if rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        await self.session.commit()
