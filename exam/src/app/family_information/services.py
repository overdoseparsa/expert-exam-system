# services.py for family_information
# selectors.py for family_information
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, delete, update
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import datetime

from .models import Spouse, Child, Sibling
from .schemas import (
    SpouseCreate, SpouseUpdate,
    ChildCreate, ChildUpdate,
    SiblingCreate, SiblingUpdate
)

class SpouseService:
    @staticmethod
    async def get_by_user(db: AsyncSession, user_id) -> Optional[Spouse]:
        query = select(Spouse).where(Spouse.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_id , data: SpouseCreate) -> Spouse:
        """ایجاد همسر جدید"""
        
        if await SpouseService.exists(db, user_id):
            raise Exception("شما قبلا همسر ثبت کردید")
        
        spouse = Spouse(
            user_id=user_id,
            full_name=data.full_name,
            job=data.job
        )
        db.add(spouse)
        await db.flush()
        return spouse
    
    @staticmethod
    async def update(
        db: AsyncSession,
        spouse: Spouse,
        data: SpouseUpdate
        ) -> Spouse:
        """به‌روزرسانی اطلاعات همسر"""
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(spouse, field, value)
        
        spouse.updated_at = datetime.utcnow()
        db.add(spouse)
        await db.flush()
        return spouse
    
    @staticmethod
    async def delete(
        db: AsyncSession,
        spouse: Spouse
        ) -> None:
        """حذف اطلاعات همسر"""
        await db.delete(spouse)
        await db.flush()
    
    @staticmethod
    async def exists(db: AsyncSession,user_id) -> bool:
        """بررسی وجود همسر"""
        query = select(Spouse).where(Spouse.user_id == user_id)
        result = await db.execute(query)
        return result.first() is not None


# ========== Child Service ==========
class ChildService:
    @staticmethod
    async def get_by_applicant(db: AsyncSession, user_id) -> List[Child]:
        """دریافت لیست فرزندان"""
        query = select(Child).where(Child.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, child_id: int, user_id) -> Optional[Child]:
        """دریافت یک فرزند با آیدی"""
        query = select(Child).where(
            and_(
                Child.id == child_id,
                Child.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_id, data: ChildCreate) -> Child:
        """ایجاد فرزند جدید"""
        child = Child(
            user_id=user_id,
            full_name=data.full_name,
            age=data.age,
            gender=data.gender
        )
        db.add(child)
                
        await db.commit()
        await db.refresh(child)
        await db.flush()
        return child
    
    @staticmethod
    async def update(db: AsyncSession, child: Child, data: ChildUpdate) -> Child:
        """به‌روزرسانی اطلاعات فرزند"""
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(child, field, value)
        
        child.updated_at = datetime.utcnow()
        db.add(child)
        await db.flush()
        return child
    
    @staticmethod
    async def delete(db: AsyncSession, child: Child) -> None:
        """حذف فرزند"""
        await db.delete(child)
        await db.flush()
    
    @staticmethod
    async def count_by_applicant(db: AsyncSession, user_id) -> int:
        """تعداد فرزندان"""
        query = select(Child).where(Child.user_id == user_id)
        result = await db.execute(query)
        return len(result.scalars().all())


# ========== Sibling Service ==========
class SiblingService:
    @staticmethod
    async def get_by_applicant(db: AsyncSession, user_id) -> List[Sibling]:
        """دریافت لیست خواهر/برادرها"""
        query = select(Sibling).where(Sibling.user_id == user_id)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db: AsyncSession, sibling_id: int, user_id) -> Optional[Sibling]:
        """دریافت یک خواهر/برادر با آیدی"""
        query = select(Sibling).where(
            and_(
                Sibling.id == sibling_id,
                Sibling.user_id == user_id
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_id , data: SiblingCreate) -> Sibling:
        """ایجاد خواهر/برادر جدید"""
        sibling = Sibling(
            user_id=user_id,
            full_name=data.full_name,
            age=data.age,
            sibling_type=data.sibling_type,
            marital_status=data.marital_status,
            job=data.job
        )
        db.add(sibling)
        await db.commit() 
        await db.refresh(sibling)
        await db.flush()
        return sibling
    
    @staticmethod
    async def update(db: AsyncSession, sibling: Sibling, data: SiblingUpdate) -> Sibling:
        """به‌روزرسانی اطلاعات خواهر/برادر"""
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(sibling, field, value)
        
        sibling.updated_at = datetime.utcnow()
        db.add(sibling)
        await db.flush()
        return sibling
    
    @staticmethod
    async def delete(db: AsyncSession, sibling: Sibling) -> None:
        """حذف خواهر/برادر"""
        await db.delete(sibling)
        await db.flush()
    
    @staticmethod
    async def count_by_applicant(db: AsyncSession, user_id) -> int:
        """تعداد خواهر/برادرها"""
        query = select(Sibling).where(Sibling.user_id == user_id)
        result = await db.execute(query)
        return len(result.scalars().all())