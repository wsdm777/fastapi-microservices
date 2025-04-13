from fastapi import FastAPI
from auth.router import router as AuthRouter
from user.router import router as UserRouter
from rank.router import router as RankRouter

app = FastAPI()


@app.post("/ping")
async def status():
    return {"message": "ok"}


app.include_router(AuthRouter)
app.include_router(UserRouter)
app.include_router(RankRouter)
