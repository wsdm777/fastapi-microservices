from logging.config import fileConfig
from sqlalchemy import Connection, engine_from_config, text
from sqlalchemy import pool
from alembic import context
from database.models import Base, User
from config import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_USER,
    SUPERUSER_EMAIL,
    SUPERUSER_PASSWORD,
)

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
        schema = "user_auth"

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=schema,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()

        create_superuser_if_not_exists(connection=connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
