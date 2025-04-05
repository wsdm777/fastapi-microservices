from sqlalchemy import Connection, text

from config import SUPERUSER_EMAIL, SUPERUSER_PASSWORD
from database.models import User


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

    password_hash = User.hash_password(SUPERUSER_PASSWORD)

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
