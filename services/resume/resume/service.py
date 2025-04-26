from beanie import PydanticObjectId
from fastapi import HTTPException, status

from resume.repository import ResumeRepository
from resume.models import Resume, ResumeCreate


class ResumeService:
    def __init__(self):
        self.repository = ResumeRepository()

    async def create_resume(self, resume: ResumeCreate) -> Resume:
        return await self.repository.create_resume(
            Resume.model_validate(resume.model_dump())
        )

    async def get_resume(self, resume_id: PydanticObjectId) -> Resume:
        resume = await self.repository.get_resume(resume_id)
        if resume is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        return resume
