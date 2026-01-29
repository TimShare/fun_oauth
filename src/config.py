from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения"""

    # Основные настройки приложения
    app_name: str = "FastAPI OAuth App"
    app_version: str = "1.0.0"
    debug: bool = True

    # Настройки сервера
    host: str = "0.0.0.0"
    port: int = 8000

    # Настройки безопасности
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Google OAuth настройки
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str

    # Frontend URL для редиректов
    frontend_url: str = "http://localhost:3000"

    # Database URL
    database_url: str = "sqlite:///./oauth_app.db"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (с кэшированием)"""
    return Settings()
