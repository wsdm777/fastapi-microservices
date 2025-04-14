from sqlalchemy import and_, asc, delete, desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Rank, User
from sqlalchemy.orm import joinedload, contains_eager

from user.schemas import UserFilterParams


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, obj):
        self.session.add(obj)


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

    async def update_user_password(self, login: str, password: str) -> bool:
        stmt = update(User).filter(User.login == login).values(password_hash=password)
        res = await self.session.execute(stmt)
        return res.rowcount

    async def get_users(self, params: UserFilterParams):
        query = select(User).join(User.rank).options(contains_eager(User.rank))

        sort_type = asc if params.sort_order == "asc" else desc

        query = query.order_by(
            sort_type(Rank.level),
            sort_type(User.surname),
            sort_type(User.name),
            sort_type(User.id),
        )

        filters = []
        if params.level is not None:
            filters.append(Rank.level == params.level)
        if params.rank is not None:
            filters.append(User.rank_id == params.rank)
        if params.name is not None:
            filters.append(User.name.ilike(f"%{params.name}%"))
        if params.surname is not None:
            filters.append(User.surname.ilike(f"%{params.surname}%"))
        if filters:
            query = query.filter(and_(*filters))

        if params.cursor:
            cursor_value = int(params.cursor)
            if params.sort_order == "asc":
                query = query.filter(User.id > cursor_value)
            else:
                query = query.filter(User.id < cursor_value)

        query = query.limit(params.limit)
        res = await self.session.execute(query)
        return res.scalars().all()

    async def remove_user_by_id(self, user_id: int) -> int:
        stmt = delete(User).filter(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.rowcount
