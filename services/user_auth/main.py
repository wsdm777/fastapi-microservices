from fastapi import FastAPI

app = FastAPI()


@app.post("/ping")
async def status():
    return {"message": "ok"}
