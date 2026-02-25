# router.py for work_experience
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from database import get_db
from auth.depends import get_current_user
from auth.models import User
from .schemas import (
    WorkExperienceCreate, WorkExperienceUpdate, WorkExperienceResponse,
    WorkExperienceBulkCreate, TotalExperienceResponse
)
from .services import WorkExperienceService
from .selectors import WorkExperienceSelector

router = APIRouter(prefix="/work-experience/", tags=["Work Experience"])


# ========== WORK EXPERIENCE ==========
@router.get("/", response_model=List[WorkExperienceResponse])
async def get_work_experiences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    experiences = await WorkExperienceService.get_by_user(db, current_user.id)
    return experiences


@router.post("/", response_model=WorkExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_work_experience(
    work_data: WorkExperienceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """اضافه کردن سابقه کاری جدید"""
    try:
        new_work = await WorkExperienceService.create(db, current_user.id, work_data)
        
        # TODO: تغییر وضعیت applicant
        # from app.applicant.services import update_applicant_status
        
        await db.commit()
        await db.refresh(new_work)
        
        return new_work
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت سابقه کاری: {str(e)}"
        )


@router.get("/{work_id}/", response_model=WorkExperienceResponse)
async def get_work_experience(
    work_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت اطلاعات یک سابقه کاری خاص"""
    work_exp = await WorkExperienceService.get_by_id(db, work_id, current_user.id)
    
    if not work_exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سابقه کاری یافت نشد"
        )
    
    return work_exp


@router.put("/{work_id}/", response_model=WorkExperienceResponse)
async def update_work_experience(
    work_id: int,
    work_data: WorkExperienceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی اطلاعات سابقه کاری"""
    work_exp = await WorkExperienceService.get_by_id(db, work_id, current_user.id)
    
    if not work_exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سابقه کاری یافت نشد"
        )
    
    try:
        updated_work = await WorkExperienceService.update(db, work_exp, work_data)
        
        await db.commit()
        await db.refresh(updated_work)
        
        return updated_work
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/{work_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_work_experience(
    work_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """حذف سابقه کاری"""
    work_exp = await WorkExperienceService.get_by_id(db, work_id, current_user.id)
    
    if not work_exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سابقه کاری یافت نشد"
        )
    
    try:
        await WorkExperienceService.delete(db, work_exp)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


@router.get("/total-experience/", response_model=TotalExperienceResponse)
async def calculate_total_experience(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """محاسبه کل سابقه کاری به ماه"""
    total = await WorkExperienceSelector.calculate_total_experience(db, current_user.id)
    return total


@router.post("/bulk/", response_model=List[WorkExperienceResponse], status_code=status.HTTP_201_CREATED)
async def create_work_experiences_bulk(
    data: WorkExperienceBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ثبت چند سابقه کاری به صورت یکجا"""
    try:
        new_experiences = await WorkExperienceService.create_bulk(db, current_user.id, data)
        
        # TODO: تغییر وضعیت applicant
        
        await db.commit()
        
        for exp in new_experiences:
            await db.refresh(exp)
        
        return new_experiences
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت سوابق کاری: {str(e)}"
        )


# ========== Additional endpoints using selectors ==========
@router.get("/statistics/")
async def get_work_experience_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stats = await WorkExperienceSelector.get_statistics(db, current_user.id)
    return stats


@router.get("/current/")
async def get_current_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    jobs = await WorkExperienceSelector.get_current_jobs(db, current_user.id)
    return jobs