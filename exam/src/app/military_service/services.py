# services.py for military_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from datetime import datetime

from .models import MilitaryService
from .schemas import MilitaryServiceCreate, MilitaryServiceUpdate


class MilitaryService:

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> Optional[MilitaryService]:
        
        query = select(MilitaryService).where(MilitaryService.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(
        db: AsyncSession, 
        user_id: int, 
        data: MilitaryServiceCreate
    ) -> MilitaryService:

        military = MilitaryService(
            user_id=user_id,
            service_start=data.service_start,
            service_end=data.service_end,
            service_duration=data.service_duration,
            shortage_duration=data.shortage_duration,
            extra_duration=data.extra_duration,
            service_org=data.service_org,
            service_city=data.service_city,
            exemption_type=data.exemption_type,
            exemption_reason=data.exemption_reason
        )
        db.add(military)
        await db.flush()
        return military
    
    @staticmethod
    async def update(
        db: AsyncSession,
        military: MilitaryService,
        data: MilitaryServiceUpdate
    ) -> MilitaryService:

        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(military, field, value)
        
        military.updated_at = datetime.utcnow()
        db.add(military)
        await db.flush()
        return military
    
    @staticmethod
    async def delete(
        db: AsyncSession,
        military: MilitaryService
    ) -> None:

        await db.delete(military)
        await db.flush()
    
    @staticmethod
    async def exists(db: AsyncSession, user_id: int) -> bool:
        """بررسی وجود اطلاعات نظام وظیفه"""
        query = select(MilitaryService).where(MilitaryService.user_id == user_id)
        result = await db.execute(query)
        return result.first() is not None