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
    

    status = Column[str](Enum(StatusEnum), default=StatusEnum.DRAFT)
    tracking_code = Column(String(20), unique=True, nullable=True)
    

    submitted_at = Column(DateTime(timezone=True), nullable=True)
    
    # روابط

    user = relationship(
        "User",
        back_populates="applicant",
    )



class Address(AbstractModel):
    __tablename__ = "Address"
    id = Column[int](Integer, primary_key=True, index=True)
    province = Column(String(50), nullable=False)
    city = Column(String(50), nullable=False)
    address = Column(Text, nullable=False)
    postal_code = Column(String(10), nullable=True)
    
    housing_status = Column(Enum(HousingStatusEnum), nullable=False)
    ownership_duration = Column(Integer, nullable=True)  # مدت مالکیت/اجاره به سال
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 

class Contact(AbstractModel):
    __tablename__ = "contact_info"

    id = Column[int](Integer, primary_key=True, index=True)
    phone = Column[str](String(11), nullable=False)
    emergency_phone = Column[str](String(11), nullable=True)
    email = Column[str](String(100), nullable=True)
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 


class Spouse(AbstractModel):
    __tablename__ = "spouses"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    job = Column(String(100), nullable=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 

class Child(AbstractModel):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 

class Sibling(AbstractModel):
    __tablename__ = "siblings"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=False)
    

    
    sibling_type = Column(Enum(SiblingTypeEnum), nullable=False)
    marital_status = Column(Enum(MaritalStatusEnum), nullable=False)
    job = Column(String(100), nullable=True)

    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 

class MilitaryService(AbstractModel):
    __tablename__ = "military_services"
    
    id = Column(Integer, primary_key=True, index=True)
    
    service_start = Column(Date, nullable=True)
    service_end = Column(Date, nullable=True)
    service_duration = Column(String(50), nullable=True)
    shortage_duration = Column(String(50), nullable=True)
    extra_duration = Column(String(50), nullable=True)
    service_org = Column(String(200), nullable=True)
    service_city = Column(String(100), nullable=True)

    exemption_type = Column(Enum(ExemptionTypeEnum), nullable=True)
    exemption_reason = Column(Text, nullable=True)
  
    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 


class Education(AbstractModel):
    __tablename__ = "educations"
    
    id = Column[int](Integer, primary_key=True, index=True)
    

    degree = Column(Enum(DegreeEnum), nullable=False)
    field = Column(String(200), nullable=False)
    university = Column(String(200), nullable=False)
    average = Column(Float, nullable=True)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=True)
    study_status = Column(Enum(StudyStatusEnum), nullable=False)
    description = Column(Text, nullable=True)
   
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 


class WorkExperience(AbstractModel):
    __tablename__ = "work_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    
    company = Column(String(200), nullable=False)
    position = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    currently_working = Column(Boolean, default=False)
    job_description = Column(Text, nullable=True)
    leaving_reason = Column(Text, nullable=True)
    salary = Column(Numeric(12, 2), nullable=True)  # مبلغ به تومان یا ریال

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 

class Skill(AbstractModel):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    

    
    skill_name = Column(String(100), nullable=False)
    skill_level = Column(Enum(SkillLevelEnum), nullable=False)
    years_of_experience = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    

class LanguageSkill(AbstractModel):
    __tablename__ = "language_skills"
    
    id = Column(Integer, primary_key=True, index=True)

    language = Column(Enum(LanguageEnum), nullable=False)
    other_language = Column(String(100), nullable=True)
    reading = Column(Enum(ProficiencyEnum), nullable=False)
    writing = Column(Enum(ProficiencyEnum), nullable=False)
    speaking = Column(Enum(ProficiencyEnum), nullable=False)
    listening = Column(Enum(ProficiencyEnum), nullable=False)

    
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 
    
class TrainingCourse(AbstractModel):
    __tablename__ = "training_courses"
    
    id = Column(Integer, primary_key=True, index=True)
    
    title = Column(String(200), nullable=False) 
    institute = Column(String(200), nullable=False) 
    duration = Column(String(50), nullable=False) 
    start_date = Column(Date, nullable=False) 
    end_date = Column(Date, nullable=True) 
    
    has_certificate = Column(Boolean, default=False)  
    certificate_id = Column(String(100), nullable=True) 
    certificate_date = Column(Date, nullable=True)  
    
    description = Column(Text, nullable=True)  
    skills_learned = Column(Text, nullable=True) 
    instructor = Column(String(100), nullable=True)  

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
        ) 