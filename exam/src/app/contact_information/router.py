# router.py for contact_information
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.depends import get_current_user
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
)
from .schemas import (
    ContactCreate,
    ContactUpdate,
    AddressCreate,
    

) 
from auth.models import User


router = APIRouter(prefix="/contact/", tags=["Contact"])

@router.post("/contact/")
def create_user_contact(
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return create_contact(
            db=db,
            user_id=current_user.id,
            **data.dict()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/contact/")
def get_my_contact(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = get_contact_by_user_id(db, current_user.id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact



@router.put("/contact/")
def update_my_contact(
    data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return update_contact(
            db=db,
            user_id=current_user.id,
            **data.dict(exclude_unset=True)
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.post("/address/")
def create_user_address(
    data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_address(
        db=db,
        user_id=current_user.id,
        **data.dict()
    )

@router.get("/address/")
def get_my_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_addresses_by_user_id(db, current_user.id)

@router.delete("/address/{address_id}/")
def delete_user_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = get_address_by_id(db, address_id)

    if not address or address.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Address not found")

    delete_address(db, address_id)
    return {"detail": "Address deleted successfully"}