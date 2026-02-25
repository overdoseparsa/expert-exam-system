# selectors.py for military_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Optional, Tuple
from datetime import date

from .models import MilitaryService
from auth.models import User
from applicant.models import Applicant

class MilitarySelector:
    @staticmethod
    async def get_by_user_id(db: AsyncSession, user_id: int) -> Optional[MilitaryService]:
        
        query = select(MilitaryService).where(MilitaryService.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_with_applicant(db: AsyncSession, user_id: int) -> Optional[Tuple[MilitaryService, Applicant]]:
        
        query = select(MilitaryService, Applicant).join(
            Applicant, Applicant.user_id == MilitaryService.user_id
        ).where(MilitaryService.user_id == user_id)
        result = await db.execute(query)
        return result.first()
    
    @staticmethod
    async def count_all(db: AsyncSession) -> int:
        
        query = select(func.count()).select_from(MilitaryService)
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def get_by_exemption_type(db: AsyncSession, exemption_type: str) -> List[MilitaryService]:
        
        query = select(MilitaryService).where(MilitaryService.exemption_type == exemption_type)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_service_org(db: AsyncSession, service_org: str) -> List[MilitaryService]:
        
        query = select(MilitaryService).where(MilitaryService.service_org.ilike(f"%{service_org}%"))
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_statistics(db: AsyncSession) -> dict:

        total_query = select(func.count()).select_from(MilitaryService)
        total = await db.execute(total_query)
        
        exemption_stats = {}
        for exempt_type in ["educational", "guardianship", "purchase", "medical", "served", "exempt"]:
            count_query = select(func.count()).select_from(MilitaryService).where(
                MilitaryService.exemption_type == exempt_type
            )
            count = await db.execute(count_query)
            exemption_stats[exempt_type] = count.scalar() or 0
        
        return {
            "total": total.scalar() or 0,
            "by_exemption_type": exemption_stats
        }