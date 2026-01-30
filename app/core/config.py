from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings using Pydantic v2 BaseSettings"""
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://iot_user:iot_pass@postgres:5432/iot_monitor"
    DATABASE_URL_SYNC: str = "postgresql://iot_user:iot_pass@postgres:5432/iot_monitor"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "IoT Fleet Monitor"
    VERSION: str = "1.0.0"
    
    # Critical thresholds
    CRITICAL_TEMP_THRESHOLD: float = 80.0
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
