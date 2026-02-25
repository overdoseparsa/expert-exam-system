# enums.py for contact_information

from enum import Enum
class HousingStatusEnum(str, Enum):
    OWNER = "owner"
    TENANT = "tenant"
    PARENTS_HOUSE = "parents_house"
    OTHER = "other"
