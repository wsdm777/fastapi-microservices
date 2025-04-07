from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.session import get_async_session
from redis_client.redis import RedisRepository
from user.schemas import UserCreate
from database.models import User
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
