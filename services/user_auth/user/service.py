import asyncio
import logging
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


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.user_repository = UserRepository(session)
        self.rank_repository = RankRepository(session)
        self.redis = RedisRepository()
        self.session = session

    async def register(self, new_user: UserCreate) -> User:
        """Регистрация пользователя.

        Args:
            new_user (UserCreate): Данные нового пользователя

        - У пользователя должен быть уникальный логин
        - У пользователя должен быть существующий ранг

        Returns:
            User: ORM модель нового пользователя
        """
        user = User.create_user_obj(new_user)
        try:
            self.user_repository.add(user)
            await self.session.commit()
            await self.session.refresh(user)

        except IntegrityError as e:
            error = str(e.orig)

            if "unique constraint" in error.lower():
                logger.warning(
                    f"Trying to register user with an existed login {user.login}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this login already exists",
                )
            elif "foreign key constraint" in error.lower():
                logger.warning(
                    f"Trying to register user with a non-existed rank {user.rank_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Specified rank does not exist",
                )
            logger.exception("Database inegrity error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity error occurred",
            )
        logger.info(f"Registered user {user.id}")
        return user

    async def change_password(self, user_data: UserChangePasswordInfo):
        password = User.hash_password(user_data.new_password)
        res = await self.user_repository.update_user_password(user_data.login, password)
        if res != 1:
            if res == 0:
                logger.error("Can not change password")
            else:
                logger.exception("Trying to change multiple passwords")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )

        await self.session.commit()
        logger.info("Change password")
        await self.redis.invalidate_user_tokens(user_data.id)

    async def get_user(self, user_id: int):
        user = await self.user_repository.get_user(user_id, load_related=True)
        if user is None:
            logger.warning(f"Trying to get a non-existed user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        logger.info(f"Get user {user.id} info")
        return UserInfo.model_validate(user)

    async def list_users(self, params: UserFilterParams) -> tuple[list, int | None]:
        """Получение списка пользователей.

        Args:
            params (UserFilterParams): Параметры пагинации

        Returns:
            tuple[list | None, int | None]: Кортеж в формате (список пользователей, курсор последнего пользователя)
        """
        users = await self.user_repository.get_users(params=params)
        users_list = []

        for user in users:
            users_list.append(UserInfo.model_validate(user))

        next_cursor = users_list[-1].id if len(users) == params.limit else None
        logger.info(f"Get users info with params {params}")
        return users_list, next_cursor

    async def remove_user(self, user_id: int, user_level: int):
        """Удаление пользователя.

        Args:
            user_id (int): ID удаляемого пользователя
            user_level (int): Уровень доступа пользователя, который удаляет

        """
        rank_id = await self.user_repository.remove_user_by_id(user_id)

        if rank_id is None:
            logger.warning(f"Trying to delete a non-existed user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        rank = await self.rank_repository.get_rank(rank_id)

        if rank is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rank not found",
            )

        rank_level = rank[2]

        if rank_level < user_level:
            logger.warning(f"Trying to delete a user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot delete this user",
            )

        logger.info(f"Delete user {user_id}")
        await self.session.commit()

    async def change_user_rank(
        self, user_level: int, rank_id: int, changed_user_id: int
    ):
        """Меняет ранг пользователя, проверяя права вызывающего.

        Args:
            user_level (int): Уровень доступа пользователя который изменяет ранг
            rank_id (int): ID нового ранга
            changed_user_id (int): Пользователь чей ранг изменяется

        """
        rank = await self.rank_repository.get_rank_info(rank_id)

        if rank is None:
            logger.warning(
                f"Trying to set {changed_user_id} a non-existed rank {rank_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rank not found",
            )

        if rank.level < user_level:
            logger.warning(f"Trying to set rank {rank_id} to {changed_user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot set this rank",
            )

        changed_user = await self.user_repository.get_user(
            changed_user_id, load_related=True, for_update=True
        )

        if changed_user is None:
            logger.warning(
                f"Trying to set rank {rank_id} to non-existed user {changed_user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if changed_user.rank.level < user_level:
            logger.warning(f"Trying to change user {changed_user_id} rank to {rank_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot change this user",
            )

        await self.user_repository.change_user_rank(changed_user_id, rank_id)
        await self.session.commit()

        logger.info(f"Change user {changed_user_id} rank to {rank_id}")

        await self.redis.invalidate_user_tokens(changed_user_id)
