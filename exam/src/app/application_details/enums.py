# enums.py for application_details
# schemas.py for application_details
import enum

class ConnectionTypeEnum(str, enum.Enum):
    INTERNET = "internet"  # اینترنت
    ADS = "ads"  # آگهی
    PERSONAL = "personal"  # حضوری
    JOB_AGENCY = "job_agency"  # بنگاه کاریابی
    REFERRAL = "referral"  # معرف


class WorkScheduleEnum(str, enum.Enum):
    FULL_TIME = "full_time"  # تمام وقت
    PART_TIME = "part_time"  # نیمه وقت
    DAY_SHIFT = "day_shift"  # روزکار
    SHIFT_BASED = "shift_based"  # شیفت مطابق نیاز شرکت
    FLEXIBLE = "flexible"  # انعطاف‌پذیر

