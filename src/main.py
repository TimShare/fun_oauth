import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.config import get_settings
from src.routes.auth import router as auth_router


def create_app() -> FastAPI:
    """Создание и настройка FastAPI приложения"""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        description="FastAPI приложение с чистой архитектурой и Google OAuth авторизацией",
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене укажите конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Подключение роутеров
    app.include_router(auth_router)

    # Подключение статических файлов
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def root():
        """Главная страница - отдаем HTML"""
        index_path = os.path.join(static_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {
            "message": "Welcome to FastAPI OAuth App",
            "version": settings.app_version,
            "docs": "/docs",
        }

    @app.get("/health")
    async def health_check():
        """Проверка здоровья приложения"""
        return {"status": "ok"}

    return app


# Создание экземпляра приложения
app = create_app()
