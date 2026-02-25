# services.py for application_details
from sqlalchemy.orm import Session
from typing import Optional
import datetime
from .models import ApplicationDetails
from .schemas import (
    ApplicationDetailsCreate,
    ApplicationDetailsUpdate
)


class ApplicationDetailsService:
    @staticmethod
    def get_by_user(db: Session, user_id: int) -> Optional[ApplicationDetails]:
        """دریافت جزئیات درخواست بر اساس user_id"""
        return db.query(ApplicationDetails).filter(
            ApplicationDetails.user_id == user_id
        ).first()
    
    @staticmethod
    def create(
        db: Session, 
        user_id: int, 
        data: ApplicationDetailsCreate
    ) -> ApplicationDetails:
        """ایجاد جزئیات درخواست جدید"""
        new_details = ApplicationDetails(
            user_id=user_id,
            connection_type=data.connection_type,
            referrer_name=data.referrer_name,
            referrer_relationship=data.referrer_relationship,
            referrer_phone=data.referrer_phone,
            has_relatives_in_company=data.has_relatives_in_company,
            relative_name=data.relative_name,
            relative_position=data.relative_position,
            relative_relationship=data.relative_relationship,
            available_from_date=data.available_from_date,
            preferred_work_schedule=data.preferred_work_schedule,
            expected_salary=data.expected_salary,
            salary_currency=data.salary_currency,
            salary_period=data.salary_period,
            has_health_issue=data.has_health_issue,
            health_issue_description=data.health_issue_description,
            has_disability=data.has_disability,
            disability_description=data.disability_description,
            takes_medication=data.takes_medication,
            medication_details=data.medication_details,
            has_criminal_record=data.has_criminal_record,
            criminal_record_details=data.criminal_record_details,
            favorite_sport=data.favorite_sport,
            has_transportation=data.has_transportation,
            willing_to_relocate=data.willing_to_relocate,
            other_comments=data.other_comments
        )
        db.add(new_details)
        db.flush()
        return new_details
    
    @staticmethod
    def update(
        db: Session,
        details: ApplicationDetails,
        data: ApplicationDetailsUpdate
    ) -> ApplicationDetails:
        """به‌روزرسانی جزئیات درخواست"""
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(details, field, value)
        
        details.updated_at = datetime.utcnow()
        db.add(details)
        db.flush()
        return details
    
    @staticmethod
    def delete(db: Session, details: ApplicationDetails) -> None:
        """حذف جزئیات درخواست"""
        db.delete(details)
        db.flush()
    
    @staticmethod
    def exists(db: Session, user_id: int) -> bool:
        """بررسی وجود جزئیات درخواست"""
        return db.query(ApplicationDetails).filter(
            ApplicationDetails.user_id == user_id
        ).first() is not None