# selectors.py for training_courses
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Dict, Any
from datetime import date
import re

from .models import TrainingCourse


class TrainingSelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> List[TrainingCourse]:
        """دریافت لیست دوره‌های آموزشی بر اساس user_id"""
        query = select(TrainingCourse).where(TrainingCourse.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int, user_id: int) -> Optional[TrainingCourse]:
        """دریافت یک دوره آموزشی با آیدی"""
        query = select(TrainingCourse).where(
            and_(
                TrainingCourse.id == course_id,
                TrainingCourse.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_institute(db: AsyncSession, user_id: int, institute: str) -> List[TrainingCourse]:
        """دریافت دوره‌ها بر اساس مؤسسه"""
        query = select(TrainingCourse).where(
            and_(
                TrainingCourse.user_id == user_id,
                TrainingCourse.institute.ilike(f"%{institute}%")
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_with_certificate(db: AsyncSession, user_id: int) -> List[TrainingCourse]:
        """دریافت دوره‌هایی که گواهینامه دارند"""
        query = select(TrainingCourse).where(
            and_(
                TrainingCourse.user_id == user_id,
                TrainingCourse.has_certificate == True
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_year(db: AsyncSession, user_id: int, year: int) -> List[TrainingCourse]:
        """دریافت دوره‌های یک سال خاص"""
        query = select(TrainingCourse).where(
            and_(
                TrainingCourse.user_id == user_id,
                func.extract('year', TrainingCourse.start_date) == year
            )
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        """تعداد دوره‌های آموزشی یک کاربر"""
        query = select(func.count()).select_from(TrainingCourse).where(TrainingCourse.user_id == user_id)
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def extract_hours_from_duration(duration: str) -> int:
        """استخراج عدد از رشته duration (مثال: '80 ساعت' -> 80)"""
        match = re.search(r'(\d+)', duration)
        return int(match.group(1)) if match else 0
    
    @staticmethod
    async def get_summary(db: AsyncSession, user_id: int) -> Dict[str, Any]:
        """خلاصه آماری دوره‌های آموزشی"""
        query = select(TrainingCourse).where(TrainingCourse.user_id == user_id)
        result = await db.execute(query)
        courses = result.scalars().all()
        
        total_courses = len(courses)
        with_certificate = len([c for c in courses if c.has_certificate])
        
        # محاسبه کل ساعت آموزش
        total_hours = 0
        for course in courses:
            hours = await TrainingSelector.extract_hours_from_duration(course.duration)
            total_hours += hours
        
        # محاسبه سال‌های مختلف
        years = {}
        institutes = set()
        
        for course in courses:
            year = course.start_date.year
            years[year] = years.get(year, 0) + 1
            institutes.add(course.institute)
        
        return {
            "total_courses": total_courses,
            "courses_with_certificate": with_certificate,
            "certificate_percentage": round((with_certificate / total_courses * 100) if total_courses > 0 else 0, 1),
            "total_hours": total_hours,
            "average_hours_per_course": round(total_hours / total_courses, 1) if total_courses > 0 else 0,
            "courses_by_year": dict(sorted(years.items())),
            "institutes": list(institutes)
        }
    
    @staticmethod
    async def get_statistics(db: AsyncSession, user_id: int) -> Dict:
        """آمار دوره‌های آموزشی"""
        # تعداد کل
        total_query = select(func.count()).select_from(TrainingCourse).where(TrainingCourse.user_id == user_id)
        total = await db.execute(total_query)
        
        # تعداد با گواهینامه
        cert_query = select(func.count()).select_from(TrainingCourse).where(
            and_(TrainingCourse.user_id == user_id, TrainingCourse.has_certificate == True)
        )
        cert = await db.execute(cert_query)
        
        # قدیمی‌ترین دوره
        oldest_query = select(TrainingCourse).where(
            TrainingCourse.user_id == user_id
        ).order_by(TrainingCourse.start_date.asc()).limit(1)
        oldest = await db.execute(oldest_query)
        oldest_course = oldest.scalar_one_or_none()
        
        # جدیدترین دوره
        newest_query = select(TrainingCourse).where(
            TrainingCourse.user_id == user_id
        ).order_by(TrainingCourse.start_date.desc()).limit(1)
        newest = await db.execute(newest_query)
        newest_course = newest.scalar_one_or_none()
        
        return {
            "total": total.scalar() or 0,
            "with_certificate": cert.scalar() or 0,
            "oldest_course": oldest_course.title if oldest_course else None,
            "oldest_course_date": oldest_course.start_date if oldest_course else None,
            "newest_course": newest_course.title if newest_course else None,
            "newest_course_date": newest_course.start_date if newest_course else None
        }