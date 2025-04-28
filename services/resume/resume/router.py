from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from resume.service import ResumeService
from resume.models import ResumeCreate, ResumePagination, ResumeResponse
from dependencies import get_current_user, require_max_level
from schemas import AccessTokenInfo, ResponseOk

router = APIRouter(tags=["resume"], prefix="/resumes")
resume_service = ResumeService()


@router.post("/", response_model=ResumeResponse)
async def create_resume(
    resume: ResumeCreate,
    request: Request,
    _: AccessTokenInfo = require_max_level(2),
):
    return await resume_service.create_resume(resume, request)


@router.get("/list", response_model=list[ResumeResponse])
async def get_resumes(
    params: ResumePagination = Query(), _: AccessTokenInfo = Depends(get_current_user)
):
    return await resume_service.get_resumes_paginate(params)


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: PydanticObjectId, _: AccessTokenInfo = Depends(get_current_user)
):
    return await resume_service.get_resume(resume_id)


@router.get("/user/{user_id}", response_model=list[ResumeResponse])
async def get_user_resumes(
    user_id: int,
    _: AccessTokenInfo = Depends(get_current_user),
):
    return await resume_service.get_user_resumes(user_id)


@router.delete("/user/{user_id}", response_model=ResponseOk)
async def delete_user_resumes(
    user_id: int,
    _: AccessTokenInfo = require_max_level(2),
):
    await resume_service.delete_user_resumes(user_id)
    return JSONResponse(content={"message": "ok"})


@router.delete("/{resume_id}", response_model=ResponseOk)
async def delete_resume(
    resume_id: PydanticObjectId,
    _: AccessTokenInfo = require_max_level(2),
):
    await resume_service.delete_resume(resume_id)
    return JSONResponse(content={"message": "ok"})
