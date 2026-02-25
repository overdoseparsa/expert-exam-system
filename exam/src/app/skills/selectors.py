# selectors.py for skills
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict

from .models import Skill
from .schemas import SkillLevelEnum


class SkillSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[Skill]:
        """دریافت لیست مهارت‌ها بر اساس user_id"""
        query = select(Skill).where(Skill.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, skill_id: int, user_id: int) -> Optional[Skill]:
        """دریافت یک مهارت با آیدی"""
        query = select(Skill).where(
            and_(
                Skill.id == skill_id,
                Skill.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, user_id: int, skill_name: str) -> Optional[Skill]:
        """دریافت مهارت بر اساس نام (برای بررسی تکراری بودن)"""
        query = select(Skill).where(
            and_(
                Skill.user_id == user_id,
                Skill.skill_name.ilike(skill_name)
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_level(db: AsyncSession, user_id: int, level: SkillLevelEnum) -> List[Skill]:
        """دریافت مهارت‌ها بر اساس سطح"""
        query = select(Skill).where(
            and_(
                Skill.user_id == user_id,
                Skill.skill_level == level
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_experience_range(
        db: AsyncSession, 
        user_id: int, 
        min_years: int, 
        max_years: int
    ) -> List[Skill]:
        """دریافت مهارت‌ها بر اساس رنج سال تجربه"""
        query = select(Skill).where(
            and_(
                Skill.user_id == user_id,
                Skill.years_of_experience >= min_years,
                Skill.years_of_experience <= max_years
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        """تعداد مهارت‌های یک کاربر"""
        query = select(func.count()).select_from(Skill).where(Skill.user_id == user_id)
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def check_duplicate(db: AsyncSession, user_id: int, skill_name: str, exclude_id: Optional[int] = None) -> bool:
        """بررسی تکراری بودن نام مهارت"""
        query = select(Skill).where(
            and_(
                Skill.user_id == user_id,
                Skill.skill_name.ilike(skill_name)
            )
        )
        
        if exclude_id:
            query = query.where(Skill.id != exclude_id)
        
        result = await db.execute(query)
        return result.first() is not None
    
    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int) -> Dict:
        """آمار مهارت‌ها"""
        # تعداد کل
        total_query = select(func.count()).select_from(Skill).where(Skill.user_id == user_id)
        total = await db.execute(total_query)
        
        # آمار بر اساس سطح
        level_stats = {}
        for level in SkillLevelEnum:
            count_query = select(func.count()).select_from(Skill).where(
                and_(Skill.user_id == user_id, Skill.skill_level == level)
            )
            count = await db.execute(count_query)
            level_stats[level.value] = count.scalar() or 0
        
        # پرتجربه‌ترین مهارت
        most_exp_query = select(Skill).where(
            Skill.user_id == user_id
        ).order_by(Skill.years_of_experience.desc()).limit(1)
        most_exp = await db.execute(most_exp_query)
        most_exp_skill = most_exp.scalar_one_or_none()
        
        return {
            "total": total.scalar() or 0,
            "by_level": level_stats,
            "most_experienced": {
                "name": most_exp_skill.skill_name if most_exp_skill else None,
                "years": most_exp_skill.years_of_experience if most_exp_skill else 0
            }
        }