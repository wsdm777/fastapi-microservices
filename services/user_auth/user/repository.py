from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Rank, User
from sqlalchemy.orm import joinedload


class BaseRepository:
    def __init__(self, session: AsyncSession, schema="user_auth"):
        self.session = session
        self.schema = schema
        self._set_schema()

    async def _set_schema(self):
        query = text("SET search_path TO :schema").bindparams(schema=self.schema)
        await self.session.execute(query)

    async def add(self, obj):
        await self.session.add(obj)

    async def delete(self, obj):
        await self.session.delete(obj)


class UserRepository(BaseRepository):
    def __init__(self, session: AsyncSession, schema):
        super().__init__(session, schema)

    async def get_by_id(self, id, load_related=False):
        query = select(User).filter(User.id == id)
        if load_related:
            query = query.options(joinedload(User.rank))
        return await self.session.scalars(query).one_or_none()
