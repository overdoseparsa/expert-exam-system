# selectors.py for education
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict
from datetime import datetime

from .models import Education
from .schemas import EducationDegreeEnum, EducationStudyStatusEnum


class EducationSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[Education]:

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
    async def get_by_degree(db: AsyncSession, user_id: int, degree: EducationDegreeEnum) -> List[Education]:

        query = select(Education).where(
            and_(
                Education.user_id == user_id,
                Education.degree == degree
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_study_status(db: AsyncSession, user_id: int, status: EducationStudyStatusEnum) -> List[Education]:

        query = select(Education).where(
            and_(
                Education.user_id == user_id,
                Education.study_status == status
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_highest_degree(db: AsyncSession, user_id: int) -> Optional[Education]:
        """دریافت بالاترین مدرک تحصیلی"""
        query = select(Education).where(Education.user_id == user_id)
        result = await db.execute(query)
        educations = result.scalars().all()
        
        if not educations:
            return None
        
        degree_order = {
            EducationDegreeEnum.DIPLOMA: 1,
            EducationDegreeEnum.ASSOCIATE: 2,
            EducationDegreeEnum.BACHELOR: 3,
            EducationDegreeEnum.MASTER: 4,
            EducationDegreeEnum.PHD: 5,
            EducationDegreeEnum.POST_DOC: 6
        }
        
        return max(educations, key=lambda x: degree_order.get(x.degree, 0))
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:

        query = select(func.count()).select_from(Education).where(Education.user_id == user_id)
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int) -> Dict:
        total_query = select(func.count()).select_from(Education).where(Education.user_id == user_id)
        total = await db.execute(total_query)
        
        degree_stats = {}
        for degree in EducationDegreeEnum:
            count_query = select(func.count()).select_from(Education).where(
                and_(Education.user_id == user_id, Education.degree == degree)
            )
            count = await db.execute(count_query)
            degree_stats[degree.value] = count.scalar() or 0
        
        highest = await EducationSelector.get_highest_degree(db, user_id)
        
        return {
            "total": total.scalar() or 0,
            "by_degree": degree_stats,
            "highest_degree": highest.degree.value if highest else None,
            "highest_degree_field": highest.field if highest else None
        }