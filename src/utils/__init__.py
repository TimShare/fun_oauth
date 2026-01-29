"""
Утилиты для работы с паролями
"""

from passlib.context import CryptContext

# Контекст для хеширования паролей с argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хешировать пароль"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return pwd_context.verify(plain_password, hashed_password)

