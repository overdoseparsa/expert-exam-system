
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime

from .models import ApplicationDetails
from .schemas import (
    ApplicationDetailsCreate,
    ApplicationDetailsUpdate
)


class ApplicationDetailsService:

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> Optional[ApplicationDetails]:
       
        result = await db.execute(
            select(ApplicationDetails).where(ApplicationDetails.user_id == user_id)
        )
        print('reusalt is ', result)
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, app_id: int , *args,**kwargs) -> Optional[ApplicationDetails]:
        if 'user_id' in kwargs : 
            user_id = kwargs.get('user_id')
            assert user_id , "User Not Defiend"

            result = await db.execute(
                select(ApplicationDetails).where(
                    ApplicationDetails.id == app_id,
                    ApplicationDetails.user_id == user_id
                    )
                )
                    
        else :
        
            result = await db.execute(
                select(ApplicationDetails).where(ApplicationDetails.id == app_id)
            )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: int,
        data: ApplicationDetailsCreate
    ) -> ApplicationDetails:
        """ایجاد جزئیات درخواست جدید"""
        new_details = ApplicationDetails(
            user_id=user_id,
            connection_type=data.connection_type,
            referrer_name=data.referrer_name,
            referrer_relationship=data.referrer_relationship,
            referrer_phone=data.referrer_phone,
            has_relatives_in_company=data.has_relatives_in_company,
            relative_name=data.relative_name,
            relative_position=data.relative_position,
            relative_relationship=data.relative_relationship,
            available_from_date=data.available_from_date,
            preferred_work_schedule=data.preferred_work_schedule,
            expected_salary=data.expected_salary,
            salary_currency=data.salary_currency,
            salary_period=data.salary_period,
            has_health_issue=data.has_health_issue,
            health_issue_description=data.health_issue_description,
            has_disability=data.has_disability,
            disability_description=data.disability_description,
            takes_medication=data.takes_medication,
            medication_details=data.medication_details,
            has_criminal_record=data.has_criminal_record,
            criminal_record_details=data.criminal_record_details,
            favorite_sport=data.favorite_sport,
            has_transportation=data.has_transportation,
            willing_to_relocate=data.willing_to_relocate,
            other_comments=data.other_comments
        )

        db.add(new_details)                
        await db.flush()                    
        await db.commit()                   
        await db.refresh(new_details)     
        return new_details

    @staticmethod
    async def update(
        db: AsyncSession,
        details: ApplicationDetails,
        data: ApplicationDetailsUpdate
    ) -> ApplicationDetails:
        """به‌روزرسانی جزئیات درخواست"""
        update_data = data.dict(exclude_unset=True)

        for field, value in update_data.items():
            if value is not None:
                setattr(details, field, value)

        details.updated_at = datetime.utcnow()
                
        db.add(details)             
        await db.flush()               
        await db.commit()            
        await db.refresh(details)
        return details

    @staticmethod
    async def delete(db: AsyncSession, details: ApplicationDetails) -> None:
        """حذف جزئیات درخواست"""
        await db.delete(details)
        await db.flush()

    @staticmethod
    async def exists(db: AsyncSession, user_id: int) -> bool:
        """بررسی وجود جزئیات درخواست"""
        result = await db.execute(
            select(ApplicationDetails.id).where(ApplicationDetails.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None