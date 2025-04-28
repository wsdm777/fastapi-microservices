from datetime import date, timedelta
from beanie import PydanticObjectId
from resume.models import Resume


class ResumeRepository:
    async def create_resume(self, resume: Resume) -> Resume:
        return await resume.insert()

    async def get_resume(self, id: PydanticObjectId) -> Resume | None:
        return await Resume.get(id)

    async def get_user_resumes(self, user_id: int) -> list[Resume]:
        return await Resume.find(Resume.user_id == user_id).to_list()

    async def get_resumes(
        self, page: int, page_size: int, years_of_experience: int | None = None
    ) -> list[Resume]:
        skip = (page - 1) * page_size

        query = {}

        if years_of_experience is not None:
            experience_days = years_of_experience * 365
            query["experience.start_date"] = {
                "$lte": date.today() - timedelta(days=experience_days)
            }

        resumes = await Resume.find(query).skip(skip).limit(page_size).to_list()

        return resumes

    async def delete_resume(self, id: PydanticObjectId) -> int:
        result = await Resume.find(Resume.id == id).delete()
        return 0 if result is None else result.deleted_count

    async def delete_user_resumes(self, user_id: int):
        await Resume.find(Resume.user_id == user_id).delete()
