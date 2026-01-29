from typing import Optional

from src.models.user import User, UserInDB
from src.repositories.user_repository import UserRepositoryInterface


class UserService:
    """Сервис для работы с пользователями"""

    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Получить пользователя по ID"""
        user_in_db = await self.user_repository.get_user_by_id(user_id)
        if user_in_db is None:
            return None

        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            picture=user_in_db.picture,
            is_active=user_in_db.is_active,
        )

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        user_in_db = await self.user_repository.get_user_by_email(email)
        if user_in_db is None:
            return None

        return User(
            id=user_in_db.id,
            email=user_in_db.email,
            full_name=user_in_db.full_name,
            picture=user_in_db.picture,
            is_active=user_in_db.is_active,
        )
