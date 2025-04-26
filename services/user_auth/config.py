import os

from dotenv import load_dotenv

DB_HOST = os.getenv("POSTGRES_HOST")

if not os.getenv("POSTGRES_HOST"):
    DB_HOST = "localhost"
    load_dotenv("../../infra/.env")
    load_dotenv(".env")
else:
    with open("private.pem", "rb") as file:
        JWT_PRIVATE = file.read().decode("utf-8").replace("\r", "")

    with open("public.pem", "rb") as file:
        JWT_PUBLIC = file.read().decode("utf-8").replace("\r", "")

DB_NAME = os.getenv("POSTGRES_DB", "postgres")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
SUPERUSER_EMAIL = os.getenv("SUPERUSER_LOGIN", "sth@email.com")
SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD", "qwerty")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = 6379
