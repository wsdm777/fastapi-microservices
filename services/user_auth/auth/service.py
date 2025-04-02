from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.repository import AuthRepository
from user.repository import UserRepository
from database.models import RefreshToken
from database.session import get_async_session
from utils.utils import generate_access_token, generate_refresh_token, verify_password


class AuthService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.user_repository = UserRepository(session)
        self.auth_repository = AuthRepository(session)
        self.session = session

    async def authenticate_user(self, login: str, password: str) -> bool:
        password_hash = await self.user_repository.get_user_password(login)
        if not password_hash or not verify_password(password, password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
            )
        return True

    async def login(self, login: str, password: str, fingerprint: str):
        await self.authenticate_user(login, password)

        user = await self.user_repository.get_user(login=login, load_related=True)

        ref_token, ref_jti = generate_refresh_token(user.id)
        access_token = generate_access_token(user)

        token = RefreshToken(
            user_id=user.id, refresh_jti=ref_jti, fingerprint=fingerprint
        )

        self.session.add(token)
        await self.session.commit()

        return access_token, ref_token
