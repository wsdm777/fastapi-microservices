import os

from dotenv import load_dotenv

if not os.getenv("DOCKER_ENV"):
    load_dotenv("../../infra/.env")
    load_dotenv(".env")


DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
SUPERUSER_EMAIL = os.getenv("SUPERUSER_EMAIL")
SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD")
SERVICE_NAME = os.getenv("SERVICE_NAME")
