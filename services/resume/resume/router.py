from beanie import PydanticObjectId
from fastapi import APIRouter, Depends

from resume.service import ResumeService
from resume.models import ResumeCreate, ResumeResponse
from dependencies import get_current_user, require_max_level
from schemas import AccessTokenInfo


router = APIRouter(prefix="/resumes")
resume_service = ResumeService()


@router.post("/", response_model=ResumeResponse)
async def create_resume(
    resume: ResumeCreate, _: AccessTokenInfo = require_max_level(2)
):
    return await resume_service.create_resume(resume)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: PydanticObjectId, _: AccessTokenInfo = Depends(get_current_user)
):
    return await resume_service.get_resume(resume_id)
