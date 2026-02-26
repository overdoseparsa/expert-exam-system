# routers/applicant_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from database import get_db
from auth.models import User
from .enums import StatusEnum
from .schemas import (
    ApplicantCreate,
    ApplicantUpdate,
    ApplicantResponse,


)
# here we have to create 
from auth.depends import (
    get_current_user_obj as get_current_user,
    get_current_user_obj_admin as get_current_superuser,
    )

from .services import (
    create_applicant,
    delete_applicant_with_check,
    update_applicant
)
from .selectors import (
    get_applicants_by_status_with_pagination,
    get_applicant_by_user_id,
    get_applicant_by_tracking_code,
    get_applicant_by_id,

)

router = APIRouter(prefix="/applicants", tags=["applicants"])


@router.post("/", response_model=ApplicantResponse, status_code=status.HTTP_201_CREATED)
async def create_applicant_api(
    applicant_data: ApplicantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):


    try:
        new_applicant = await create_applicant(
            db, 
            applicant_data, 
            current_user.id
        )
        return new_applicant
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ایجاد درخواست: {str(e)}"
        )



@router.get("/", response_model=List[ApplicantResponse])
async def get_applicants_api(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[StatusEnum] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # فقط ادمین
):

    applicants = await get_applicants_by_status_with_pagination(
        db, status, skip, limit, search
    )
    return applicants


@router.get("/me/", response_model=ApplicantResponse)
async def get_my_applicant(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    applicant = await get_applicant_by_user_id(db, current_user.id)
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="شما هنوز درخواستی ثبت نکرده‌اید"
        )
    
    return applicant


@router.get("/{applicant_id}/", response_model=ApplicantResponse)
async def get_applicant_by_id_api(
    applicant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    applicant = await get_applicant_by_id(db, applicant_id)
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="متقاضی یافت نشد"
        )
    
    if applicant.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی غیرمجاز"
        )
    
    return applicant


@router.get("/tracking/{tracking_code}/", response_model=ApplicantResponse)
async def get_applicant_by_tracking_api(
    tracking_code: str,
    db: AsyncSession = Depends(get_db)
):

    applicant = await get_applicant_by_tracking_code(db, tracking_code)
    
    if not applicant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="درخواست با این کد رهگیری یافت نشد"
        )
    
    # فقط اطلاعات عمومی برگردانده شود
    return applicant


@router.put("/{applicant_id}/", response_model=ApplicantResponse)
async def update_applicant_api(
    applicant_id: int,
    applicant_data: ApplicantUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    try:
        updated_applicant = await update_applicant(
            db, applicant_id, applicant_data, current_user.id
        )
        
        if not updated_applicant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="متقاضی یافت نشد"
            )
        
        return updated_applicant
        
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در به‌روزرسانی: {str(e)}"
        )





@router.delete("/{applicant_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_applicant_api(
    applicant_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    try:
        deleted = await delete_applicant_with_check(
            db, applicant_id, current_user.id
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="متقاضی یافت نشد"
            )
        
        return None
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در حذف: {str(e)}"
        )


