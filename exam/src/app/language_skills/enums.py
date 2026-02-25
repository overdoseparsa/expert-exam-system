# router.py for language_skills
import enum
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