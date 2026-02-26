from .applicant import router as applicant_router
from .application_details import router as application_details_router
from .contact_information import router as contact_information_router
from .education import router as education_router
from .family_information import router as family_information_router
from .job_applications import router as job_applications_router
from .jobs_information import router as jobs_information_router
from .language_skills import router as language_skills_router
from .military_service import router as military_service_router


routers = [
    applicant_router,
    application_details_router,
    contact_information_router,
    education_router,
    family_information_router,
    job_applications_router,
    jobs_information_router,
    language_skills_router,
    military_service_router,
]