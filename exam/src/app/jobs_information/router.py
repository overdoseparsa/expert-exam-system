# router.py for jobs_information
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db
from auth.depends import get_current_user
from auth.models import User
from .schemas import JobCreate, JobUpdate, JobResponse
from .services import JobService, AdminJobAssignmentService
from .selectors import JobSelector, AdminJobAssignmentSelector

router = APIRouter(prefix="/job", tags=["Jobs Information"])


# ========== JOB ==========
@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    job: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        db_job = JobService.create(db, job)
        
        AdminJobAssignmentService.create(db, current_user.id, db_job.id)
        
        db.commit()
        db.refresh(db_job)
        
        return db_job
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ایجاد شغل: {str(e)}"
        )


@router.get("/", response_model=List[JobResponse])
def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """دریافت لیست شغل‌ها"""
    # اگر ادمین است، فقط شغل‌های خودش را ببیند
    if current_user.role == "admin":
        jobs = JobService.get_by_admin(db, current_user.id, skip, limit, active_only)
    else:
        jobs = JobService.get_all(db, skip, limit, active_only)
    
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int, 
    db: Session = Depends(get_db)
):
    """دریافت اطلاعات یک شغل خاص"""
    job = JobService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شغل یافت نشد"
        )
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int, 
    job_update: JobUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """به‌روزرسانی اطلاعات شغل"""
    job = JobService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شغل یافت نشد"
        )
    
    # بررسی دسترسی ادمین
    if current_user.role == "admin":
        is_assigned = AdminJobAssignmentSelector.check_assignment(db, current_user.id, job_id)
        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="شما به این شغل دسترسی ندارید"
            )
    
    try:
        updated_job = JobService.update(db, job, job_update)
        db.commit()
        db.refresh(updated_job)
        return updated_job
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/{job_id}")
def delete_job(
    job_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """حذف شغل"""
    job = JobService.get_by_id(db, job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شغل یافت نشد"
        )
    
    # بررسی دسترسی ادمین
    if current_user.role == "admin":
        is_assigned = AdminJobAssignmentSelector.check_assignment(db, current_user.id, job_id)
        if not is_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="شما به این شغل دسترسی ندارید"
            )
    
    try:
        # حذف انتساب‌ها
        AdminJobAssignmentService.delete_by_job(db, job_id)
        # حذف شغل
        JobService.delete(db, job)
        db.commit()
        
        return {"message": "شغل با موفقیت حذف شد"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


# ========== SEARCH ==========
@router.get("/search/", response_model=List[JobResponse])
def search_jobs(
    q: Optional[str] = Query(None, min_length=2, description="کلمه کلیدی"),
    location: Optional[str] = None,
    company: Optional[str] = None,
    job_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """جستجوی شغل‌ها"""
    jobs = JobSelector.search_jobs(
        db, 
        search_term=q, 
        location=location, 
        company=company,
        job_type=job_type
    )
    return jobs


# ========== ACTIVE JOBS ==========
@router.get("/active/", response_model=List[JobResponse])
def get_active_jobs(
    db: Session = Depends(get_db)
):
    """دریافت شغل‌های فعال"""
    jobs = JobSelector.get_active_jobs(db)
    return jobs


# ========== UPCOMING DEADLINES ==========
@router.get("/deadlines/upcoming", response_model=List[JobResponse])
def get_upcoming_deadlines(
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """دریافت شغل‌هایی که مهلت آنها نزدیک است"""
    jobs = JobSelector.get_upcoming_deadlines(db, days)
    return jobs


# ========== STATISTICS ==========
@router.get("/statistics")
def get_job_statistics(
    db: Session = Depends(get_db)
):
    """دریافت آمار شغل‌ها"""
    stats = JobSelector.get_statistics(db)
    return stats


# ========== BY DATE RANGE ==========
@router.get("/by-date/", response_model=List[JobResponse])
def get_jobs_by_date_range(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db)
):
    """دریافت شغل‌ها در بازه زمانی"""
    jobs = JobSelector.get_jobs_by_date_range(db, start_date, end_date)
    return jobs