from pydantic import BaseModel


class UserDeleteEvent(BaseModel):
    deleter_id: int
    deleted_user_id: int
    request_id: str
