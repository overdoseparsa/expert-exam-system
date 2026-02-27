# router.py for training_courses
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from auth.depends import get_current_user_obj as  get_current_user
from auth.models import User
from .schemas import (
    TrainingCourseCreate, TrainingCourseUpdate, TrainingCourseResponse,
    TrainingCourseBulkCreate, TrainingSummaryResponse
)
from .services import TrainingService
from .selectors import TrainingSelector

router = APIRouter(prefix="/training", tags=["Training Courses"])


# ========== TRAINING COURSES ==========
@router.get("/", response_model=List[TrainingCourseResponse])
async def get_training_courses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست دوره‌های آموزشی"""
    courses = await TrainingService.get_by_user(db, current_user.id)
    return courses


@router.post("/", response_model=TrainingCourseResponse, status_code=status.HTTP_201_CREATED)
async def create_training_course(
    training_data: TrainingCourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """اضافه کردن دوره آموزشی جدید"""
    try:
        new_course = await TrainingService.create(db, current_user.id, training_data)
        
        # TODO: تغییر وضعیت applicant (اگر نیاز است)
        
        await db.commit()
        await db.refresh(new_course)
        
        return new_course
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت دوره آموزشی: {str(e)}"
        )


@router.get("/{course_id}/", response_model=TrainingCourseResponse)
async def get_training_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت اطلاعات یک دوره آموزشی خاص"""
    course = await TrainingService.get_by_id(db, course_id, current_user.id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="دوره آموزشی یافت نشد"
        )
    
    return course


@router.put("/{course_id}/", response_model=TrainingCourseResponse)
async def update_training_course(
    course_id: int,
    training_data: TrainingCourseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی اطلاعات دوره آموزشی"""
    course = await TrainingService.get_by_id(db, course_id, current_user.id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="دوره آموزشی یافت نشد"
        )
    
    try:
        updated_course = await TrainingService.update(db, course, training_data)
        
        await db.commit()
        await db.refresh(updated_course)
        
        return updated_course
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/{course_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_course(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """حذف دوره آموزشی"""
    course = await TrainingService.get_by_id(db, course_id, current_user.id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="دوره آموزشی یافت نشد"
        )
    
    try:
        await TrainingService.delete(db, course)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


@router.get("/with-certificate/", response_model=List[TrainingCourseResponse])
async def get_courses_with_certificate(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت دوره‌هایی که گواهینامه دارند"""
    courses = await TrainingSelector.get_with_certificate(db, current_user.id)
    return courses


@router.get("/stats/summary/", response_model=TrainingSummaryResponse)
async def get_training_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """خلاصه آماری دوره‌های آموزشی"""
    summary = await TrainingSelector.get_summary(db, current_user.id)
    return summary


@router.post("/bulk/", response_model=List[TrainingCourseResponse], status_code=status.HTTP_201_CREATED)
async def create_training_courses_bulk(
    trainings_data: List[TrainingCourseCreate],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """اضافه کردن چند دوره آموزشی به‌صورت Bulk"""
    try:
        created_courses = await TrainingService.create_bulk(db, current_user.id, trainings_data)
        
        # TODO: تغییر وضعیت applicant (اگر نیاز است)
        
        await db.commit()
        
        # Refresh رکوردها
        for course in created_courses:
            await db.refresh(course)
        
        return created_courses
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت دوره‌های آموزشی: {str(e)}"
        )


# ========== Additional endpoints using selectors ==========
@router.get("/statistics/")
async def get_training_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت آمار دوره‌های آموزشی"""
    stats = await TrainingSelector.get_statistics(db, current_user.id)
    return stats


@router.get("/by-institute/{institute}/")
async def get_by_institute(
    institute: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت دوره‌ها بر اساس مؤسسه"""
    courses = await TrainingSelector.get_by_institute(db, current_user.id, institute)
    return courses


@router.get("/by-year/{year}/")
async def get_by_year(
    year: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت دوره‌های یک سال خاص"""
    courses = await TrainingSelector.get_by_year(db, current_user.id, year)
    return courses