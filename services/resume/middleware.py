from time import time
import uuid

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

from utils import decode_token, security
from schemas import AccessTokenInfo

request_id_ctx_var: ContextVar[str] = ContextVar("request_id")


def get_request_id() -> str:
    return request_id_ctx_var.get()


current_user_ctx_var: ContextVar[AccessTokenInfo | None] = ContextVar(
    "current_user", default=None
)


def get_current_user_from_ctx() -> AccessTokenInfo | None:
    return current_user_ctx_var.get()


current_user_id_ctx_var: ContextVar[int | None] = ContextVar(
    "current_user_id", default=None
)


def get_current_user_id_from_ctx():
    return current_user_id_ctx_var.get()


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_ctx_var.set(request_id)

        response: Response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        return response


class CurrentUserMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        credentials = await security(request)

        if credentials:
            try:
                token = credentials.credentials
                payload = decode_token(token)
                payload["id"] = int(payload["sub"])
                payload.pop("sub")
                user = AccessTokenInfo.model_validate(payload)
                current_user_ctx_var.set(user)
                current_user_id_ctx_var.set(user.id)
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code, content={"detail": e.detail}
                )

        response = await call_next(request)
        return response


REQUEST_COUNTER = Counter(
    "fastapi_requests_total",
    "Total HTTP requests",
    ["app_name", "method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "fastapi_request_duration_seconds",
    "Request duration",
    ["app_name", "method", "endpoint"],
)

IN_PROGRESS = Gauge(
    "fastapi_requests_in_progress",
    "Requests in progress",
    ["app_name", "method", "endpoint"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        app_name = "resume"
        method = request.method
        endpoint = request.url.path.replace("/resume-api", "")
        status = 500

        labels_base = dict(app_name=app_name, method=method, endpoint=endpoint)
        IN_PROGRESS.labels(**labels_base).inc()
        start = time()

        response = await call_next(request)
        status = response.status_code

        duration = time() - start
        REQUEST_COUNTER.labels(
            app_name=app_name,
            method=method,
            endpoint=endpoint,
            status=status,
        ).inc()
        REQUEST_DURATION.labels(**labels_base).observe(duration)
        IN_PROGRESS.labels(**labels_base).dec()

        return response
