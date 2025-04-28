from sqlalchemy import and_, asc, delete, desc, select, tuple_, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Rank, User
from sqlalchemy.orm import contains_eager, selectinload

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
        for_update: bool = False,
    ) -> User | None:
        query = select(User)
        if not login and not id:
            raise ValueError("Enter id or login")
        if for_update:
            query = query.with_for_update()
        if id:
            query = query.filter(User.id == id)
        if login:
            query = query.filter(User.login == login)
        if load_related:
            query = query.options(selectinload(User.rank))
        return (await self.session.scalars(query)).one_or_none()

    async def get_user_password(self, login: str) -> str | None:
        query = select(User.password_hash).filter(User.login == login)
        return (await self.session.execute(query)).scalar_one_or_none()

    async def update_user_password(self, login: str, password: str) -> int:
        stmt = update(User).filter(User.login == login).values(password_hash=password)
        return (await self.session.execute(stmt)).rowcount

    async def get_users(self, params: UserFilterParams):
        query = select(User).join(User.rank).options(contains_eager(User.rank))

        sort_type = asc if params.sort_order == "asc" else desc

        query = query.order_by(
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

        cursor = params.decoded_cursor

        if cursor is not None:
            if params.sort_order == "asc":
                query = query.filter(
                    tuple_(User.id, User.surname, User.name)
                    > (cursor.id, cursor.surname, cursor.name)
                )
            else:
                query = query.filter(
                    tuple_(User.id, User.surname, User.name)
                    < (cursor.id, cursor.surname, cursor.name)
                )

        query = query.limit(params.limit)
        return (await self.session.execute(query)).scalars().all()

    async def remove_user_by_id(self, user_id: int) -> int | None:
        stmt = delete(User).filter(User.id == user_id).returning(User.rank_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def change_user_rank(self, user_id: int, rank_id: int):
        stmt = update(User).filter(User.id == user_id).values(rank_id=rank_id)
        await self.session.execute(stmt)
