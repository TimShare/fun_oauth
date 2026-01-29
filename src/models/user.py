from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Базовая модель пользователя"""

    email: EmailStr
    full_name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    """Модель для создания пользователя через OAuth"""

    google_id: str


class UserRegister(BaseModel):
    """Модель для регистрации пользователя с паролем"""

    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Модель для входа пользователя"""

    email: EmailStr
    password: str


class UserInDB(UserBase):
    """Модель пользователя в базе данных"""

    id: str
    google_id: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserBase):
    """Модель пользователя для ответа API"""

    id: str
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Модель токена доступа"""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Данные из токена"""

    user_id: Optional[str] = None
    email: Optional[str] = None
