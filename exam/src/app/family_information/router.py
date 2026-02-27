from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from database import get_db
from auth.depends  import get_current_user_obj as get_current_user
from auth.models import User
from .schemas import (
    SpouseCreate, SpouseUpdate, SpouseResponse,
    ChildCreate, ChildUpdate, ChildResponse,
    SiblingCreate, SiblingUpdate, SiblingResponse
)
from .services import SpouseService, ChildService, SiblingService
from .selectors import SpouseSelector, ChildSelector, SiblingSelector

router = APIRouter(prefix="/family", tags=["Family Information"])



# ========== SPOUSE ==========
@router.get("/spouse/", response_model=Optional[SpouseResponse])
async def get_spouse(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    spouse = await SpouseService.get_by_user(db, current_user.id)
    return spouse


@router.post("/spouse/", response_model=SpouseResponse, status_code=status.HTTP_201_CREATED) # TODO 
async def create_spouse(
    spouse_data: SpouseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    try:
        new_spouse = await SpouseService.create(db, current_user.id, spouse_data)

        # تغییر وضعیت applicant
        # from app.applicant.services import update_applicant_status  # فرض می‌کنم این سرویس وجود دارد
        
        # if applicant.status == Applicant.StatusEnum.PERSONAL_COMPLETED: # must change 
        #     await ApplicantService.update_status(db, applicant, Applicant.StatusEnum.FAMILY_COMPLETED)
        
        await db.commit()
        await db.refresh(new_spouse)
        
        return new_spouse
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ثبت اطلاعات همسر: {str(e)}"
        )


@router.put("/spouse/", response_model=SpouseResponse)
async def update_spouse(
    spouse_data: SpouseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    spouse = await SpouseService.get_by_user(db, current_user.id)
    if not spouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شما هنوز اطلاعات همسر را ثبت نکرده‌اید"
        )
    
    try:
        updated_spouse = await SpouseService.update(db, spouse, spouse_data)
        
        # به‌روزرسانی applicant

        await db.refresh(updated_spouse)
        return updated_spouse
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/spouse/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spouse(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """حذف اطلاعات همسر"""
    spouse = await SpouseService.get_by_user(db, current_user.id)
    if not spouse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="اطلاعات همسر یافت نشد"
        )
    
    try:
        await SpouseService.delete(db, spouse)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


# ========== CHILDREN ==========
@router.get("/children/", response_model=List[ChildResponse])
async def get_children(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت لیست فرزندان"""
    children = await ChildSelector.get_by_user_id(db, current_user.id)
    return children


@router.post("/children/", response_model=ChildResponse, status_code=status.HTTP_201_CREATED) # TODO 
async def create_child(
    child_data: ChildCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        new_child = await ChildService.create(db, current_user.id, child_data)
        
        # # تغییر وضعیت applicant اگر نیاز باشد
        # from services.applicant import ApplicantService
        
        # if applicant.status == Applicant.StatusEnum.PERSONAL_COMPLETED:
        #     await ApplicantService.update_status(db, applicant, Applicant.StatusEnum.FAMILY_COMPLETED)
        # else:
        #     applicant.updated_at = datetime.utcnow()
        #     db.add(applicant)

        return new_child
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در اضافه کردن فرزند: {str(e)}"
        )


@router.get("/children/{child_id}", response_model=ChildResponse)
async def get_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت اطلاعات یک فرزند خاص"""
    child = await ChildService.get_by_id(db, child_id, current_user.id)
    
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="فرزند یافت نشد"
        )
    
    return child


@router.put("/children/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: int,
    child_data: ChildUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    child = await ChildService.get_by_id(db, child_id, current_user.id)
    
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="فرزند یافت نشد"
        )
    
    try:
        updated_child = await ChildService.update(db, child, child_data)
        

        await db.refresh(updated_child)
        
        return updated_child
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/children/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(
    child_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    child = await ChildService.get_by_id(db, child_id, current_user.id)
    
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="فرزند یافت نشد"
        )
    
    try:
        await ChildService.delete(db, child)
        # applicant.updated_at = datetime.utcnow()
        # db.add(applicant)
        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


# ========== SIBLINGS ==========
@router.get("/siblings/", response_model=List[SiblingResponse])
async def get_siblings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    siblings = await SiblingService.get_by_applicant(db, current_user.id)
    return siblings


@router.post("/siblings/", response_model=SiblingResponse, status_code=status.HTTP_201_CREATED)
async def create_sibling(
    sibling_data: SiblingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """اضافه کردن خواهر/برادر جدید"""
    try:
        new_sibling = await SiblingService.create(db, current_user.id, sibling_data)
        

       
        
        return new_sibling
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در اضافه کردن خواهر/برادر: {str(e)}"
        )


@router.get("/siblings/{sibling_id}/", response_model=SiblingResponse)
async def get_sibling(
    sibling_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    sibling = await SiblingService.get_by_id(db, sibling_id, current_user.id)
    
    if not sibling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="خواهر/برادر یافت نشد"
        )
    
    return sibling


@router.put("/siblings/{sibling_id}/", response_model=SiblingResponse)
async def update_sibling(
    sibling_id: int,
    sibling_data: SiblingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    sibling = await SiblingService.get_by_id(db, sibling_id, current_user.id)
    
    if not sibling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="خواهر/برادر یافت نشد"
        )
    
    try:
        updated_sibling = await SiblingService.update(db, sibling, sibling_data)
        
        # به‌روزرسانی applicant
        # applicant.updated_at = datetime.utcnow()
        # db.add(applicant)
        
        await db.commit()
        await db.refresh(updated_sibling)
        
        return updated_sibling
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )


@router.delete("/siblings/{sibling_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sibling(
    sibling_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """حذف خواهر/برادر"""
    sibling = await SiblingService.get_by_id(db, sibling_id, current_user.id)
    
    if not sibling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="خواهر/برادر یافت نشد"
        )
    
    try:
        await SiblingService.delete(db, sibling)

        
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


# ========== Additional endpoints using selectors ==========
@router.get("/children/statistics")
async def get_children_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """دریافت آمار فرزندان"""
    stats = await ChildSelector.get_statistics(db, current_user.user_id)
    return stats


@router.get("/siblings/statistics")
async def get_siblings_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stats = await SiblingSelector.get_statistics(db, current_user.id)
    return stats