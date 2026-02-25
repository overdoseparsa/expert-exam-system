# selectors.py for work_experience
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict
from datetime import datetime, date

from .models import WorkExperience


class WorkExperienceSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[WorkExperience]:

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
    async def get_current_jobs(db: AsyncSession, user_id: int) -> List[WorkExperience]:

        query = select(WorkExperience).where(
            and_(
                WorkExperience.user_id == user_id,
                WorkExperience.currently_working == True
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_company(db: AsyncSession, user_id: int, company: str) -> List[WorkExperience]:

        query = select(WorkExperience).where(
            and_(
                WorkExperience.user_id == user_id,
                WorkExperience.company.ilike(f"%{company}%")
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_date_range(
        db: AsyncSession, 
        user_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[WorkExperience]:

        query = select(WorkExperience).where(
            and_(
                WorkExperience.user_id == user_id,
                WorkExperience.start_date >= start_date,
                WorkExperience.start_date <= end_date
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:

        query = select(func.count()).select_from(WorkExperience).where(WorkExperience.user_id == user_id)
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def calculate_total_experience(db: AsyncSession, user_id: int) -> Dict:

        query = select(WorkExperience).where(WorkExperience.user_id == user_id)
        result = await db.execute(query)
        experiences = result.scalars().all()
        
        total_months = 0
        today = datetime.utcnow().date()
        
        for work in experiences:
            if work.currently_working:
                end_date = today
            elif work.end_date:
                end_date = work.end_date
            else:
                continue
            
            delta = (end_date.year - work.start_date.year) * 12 + (end_date.month - work.start_date.month)
            total_months += max(0, delta)
        
        years = total_months // 12
        months = total_months % 12
        
        return {
            "total_months": total_months,
            "years": years,
            "months": months,
            "formatted": f"{years} سال و {months} ماه"
        }
    
    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int) -> Dict:

        total_query = select(func.count()).select_from(WorkExperience).where(WorkExperience.user_id == user_id)
        total = await db.execute(total_query)
        
        current_query = select(func.count()).select_from(WorkExperience).where(
            and_(WorkExperience.user_id == user_id, WorkExperience.currently_working == True)
        )
        current = await db.execute(current_query)
        
        max_salary_query = select(func.max(WorkExperience.salary)).where(WorkExperience.user_id == user_id)
        max_salary = await db.execute(max_salary_query)
        
        total_exp = await WorkExperienceSelector.calculate_total_experience(db, user_id)
        
        return {
            "total": total.scalar() or 0,
            "current_jobs": current.scalar() or 0,
            "max_salary": max_salary.scalar(),
            "total_experience": total_exp
        }