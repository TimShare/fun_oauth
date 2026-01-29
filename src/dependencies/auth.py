from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.config import get_settings
from src.database import get_db
from src.repositories.user_repository import SQLAlchemyUserRepository
from src.services.auth_service import AuthService
from src.services.user_service import UserService
from src.models.user import UserInDB


# Security scheme
security = HTTPBearer()


def get_user_repository(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    """Получить репозиторий пользователей (Dependency Injection)"""
    return SQLAlchemyUserRepository(db)


def get_auth_service(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> AuthService:
    """Получить сервис аутентификации (Dependency Injection)"""
    settings = get_settings()
    return AuthService(
        user_repository=user_repository,
        secret_key=settings.secret_key,
        algorithm=settings.algorithm,
        access_token_expire_minutes=settings.access_token_expire_minutes
    )


def get_user_service(
    user_repository: SQLAlchemyUserRepository = Depends(get_user_repository)
) -> UserService:
    """Получить сервис пользователей (Dependency Injection)"""
    return UserService(user_repository=user_repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserInDB:
    """
    Получить текущего авторизованного пользователя.
    Используется как dependency для защищенных эндпоинтов.
    """
    token = credentials.credentials
    user = await auth_service.get_current_user(token)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )

    return user
