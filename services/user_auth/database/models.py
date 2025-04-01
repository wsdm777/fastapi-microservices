from datetime import date, timedelta
from sqlalchemy import Column, Date, ForeignKey, Index, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

REFRESH_TOKEN_DAY_TTL = 30


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_auth"}

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(nullable=False, unique=True)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    rank_id: Mapped[int] = mapped_column(ForeignKey("user_auth.ranks.id"))
    password_hash: Mapped[str] = mapped_column(nullable=False)
    rank = relationship("Rank")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_auth.users.id", ondelete="CASCADE"), index=True
    )
    refresh_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    fingerprint: Mapped[str] = mapped_column(nullable=False)
    expired_at: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date() + timedelta(days=REFRESH_TOKEN_DAY_TTL),
        nullable=False,
    )

    user = relationship(User)

    __table_args__ = {"schema": "user_auth"}


class Rank(Base):
    __tablename__ = "ranks"
    __table_args__ = {"schema": "user_auth"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    level: Mapped[int] = mapped_column(nullable=False, unique=True)

    permissions = relationship(
        "Permission", secondary="rank_permissions", back_populates="ranks"
    )


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = {"schema": "user_auth"}

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    ranks = relationship(
        "Rank", secondary="rank_permissions", back_populates="permissions"
    )


rank_permissions = Table(
    "rank_permissions",
    Base.metadata,
    Column(
        "rank_id",
        ForeignKey("user_auth.ranks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        ForeignKey("user_auth.permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    schema="user_auth",
)
