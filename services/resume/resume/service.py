import logging

from beanie import PydanticObjectId
from fastapi import HTTPException, Request, status

from resume.repository import ResumeRepository
from resume.models import Resume, ResumeCreate, ResumePagination
from utils import check_user_exists


logger = logging.getLogger(__name__)


class ResumeService:
    def __init__(self):
        self.repository = ResumeRepository()

    async def create_resume(self, resume: ResumeCreate, request: Request) -> Resume:
        await check_user_exists(resume.user_id, request)
        new_resume = await self.repository.create_resume(
            Resume.model_validate(resume.model_dump())
        )
        logger.info(f"Created resume {new_resume.id}")
        return new_resume

    async def get_resume(self, resume_id: PydanticObjectId) -> Resume:
        resume = await self.repository.get_resume(resume_id)
        if resume is None:
            logger.warning(f"Trying to get non-existed resume {resume_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        logger.info(f"Get resume {resume_id} info")
        return resume

    async def get_user_resumes(self, user_id: int) -> list[Resume]:
        user_resumes = await self.repository.get_user_resumes(user_id)
        count = len(user_resumes)
        logger.info(f"Get user {user_id} resumes, {count=}")
        return user_resumes

    async def get_resumes_paginate(self, params: ResumePagination):
        resumes = await self.repository.get_resumes(
            params.page, params.page_size, params.minimal_experience_age
        )
        logger.info(f"Get resumes info with {params=}")
        return resumes

    async def delete_resume(self, resume_id: PydanticObjectId):
        deleted_rows = await self.repository.delete_resume(resume_id)
        if deleted_rows == 0:
            logger.warning(f"Trying to delete non-existed resume {resume_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found",
            )
        logger.info(f"Deleted resume {resume_id}")

    async def delete_user_resumes(self, user_id: int):
        await self.repository.delete_user_resumes(user_id)
        logger.info(f"Deleted user {user_id} resumes")
