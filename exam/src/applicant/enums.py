import enum 

class GenderEnum(str, enum.Enum):
        MALE = "male"
        FEMALE = "female"
    
class MaritalStatusEnum(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"

class BloodTypeEnum(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"

class StatusEnum(str, enum.Enum):
    DRAFT = "draft"
    PERSONAL_COMPLETED = "personal_completed"
    FAMILY_COMPLETED = "family_completed"
    EDUCATION_COMPLETED = "education_completed"
    EXPERIENCE_COMPLETED = "experience_completed"
    MILITARY_COMPLETED = "military_completed"
    SKILLS_COMPLETED = "skills_completed"
    DOCUMENTS_COMPLETED = "documents_completed"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class HousingStatusEnum(str, enum.Enum):
    OWNER = "owner"  
    TENANT = "tenant"  
    PARENTS_HOUSE = "parents_house" 
    OTHER = "other"

class GenderEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

class SiblingTypeEnum(str, enum.Enum):
    BROTHER = "brother"
    SISTER = "sister"

class MaritalStatusEnum(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"

    
class ExemptionTypeEnum(str, enum.Enum):
    EDUCATIONAL = "educational"
    GUARDIANSHIP = "guardianship"
    PURCHASE = "purchase"
    MEDICAL = "medical"
    SERVED = "served"
    EXEMPT = "exempt"


class DegreeEnum(str, enum.Enum):
    DIPLOMA = "diploma"
    ASSOCIATE = "associate"
    BACHELOR = "bachelor"
    MASTER = "master"
    PHD = "phd"
    POST_DOC = "post_doc"

class StudyStatusEnum(str, enum.Enum):
    GRADUATED = "graduated"
    STUDENT = "student"
    DROPPED = "dropped"
    CONTINUING = "continuing"

class SkillLevelEnum(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

    
class LanguageEnum(str, enum.Enum):
    ENGLISH = "english"
    ARABIC = "arabic"
    FRENCH = "french"
    GERMAN = "german"
    TURKISH = "turkish"
    SPANISH = "spanish"
    RUSSIAN = "russian"
    CHINESE = "chinese"
    JAPANESE = "japanese"
    OTHER = "other"

class ProficiencyEnum(str, enum.Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"
