from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RefreshToken
from user.repository import BaseRepository


class AuthRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def delete_refresh_token(self, token_jti: str):
        stmt = delete(RefreshToken).filter(RefreshToken.refresh_jti == token_jti)
        result = await self.session.execute(stmt)
        return result.rowcount
