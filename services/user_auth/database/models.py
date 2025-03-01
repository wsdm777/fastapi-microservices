from datetime import date, timedelta
from sqlalchemy import Date, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase

REFRESH_TOKEN_DAY_TTL = 30


class Base(DeclarativeBase): ...


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    surname: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[int] = mapped_column()


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    refresh_token: Mapped[str] = mapped_column(nullable=False, unique=True)
    fingerprint: Mapped[str] = mapped_column(nullable=False)
    expired_at: Mapped[date] = mapped_column(
        Date,
        server_default=func.current_date() + timedelta(days=REFRESH_TOKEN_DAY_TTL),
        nullable=False,
    )

    user = relationship(User)

    __table_args__ = (
        Index("ix_refresh_user_id", user_id),
        Index("ix_refresh_token_hash", refresh_token, postgresql_using="hash"),
    )
