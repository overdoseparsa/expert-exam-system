# router.py for skills
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from database import get_db
from auth.depends import get_current_user
from auth.models import User
from .schemas import (
    SkillCreate, SkillUpdate, SkillResponse,
    SkillLevelEnum, SkillBulkCreate
)
from .services import SkillService
from .selectors import SkillSelector

router = APIRouter(prefix="/skills/", tags=["Skills"])


# ========== SKILLS ==========
@router.get("/", response_model=List[SkillResponse])
async def get_skills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست مهارت‌ها"""
    skills = await SkillService.get_by_user(db, current_user.id)
    return skills


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    skill_data: SkillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """اضافه کردن مهارت جدید"""
    try:
        # بررسی عدم تکراری بودن مهارت
        is_duplicate = await SkillSelector.check_duplicate(
            db, current_user.id, skill_data.skill_name
        )
        
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این مهارت قبلاً ثبت شده است"
            )
        
        new_skill = await SkillService.create(db, current_user.id, skill_data)
        
        # TODO: تغییر وضعیت applicant
        # from app.applicant.services import update_applicant_status
        
        await db.commit()
        await db.refresh(new_skill)
        
        return new_skill
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت مهارت: {str(e)}"
        )


@router.get("/{skill_id}/", response_model=SkillResponse)
async def get_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت اطلاعات یک مهارت خاص"""
    skill = await SkillService.get_by_id(db, skill_id, current_user.id)
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مهارت یافت نشد"
        )
    
    return skill


@router.put("/{skill_id}/", response_model=SkillResponse)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی اطلاعات مهارت"""
    skill = await SkillService.get_by_id(db, skill_id, current_user.id)
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مهارت یافت نشد"
        )
    
    try:
        # اگر نام مهارت تغییر می‌کند، بررسی تکراری نبودن
        if skill_data.skill_name and skill_data.skill_name != skill.skill_name:
            is_duplicate = await SkillSelector.check_duplicate(
                db, current_user.id, skill_data.skill_name, exclude_id=skill_id
            )
            
            if is_duplicate:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="این نام مهارت قبلاً ثبت شده است"
                )
        
        updated_skill = await SkillService.update(db, skill, skill_data)
        
        await db.commit()
        await db.refresh(updated_skill)
        
        return updated_skill
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/{skill_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """حذف مهارت"""
    skill = await SkillService.get_by_id(db, skill_id, current_user.id)
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مهارت یافت نشد"
        )
    
    try:
        await SkillService.delete(db, skill)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


@router.get("/by-level/{level}/", response_model=List[SkillResponse])
async def get_skills_by_level(
    level: SkillLevelEnum,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    skills = await SkillSelector.get_by_level(db, current_user.id, level)
    return skills


@router.post("/bulk", response_model=List[SkillResponse], status_code=status.HTTP_201_CREATED)
async def create_skills_bulk(
    skills_data: SkillBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    added_skills = []
    
    try:
        for skill_data in skills_data.skills:
            # بررسی تکراری بودن مهارت
            is_duplicate = await SkillSelector.check_duplicate(
                db, current_user.id, skill_data.skill_name
            )
            
            if is_duplicate:
                continue  # از ثبت تکراری عبور می‌کنیم
            
            new_skill = await SkillService.create(db, current_user.id, skill_data)
            added_skills.append(new_skill)

        if added_skills:
            # TODO: تغییر وضعیت applicant
            
            await db.commit()

            # ریفرش تمام رکوردها
            for skill in added_skills:
                await db.refresh(skill)

        return added_skills

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت مهارت‌ها: {str(e)}"
        )


@router.get("/statistics/")
async def get_skills_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت آمار مهارت‌ها"""
    stats = await SkillSelector.get_statistics(db, current_user.id)
    return stats


@router.get("/check-duplicate/{skill_name}/")
async def check_duplicate_skill(
    skill_name: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """بررسی تکراری بودن نام مهارت"""
    is_duplicate = await SkillSelector.check_duplicate(db, current_user.id, skill_name)
    return {"is_duplicate": is_duplicate}