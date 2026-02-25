# services.py for job_applications
from sqlalchemy.orm import Session
from typing import List, Optional

from .models import JobApplication
from .schemas import (
    JobApplicationBatch,
    JobApplicationUpdate,
    SingleJobApplication
)

from jobs_information.models import JobDB
import datetime

class JobApplicationService:
    @staticmethod
    def create_batch(
        db: Session, 
        user_id: int, 
        application_batch: JobApplicationBatch
    ) -> List[JobApplication]:
        
        created_applications = []
        
        for app_data in application_batch.applications:
            new_application = JobApplication(
                user_id=user_id,
                job_id=app_data.job_id,
                score=app_data.score,
                priority=app_data.priority,
                status="pending"
            )
            db.add(new_application)
            created_applications.append(new_application)
        
        db.flush()
        return created_applications
    
    @staticmethod
    def create_single(
        db: Session,
        user_id: int,
        application_data: SingleJobApplication
    ) -> JobApplication:
        """ایجاد یک درخواست شغل"""
        new_application = JobApplication(
            user_id=user_id,
            job_id=application_data.job_id,
            score=application_data.score,
            priority=application_data.priority,
            status="pending"
        )
        db.add(new_application)
        db.flush()
        return new_application
    
    @staticmethod
    def get_by_id(db: Session, application_id: int, user_id: Optional[int] = None) -> Optional[JobApplication]:
        """دریافت درخواست با آیدی"""
        query = db.query(JobApplication).filter(JobApplication.id == application_id)
        if user_id:
            query = query.filter(JobApplication.user_id == user_id)
        return query.first()
    
    @staticmethod
    def get_by_user(db: Session, user_id: int) -> List[JobApplication]:
        """دریافت درخواست‌های یک کاربر"""
        return db.query(JobApplication).filter(JobApplication.user_id == user_id).all()
    
    @staticmethod
    def update(
        db: Session, 
        application: JobApplication, 
        update_data: JobApplicationUpdate
    ) -> JobApplication:
        """به‌روزرسانی درخواست شغل"""
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(application, field, value)
        
        application.updated_at = datetime.utcnow()
        db.add(application)
        db.flush()
        return application
    
    @staticmethod
    def delete(db: Session, application: JobApplication) -> None:
        """حذف درخواست شغل"""
        db.delete(application)
        db.flush()
    
    @staticmethod
    def count_by_user(db: Session, user_id: int) -> int:
        """تعداد درخواست‌های یک کاربر"""
        return db.query(JobApplication).filter(JobApplication.user_id == user_id).count()
    
    @staticmethod
    def validate_jobs(db: Session, job_ids: List[int]) -> List[JobDB]:
        """اعتبارسنجی شغل‌ها"""
        jobs = db.query(JobDB).filter(JobDB.id.in_(job_ids)).all()
        
        if len(jobs) != len(job_ids):
            missing_ids = set(job_ids) - {job.id for job in jobs}
            raise ValueError(f"شغل‌های با آیدی {missing_ids} یافت نشد")
        
        # بررسی فعال بودن شغل‌ها
        inactive_jobs = [job for job in jobs if not job.is_active]
        if inactive_jobs:
            raise ValueError(f"شغل‌های زیر غیرفعال هستند: {', '.join([j.title for j in inactive_jobs])}")
        
        # بررسی مهلت درخواست
        expired_jobs = []
        for job in jobs:
            if job.deadline and job.deadline < datetime.utcnow().date():
                expired_jobs.append(job.title)
        
        if expired_jobs:
            raise ValueError(f"مهلت درخواست برای شغل‌های زیر به پایان رسیده: {', '.join(expired_jobs)}")
        
        return jobs