from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RefreshToken
from user.repository import BaseRepository


class AuthRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def delete_refresh_token(self, token_jti: str) -> int:
        stmt = delete(RefreshToken).filter(RefreshToken.refresh_jti == token_jti)
        return (await self.session.execute(stmt)).rowcount

    async def get_refresh_token(self, jti: str) -> RefreshToken | None:
        query = select(RefreshToken).filter(RefreshToken.refresh_jti == jti)
        return (await self.session.execute(query)).scalar_one_or_none()
