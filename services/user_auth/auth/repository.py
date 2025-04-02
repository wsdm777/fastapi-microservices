from sqlalchemy.ext.asyncio import AsyncSession

from user.repository import BaseRepository


class AuthRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
