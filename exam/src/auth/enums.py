import enum

class StatusEnum(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"

class RoleEnum(str,enum.Enum):
    ADMIN = "admin"
    USER  =  "user"
    MANGER= "manger"