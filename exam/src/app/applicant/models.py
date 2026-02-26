from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    Text,
    Float,
    ForeignKey,
    Enum,
    DateTime,
    Numeric,
    UniqueConstraint,
    Index,
    JSON
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import Base
from .enums import (
    DegreeEnum,
    ExemptionTypeEnum,
    GenderEnum,
    LanguageEnum,
    MaritalStatusEnum,
    BloodTypeEnum,
    ProficiencyEnum,
    SiblingTypeEnum,
    SkillLevelEnum,
    StatusEnum,
    HousingStatusEnum,
    StudyStatusEnum,
)
from auth.models import User

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

class Applicant(AbstractModel):

    __tablename__ = "UsersDetails"
    
    id = Column(
        Integer,
        primary_key=True, 
        index=True
    )
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False) # One To One Field for Each User
    
    name = Column(String(200), nullable=False)
    family = Column(String(200), nullable=False)
    national_code = Column(String(10), unique=True, index=True, nullable=False)
    father_name = Column[str](String(100), nullable=False)



    id_number = Column(String(20), nullable=False)
    insurance_number = Column(String(30), nullable=True)
    id_place = Column(String(100), nullable=False)
    father_job = Column(String(100), nullable=True)
    
    birth_date = Column(Date, nullable=False)
    nationality = Column(String(50), default="ایرانی")
    birth_place = Column(String(100), nullable=False)
    religion = Column(String(50), default="اسلام")
    gender = Column(Enum(GenderEnum), nullable=False) 
    blood_type = Column(Enum(BloodTypeEnum), nullable=True)  
    marital_status = Column(Enum(MaritalStatusEnum), nullable=False, default=MaritalStatusEnum.SINGLE) 
    marriage_date = Column(Date, nullable=True)
    

    tracking_code = Column(String(20), unique=True, nullable=True)
    

    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # روابط

    user = relationship(
        "User",
        backref="applicant",  
        uselist=False  
    )


