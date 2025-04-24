from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from middleware import CurrentUserMiddleware, MetricsMiddleware, RequestIdMiddleware


app = FastAPI(root_path="/resume-api")

app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestIdMiddleware)
app.add_middleware(CurrentUserMiddleware)


@app.get("/ping")
async def status():
    return {"message": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
