# services.py for skills
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from .models import Skill
from schemas import SkillCreate, SkillUpdate, SkillBulkCreate


class SkillService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[Skill]:
        """دریافت لیست مهارت‌ها"""
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
    async def create(db: AsyncSession, user_id: int, data: SkillCreate) -> Skill:
        """ایجاد مهارت جدید"""
        skill = Skill(
            user_id=user_id,
            skill_name=data.skill_name,
            skill_level=data.skill_level,
            years_of_experience=data.years_of_experience,
            description=data.description
        )
        db.add(skill)
        await db.flush()
        return skill
    
    @staticmethod
    async def create_bulk(db: AsyncSession, user_id: int, data: SkillBulkCreate) -> List[Skill]:
        """ایجاد چند مهارت به صورت یکجا"""
        new_skills = []
        
        for skill_data in data.skills:
            skill = Skill(
                user_id=user_id,
                skill_name=skill_data.skill_name,
                skill_level=skill_data.skill_level,
                years_of_experience=skill_data.years_of_experience,
                description=skill_data.description
            )
            db.add(skill)
            new_skills.append(skill)
        
        await db.flush()
        return new_skills
    
    @staticmethod
    async def update(db: AsyncSession, skill: Skill, data: SkillUpdate) -> Skill:
        """به‌روزرسانی اطلاعات مهارت"""
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(skill, field, value)
        
        skill.updated_at = datetime.utcnow()
        db.add(skill)
        await db.flush()
        return skill
    
    @staticmethod
    async def delete(db: AsyncSession, skill: Skill) -> None:
        """حذف مهارت"""
        await db.delete(skill)
        await db.flush()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        """تعداد مهارت‌های کاربر"""
        query = select(Skill).where(Skill.user_id == user_id)
        result = await db.execute(query)
        return len(result.scalars().all())