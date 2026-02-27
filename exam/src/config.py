from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # JWT settings
    SECRET_KEY: str = "CHANGE_ME_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./exam.db"
    SQL_ECHO: bool = False

    # Auth cookie settings
    AUTH_TOKEN_NAME: str = "Access-Token"
    HTTP_ONLY: bool = True
    HTTP_SECURE: bool = True  # set True in production with HTTPS
    SAME_SITE: str = "none"
    ALLOWED_ORIGINS_LIST :list[str] = ['https://localhost:3000']
    class Config:
        env_file = ".env"
        case_sensitive = True

    
settings = Settings()

