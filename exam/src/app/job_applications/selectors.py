# selectors.py for job_applications
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict
from datetime import datetime

from .models import JobApplication
from app.jobs_information.models import JobDB


class JobApplicationSelector:
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
        return db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).order_by(JobApplication.priority).all()
    
    @staticmethod
    def get_by_job(db: Session, job_id: int) -> List[JobApplication]:
        """دریافت درخواست‌های یک شغل"""
        return db.query(JobApplication).filter(
            JobApplication.job_id == job_id
        ).order_by(JobApplication.score.desc()).all()
    
    @staticmethod
    def get_by_status(db: Session, status: str, user_id: Optional[int] = None) -> List[JobApplication]:
        """دریافت درخواست‌ها بر اساس وضعیت"""
        query = db.query(JobApplication).filter(JobApplication.status == status)
        if user_id:
            query = query.filter(JobApplication.user_id == user_id)
        return query.all()
    
    @staticmethod
    def check_exists(db: Session, user_id: int, job_id: int) -> bool:
        """بررسی وجود درخواست برای شغل خاص"""
        return db.query(JobApplication).filter(
            and_(
                JobApplication.user_id == user_id,
                JobApplication.job_id == job_id
            )
        ).first() is not None
    
    @staticmethod
    def count_by_user(db: Session, user_id: int) -> int:
        """تعداد درخواست‌های یک کاربر"""
        return db.query(JobApplication).filter(JobApplication.user_id == user_id).count()
    
    @staticmethod
    def get_available_jobs(db: Session, user_id: int) -> List[JobDB]:
        """دریافت شغل‌های قابل درخواست برای کاربر"""
        # شغل‌هایی که کاربر قبلاً برای آنها درخواست نداده
        applied_job_ids = db.query(JobApplication.job_id).filter(
            JobApplication.user_id == user_id
        ).subquery()
        
        available_jobs = db.query(JobDB).filter(
            JobDB.is_active == True,
            JobDB.id.notin_(applied_job_ids),
            (JobDB.deadline.is_(None) | (JobDB.deadline >= datetime.utcnow().date()))
        ).order_by(JobDB.posted_date.desc()).all()
        
        return available_jobs
    
    @staticmethod
    def get_summary(db: Session, user_id: int) -> Dict:
        """خلاصه درخواست‌های شغل کاربر"""
        applications = db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        ).all()
        
        total_applications = len(applications)
        status_count = {
            "pending": 0,
            "reviewed": 0,
            "accepted": 0,
            "rejected": 0,
            "withdrawn": 0
        }
        
        for app in applications:
            status_count[app.status] = status_count.get(app.status, 0) + 1
        
        # میانگین امتیاز
        avg_score = sum(app.score for app in applications) / total_applications if applications else 0
        
        # آخرین درخواست
        last_app = applications[-1] if applications else None
        
        return {
            "total_applications": total_applications,
            "status_distribution": status_count,
            "average_score": round(avg_score, 2),
            "last_application": last_app.applied_at if last_app else None,
            "can_apply_more": total_applications < 3
        }
    
    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """آمار کلی درخواست‌ها"""
        total = db.query(JobApplication).count()
        
        # آمار بر اساس وضعیت
        status_stats = {}
        for status in ["pending", "reviewed", "accepted", "rejected", "withdrawn"]:
            count = db.query(JobApplication).filter(JobApplication.status == status).count()
            status_stats[status] = count
        
        # آمار بر اساس امتیاز
        score_stats = {}
        for score in [5.1, 5.2, 5.3, 5.4]:
            count = db.query(JobApplication).filter(JobApplication.score == score).count()
            score_stats[str(score)] = count
        
        return {
            "total_applications": total,
            "by_status": status_stats,
            "by_score": score_stats
        }