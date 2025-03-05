from logging.config import fileConfig
import re
from sqlalchemy import engine_from_config, text
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context
from database.models import Base
from config import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_USER,
    SERVICE_NAME,
    SUPERUSER_EMAIL,
    SUPERUSER_PASSWORD,
)
from repository.user_repo import hash_password

config = context.config

section = config.config_ini_section
config.set_section_option(section, "DB_HOST", DB_HOST)
config.set_section_option(section, "DB_USER", DB_USER)
config.set_section_option(section, "DB_NAME", DB_NAME)
config.set_section_option(section, "DB_PASS", DB_PASS)
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def create_superuser_if_not_exists(connection: Connection):
    # Проверяем, есть ли хотя бы один суперпользователь
    query_check_admin = text(
        """
        SELECT 1 FROM users WHERE is_superuser = true LIMIT 1
    """
    )
    result = connection.execute(query_check_admin).fetchone()

    # Если суперпользователь уже существует, выходим из функции
    if result:
        print("[INFO] Superuser already exists.")
        return

    # Если суперпользователь не найден, хешируем пароль и создаем нового
    password_hash = hash_password(SUPERUSER_PASSWORD)

    query_create_admin = text(
        """
        INSERT INTO users (username, password_hash, is_superuser)
        VALUES (:username, :password_hash, true)
    """
    )
    connection.execute(
        query_create_admin,
        {
            "username": SUPERUSER_EMAIL,
            "password_hash": password_hash,
        },
    )
    connection.commit()
    print("[INFO] Superuser created.")


def get_schemas(connection: Connection):
    result = connection.execute(
        text(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE :pattern"
        ),
        {"pattern": f"%_{SERVICE_NAME}"},
    )
    return [row[0] for row in result.fetchall()]


def is_valid_schema_name(schema: str) -> bool:
    # Проверка на допустимые символы: буквы, цифры и подчеркивания
    return bool(re.match(r"^[a-zA-Z0-9_]+$", schema))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        schemas = get_schemas(connection)
        if not schemas:
            print(f"[INFO] No schemas found for service: {SERVICE_NAME}")
            return

        for schema in schemas:
            print(f"[INFO] Running migrations for schema: {schema}")

            if not is_valid_schema_name(schema):
                print(f"[ERROR] Invalid schema name: {schema}")
                continue

            query = text(f"SET search_path TO {schema}")
            connection.execute(query)

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                version_table_schema=schema,
                include_schemas=True,
            )

            with context.begin_transaction():
                context.run_migrations()

            connection.commit()

            print(f"[SUCCESS] Done: {schema}")


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
