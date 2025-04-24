import os

from dotenv import load_dotenv


with open("public.pem", "rb") as file:
    JWT_PUBLIC = file.read().decode("utf-8").replace("\r", "")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = 6379
