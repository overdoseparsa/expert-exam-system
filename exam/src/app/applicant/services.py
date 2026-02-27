# services/applicant_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import random
import string

from .models import Applicant
from auth.models import User
from .enums import StatusEnum, GenderEnum, BloodTypeEnum, MaritalStatusEnum
from .selectors import (
    get_applicant_by_user_id ,
    get_applicant_by_national_code,
    get_applicant_by_id,
    count_applicants,
    get_today_submissions_count,
    )
from .schemas import ApplicantCreate, ApplicantUpdate


async def create_applicant(
    db: AsyncSession,
    applicant_data: ApplicantCreate,
    user_id: int
) -> Applicant:
    """Create a new applicant"""
    
    # Check if user already has an applicant
    existing = await get_applicant_by_user_id(db, user_id)
    if existing:
        raise ValueError("User already has an applicant profile")
    
    # Check if national code is unique
    existing_national = await get_applicant_by_national_code(
        db, applicant_data.national_code
    )
    if existing_national:
        raise ValueError("National code already exists")
    
    # Create applicant instance
    applicant = Applicant(
        user_id=user_id,
        name=applicant_data.name,
        family=applicant_data.family,
        national_code=applicant_data.national_code,
        father_name=applicant_data.father_name,
        id_number=applicant_data.id_number,
        insurance_number=applicant_data.insurance_number,
        id_place=applicant_data.id_place,
        father_job=applicant_data.father_job,
        birth_date=applicant_data.birth_date,
        nationality=applicant_data.nationality or "ایرانی",
        birth_place=applicant_data.birth_place,
        religion=applicant_data.religion or "اسلام",
        gender=applicant_data.gender,
        blood_type=applicant_data.blood_type,
        marital_status=applicant_data.marital_status,
        marriage_date=applicant_data.marriage_date,
    )
    
    db.add(applicant)
    await db.commit()
    await db.refresh(applicant)
    return applicant

from fastapi import Depends
async def update_applicant(
    db: AsyncSession,
    applicant_id: int,
    applicant_data: ApplicantUpdate,
    user_id: Optional[int] = None
) -> Optional[Applicant]:
    """Update an existing applicant"""
    
    applicant = await get_applicant_by_id(db, applicant_id)
    if not applicant:
        return None
    
    # Check permission if user_id provided
    if user_id and applicant.user_id != user_id:
        raise PermissionError("You don't have permission to update this applicant")
    
    # Check national code uniqueness if being updated
    if applicant_data.national_code and applicant_data.national_code != applicant.national_code:
        existing = await get_applicant_by_national_code(
            db, applicant_data.national_code
        )
        if existing and existing.id != applicant_id:
            raise ValueError("National code already exists")
    
    # Update fields
    update_data = applicant_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(applicant, field, value)
    
    await db.commit()
    await db.refresh(applicant)
    return applicant


async def delete_applicant(
    db: AsyncSession,
    applicant_id: int,
    user_id: Optional[int] = None
) -> bool:
    """Delete an applicant"""
    
    applicant = await get_applicant_by_id(db, applicant_id)
    if not applicant:
        return False
    
    # Check permission if user_id provided
    if user_id and applicant.user_id != user_id:
        raise PermissionError("You don't have permission to delete this applicant")
    
    await db.delete(applicant)
    await db.commit()
    return True


def _generate_tracking_code() -> str:
    """Generate a unique tracking code"""
    timestamp = datetime.now().strftime("%y%m%d%H%M")
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"AP{timestamp}{random_part}"


async def get_applicant_statistics(db: AsyncSession) -> Dict[str, Any]:
    """Get statistics about applicants"""
    
    total = await count_applicants(db)
    draft = await count_applicants(db, status=StatusEnum.DRAFT)
    submitted = await count_applicants(db, status=StatusEnum.SUBMITTED)
    approved = await count_applicants(db, status=StatusEnum.APPROVED)
    rejected = await count_applicants(db, status=StatusEnum.REJECTED)
    
    male = await count_applicants(db, gender=GenderEnum.MALE)
    female = await count_applicants(db, gender=GenderEnum.FEMALE)
    
    return {
        "total": total,
        "by_status": {
            "draft": draft,
            "submitted": submitted,
            "approved": approved,
            "rejected": rejected
        },
        "by_gender": {
            "male": male,
            "female": female
        }
    }


