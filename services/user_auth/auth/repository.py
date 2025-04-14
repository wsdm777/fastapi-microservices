from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RefreshToken
from user.repository import BaseRepository


class AuthRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def delete_refresh_token(self, token_jti: str) -> int:
        stmt = delete(RefreshToken).filter(RefreshToken.refresh_jti == token_jti)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_refresh_token(self, jti: str) -> RefreshToken:
        query = select(RefreshToken).filter(RefreshToken.refresh_jti == jti)
        token = await self.session.execute(query)
        return token.scalars().one_or_none()
