import uuid
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

from auth.utils import decode_token
from auth.schemas import AccessTokenInfo

request_id_ctx_var: ContextVar[str] = ContextVar("request_id")


def get_request_id() -> str:
    return request_id_ctx_var.get()


security = HTTPBearer(auto_error=False)

current_user_ctx_var: ContextVar[AccessTokenInfo | None] = ContextVar(
    "current_user", default=None
)


def get_current_user_from_ctx() -> AccessTokenInfo | None:
    return current_user_ctx_var.get()


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
                payload = decode_token(token, token_type="access")
                payload["id"] = int(payload["sub"])
                payload.pop("sub")
                user = AccessTokenInfo.model_validate(payload)
                current_user_ctx_var.set(user)
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code, content={"detail": e.detail}
                )

        response = await call_next(request)
        return response
