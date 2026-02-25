# services.py for work_experience
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from .models import WorkExperience
from .schemas import WorkExperienceCreate, WorkExperienceUpdate, WorkExperienceBulkCreate


class WorkExperienceService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[WorkExperience]:

        query = select(WorkExperience).where(WorkExperience.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, work_id: int, user_id: int) -> Optional[WorkExperience]:

        query = select(WorkExperience).where(
            and_(
                WorkExperience.id == work_id,
                WorkExperience.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_id: int, data: WorkExperienceCreate) -> WorkExperience:
        """ایجاد سابقه کاری جدید"""
        work_exp = WorkExperience(
            user_id=user_id,
            company=data.company,
            position=data.position,
            start_date=data.start_date,
            end_date=data.end_date,
            currently_working=data.currently_working,
            job_description=data.job_description,
            leaving_reason=data.leaving_reason,
            salary=data.salary
        )
        db.add(work_exp)
        await db.flush()
        return work_exp
    
    @staticmethod
    async def create_bulk(
        db: AsyncSession, 
        user_id: int, 
        data: WorkExperienceBulkCreate
    ) -> List[WorkExperience]:

        new_experiences = []
        
        for work in data.experiences:
            experience = WorkExperience(
                user_id=user_id,
                company=work.company,
                position=work.position,
                start_date=work.start_date,
                end_date=work.end_date,
                currently_working=work.currently_working,
                job_description=work.job_description,
                leaving_reason=work.leaving_reason,
                salary=work.salary
            )
            db.add(experience)
            new_experiences.append(experience)
        
        await db.flush()
        return new_experiences
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        work_exp: WorkExperience, 
        data: WorkExperienceUpdate
    ) -> WorkExperience:

        update_data = data.dict(exclude_unset=True)
        

        if 'currently_working' in update_data and update_data['currently_working']:
            work_exp.end_date = None
            if 'end_date' in update_data:
                update_data.pop('end_date')
        
        for field, value in update_data.items():
            if value is not None:
                setattr(work_exp, field, value)
        
        work_exp.updated_at = datetime.utcnow()
        db.add(work_exp)
        await db.flush()
        return work_exp
    
    @staticmethod
    async def delete(db: AsyncSession, work_exp: WorkExperience) -> None:

        await db.delete(work_exp)
        await db.flush()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        
        query = select(WorkExperience).where(WorkExperience.user_id == user_id)
        result = await db.execute(query)
        return len(result.scalars().all())