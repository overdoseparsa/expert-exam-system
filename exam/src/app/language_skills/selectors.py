# selectors.py for language_skills
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func , or_
from typing import List, Optional, Dict, Any

from .models import LanguageSkill
from .schemas import LanguageEnum, ProficiencyEnum


class LanguageSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[LanguageSkill]:

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
    async def get_by_language(
        db: AsyncSession, 
        user_id: int, 
        language: LanguageEnum,
        other_language: Optional[str] = None
    ) -> Optional[LanguageSkill]:
        """دریافت مهارت زبانی بر اساس زبان (برای بررسی تکراری بودن)"""
        query = select(LanguageSkill).where(
            and_(
                LanguageSkill.user_id == user_id,
                LanguageSkill.language == language
            )
        )
        
        if language == LanguageEnum.OTHER and other_language:
            query = query.where(LanguageSkill.other_language == other_language)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_proficiency(
        db: AsyncSession, 
        user_id: int, 
        proficiency: ProficiencyEnum
    ) -> List[LanguageSkill]:
        """دریافت مهارت‌های زبانی بر اساس سطح تسلط در یک مهارت خاص"""
        query = select(LanguageSkill).where(
            and_(
                LanguageSkill.user_id == user_id,
                or_(
                    LanguageSkill.reading == proficiency,
                    LanguageSkill.writing == proficiency,
                    LanguageSkill.speaking == proficiency,
                    LanguageSkill.listening == proficiency
                )
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        """تعداد مهارت‌های زبانی یک کاربر"""
        query = select(func.count()).select_from(LanguageSkill).where(LanguageSkill.user_id == user_id)
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def check_duplicate(
        db: AsyncSession, 
        user_id: int, 
        language: LanguageEnum,
        other_language: Optional[str] = None,
        exclude_id: Optional[int] = None
    ) -> bool:
        """بررسی تکراری بودن زبان"""
        query = select(LanguageSkill).where(
            and_(
                LanguageSkill.user_id == user_id,
                LanguageSkill.language == language
            )
        )
        
        if language == LanguageEnum.OTHER and other_language:
            query = query.where(LanguageSkill.other_language == other_language)
        
        if exclude_id:
            query = query.where(LanguageSkill.id != exclude_id)
        
        result = await db.execute(query)
        return result.first() is not None
    
    @staticmethod
    async def get_proficiency_summary(db: AsyncSession, user_id: int) -> Dict[str, List[Dict[str, Any]]]:
        """خلاصه مهارت‌های زبانی بر اساس تسلط"""
        query = select(LanguageSkill).where(LanguageSkill.user_id == user_id)
        result = await db.execute(query)
        languages = result.scalars().all()
        
        summary = {
            "native": [],
            "advanced": [],
            "intermediate": [],
            "basic": []
        }
        
        # امتیازات برای محاسبه میانگین
        proficiency_scores = {
            ProficiencyEnum.BASIC: 1,
            ProficiencyEnum.INTERMEDIATE: 2,
            ProficiencyEnum.ADVANCED: 3,
            ProficiencyEnum.NATIVE: 4
        }
        
        for lang in languages:
            # میانگین تسلط
            avg_score = (
                proficiency_scores[lang.reading] +
                proficiency_scores[lang.writing] +
                proficiency_scores[lang.speaking] +
                proficiency_scores[lang.listening]
            ) / 4
            
            # تعیین سطح کلی
            if avg_score >= 3.5:
                level = "native"
            elif avg_score >= 2.5:
                level = "advanced"
            elif avg_score >= 1.5:
                level = "intermediate"
            else:
                level = "basic"
            
            language_name = lang.other_language if lang.language == LanguageEnum.OTHER else lang.language.value
            summary[level].append({
                "language": language_name,
                "reading": lang.reading.value,
                "writing": lang.writing.value,
                "speaking": lang.speaking.value,
                "listening": lang.listening.value,
                "average_score": round(avg_score, 2)
            })
        
        return summary
    
    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int) -> Dict:
        """آمار مهارت‌های زبانی"""
        # تعداد کل
        total_query = select(func.count()).select_from(LanguageSkill).where(LanguageSkill.user_id == user_id)
        total = await db.execute(total_query)
        
        # آمار بر اساس زبان
        language_stats = {}
        for lang in LanguageEnum:
            count_query = select(func.count()).select_from(LanguageSkill).where(
                and_(LanguageSkill.user_id == user_id, LanguageSkill.language == lang)
            )
            count = await db.execute(count_query)
            language_stats[lang.value] = count.scalar() or 0
        
        return {
            "total": total.scalar() or 0,
            "by_language": language_stats
        }