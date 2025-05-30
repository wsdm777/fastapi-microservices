from datetime import datetime, timedelta
import bcrypt
from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

from auth.schemas import RefreshCreate
from rank.schemas import RankCreate
from user.schemas import UserCreate

REFRESH_TOKEN_DAY_TTL = 30
ACCESS_TOKEN_MINUTES_TTL = 150


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    rank_id: Mapped[int] = mapped_column(ForeignKey("ranks.id"))
    password_hash: Mapped[str] = mapped_column(nullable=False)
    rank = relationship("Rank", back_populates="users")

    @classmethod
    def create_user_obj(cls, user_data: UserCreate) -> "User":
        return cls(
            login=user_data.login,
            password_hash=cls.hash_password(user_data.password),
            name=user_data.name,
            surname=user_data.surname,
            rank_id=user_data.rank_id,
        )

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    refresh_jti: Mapped[str] = mapped_column(nullable=False, unique=True)
    fingerprint: Mapped[str] = mapped_column(nullable=False)
    expired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.timezone("UTC", func.now())
        + timedelta(days=REFRESH_TOKEN_DAY_TTL),
        nullable=False,
        index=True,
    )

    user = relationship(User)

    @classmethod
    def create_token_obj(cls, ref_data: RefreshCreate) -> "RefreshToken":
        return cls(**ref_data.model_dump())


class Rank(Base):
    __tablename__ = "ranks"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    level: Mapped[int] = mapped_column(nullable=False, unique=True)

    users = relationship("User", back_populates="rank")

    @classmethod
    def create_rank_obj(cls, data: RankCreate) -> "Rank":
        return cls(**data.model_dump())
