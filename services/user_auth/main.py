import logging
from fastapi import FastAPI

from middleware import RequestIdMiddleware
from logger import setup_logging
from auth.router import router as AuthRouter
from user.router import router as UserRouter
from rank.router import router as RankRouter

app = FastAPI()

app.add_middleware(RequestIdMiddleware)

setup_logging()
logger = logging.getLogger(__name__)


@app.post("/ping")
async def status():
    logger.info("Проверка статуса")
    return {"message": "ok"}


app.include_router(AuthRouter)
app.include_router(UserRouter)
app.include_router(RankRouter)
