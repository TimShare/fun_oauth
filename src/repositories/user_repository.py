import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional

from sqlalchemy.orm import Session

from src.database import UserModel
from src.models.user import UserCreate, UserInDB


class UserRepositoryInterface(ABC):
    """Интерфейс репозитория пользователей"""

    @abstractmethod
    async def create_user(self, user: UserCreate) -> UserInDB:
        """Создать нового пользователя"""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Получить пользователя по ID"""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Получить пользователя по email"""
        pass

    @abstractmethod
    async def get_user_by_google_id(self, google_id: str) -> Optional[UserInDB]:
        """Получить пользователя по Google ID"""
        pass

    @abstractmethod
    async def update_user(self, user_id: str, user_data: Dict) -> Optional[UserInDB]:
        """Обновить данные пользователя"""
        pass

    @abstractmethod
    async def create_user_with_password(
        self, email: str, hashed_password: str, full_name: Optional[str] = None
    ) -> UserInDB:
        """Создать пользователя с паролем"""
        pass


class SQLAlchemyUserRepository(UserRepositoryInterface):
    """
    SQLAlchemy реализация репозитория пользователей.
    Использует реальную БД (SQLite для разработки, PostgreSQL для продакшена)
    """

    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, user: UserCreate) -> UserInDB:
        """Создать нового пользователя через OAuth"""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()

        db_user = UserModel(
            id=user_id,
            email=user.email,
            full_name=user.full_name,
            picture=user.picture,
            google_id=user.google_id,
            hashed_password=None,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return UserInDB(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            picture=db_user.picture,
            google_id=db_user.google_id,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )

    async def create_user_with_password(
        self, email: str, hashed_password: str, full_name: Optional[str] = None
    ) -> UserInDB:
        """Создать пользователя с паролем (обычная регистрация)"""
        user_id = str(uuid.uuid4())
        now = datetime.utcnow()

        db_user = UserModel(
            id=user_id,
            email=email,
            full_name=full_name,
            picture=None,
            google_id=None,
            hashed_password=hashed_password,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)

        return UserInDB(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            picture=db_user.picture,
            google_id=db_user.google_id,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Получить пользователя по ID"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None

        return UserInDB(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            picture=db_user.picture,
            google_id=db_user.google_id,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Получить пользователя по email"""
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        if not db_user:
            return None

        return UserInDB(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            picture=db_user.picture,
            google_id=db_user.google_id,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )

    async def get_user_by_google_id(self, google_id: str) -> Optional[UserInDB]:
        """Получить пользователя по Google ID"""
        db_user = (
            self.db.query(UserModel).filter(UserModel.google_id == google_id).first()
        )
        if not db_user:
            return None

        return UserInDB(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            picture=db_user.picture,
            google_id=db_user.google_id,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )

    async def update_user(self, user_id: str, user_data: Dict) -> Optional[UserInDB]:
        """Обновить данные пользователя"""
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not db_user:
            return None

        # Обновляем поля
        for key, value in user_data.items():
            if hasattr(db_user, key) and key not in ["id", "google_id", "created_at"]:
                setattr(db_user, key, value)

        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)

        return UserInDB(
            id=db_user.id,
            email=db_user.email,
            full_name=db_user.full_name,
            picture=db_user.picture,
            google_id=db_user.google_id,
            hashed_password=db_user.hashed_password,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
