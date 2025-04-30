import os

with open("public.pem", "rb") as file:
    JWT_PUBLIC = file.read().decode("utf-8").replace("\r", "")


REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = 6379
MONGO_HOST = os.getenv("MONGO_HOST", "mongo")
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "mongo")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "mongo")
MONGO_URL = f"mongodb://{MONGO_PASS}:{MONGO_PASS}@{MONGO_HOST}:27017"
KAFKA_URL = os.getenv("KAFKA_URL", "kafka:9091")
SCHEMA_REGISTRY_URL = os.getenv("SCHEMA_REGISTRY_URL", "schema-registry:8081")
