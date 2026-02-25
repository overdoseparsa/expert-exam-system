# selectors.py for jobs_information
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc,func
from typing import List, Optional, Dict
from datetime import date

from .models import JobDB
from admin.models import AdminJobAssignment
from auth.models import User


class JobSelector:
    @staticmethod
    def get_by_id(db: Session, job_id: int) -> Optional[JobDB]:
        return db.query(JobDB).filter(JobDB.id == job_id).first()
    
    @staticmethod
    def get_active_jobs(db: Session) -> List[JobDB]:
        """دریافت شغل‌های فعال"""
        return db.query(JobDB).filter(JobDB.is_active == True).order_by(desc(JobDB.posted_date)).all()
    
    @staticmethod
    def get_jobs_by_admin(db: Session, admin_id: int, active_only: bool = True) -> List[JobDB]:
        """دریافت شغل‌های یک ادمین خاص"""
        query = db.query(JobDB).filter(
            JobDB.id.in_(
                db.query(AdminJobAssignment.job_id).filter(
                    AdminJobAssignment.admin_id == admin_id
                )
            )
        )
        
        if active_only:
            query = query.filter(JobDB.is_active == True)
        
        return query.order_by(desc(JobDB.posted_date)).all()
    
    @staticmethod
    def search_jobs(
        db: Session,
        search_term: Optional[str] = None,
        location: Optional[str] = None,
        company: Optional[str] = None,
        job_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[JobDB]:
        """جستجوی شغل‌ها"""
        query = db.query(JobDB)
        
        if active_only:
            query = query.filter(JobDB.is_active == True)
        
        filters = []
        if search_term:
            filters.append(
                or_(
                    JobDB.title.contains(search_term),
                    JobDB.description.contains(search_term),
                    JobDB.requirements.contains(search_term)
                )
            )
        
        if location:
            filters.append(JobDB.location.contains(location))
        
        if company:
            filters.append(JobDB.company.contains(company))
        
        if job_type:
            filters.append(JobDB.job_type == job_type)
        
        if filters:
            query = query.filter(and_(*filters))
        
        return query.order_by(desc(JobDB.posted_date)).all()
    
    @staticmethod
    def get_jobs_by_date_range(
        db: Session,
        start_date: date,
        end_date: date,
        active_only: bool = True
    ) -> List[JobDB]:
        """دریافت شغل‌ها در بازه زمانی"""
        query = db.query(JobDB).filter(
            and_(
                JobDB.posted_date >= start_date,
                JobDB.posted_date <= end_date
            )
        )
        
        if active_only:
            query = query.filter(JobDB.is_active == True)
        
        return query.order_by(desc(JobDB.posted_date)).all()
    
    @staticmethod
    def get_upcoming_deadlines(db: Session, days: int = 7) -> List[JobDB]:

        from datetime import timedelta
        today = date.today()
        deadline_threshold = today + timedelta(days=days)
        
        return db.query(JobDB).filter(
            and_(
                JobDB.is_active == True,
                JobDB.deadline.isnot(None),
                JobDB.deadline <= deadline_threshold,
                JobDB.deadline >= today
            )
        ).order_by(JobDB.deadline).all()
    
    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """آمار کلی شغل‌ها"""
        total_jobs = db.query(JobDB).count()
        active_jobs = db.query(JobDB).filter(JobDB.is_active == True).count()
        
        # آمار بر اساس نوع شغل
        job_type_stats = {}
        job_types = db.query(JobDB.job_type, func.count(JobDB.id)).filter(
            JobDB.job_type.isnot(None)
        ).group_by(JobDB.job_type).all()
        
        for job_type, count in job_types:
            job_type_stats[job_type] = count
        
        # آمار بر اساس شرکت
        company_stats = {}
        companies = db.query(JobDB.company, func.count(JobDB.id)).group_by(
            JobDB.company
        ).order_by(desc(func.count(JobDB.id))).limit(10).all()
        
        for company, count in companies:
            company_stats[company] = count
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "inactive_jobs": total_jobs - active_jobs,
            "by_job_type": job_type_stats,
            "top_companies": company_stats
        }


class AdminJobAssignmentSelector:
    @staticmethod
    def get_by_admin(db: Session, admin_id: int) -> List[AdminJobAssignment]:
        """دریافت انتساب‌های یک ادمین"""
        return db.query(AdminJobAssignment).filter(
            AdminJobAssignment.admin_id == admin_id
        ).all()
    
    @staticmethod
    def get_by_job(db: Session, job_id: int) -> List[AdminJobAssignment]:
        """دریافت انتساب‌های یک شغل"""
        return db.query(AdminJobAssignment).filter(
            AdminJobAssignment.job_id == job_id
        ).all()
    
    @staticmethod
    def check_assignment(db: Session, admin_id: int, job_id: int) -> bool:
        """بررسی وجود انتساب"""
        return db.query(AdminJobAssignment).filter(
            and_(
                AdminJobAssignment.admin_id == admin_id,
                AdminJobAssignment.job_id == job_id
            )
        ).first() is not None