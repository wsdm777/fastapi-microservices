from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from sqlalchemy.orm import joinedload


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_user(
        self,
        id: int | None = None,
        login: str | None = None,
        load_related: bool = False,
    ) -> User | None:
        query = select(User)
        if not login and not id:
            raise ValueError("Enter id or login")
        if id:
            query = query.filter(User.id == id)
        if login:
            query = query.filter(User.login == login)
        if load_related:
            query = query.options(joinedload(User.rank))
        user = await self.session.scalars(query)
        return user.one_or_none()

    async def get_user_password(self, login: str) -> str | None:
        query = select(User.password_hash).filter(User.login == login)
        password = await self.session.scalars(query)
        return password.one_or_none()
