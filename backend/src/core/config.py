"""
Конфигурация приложения
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # Игнорировать дополнительные поля
    )

    # Основные настройки
    APP_NAME: str = "Metal Inspection System"
    ENVIRONMENT: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True)

    # База данных
    DATABASE_URL: str = Field(
        default="sqlite:///./metal_inspection.db",
        description="Database connection URL"
    )
    DB_ECHO: bool = Field(default=False, description="Echo SQL queries")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis connection URL")

    # Безопасность
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=480, description="Access token expiration time")

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000"
        ],
        description="Allowed CORS origins"
    )

    # Email настройки
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP host")
    SMTP_PORT: int = Field(default=587, description="SMTP port")
    SMTP_USER: str = Field(default="your-email@gmail.com", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="your-app-password", description="SMTP password")
    EMAIL_FROM: str = Field(default="noreply@metalinspection.com", description="From email address")

    # Frontend URL
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Frontend URL")

    # Файлы и сертификаты
    UPLOAD_PATH: str = Field(default="./uploads", description="Path for file uploads")
    CERTIFICATES_PATH: str = Field(default="./certificates", description="Path for certificates")
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024, description="Max upload size in bytes (10MB)")
    ALLOWED_EXTENSIONS: List[str] = Field(
        default=[".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".xls", ".xlsx"],
        description="Allowed file extensions"
    )

    # Роли пользователей
    USER_ROLES: List[str] = Field(
        default=[
            "warehouse_keeper",
            "quality_control",
            "lab_destructive",
            "lab_non_destructive",
            "production",
            "administrator"
        ],
        description="Available user roles"
    )

    # Статусы материалов
    MATERIAL_STATUSES: List[str] = Field(
        default=[
            "received",
            "quarantine",
            "testing",
            "approved",
            "rejected",
            "released"
        ],
        description="Material workflow statuses"
    )

    # Настройки workflow
    WORKFLOW_AUTO_TRANSITION: bool = Field(
        default=True,
        description="Enable automatic workflow transitions"
    )
    WORKFLOW_NOTIFICATION: bool = Field(
        default=True,
        description="Enable workflow notifications"
    )

    # Логирование
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FILE: Optional[str] = Field(default="logs/app.log", description="Log file path")


# Создание экземпляра настроек
settings = Settings()