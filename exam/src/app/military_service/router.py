# router.py for military_service
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from database import get_db
from auth.depends import get_current_user
from auth.models import User
from .schemas import (
    MilitaryServiceCreate, 
    MilitaryServiceUpdate, 
    MilitaryServiceResponse
)
from .services import MilitaryService as MilitaryServiceService
from .selectors import MilitarySelector

router = APIRouter(prefix="/military/", tags=["Military Service"])


@router.get("/", response_model=Optional[MilitaryServiceResponse])
async def get_military_service(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت اطلاعات نظام وظیفه"""
    military = await MilitaryServiceService.get_by_user(db, current_user.id)
    return military


@router.post("/", response_model=MilitaryServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_military_service(
    military_data: MilitaryServiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """ایجاد اطلاعات نظام وظیفه"""
    # بررسی آیا قبلاً اطلاعات نظام وظیفه دارد
    exists = await MilitaryServiceService.exists(db, current_user.id)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="شما قبلاً اطلاعات نظام وظیفه را ثبت کرده‌اید"
        )
    
    try:
        new_military = await MilitaryServiceService.create(db, current_user.id, military_data)
        
        # TODO: تغییر وضعیت applicant
        # from app.applicant.services import update_applicant_status
        
        await db.commit()
        await db.refresh(new_military)
        
        return new_military
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت اطلاعات نظام وظیفه: {str(e)}"
        )


@router.put("/", response_model=MilitaryServiceResponse)
async def update_military_service(
    military_data: MilitaryServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی اطلاعات نظام وظیفه"""
    military = await MilitaryServiceService.get_by_user(db, current_user.id)
    if not military:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شما هنوز اطلاعات نظام وظیفه را ثبت نکرده‌اید"
        )
    
    try:
        updated_military = await MilitaryServiceService.update(db, military, military_data)
        
        await db.commit()
        await db.refresh(updated_military)
        
        return updated_military
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_military_service(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """حذف اطلاعات نظام وظیفه"""
    military = await MilitaryServiceService.get_by_user(db, current_user.id)
    if not military:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="اطلاعات نظام وظیفه یافت نشد"
        )
    
    try:
        await MilitaryServiceService.delete(db, military)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


# ========== Additional endpoints using selectors ==========
@router.get("/statistics")
async def get_military_statistics(
    db: AsyncSession = Depends(get_db)
):
    """دریافت آمار کلی نظام وظیفه"""
    stats = await MilitarySelector.get_statistics(db)
    return stats


@router.get("/by-exemption/{exemption_type}")
async def get_by_exemption_type(
    exemption_type: str,
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست بر اساس نوع معافیت"""
    militaries = await MilitarySelector.get_by_exemption_type(db, exemption_type)
    return militaries