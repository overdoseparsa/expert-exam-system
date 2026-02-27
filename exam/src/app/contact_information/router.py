# router.py for contact_information
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from auth.depends import get_current_user_obj as get_current_user
from .services import (
    create_contact,
    update_contact,
    create_address,
    delete_address,
)
from .selectors import (
    get_contact_by_user_id, 
    get_addresses_by_user_id,
    get_address_by_id,
    get_addresses_by_all,
    get_contact_by_user_all
)
from .schemas import (
    ContactCreate,
    AddressCreate,

    ContactInfoUpdate,
    AddressUpdate,

    ContactInfoResponse,
    AddressResponse

) 
from auth.models import User
from typing import List

router = APIRouter(prefix="/contact", tags=["Contact"])

@router.post("/contact/")
async def create_user_contact(
    data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await create_contact(
            db=db,
            user_id=current_user.id,
            **data.dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/contact/" , response_model=List[ContactInfoResponse])
async def get_my_contact(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = await get_contact_by_user_all(
        db,
        current_user.id
        )

    return contact



@router.put("/contact/{contact}/",response_model=ContactInfoResponse)
async def update_my_contact(
    contact :int , 
    data: ContactInfoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await update_contact(
            db=db,
            user_id=current_user.id,
            content_id = contact,
            **data.dict(exclude_unset=True)
            
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post("/address/",response_model=AddressResponse)
async def create_user_address(
    data: AddressCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_address(
        db=db,
        user_id=current_user.id,
        **data.dict()
    )

@router.get("/address/",response_model=List[AddressResponse])
async def get_my_addresses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_addresses_by_all(db, current_user.id)


@router.delete("/address/{address_id}/")
async def delete_user_address(
    address_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = await get_address_by_id(db, address_id)

    if not address or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")

    await delete_address(db, address_id)
    return {"detail": "Address deleted successfully"}