import logging
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.repository import AuthRepository
from auth.schemas import RefreshCreate, RefreshingAccess, UserCreadentials
from user.repository import UserRepository
from database.models import RefreshToken, User
from database.session import get_async_session
from auth.utils import (
    decode_token,
    generate_access_token,
    generate_refresh_token,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.user_repository = UserRepository(session)
        self.auth_repository = AuthRepository(session)
        self.session = session

    async def authenticate_user(self, login: str, password: str, password_hash) -> bool:
        if not User.verify_password(password, password_hash):
            logger.warning(f"Bad credentials for user {login}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
            )
        return True

    async def login(self, user: UserCreadentials) -> tuple[str, str]:

        user_orm = await self.user_repository.get_user(
            login=user.login, load_related=True
        )

        if user_orm is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
            )

        await self.authenticate_user(user.login, user.password, user_orm.password_hash)

        fingerprint = user.fingerprint

        ref_token, ref_jti = generate_refresh_token(user_orm.id)
        access_token = generate_access_token(user_orm, ref_jti)

        token = RefreshToken.create_token_obj(
            RefreshCreate(
                user_id=user_orm.id, refresh_jti=ref_jti, fingerprint=fingerprint
            )
        )
        logger.info("Login")
        self.auth_repository.add(token)
        await self.session.commit()

        return access_token, ref_token

    async def logout(self, ref_jti: str):
        deleted_rows = await self.auth_repository.delete_refresh_token(ref_jti)
        if deleted_rows > 1:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        logger.info(f"Logout, delete refresh token {ref_jti}")
        await self.session.commit()

    async def refresh_access(self, data: RefreshingAccess) -> tuple[str, str]:
        """
        Удаление старого refresh токена и выдача новой пары access refresh
        """
        refresh_info = decode_token(token=data.refresh_token, token_type="refresh")
        token = await self.auth_repository.get_refresh_token(jti=refresh_info["jti"])
        if token is None or token.fingerprint != data.fingerprint:
            if token:
                logger.warning(
                    f"Wrong fingerprint {data.fingerprint} while refresh a pair of tokens for user {token.user_id}"
                )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
            )
        await self.auth_repository.delete_refresh_token(refresh_info["jti"])

        user = await self.user_repository.get_user(id=token.user_id, load_related=True)

        if user is None:
            logger.warning(
                f"Trying to refresh a pair of tokens for non-existed user {token.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        ref_token, ref_jti = generate_refresh_token(user.id)
        access_token = generate_access_token(user, ref_jti)

        token = RefreshToken.create_token_obj(
            RefreshCreate(
                user_id=user.id, refresh_jti=ref_jti, fingerprint=data.fingerprint
            )
        )

        self.auth_repository.add(token)
        await self.session.commit()

        logger.info("Refresh a pair of tokens")

        return access_token, ref_token
