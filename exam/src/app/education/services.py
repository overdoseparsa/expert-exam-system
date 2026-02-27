# services.py for education
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from .models import Education
from .schemas import EducationCreate, EducationUpdate, EducationBulkCreate


class EducationService:

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[Education]:
        query = select(Education).where(Education.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, education_id: int, user_id: int) -> Optional[Education]:
        query = select(Education).where(
            and_(
                Education.id == education_id,
                Education.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_id: int, data: EducationCreate) -> Education:
        # we dont use EducationService.create for each for call db.flash
        education = Education(
            user_id=user_id,
            degree=data.degree,
            field=data.field,
            university=data.university,
            average=data.average,
            start_year=data.start_year,
            end_year=data.end_year,
            study_status=data.study_status,
            description=data.description
        ) 
        db.add(education)
        await db.flush()
        return education
    
    @staticmethod
    async def create_bulk(db: AsyncSession, user_id: int, data: EducationBulkCreate) -> List[Education]:
        """ایجاد چند مدرک تحصیلی به صورت یکجا"""
        new_educations = []
        # TODO fix this dont use depubcate 
        for edu in data.educations:
            education = Education(
                user_id=user_id,
                degree=edu.degree,
                field=edu.field,
                university=edu.university,
                average=edu.average,
                start_year=edu.start_year,
                end_year=edu.end_year,
                study_status=edu.study_status,
                description=edu.description
            )
            db.add(education)
            new_educations.append(education)
        
        await db.flush()
        return new_educations
    
    @staticmethod
    async def update(db: AsyncSession, education: Education, data: EducationUpdate) -> Education:
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(education, field, value)
        
        education.updated_at = datetime.utcnow()
        db.add(education)
        await db.flush()
        return education
    
    @staticmethod
    async def delete(db: AsyncSession, education: Education) -> None:
        await db.delete(education)
        await db.flush()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        query = select(Education).where(Education.user_id == user_id)
        result = await db.execute(query)
        return len(result.scalars().all())