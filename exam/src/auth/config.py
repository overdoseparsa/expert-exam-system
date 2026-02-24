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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

