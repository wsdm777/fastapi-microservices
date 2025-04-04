import os

from dotenv import load_dotenv

if not os.getenv("POSTGRES_HOST"):
    load_dotenv("../../infra/.env")
    load_dotenv(".env")
else:
    with open("private.pem", "rb") as file:
        JWT_PRIVATE = file.read().decode("utf-8").replace("\r", "")

    with open("public.pem", "rb") as file:
        JWT_PUBLIC = file.read().decode("utf-8").replace("\r", "")

DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
SUPERUSER_EMAIL = os.getenv("SUPERUSER_LOGIN")
SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD")
SERVICE_NAME = os.getenv("SERVICE_NAME")
