# services.py for training_courses
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import datetime

from .models import TrainingCourse
from .schemas import TrainingCourseCreate, TrainingCourseUpdate, TrainingCourseBulkCreate


class TrainingService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> List[TrainingCourse]:
        """دریافت لیست دوره‌های آموزشی"""
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
    async def create(db: AsyncSession, user_id: int, data: TrainingCourseCreate) -> TrainingCourse:
        """ایجاد دوره آموزشی جدید"""
        course = TrainingCourse(
            user_id=user_id,
            title=data.title,
            institute=data.institute,
            duration=data.duration,
            start_date=data.start_date,
            end_date=data.end_date,
            has_certificate=data.has_certificate,
            certificate_id=data.certificate_id,
            certificate_date=data.certificate_date,
            description=data.description,
            skills_learned=data.skills_learned,
            instructor=data.instructor
        )
        db.add(course)
        await db.flush()
        return course
    
    @staticmethod
    async def create_bulk(
        db: AsyncSession, 
        user_id: int, 
        data: List[TrainingCourseCreate]
    ) -> List[TrainingCourse]:
        """ایجاد چند دوره آموزشی به صورت یکجا"""
        new_courses = []
        
        for course_data in data:
            course = TrainingCourse(
                user_id=user_id,
                title=course_data.title,
                institute=course_data.institute,
                duration=course_data.duration,
                start_date=course_data.start_date,
                end_date=course_data.end_date,
                has_certificate=course_data.has_certificate,
                certificate_id=course_data.certificate_id,
                certificate_date=course_data.certificate_date,
                description=course_data.description,
                skills_learned=course_data.skills_learned,
                instructor=course_data.instructor
            )
            db.add(course)
            new_courses.append(course)
        
        await db.flush()
        return new_courses
    
    @staticmethod
    async def update(
        db: AsyncSession, 
        course: TrainingCourse, 
        data: TrainingCourseUpdate
    ) -> TrainingCourse:
        """به‌روزرسانی اطلاعات دوره آموزشی"""
        update_data = data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(course, field, value)
        
        course.updated_at = datetime.utcnow()
        db.add(course)
        await db.flush()
        return course
    
    @staticmethod
    async def delete(db: AsyncSession, course: TrainingCourse) -> None:
        """حذف دوره آموزشی"""
        await db.delete(course)
        await db.flush()
    
    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        """تعداد دوره‌های آموزشی کاربر"""
        query = select(TrainingCourse).where(TrainingCourse.user_id == user_id)
        result = await db.execute(query)
        return len(result.scalars().all())