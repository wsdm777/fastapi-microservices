from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from auth.repository import AuthRepository
from auth.schemas import RefreshCreate, UserCreadentials
from user.repository import UserRepository
from database.models import RefreshToken, User
from database.session import get_async_session
from auth.utils import (
    generate_access_token,
    generate_refresh_token,
)


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.user_repository = UserRepository(session)
        self.auth_repository = AuthRepository(session)
        self.session = session

    async def authenticate_user(self, login: str, password: str) -> bool:
        password_hash = await self.user_repository.get_user_password(login)
        if not password_hash or not User.verify_password(password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
            )
        return True

    async def login(self, user: UserCreadentials) -> tuple[str, str]:
        await self.authenticate_user(user.login, user.password)

        fingerprint = user.fingerprint

        user = await self.user_repository.get_user(login=user.login, load_related=True)

        ref_token, ref_jti = generate_refresh_token(user.id)
        access_token = generate_access_token(user, ref_jti)
        token = RefreshToken.create_token_obj(
            RefreshCreate(user_id=user.id, refresh_jti=ref_jti, fingerprint=fingerprint)
        )
        self.auth_repository.add(token)
        await self.session.commit()

        return access_token, ref_token

    async def logout(self, ref_jti: str) -> bool:
        deleted_rows = await self.auth_repository.delete_refresh_token(ref_jti)
        if deleted_rows != 1:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong",
            )
        await self.session.commit()

        return True
