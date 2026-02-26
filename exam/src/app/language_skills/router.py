from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from auth.depends import get_current_user
from auth.models import User
from .schemas import (
    LanguageSkillCreate, LanguageSkillUpdate, LanguageSkillResponse,
    LanguageEnum, ProficiencyEnum, LanguageSkillBulkCreate,
    ProficiencySummaryResponse
)
from .services import LanguageService
from .selectors import LanguageSelector

router = APIRouter(prefix="/languages", tags=["Language Skills"])


# ========== LANGUAGE SKILLS ==========
@router.get("/", response_model=List[LanguageSkillResponse])
async def get_language_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست مهارت‌های زبانی"""
    languages = await LanguageService.get_by_user(db, current_user.id)
    return languages


@router.post("/", response_model=LanguageSkillResponse, status_code=status.HTTP_201_CREATED)
async def create_language_skill(
    language_data: LanguageSkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """اضافه کردن مهارت زبانی جدید"""
    try:
        # بررسی عدم تکراری بودن زبان
        is_duplicate = await LanguageSelector.check_duplicate(
            db, 
            current_user.id, 
            language_data.language,
            language_data.other_language
        )
        
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این زبان قبلاً ثبت شده است"
            )
        
        new_language = await LanguageService.create(db, current_user.id, language_data)
        
        # TODO: تغییر وضعیت applicant (اگر نیاز است)
        
        await db.commit()
        await db.refresh(new_language)
        
        return new_language
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت مهارت زبانی: {str(e)}"
        )


@router.get("/{language_id}/", response_model=LanguageSkillResponse)
async def get_language_skill(
    language_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت اطلاعات یک مهارت زبانی خاص"""
    language = await LanguageService.get_by_id(db, language_id, current_user.id)
    
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مهارت زبانی یافت نشد"
        )
    
    return language


@router.put("/{language_id}/", response_model=LanguageSkillResponse)
async def update_language_skill(
    language_id: int,
    language_data: LanguageSkillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی اطلاعات مهارت زبانی"""
    language = await LanguageService.get_by_id(db, language_id, current_user.id)
    
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مهارت زبانی یافت نشد"
        )
    
    try:
        # اگر زبان تغییر می‌کند، بررسی تکراری نبودن
        if language_data.language and language_data.language != language.language:
            is_duplicate = await LanguageSelector.check_duplicate(
                db, 
                current_user.id, 
                language_data.language,
                language_data.other_language or language.other_language,
                exclude_id=language_id
            )
            
            if is_duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="این زبان قبلاً ثبت شده است"
                )
        
        updated_language = await LanguageService.update(db, language, language_data)
        
        await db.commit()
        await db.refresh(updated_language)
        
        return updated_language
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/{language_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_language_skill(
    language_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """حذف مهارت زبانی"""
    language = await LanguageService.get_by_id(db, language_id, current_user.id)
    
    if not language:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مهارت زبانی یافت نشد"
        )
    
    try:
        await LanguageService.delete(db, language)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


@router.get("/proficiency-summary/", response_model=ProficiencySummaryResponse)
async def get_proficiency_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """خلاصه مهارت‌های زبانی بر اساس تسلط"""
    summary = await LanguageSelector.get_proficiency_summary(db, current_user.id)
    return summary


@router.post("/bulk/", response_model=List[LanguageSkillResponse], status_code=status.HTTP_201_CREATED)
async def create_language_skills_bulk(
    bulk_data: LanguageSkillBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ثبت چند مهارت زبانی به صورت همزمان"""
    created_skills = []

    try:
        # بررسی تکراری بودن هر کدام
        for skill_data in bulk_data.skills:
            is_duplicate = await LanguageSelector.check_duplicate(
                db, 
                current_user.id, 
                skill_data.language,
                skill_data.other_language
            )
            
            if is_duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"زبان {skill_data.language} قبلاً ثبت شده است"
                )
        
        # ایجاد رکوردها
        created_skills = await LanguageService.create_bulk(db, current_user.id, bulk_data)
        
        # TODO: تغییر وضعیت applicant (اگر نیاز است)
        
        await db.commit()

        # ریفرش رکوردها
        for skill in created_skills:
            await db.refresh(skill)
        
        return created_skills

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت مهارت‌های زبانی: {str(e)}"
        )


# ========== Additional endpoints using selectors ==========
@router.get("/statistics/")
async def get_language_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت آمار مهارت‌های زبانی"""
    stats = await LanguageSelector.get_statistics(db, current_user.id)
    return stats


@router.get("/by-language/{language}/")
async def get_by_language(
    language: LanguageEnum,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت بر اساس زبان"""
    lang = await LanguageSelector.get_by_language(db, current_user.id, language)
    return lang