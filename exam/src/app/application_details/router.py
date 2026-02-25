# router.py for application_details
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, date

from database import get_db
from auth.depends import get_current_user
from auth.models import User
from application_details.models import ApplicationDetails 

from .schemas import (
    ApplicationDetailsCreate,
    ApplicationDetailsUpdate,
    ApplicationDetailsResponse,
    DetailsSummaryResponse
)
from .services import ApplicationDetailsService
from .selectors import ApplicationDetailsSelector


router = APIRouter(prefix="/application-details", tags=["Application Details"])





# ========== APPLICATION DETAILS ==========
@router.get("/", response_model=Optional[ApplicationDetailsResponse])
def get_application_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت جزئیات درخواست"""
    details = ApplicationDetailsService.get_by_user(db, current_user.id)
    return details


@router.post("/", response_model=ApplicationDetailsResponse, status_code=status.HTTP_201_CREATED)
def create_application_details(
    details_data: ApplicationDetailsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ایجاد جزئیات درخواست"""
    # بررسی آیا قبلاً ApplicationDetails دارد
    exists = ApplicationDetailsService.exists(db, current_user.id)
    if exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="شما قبلاً جزئیات درخواست را ثبت کرده‌اید"
        )
    
    try:
        new_details = ApplicationDetailsService.create(db, current_user.id, details_data)
        

        

        
        db.commit()
        db.refresh(new_details)
        
        return new_details
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت جزئیات درخواست: {str(e)}"
        )


@router.put("/", response_model=ApplicationDetailsResponse)
def update_application_details(
    details_data: ApplicationDetailsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """به‌روزرسانی جزئیات درخواست"""
    details = ApplicationDetailsService.get_by_user(db, current_user.id)
    
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شما هنوز جزئیات درخواست را ثبت نکرده‌اید"
        )
    
    try:
        # اعتبارسنجی تاریخ آمادگی اگر آپدیت شده
        if 'available_from_date' in details_data.dict(exclude_unset=True):
            if details_data.available_from_date and details_data.available_from_date < date.today():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="تاریخ آمادگی نمی‌تواند از امروز عقب‌تر باشد"
                )
        
        updated_details = ApplicationDetailsService.update(db, details, details_data)

        
        db.commit()
        db.refresh(updated_details)
        
        return updated_details
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_application_details(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
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


@router.get("/summary", response_model=DetailsSummaryResponse)
def get_details_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """خلاصه آماری جزئیات درخواست"""
    details = ApplicationDetailsService.get_by_user(db, current_user.id)
    
    if not details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="جزئیات درخواست ثبت نشده است"
        )
    
    summary = ApplicationDetailsSelector.get_summary(db, details)
    return summary


# ========== ADMIN ENDPOINTS ==========
@router.get("/admin/all")
def get_all_application_details(
    db: Session = Depends(get_db),
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


@router.get("/statistics")
def get_application_details_statistics(
    db: Session = Depends(get_db),
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