async def bulk_update_applicants_status(
    db: AsyncSession,
    applicant_ids: List[int],
    new_status: StatusEnum,
    admin_user_id: int
) -> int:
    """Bulk update applicants status (admin only)"""
    
    result = await db.execute(
        select(Applicant).where(Applicant.id.in_(applicant_ids))
    )
    applicants = result.scalars().all()
    
    for applicant in applicants:
        applicant.status = new_status
        if new_status == StatusEnum.SUBMITTED:
            applicant.submitted_at = datetime.now()
    
    await db.commit()
    return len(applicants)



async def check_applicant_ownership(
    db: AsyncSession,
    applicant_id: int,
    user_id: int
) -> Optional[Applicant]:
    """Check if applicant belongs to user and return it"""
    applicant = await get_applicant_by_id(db, applicant_id)
    
    if not applicant or applicant.user_id != user_id:
        return None
    
    return applicant


async def update_applicant_status(
    db: AsyncSession,
    applicant_id: int,
    new_status: StatusEnum,
    admin_user_id: int
) -> Optional[Applicant]:
    """Update applicant status (admin only)"""
    applicant = await get_applicant_by_id(db, applicant_id)
    
    if not applicant:
        return None
    
    applicant.status = new_status
    
    if new_status == StatusEnum.SUBMITTED and not applicant.submitted_at:
        applicant.submitted_at = datetime.now()
    
    await db.commit()
    await db.refresh(applicant)
    return applicant


async def update_personal_info(
    db: AsyncSession,
    applicant_id: int,
    user_id: int,
    personal_data: Dict[str, Any]
) -> Optional[Applicant]:
    """Update personal information of applicant"""
    applicant = await check_applicant_ownership(db, applicant_id, user_id)
    
    if not applicant:
        return None
    
    # Update fields
    for field, value in personal_data.items():
        if value is not None:
            setattr(applicant, field, value)
    
    # Check if personal info is complete
    required_fields = ['name', 'family', 'national_code', 'birth_date', 'gender', 'marital_status']
    if all(getattr(applicant, field) for field in required_fields):
        # You might want to set a specific status here
        pass
    
    await db.commit()
    await db.refresh(applicant)
    return applicant


async def submit_application(
    db: AsyncSession,
    applicant_id: int,
    user_id: int
) -> Optional[Applicant]:
    """Submit application for review"""
    applicant = await check_applicant_ownership(db, applicant_id, user_id)
    
    if not applicant:
        return None
    
    # Check if all sections are completed
    # You can define your own logic here
    required_sections_completed = True  # Implement your logic
    
    if not required_sections_completed:
        raise ValueError("Please complete all sections before submission")
    
    applicant.status = StatusEnum.SUBMITTED
    applicant.submitted_at = datetime.now()
    
    await db.commit()
    await db.refresh(applicant)
    return applicant


async def delete_applicant_with_check(
    db: AsyncSession,
    applicant_id: int,
    user_id: int
) -> bool:
    """Delete applicant with ownership and status check"""
    applicant = await check_applicant_ownership(db, applicant_id, user_id)
    
    if not applicant:
        return False
    
    # Only allow deletion in DRAFT or REJECTED status
    if applicant.status not in [StatusEnum.DRAFT, StatusEnum.REJECTED]:
        raise ValueError("Cannot delete application in this stage")
    
    await db.delete(applicant)
    await db.commit()
    return True


async def get_applicant_statistics(db: AsyncSession) -> Dict[str, int]:
    """Get applicant statistics for admin"""
    total = await count_applicants(db)
    draft = await count_applicants(db, status=StatusEnum.DRAFT)
    submitted = await count_applicants(db, status=StatusEnum.SUBMITTED)
    approved = await count_applicants(db, status=StatusEnum.APPROVED)
    rejected = await count_applicants(db, status=StatusEnum.REJECTED)
    today_submissions = await get_today_submissions_count(db)
    
    return {
        "total": total,
        "draft": draft,
        "submitted": submitted,
        "approved": approved,
        "rejected": rejected,
        "today_submissions": today_submissions
    }

# async def update_applicant_user_by_self(
#     user_id : int , 
    
# ): 
