from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from middleware import MetricsMiddleware, RequestIdMiddleware, CurrentUserMiddleware
from logger import setup_logging
from auth.router import router as AuthRouter
from kafka_client.producer import init_kafka_producer, stop_kafka_producer
from user.router import router as UserRouter
from rank.router import router as RankRouter


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_kafka_producer()
    yield
    await stop_kafka_producer()


app = FastAPI(root_path="/user-api", lifespan=lifespan)

app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(CurrentUserMiddleware)

setup_logging()
logger = logging.getLogger(__name__)


@app.get("/ping")
async def status():
    logger.info("Проверка статуса")
    return {"message": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(AuthRouter)
app.include_router(UserRouter)
app.include_router(RankRouter)
