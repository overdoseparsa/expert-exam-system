from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from database import get_db
from auth.depends import get_current_user
from auth.models import User
from .schemas import (
    EducationCreate,
    EducationUpdate,
    EducationResponse,
    EducationBulkCreate,
    EducationDegreeEnum,
    EducationStudyStatusEnum,
)
from .services import EducationService
from .selectors import EducationSelector

router = APIRouter(prefix="/education", tags=["Education"])


# ========== EDUCATION ==========
@router.get("/", response_model=List[EducationResponse])
async def get_educations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    educations = await EducationService.get_by_user(db, current_user.id)
    return educations


@router.post("/", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def create_education(
    education_data: EducationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    try:
        new_education = await EducationService.create(db, current_user.id, education_data)
        
        # TODO: تغییر وضعیت applicant
        # from app.applicant.services import update_applicant_status
        
        await db.commit()
        await db.refresh(new_education)
        
        return new_education
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت مدرک تحصیلی: {str(e)}"
        )


@router.get("/{education_id}/", response_model=EducationResponse)
async def get_education(
    education_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    education = await EducationService.get_by_id(db, education_id, current_user.id)
    
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مدرک تحصیلی یافت نشد"
        )
    
    return education


@router.put("/{education_id}/", response_model=EducationResponse)
async def update_education(
    education_id: int,
    education_data: EducationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    education = await EducationService.get_by_id(db, education_id, current_user.id)
    
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مدرک تحصیلی یافت نشد"
        )
    
    try:
        updated_education = await EducationService.update(db, education, education_data)
        
        await db.commit()
        await db.refresh(updated_education)
        
        return updated_education
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/{education_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(
    education_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    education = await EducationService.get_by_id(db, education_id, current_user.id)
    
    if not education:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مدرک تحصیلی یافت نشد"
        )
    
    try:
        await EducationService.delete(db, education)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


@router.get("/highest-degree/", response_model=Optional[EducationResponse])
async def get_highest_degree(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    highest = await EducationSelector.get_highest_degree(db, current_user.id)
    return highest


@router.post("/bulk/", response_model=List[EducationResponse], status_code=status.HTTP_201_CREATED)
async def create_educations_bulk(
    data: EducationBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        new_educations = await EducationService.create_bulk(db, current_user.id, data)
        
        # TODO: تغییر وضعیت applicant
        
        await db.commit()
        
        for edu in new_educations:
            await db.refresh(edu)
        
        return new_educations
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت مدارک تحصیلی: {str(e)}"
        )


# ========== Additional endpoints using selectors ==========
@router.get("/statistics/")
async def get_education_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stats = await EducationSelector.get_statistics(db, current_user.id)
    return stats


@router.get("/by-degree/{degree}/")
async def get_by_degree(
    degree: EducationDegreeEnum,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    educations = await EducationSelector.get_by_degree(db, current_user.id, degree)
    return educations


@router.get("/by-status/{status}/")
async def get_by_status(
    status: EducationStudyStatusEnum,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    educations = await EducationSelector.get_by_study_status(db, current_user.id, status)
    return educations