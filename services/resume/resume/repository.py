from beanie import PydanticObjectId
from resume.models import Resume


class ResumeRepository:
    async def create_resume(self, resume: Resume) -> Resume:
        return await resume.insert()

    async def get_resume(self, id: PydanticObjectId) -> Resume | None:
        return await Resume.get(id)
