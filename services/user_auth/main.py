from fastapi import FastAPI
from auth.router import router as AuthRouter
from user.router import router as UserRouter

app = FastAPI()


@app.post("/ping")
async def status():
    return {"message": "ok"}


app.include_router(AuthRouter)
app.include_router(UserRouter)
