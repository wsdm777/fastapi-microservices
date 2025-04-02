from fastapi import FastAPI
from auth.router import router as authRouter

app = FastAPI()


@app.post("/ping")
async def status():
    return {"message": "ok"}


app.include_router(authRouter)
