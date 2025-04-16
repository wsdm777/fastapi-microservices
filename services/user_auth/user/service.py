from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from database.session import get_async_session
from database.models import User
from redis_client.redis import RedisRepository
from rank.repository import RankRepository
from user.schemas import UserCreate, UserFilterParams, UserInfo
from user.schemas import UserChangePasswordInfo
from user.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.user_repository = UserRepository(session)
        self.rank_repository = RankRepository(session)
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
        return UserInfo.model_validate(user)

    async def list_users(self, params: UserFilterParams):
        users = await self.user_repository.get_users(params=params)
        users_list = []

        for user in users:
            users_list.append(UserInfo.model_validate(user))

        next_cursor = users_list[-1].id if len(users) == params.limit else None

        return users_list, next_cursor

    async def remove_user(self, user_id: int, user_level: int):
        rank_id = await self.user_repository.remove_user_by_id(user_id)

        if rank_id is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        rank = await self.rank_repository.get_rank(rank_id)
        rank_level = rank[2]

        if rank_level < user_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot delete this user",
            )

        await self.session.commit()

    async def change_user_rank(
        self, user_level: int, rank_id: int, changed_user_id: int
    ):
        """Меняет ранг пользователя

        Args:
            user_level (int): Уровень доступа пользователя который изменяет ранг
            rank_id (int): Id нового ранга
            changed_user_id (int): Пользователь чей ранг изменяется

        """
        rank = await self.rank_repository.get_rank(rank_id)

        if rank is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rank not found",
            )

        rank_level = rank[2]

        if rank_level < user_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot set this rank",
            )

        changed_user = await self.user_repository.get_user(
            changed_user_id, load_related=True, for_update=True
        )

        if changed_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if changed_user.rank.level < user_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change this user",
            )

        await self.user_repository.change_user_rank(changed_user_id, rank_id)
        await self.session.commit()
