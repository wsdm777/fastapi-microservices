from datetime import date
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List


class Experience(BaseModel):
    company: str
    position: str
    start_date: date
    end_date: date | None = None
    description: str | None = None


class ResumeBase(BaseModel):
    user_id: int
    first_name: str
    second_name: str
    email: EmailStr
    phone: str | None = None
    skills: List[str]
    education: List[str]
    experience: List[Experience]
    summary: str | None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class ResumeCreate(ResumeBase):
    pass


class Resume(Document, ResumeBase):
    id: PydanticObjectId | None = Field(default_factory=PydanticObjectId, alias="_id")

    class Settings:
        name = "resumes"


class ResumeResponse(ResumeBase):
    id: PydanticObjectId


class ResumePagination(BaseModel):
    page: int
    page_size: int = 10
    minimal_experience_age: int | None = None
