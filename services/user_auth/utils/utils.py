from datetime import datetime, timedelta, timezone
import uuid
import bcrypt
from sqlalchemy import Connection, text
import jwt

from config import JWT_PRIVATE, SUPERUSER_EMAIL, SUPERUSER_PASSWORD
from database.models import ACCESS_TOKEN_MINUTES_TTL, REFRESH_TOKEN_DAY_TTL, User


def create_superuser_if_not_exists(connection: Connection):
    query = text(f"SET search_path TO user_auth")
    connection.execute(query)

    connection.commit()

    query_check_admin = text(
        """
        SELECT 1 FROM users LIMIT 1
    """
    )
    result = connection.execute(query_check_admin).fetchone()

    if result:
        return

    print("Creating root user")

    password_hash = hash_password(SUPERUSER_PASSWORD)

    result = connection.execute(
        text("INSERT INTO ranks (name, level) VALUES ('owner', 0) RETURNING id")
    )
    new_rank_id = result.scalar()
    stmt_create_admin = text(
        """
        INSERT INTO users (login, name, surname, rank_id, password_hash)
        VALUES (:login, 'root', 'root', :rank, :password_hash)
    """
    )
    connection.execute(
        stmt_create_admin,
        {
            "login": f"{SUPERUSER_EMAIL}",
            "rank": new_rank_id,
            "password_hash": password_hash,
        },
    )
    connection.commit()
    print("[INFO] Superuser created.")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def generate_refresh_token(
    user_id: int, expires_delta: timedelta = timedelta(days=REFRESH_TOKEN_DAY_TTL)
) -> tuple[str:str]:
    expire = datetime.now(timezone.utc) + expires_delta
    jti = str(uuid.uuid4())
    payload = {"exp": expire, "jti": jti, "sub": user_id}
    token = jwt.encode(payload=payload, key=JWT_PRIVATE, algorithm="RS256")
    return token, jti


def generate_access_token(
    user: User, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_MINUTES_TTL)
) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": user.id,
        "login": user.login,
        "level": user.rank.level,
        "exp": expire,
    }
    token = jwt.encode(payload=payload, key=JWT_PRIVATE, algorithm="RS256")
    return token
