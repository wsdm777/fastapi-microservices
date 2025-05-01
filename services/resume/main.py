from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from middleware import CurrentUserMiddleware, MetricsMiddleware, RequestIdMiddleware
from config import MONGO_URL
from resume.models import Resume
from resume.router import router as ResumeRouter
from logger import setup_logging
from kafka_client.consumer import start_kafka_consumer, stop_kafka_consumer

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    client = AsyncIOMotorClient(MONGO_URL)
    database = client["hrm"]
    await init_beanie(database=database, document_models=[Resume])

    app.state.mongo_client = client
    await start_kafka_consumer()
    yield

    await stop_kafka_consumer()
    client.close()


app = FastAPI(root_path="/resume-api", lifespan=lifespan)


app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(CurrentUserMiddleware)


@app.get("/ping")
async def status():
    logger.info("Проверка статуса")
    return {"message": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(ResumeRouter)
