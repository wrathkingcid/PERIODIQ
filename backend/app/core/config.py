from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "PERIODIQ - Universal Automatic Timetable Generator"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "periodiq-super-secret-jwt-key-production-ready-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database: Defaults to SQLite for local zero-config execution; seamlessly accepts PostgreSQL
    DATABASE_URL: str = "sqlite:///./periodiq.db"
    
    # Solver defaults
    DEFAULT_SOLVER_TIMEOUT_SECONDS: int = 45
    MAX_SOLVER_TIMEOUT_SECONDS: int = 180
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
