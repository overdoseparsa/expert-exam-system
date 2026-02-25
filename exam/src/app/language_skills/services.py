# services.py for language_skills
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from .models import LanguageSkill
from .schemas import LanguageSkillCreate, LanguageSkillUpdate, LanguageSkillBulkCreate


class LanguageService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[LanguageSkill]:
        """دریافت لیست مهارت‌های زبانی"""
        query = select(LanguageSkill).where(LanguageSkill.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, language_id: int, user_id: int) -> Optional[LanguageSkill]:
        """دریافت یک مهارت زبانی با آیدی"""
        query = select(LanguageSkill).where(
            and_(
                LanguageSkill.id == language_id,
                LanguageSkill.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_id: int, data: LanguageSkillCreate) -> LanguageSkill:
        """ایجاد مهارت زبانی جدید"""
        language = LanguageSkill(
            user_id=user_id,
            language=data.language,
            other_language=data.other_language,
            reading=data.reading,
            writing=data.writing,
            speaking=data.speaking,
            listening=data.listening
        )
        db.add(language)
        await db.flush()
        return language
    
    @staticmethod
    async def create_bulk(
        db: AsyncSession, 
        user_id: int, 
        data: LanguageSkillBulkCreate
    ) -> List[LanguageSkill]:
        """ایجاد چند مهارت زبانی به صورت یکجا"""
        new_languages = []
        
        for lang_data in data.skills:
            language = LanguageSkill(
                user_id=user_id,
                language=lang_data.language,
                other_language=lang_data.other_language,
                reading=lang_data.reading,
                writing=lang_data.writing,
                speaking=lang_data.speaking,
                listening=lang_data.listening
            )
            db.add(language)
            new_languages.append(language)
        
        await db.flush()
        return new_languages
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        language: LanguageSkill, 
        data: LanguageSkillUpdate
    ) -> LanguageSkill:
        """به‌روزرسانی اطلاعات مهارت زبانی"""
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(language, field, value)
        
        language.updated_at = datetime.utcnow()
        db.add(language)
        await db.flush()
        return language
    
    @staticmethod
    async def delete(db: AsyncSession, language: LanguageSkill) -> None:
        """حذف مهارت زبانی"""
        await db.delete(language)
        await db.flush()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        """تعداد مهارت‌های زبانی کاربر"""
        query = select(LanguageSkill).where(LanguageSkill.user_id == user_id)
        result = await db.execute(query)
        return len(result.scalars().all())