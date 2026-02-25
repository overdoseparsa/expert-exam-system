# services.py for jobs_information
from sqlalchemy.orm import Session
from typing import List, Optional


from .models import JobDB
from admin.models import AdminJobAssignment
from auth.models import User


from .schemas import JobCreate, JobUpdate


class JobService:

    @staticmethod
    def create(db: Session, job_data: JobCreate) -> JobDB:
        db_job = JobDB(**job_data.dict())
        db.add(db_job)
        db.flush()
        return db_job
    
    @staticmethod
    def get_by_id(db: Session, job_id: int) -> Optional[JobDB]:
        return db.query(JobDB).filter(JobDB.id == job_id).first()
    
    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 50,
        active_only: bool = True
    ) -> List[JobDB]:
        query = db.query(JobDB)
        if active_only:
            query = query.filter(JobDB.is_active == True)
        return query.order_by(JobDB.posted_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_by_admin(
        db: Session,
        admin_id: int,
        skip: int = 0,
        limit: int = 50,
        active_only: bool = True
    ) -> List[JobDB]:
        query = db.query(JobDB).filter(
            JobDB.id.in_(
                db.query(AdminJobAssignment.job_id).filter(
                    AdminJobAssignment.admin_id == admin_id
                )
            )
        )
        
        if active_only:
            query = query.filter(JobDB.is_active == True)
        
        return query.order_by(JobDB.posted_date.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db: Session, job: JobDB, job_data: JobUpdate) -> JobDB:
        update_data = job_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(job, field, value)
        
        db.add(job)
        db.flush()
        return job
    
    @staticmethod
    def delete(db: Session, job: JobDB) -> None:
        db.delete(job)
        db.flush()
    
    @staticmethod
    def count(db: Session, active_only: bool = True) -> int:
        query = db.query(JobDB)
        if active_only:
            query = query.filter(JobDB.is_active == True)
        return query.count()


class AdminJobAssignmentService:
    @staticmethod
    def create(db: Session, admin_id: int, job_id: int) -> AdminJobAssignment:
        admin_job_assignment = AdminJobAssignment(
            admin_id=admin_id,
            job_id=job_id
        )
        db.add(admin_job_assignment)
        db.flush()
        return admin_job_assignment
    
    @staticmethod
    def delete(db: Session, assignment_id: int) -> None:
        assignment = db.query(AdminJobAssignment).filter(
            AdminJobAssignment.id == assignment_id
        ).first()
        if assignment:
            db.delete(assignment)
            db.flush()
    
    @staticmethod
    def delete_by_job(db: Session, job_id: int) -> None:
        """حذف همه انتساب‌های یک شغل"""
        db.query(AdminJobAssignment).filter(
            AdminJobAssignment.job_id == job_id
        ).delete()
        db.flush()