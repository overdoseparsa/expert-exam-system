from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import Optional, Dict
from datetime import datetime, date

from .models import ApplicationDetails
from app.applicant.models import Applicant
from .enums import ConnectionTypeEnum, WorkScheduleEnum


class ApplicationDetailsSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> Optional[ApplicationDetails]:
        """دریافت جزئیات درخواست بر اساس user_id"""
        result = await db.execute(
            select(ApplicationDetails).where(ApplicationDetails.user_id == user_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_with_applicant(db: AsyncSession, user_id: int) -> Optional[tuple]:
        """دریافت جزئیات درخواست به همراه applicant"""
        result = await db.execute(
            select(ApplicationDetails, Applicant)
            .join(Applicant, Applicant.user_id == ApplicationDetails.user_id)
            .where(ApplicationDetails.user_id == user_id)
        )
        return result.first()

    @staticmethod
    async def count_all(db: AsyncSession) -> int:
        """تعداد کل جزئیات درخواست"""
        result = await db.execute(select(func.count(ApplicationDetails.id)))
        return result.scalar() or 0

    @staticmethod
    async def get_by_connection_type(db: AsyncSession, connection_type: str) -> list:
        """دریافت بر اساس نحوه آشنایی"""
        result = await db.execute(
            select(ApplicationDetails).where(ApplicationDetails.connection_type == connection_type)
        )
        return result.scalars().all()

    @staticmethod
    async def get_by_work_schedule(db: AsyncSession, schedule: str) -> list:
        """دریافت بر اساس نوع ساعت کاری"""
        result = await db.execute(
            select(ApplicationDetails).where(ApplicationDetails.preferred_work_schedule == schedule)
        )
        return result.scalars().all()

    @staticmethod
    async def get_available_from_range(db: AsyncSession, start_date: date, end_date: date) -> list:
        """دریافت بر اساس بازه تاریخ آمادگی"""
        result = await db.execute(
            select(ApplicationDetails).where(
                and_(
                    ApplicationDetails.available_from_date >= start_date,
                    ApplicationDetails.available_from_date <= end_date
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_salary_range(db: AsyncSession, min_salary: float, max_salary: float) -> list:
        """دریافت بر اساس بازه حقوق"""
        result = await db.execute(
            select(ApplicationDetails).where(
                and_(
                    ApplicationDetails.expected_salary >= min_salary,
                    ApplicationDetails.expected_salary <= max_salary
                )
            )
        )
        return result.scalars().all()

    @staticmethod
    async def get_summary_func(details: ApplicationDetails) -> Dict:

        if not details:
            return {"message": "جزئیات درخواست ثبت نشده است"}

        connection_stats = {
            "connection_type": details.connection_type.value,
            "has_referrer": details.connection_type == ConnectionTypeEnum.REFERRAL,
            "referrer_name": details.referrer_name if details.connection_type == ConnectionTypeEnum.REFERRAL else None
        }

        relatives_stats = {
            "has_relatives_in_company": details.has_relatives_in_company,
            "relative_name": details.relative_name if details.has_relatives_in_company else None,
            "relative_position": details.relative_position if details.has_relatives_in_company else None
        }

        health_stats = {
            "has_health_issue": details.has_health_issue,
            "has_disability": details.has_disability,
            "takes_medication": details.takes_medication
        }

        salary_stats = {
            "expected_salary": float(details.expected_salary),
            "salary_currency": details.salary_currency,
            "salary_period": details.salary_period
        }

        record_stats = {
            "has_criminal_record": details.has_criminal_record,
            "willing_to_relocate": details.willing_to_relocate,
            "has_transportation": details.has_transportation
        }

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
    async def get_statistics(db: AsyncSession) -> Dict:
        """آمار کلی جزئیات درخواست"""
        total_result = await db.execute(select(func.count(ApplicationDetails.id)))
        total = total_result.scalar() or 0

        connection_stats = {}
        for conn_type in ConnectionTypeEnum:
            count_result = await db.execute(
                select(func.count(ApplicationDetails.id)).where(ApplicationDetails.connection_type == conn_type)
            )
            connection_stats[conn_type.value] = count_result.scalar() or 0

        schedule_stats = {}
        for schedule in WorkScheduleEnum:
            count_result = await db.execute(
                select(func.count(ApplicationDetails.id)).where(ApplicationDetails.preferred_work_schedule == schedule)
            )
            schedule_stats[schedule.value] = count_result.scalar() or 0

        relatives_result = await db.execute(
            select(func.count(ApplicationDetails.id)).where(ApplicationDetails.has_relatives_in_company == True)
        )
        health_result = await db.execute(
            select(func.count(ApplicationDetails.id)).where(ApplicationDetails.has_health_issue == True)
        )
        criminal_result = await db.execute(
            select(func.count(ApplicationDetails.id)).where(ApplicationDetails.has_criminal_record == True)
        )
        avg_salary_result = await db.execute(
            select(func.avg(ApplicationDetails.expected_salary))
        )

        return {
            "total": total,
            "by_connection_type": connection_stats,
            "by_work_schedule": schedule_stats,
            "with_relatives_in_company": relatives_result.scalar() or 0,
            "with_health_issues": health_result.scalar() or 0,
            "with_criminal_record": criminal_result.scalar() or 0,
            "average_expected_salary": float(avg_salary_result.scalar() or 0)
        }
    @staticmethod
    async def get_summery(
        details : list[ApplicationDetails],

    ):
        result = []
        for detail in details :
            result.append(
                await ApplicationDetailsSelector.get_summary_func(
                    detail
                )
            )
        return result 