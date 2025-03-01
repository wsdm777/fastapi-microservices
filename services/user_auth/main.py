from fastapi import FastAPI

app = FastAPI()


@app.post("/ping")
async def greet():
    return "pong"
