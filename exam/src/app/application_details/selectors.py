from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, Dict
from datetime import datetime, date

from .models import ApplicationDetails
from app.applicant.models import Applicant
from .enums import ConnectionTypeEnum , WorkScheduleEnum


class ApplicationDetailsSelector:
    @staticmethod
    def get_by_user_id(db: Session, user_id: int) -> Optional[ApplicationDetails]:
        """دریافت جزئیات درخواست بر اساس user_id"""
        return db.query(ApplicationDetails).filter(
            ApplicationDetails.user_id == user_id
        ).first()
    
    @staticmethod
    def get_with_applicant(db: Session, user_id: int) -> Optional[tuple]:
        """دریافت جزئیات درخواست به همراه applicant"""
        return db.query(ApplicationDetails, Applicant).join(
            Applicant, Applicant.user_id == ApplicationDetails.user_id
        ).filter(ApplicationDetails.user_id == user_id).first()
    
    @staticmethod
    def count_all(db: Session) -> int:
        """تعداد کل جزئیات درخواست"""
        return db.query(ApplicationDetails).count()
    
    @staticmethod
    def get_by_connection_type(db: Session, connection_type: str) -> list:
        """دریافت بر اساس نحوه آشنایی"""
        return db.query(ApplicationDetails).filter(
            ApplicationDetails.connection_type == connection_type
        ).all()
    
    @staticmethod
    def get_by_work_schedule(db: Session, schedule: str) -> list:
        """دریافت بر اساس نوع ساعت کاری"""
        return db.query(ApplicationDetails).filter(
            ApplicationDetails.preferred_work_schedule == schedule
        ).all()
    
    @staticmethod
    def get_available_from_range(db: Session, start_date: date, end_date: date) -> list:
        """دریافت بر اساس بازه تاریخ آمادگی"""
        return db.query(ApplicationDetails).filter(
            and_(
                ApplicationDetails.available_from_date >= start_date,
                ApplicationDetails.available_from_date <= end_date
            )
        ).all()
    
    @staticmethod
    def get_salary_range(db: Session, min_salary: float, max_salary: float) -> list:
        """دریافت بر اساس بازه حقوق"""
        return db.query(ApplicationDetails).filter(
            and_(
                ApplicationDetails.expected_salary >= min_salary,
                ApplicationDetails.expected_salary <= max_salary
            )
        ).all()
    
    @staticmethod
    def get_summary(db: Session, details: ApplicationDetails) -> Dict:
        """خلاصه آماری جزئیات درخواست"""
        if not details:
            return {"message": "جزئیات درخواست ثبت نشده است"}
        
        # آمار نحوه آشنایی
        connection_stats = {
            "connection_type": details.connection_type.value,
            "has_referrer": details.connection_type == ConnectionTypeEnum.REFERRAL,
            "referrer_name": details.referrer_name if details.connection_type == ConnectionTypeEnum.REFERRAL else None
        }
        
        # آمار بستگان
        relatives_stats = {
            "has_relatives_in_company": details.has_relatives_in_company,
            "relative_name": details.relative_name if details.has_relatives_in_company else None,
            "relative_position": details.relative_position if details.has_relatives_in_company else None
        }
        
        # آمار سلامتی
        health_stats = {
            "has_health_issue": details.has_health_issue,
            "has_disability": details.has_disability,
            "takes_medication": details.takes_medication
        }
        
        # آمار حقوق
        salary_stats = {
            "expected_salary": float(details.expected_salary),
            "salary_currency": details.salary_currency,
            "salary_period": details.salary_period
        }
        
        # آمار سوابق
        record_stats = {
            "has_criminal_record": details.has_criminal_record,
            "willing_to_relocate": details.willing_to_relocate,
            "has_transportation": details.has_transportation
        }
        
        # محاسبه روزهای باقی‌مانده
        today = date.today()
        days_until = (details.available_from_date - today).days
        
        return {
            "connection_info": connection_stats,
            "relatives_info": relatives_stats,
            "health_info": health_stats,
            "salary_info": salary_stats,
            "record_info": record_stats,
            "available_from": details.available_from_date.isoformat(),
            "work_schedule": details.preferred_work_schedule.value,
            "favorite_sport": details.favorite_sport,
            "days_until_available": max(0, days_until)
        }
    
    @staticmethod
    def get_statistics(db: Session) -> Dict:
        """آمار کلی جزئیات درخواست"""
        total = db.query(ApplicationDetails).count()
        
        # آمار بر اساس نحوه آشنایی
        connection_stats = {}
        for conn_type in ConnectionTypeEnum:
            count = db.query(ApplicationDetails).filter(
                ApplicationDetails.connection_type == conn_type
            ).count()
            connection_stats[conn_type.value] = count
        
        # آمار بر اساس نوع ساعت کاری
        schedule_stats = {}
        for schedule in WorkScheduleEnum:
            count = db.query(ApplicationDetails).filter(
                ApplicationDetails.preferred_work_schedule == schedule
            ).count()
            schedule_stats[schedule.value] = count
        
        # آمار بستگان در شرکت
        relatives_count = db.query(ApplicationDetails).filter(
            ApplicationDetails.has_relatives_in_company == True
        ).count()
        
        # آمار مسائل سلامتی
        health_count = db.query(ApplicationDetails).filter(
            ApplicationDetails.has_health_issue == True
        ).count()
        
        # آمار سابقه کیفری
        criminal_count = db.query(ApplicationDetails).filter(
            ApplicationDetails.has_criminal_record == True
        ).count()
        
        # میانگین حقوق درخواستی
        avg_salary = db.query(func.avg(ApplicationDetails.expected_salary)).scalar() or 0
        
        return {
            "total": total,
            "by_connection_type": connection_stats,
            "by_work_schedule": schedule_stats,
            "with_relatives_in_company": relatives_count,
            "with_health_issues": health_count,
            "with_criminal_record": criminal_count,
            "average_expected_salary": float(avg_salary)
        }