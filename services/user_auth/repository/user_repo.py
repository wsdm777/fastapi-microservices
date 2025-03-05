from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import bcrypt
from database.models import User


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


class UserRepository:
    def __init__(self, session: AsyncSession, schema):
        self.session = session
        self.schema = schema
        self._set_schema()

    async def _set_schema(self):
        query = text("SET search_path TO :schema").bindparams(schema=self.schema)
        await self.session.execute(query)

    async def create_user(self, username: str, password_hash: str):
        user = User(username=username, password_hash=password_hash)
        self.session.add(user)
        await self.session.commit()
        return user
