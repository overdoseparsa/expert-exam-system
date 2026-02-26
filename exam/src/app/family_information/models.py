
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Enum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
from .enums import (
    GenderEnum,
    SiblingTypeEnum,
    MaritalStatusEnum
)

class AbstractModel(Base):
    """
    Common base model for all tables.
    """

    __abstract__ = True

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )

class Spouse(AbstractModel):
    __tablename__ = "spouses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(200), nullable=False)
    job = Column(String(100), nullable=True)

    user = relationship("User", backref="spouse")

class Child(AbstractModel):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    full_name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=False)
    
    gender = Column(Enum(GenderEnum), nullable=False)

    user = relationship("User", backref="child")

class Sibling(AbstractModel):
    __tablename__ = "siblings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),  nullable=False)
    full_name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=False)
    
    sibling_type = Column(Enum(SiblingTypeEnum), nullable=False)
    marital_status = Column(Enum(MaritalStatusEnum), nullable=False)
    job = Column(String(100), nullable=True)
   
    user = relationship("User", backref="siblings")

