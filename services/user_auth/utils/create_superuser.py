from sqlalchemy import text
from config import SUPERUSER_USERNAME, SUPERUSER_PASSWORD


def create_superuser(connection):
    check_query = text(
        """
        SELECT 1 FROM users WHERE is_superuser = true LIMIT 1
    """
    )

    result = connection.execute(check_query).first()
    if result:
        return

    query = text(
        """
        INSERT INTO users (username, password, is_superuser)
        SELECT :username, :password, true
        WHERE NOT EXISTS (
            SELECT 1 FROM users WHERE username = :username
        )
    """
    )

    connection.execute(
        query,
        {
            "username": SUPERUSER_USERNAME,
            "password": SUPERUSER_PASSWORD,
        },
    )
    connection.commit()
