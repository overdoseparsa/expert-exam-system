# router.py for application_details
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, date

from database import get_db
from auth.depends import get_current_user_obj as get_current_user
from auth.models import User
from .models import ApplicationDetails 

from .schemas import (
    ApplicationDetailsCreate,
    ApplicationDetailsUpdate,
    ApplicationDetailsResponse,
    DetailsSummaryResponse
)
from .services import ApplicationDetailsService
from .selectors import ApplicationDetailsSelector

from typing import List

router = APIRouter(prefix="/application-details", tags=["Application Details"])





@router.get("/", response_model=List[ApplicationDetailsResponse])
async def get_application_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    print("user is " , current_user)
    """دریافت جزئیات درخواست"""
    details = await ApplicationDetailsService.get_by_user(db, current_user.id)
    print('')
    return details


@router.post("/", response_model=ApplicationDetailsResponse, status_code=status.HTTP_201_CREATED)
async def create_application_details(
    details_data: ApplicationDetailsCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):


    try:
        new_details = await  ApplicationDetailsService.create(db, current_user.id, details_data)
    

        
        return new_details
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت جزئیات درخواست: {str(e)}"
        )


@router.put("/{application_details}/", response_model=ApplicationDetailsResponse)
async def update_application_details(
    application_details :int , 
    details_data: ApplicationDetailsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی جزئیات درخواست"""
    details = await  ApplicationDetailsService.get_by_id(
        db,
        application_details,
        user_id = current_user.id
        )
    
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شما هنوز جزئیات درخواست را ثبت نکرده‌اید"
        )
    
    try:
        if 'available_from_date' in details_data.dict(exclude_unset=True):
            if details_data.available_from_date and details_data.available_from_date < date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="تاریخ آمادگی نمی‌تواند از امروز عقب‌تر باشد"
                )
        
        updated_details = await  ApplicationDetailsService.update(
            db,
            details,
            details_data
            )


        
        return updated_details
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )



@router.patch("/{application_details}/", response_model=ApplicationDetailsResponse)
async def patch_application_details(
    application_details: int,
    details_data: ApplicationDetailsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    # دریافت جزئیات کاربر
    details = await ApplicationDetailsService.get_by_id(
        db,
        application_details,
        user_id = current_user.id, 

        )
    
    if not details or details.id != application_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شما هنوز جزئیات درخواست را ثبت نکرده‌اید"
        )

    # اعتبارسنجی تاریخ آمادگی
    if 'available_from_date' in details_data.dict(exclude_unset=True):
        if details_data.available_from_date and details_data.available_from_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="تاریخ آمادگی نمی‌تواند از امروز عقب‌تر باشد"
            )
    
    # به‌روزرسانی
    try:
        updated_details = await ApplicationDetailsService.update(
            db,
            details,
            details_data
        )
        await db.commit()
        await db.refresh(updated_details)
        return updated_details

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """حذف جزئیات درخواست"""
    details = ApplicationDetailsService.get_by_user(db, current_user.id)
    
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="جزئیات درخواست یافت نشد"
        )
    
    try:
        ApplicationDetailsService.delete(db, details)
        
        # به‌روزرسانی applicant

        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


@router.get("/summary/", response_model=List[DetailsSummaryResponse])
async def get_details_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    details = await ApplicationDetailsService.get_by_user(
        db,
        current_user.id
        )
    
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="جزئیات درخواست ثبت نشده است"
        )
    
    summary = await ApplicationDetailsSelector.get_summery(details)
    return summary


# ========== ADMIN ENDPOINTS ==========
@router.get("/admin/all/")
def get_all_application_details(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """دریافت همه جزئیات درخواست (فقط ادمین)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی به این بخش ندارید"
        )
    
    details = db.query(ApplicationDetails).all()
    return details


@router.get("/statistics/")
def get_application_details_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """آمار کلی جزئیات درخواست (فقط ادمین)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی به این بخش ندارید"
        )
    
    stats = ApplicationDetailsSelector.get_statistics(db)
    return stats