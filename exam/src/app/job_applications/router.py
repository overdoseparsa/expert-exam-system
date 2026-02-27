# router.py for job_applications
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from database import get_db
from auth.depends import get_current_user_obj as get_current_user
from auth.models import User
from app.jobs_information.models import JobDB 
from .models  import JobApplication
from app.applicant.models import Applicant

from .schemas import (
    JobApplicationBatch,
    JobApplicationResponse,
    JobApplicationUpdate,
    SingleJobApplication,
    AvailableJobResponse,
    ApplicationsSummaryResponse
)
from .services import JobApplicationService
from .selectors import JobApplicationSelector


router = APIRouter(prefix="/job-applications", tags=["Job Applications"])





# ========== JOB APPLICATIONS ==========
@router.get("/", response_model=List[JobApplicationResponse])
async def get_my_job_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت لیست درخواست‌های شغل کاربر"""
    applications = await JobApplicationService.get_by_user(db, current_user.id)
    
    # اضافه کردن اطلاعات شغل به پاسخ
    result = []
    for app in applications:
        job = await  db.query(JobDB).filter(JobDB.id == app.job_id).first()
        app_data = JobApplicationResponse.from_orm(app)
        if job:
            app_data.job_title = job.title
            app_data.company = job.company
            app_data.location = job.location
        result.append(app_data)
    
    return result


@router.post("/apply", response_model=List[JobApplicationResponse], status_code=status.HTTP_201_CREATED)
def apply_for_jobs(
    application_batch: JobApplicationBatch,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """ثبت درخواست برای ۳ شغل"""
    try:
        # بررسی اینکه قبلاً درخواست نداده باشد
        existing_count = JobApplicationSelector.count_by_user(db, current_user.id)
        if existing_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="شما قبلاً برای شغل‌ها درخواست داده‌اید"
            )
        
        # بررسی وجود و اعتبار شغل‌ها
        job_ids = [app.job_id for app in application_batch.applications]
        jobs = JobApplicationService.validate_jobs(db, job_ids)
        
        # ایجاد درخواست‌ها
        created_applications = JobApplicationService.create_batch(
            db, current_user.id, application_batch
        )
        

        db.commit()
        
        # برگرداندن پاسخ با اطلاعات کامل
        result = []
        for app in created_applications:
            job = next(j for j in jobs if j.id == app.job_id)
            app_data = JobApplicationResponse.from_orm(app)
            app_data.job_title = job.title
            app_data.company = job.company
            app_data.location = job.location
            result.append(app_data)
        
        return result
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت درخواست‌ها: {str(e)}"
        )


@router.put("/{application_id}", response_model=JobApplicationResponse)
def update_job_application(
    application_id: int,
    update_data: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """به‌روزرسانی درخواست شغل"""
    application = JobApplicationService.get_by_id(db, application_id, current_user.id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="درخواست شغل یافت نشد"
        )
    
    try:
        updated_app = JobApplicationService.update(db, application, update_data)
        

        db.commit()
        db.refresh(updated_app)
        
        # اضافه کردن اطلاعات شغل
        job = db.query(JobDB).filter(JobDB.id == updated_app.job_id).first()
        response = JobApplicationResponse.from_orm(updated_app)
        if job:
            response.job_title = job.title
            response.company = job.company
            response.location = job.location
        
        return response
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """حذف درخواست شغل (انصراف)"""
    application = JobApplicationService.get_by_id(db, application_id, current_user.id)
    
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="درخواست شغل یافت نشد"
        )
    
    try:
        JobApplicationService.delete(db, application)
        
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


@router.get("/available-jobs", response_model=List[AvailableJobResponse])
def get_available_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """دریافت لیست شغل‌های فعال و موجود"""
    available_jobs = JobApplicationSelector.get_available_jobs(db, current_user.id)
    
    result = []
    for job in available_jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "posted_date": job.posted_date,
            "deadline": job.deadline,
            "job_type": job.job_type,
            "salary": job.salary
        })
    
    return result


@router.get("/summary", response_model=ApplicationsSummaryResponse)
def get_applications_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """خلاصه درخواست‌های شغل کاربر"""
    summary = JobApplicationSelector.get_summary(db, current_user.id)
    return summary


# ========== ADMIN ENDPOINTS ==========
@router.get("/admin/all", response_model=List[JobApplicationResponse])
def get_all_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """دریافت همه درخواست‌ها (فقط ادمین)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی به این بخش ندارید"
        )
    
    applications = db.query(JobApplication).all()
    
    # اضافه کردن اطلاعات شغل و کاربر
    result = []
    for app in applications:
        job = db.query(JobDB).filter(JobDB.id == app.job_id).first()
        user = db.query(User).filter(User.id == app.user_id).first()
        applicant = db.query(Applicant).filter(Applicant.user_id == app.user_id).first()
        
        app_data = JobApplicationResponse.from_orm(app)
        if job:
            app_data.job_title = job.title
            app_data.company = job.company
        app_data.applicant_name = f"{applicant.name} {applicant.family}" if applicant else None
        
        result.append(app_data)
    
    return result


@router.get("/statistics")
def get_application_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """آمار کلی درخواست‌ها (فقط ادمین)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی به این بخش ندارید"
        )
    
    stats = JobApplicationSelector.get_statistics(db)
    return stats