# selectors/applicant_selectors.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from datetime import date, datetime

from .models import Applicant
from .enums import GenderEnum, BloodTypeEnum, MaritalStatusEnum, StatusEnum


async def get_applicant_by_id(db: AsyncSession, applicant_id: int) -> Optional[Applicant]:
    """Get applicant by ID"""
    result = await db.execute(
        select(Applicant).where(Applicant.id == applicant_id)
    )
    return result.scalar_one_or_none()


async def get_applicant_by_user_id(db: AsyncSession, user_id: int) -> Optional[Applicant]:
    """Get applicant by user ID (one-to-one relationship)"""
    result = await db.execute(
        select(Applicant).where(Applicant.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_applicant_by_national_code(db: AsyncSession, national_code: str) -> Optional[Applicant]:
    """Get applicant by national code"""
    result = await db.execute(
        select(Applicant).where(Applicant.national_code == national_code)
    )
    return result.scalar_one_or_none()


async def get_applicant_by_tracking_code(db: AsyncSession, tracking_code: str) -> Optional[Applicant]:
    """Get applicant by tracking code"""
    result = await db.execute(
        select(Applicant).where(Applicant.tracking_code == tracking_code)
    )
    return result.scalar_one_or_none()


async def get_all_applicants(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[StatusEnum] = None,
    gender: Optional[GenderEnum] = None,
    marital_status: Optional[MaritalStatusEnum] = None,
    blood_type: Optional[BloodTypeEnum] = None,
    nationality: Optional[str] = None,
    religion: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> List[Applicant]:
    """Get all applicants with optional filters"""
    query = select(Applicant)
    
    filters = []
    if status:
        filters.append(Applicant.status == status)
    if gender:
        filters.append(Applicant.gender == gender)
    if marital_status:
        filters.append(Applicant.marital_status == marital_status)
    if blood_type:
        filters.append(Applicant.blood_type == blood_type)
    if nationality:
        filters.append(Applicant.nationality == nationality)
    if religion:
        filters.append(Applicant.religion == religion)
    if from_date:
        filters.append(Applicant.birth_date >= from_date)
    if to_date:
        filters.append(Applicant.birth_date <= to_date)
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def get_applicants_by_name_family(
    db: AsyncSession, 
    name: Optional[str] = None, 
    family: Optional[str] = None
) -> List[Applicant]:
    """Get applicants by name and/or family"""
    query = select(Applicant)
    
    filters = []
    if name:
        filters.append(Applicant.name.ilike(f"%{name}%"))
    if family:
        filters.append(Applicant.family.ilike(f"%{family}%"))
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    return result.scalars().all()






async def get_applicants_by_status(db: AsyncSession, status: StatusEnum) -> List[Applicant]:
    """Get applicants by status"""
    result = await db.execute(
        select(Applicant).where(Applicant.status == status)
    )
    return result.scalars().all()




async def count_applicants(
    db: AsyncSession,
    status: Optional[StatusEnum] = None,
    gender: Optional[GenderEnum] = None
) -> int:
    """Count applicants with optional filters"""
    query = select(Applicant)
    
    filters = []
    if status:
        filters.append(Applicant.status == status)
    if gender:
        filters.append(Applicant.gender == gender)
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    return len(result.scalars().all())


async def search_applicants(
    db: AsyncSession,
    search_term: str,
    skip: int = 0,
    limit: int = 100
) -> List[Applicant]:
    """Search applicants by multiple fields"""
    query = select(Applicant).where(
        or_(
            Applicant.name.ilike(f"%{search_term}%"),
            Applicant.family.ilike(f"%{search_term}%"),
            Applicant.national_code.ilike(f"%{search_term}%"),
            Applicant.father_name.ilike(f"%{search_term}%"),
            Applicant.id_number.ilike(f"%{search_term}%"),
            Applicant.tracking_code.ilike(f"%{search_term}%")
        )
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_applicant_with_user(db: AsyncSession, applicant_id: int) -> Optional[Applicant]:
    """Get applicant with related user data"""
    result = await db.execute(
        select(Applicant)
        .where(Applicant.id == applicant_id)
        .options(selectinload(Applicant.user))
    )
    return result.scalar_one_or_none()


# selectors/applicant_selectors.py - اضافه کردن این توابع به فایل قبلی

async def get_applicants_by_status_with_pagination(
    db: AsyncSession,
    status: Optional[StatusEnum] = None,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
) -> List[Applicant]:
    """Get applicants with pagination and search"""
    query = select(Applicant)
    
    filters = []
    if status:
        filters.append(Applicant.status == status)
    
    if search:
        filters.append(
            or_(
                Applicant.name.ilike(f"%{search}%"),
                Applicant.family.ilike(f"%{search}%"),
                Applicant.national_code.ilike(f"%{search}%"),
                Applicant.tracking_code.ilike(f"%{search}%")
            )
        )
    
    if filters:
        query = query.where(and_(*filters))
    
    query = query.order_by(Applicant.submitted_at.desc().nulls_last()).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def count_applicants_by_filters(
    db: AsyncSession,
    status: Optional[StatusEnum] = None,
    search: Optional[str] = None
) -> int:
    """Count applicants with filters"""
    query = select(Applicant)
    
    filters = []
    if status:
        filters.append(Applicant.status == status)
    
    if search:
        filters.append(
            or_(
                Applicant.name.ilike(f"%{search}%"),
                Applicant.family.ilike(f"%{search}%"),
                Applicant.national_code.ilike(f"%{search}%"),
                Applicant.tracking_code.ilike(f"%{search}%")
            )
        )
    
    if filters:
        query = query.where(and_(*filters))
    
    result = await db.execute(query)
    return len(result.scalars().all())


async def get_applicant_with_user_check(
    db: AsyncSession,
    applicant_id: int,
    user_id: int
) -> Optional[Applicant]:
    """Get applicant by ID and check if it belongs to user"""
    result = await db.execute(
        select(Applicant).where(
            and_(
                Applicant.id == applicant_id,
                Applicant.user_id == user_id
            )
        )
    )
    return result.scalar_one_or_none()


async def get_today_submissions_count(db: AsyncSession) -> int:
    """Get count of today's submissions"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    result = await db.execute(
        select(Applicant).where(
            and_(
                Applicant.submitted_at >= today_start,
                Applicant.submitted_at <= today_end,
                Applicant.status == StatusEnum.SUBMITTED
            )
        )
    )
    return len(result.scalars().all())