from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional, Tuple
from datetime import datetime

from .models import Spouse, Child, Sibling, Applicant
from .schemas import ChildGenderEnum, SiblingTypeEnum, SiblingMaritalStatusEnum


class SpouseSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> Optional[Spouse]:
        
        query = select(Spouse).where(Spouse.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_with_applicant(db: AsyncSession, user_id: int) -> Optional[Tuple[Spouse, Applicant]]:
        
        query = select(Spouse, Applicant).join(
            Applicant, Applicant.user_id == Spouse.user_id
        ).where(Spouse.user_id == user_id)
        result = await db.execute(query)
        return result.first()
    
    @staticmethod
    async def count_all(db: AsyncSession) -> int:
        
        query = select(func.count()).select_from(Spouse)
        result = await db.execute(query)
        return result.scalar()


class ChildSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[Child]:
       
        query = select(Child).where(Child.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, child_id: int) -> Optional[Child]:
        
        query = select(Child).where(Child.id == child_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_gender(db: AsyncSession, user_id: int, gender: ChildGenderEnum) -> List[Child]:
       
        query = select(Child).where(
            and_(
                Child.user_id == user_id,
                Child.gender == gender
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_age_range(db: AsyncSession, user_id: int, min_age: int, max_age: int) -> List[Child]:
       
        query = select(Child).where(
            and_(
                Child.user_id == user_id,
                Child.age >= min_age,
                Child.age <= max_age
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:

        query = select(func.count()).select_from(Child).where(Child.user_id == user_id)
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int) -> dict:
       
        total_query = select(func.count()).select_from(Child).where(Child.user_id == user_id)
        total = await db.execute(total_query)
        
        male_query = select(func.count()).select_from(Child).where(
            and_(Child.user_id == user_id, Child.gender == ChildGenderEnum.MALE)
        )
        male = await db.execute(male_query)
        
        female_query = select(func.count()).select_from(Child).where(
            and_(Child.user_id == user_id, Child.gender == ChildGenderEnum.FEMALE)
        )
        female = await db.execute(female_query)
        
        avg_age_query = select(func.avg(Child.age)).where(Child.user_id == user_id)
        avg_age = await db.execute(avg_age_query)
        
        return {
            "total": total.scalar() or 0,
            "male": male.scalar() or 0,
            "female": female.scalar() or 0,
            "average_age": round(avg_age.scalar() or 0, 1)
        }


class SiblingSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[Sibling]:
        query = select(Sibling).where(Sibling.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, sibling_id: int) -> Optional[Sibling]:
        """دریافت خواهر/برادر بر اساس آیدی"""
        query = select(Sibling).where(Sibling.id == sibling_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_type(db: AsyncSession, user_id: int, sibling_type: SiblingTypeEnum) -> List[Sibling]:
        query = select(Sibling).where(
            and_(
                Sibling.user_id == user_id,
                Sibling.sibling_type == sibling_type
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_marital_status(db: AsyncSession, user_id: int, status: SiblingMaritalStatusEnum) -> List[Sibling]:
        query = select(Sibling).where(
            and_(
                Sibling.user_id == user_id,
                Sibling.marital_status == status
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_age_range(db: AsyncSession, user_id: int, min_age: int, max_age: int) -> List[Sibling]:
        """دریافت خواهر/برادرها بر اساس رنج سنی"""
        query = select(Sibling).where(
            and_(
                Sibling.user_id == user_id,
                Sibling.age >= min_age,
                Sibling.age <= max_age
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        """تعداد خواهر/برادرهای یک کاربر"""
        query = select(func.count()).select_from(Sibling).where(Sibling.user_id == user_id)
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int) -> dict:
        """آمار خواهر/برادرها"""
        # تعداد کل
        total_query = select(func.count()).select_from(Sibling).where(Sibling.user_id == user_id)
        total = await db.execute(total_query)
        
        # تعداد برادرها
        brother_query = select(func.count()).select_from(Sibling).where(
            and_(Sibling.user_id == user_id, Sibling.sibling_type == SiblingTypeEnum.BROTHER)
        )
        brothers = await db.execute(brother_query)
        
        # تعداد خواهرها
        sister_query = select(func.count()).select_from(Sibling).where(
            and_(Sibling.user_id == user_id, Sibling.sibling_type == SiblingTypeEnum.SISTER)
        )
        sisters = await db.execute(sister_query)
        
        # تعداد مجردها
        single_query = select(func.count()).select_from(Sibling).where(
            and_(Sibling.user_id == user_id, Sibling.marital_status == SiblingMaritalStatusEnum.SINGLE)
        )
        single = await db.execute(single_query)
        
        # تعداد متاهل‌ها
        married_query = select(func.count()).select_from(Sibling).where(
            and_(Sibling.user_id == user_id, Sibling.marital_status == SiblingMaritalStatusEnum.MARRIED)
        )
        married = await db.execute(married_query)
        
        # میانگین سن
        avg_age_query = select(func.avg(Sibling.age)).where(Sibling.user_id == user_id)
        avg_age = await db.execute(avg_age_query)
        
        return {
            "total": total.scalar() or 0,
            "brothers": brothers.scalar() or 0,
            "sisters": sisters.scalar() or 0,
            "single": single.scalar() or 0,
            "married": married.scalar() or 0,
            "average_age": round(avg_age.scalar() or 0, 1)
        }