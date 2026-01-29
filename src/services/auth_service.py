from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from src.models.user import Token, TokenData, UserInDB
from src.repositories.user_repository import UserRepositoryInterface
from src.utils import hash_password, verify_password


class AuthService:
    """Сервис аутентификации и авторизации"""

    def __init__(
        self,
        user_repository: UserRepositoryInterface,
        secret_key: str,
        algorithm: str,
        access_token_expire_minutes: int,
    ):
        self.user_repository = user_repository
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes

    def create_access_token(self, user: UserInDB) -> Token:
        """Создать JWT токен доступа для пользователя"""
        expires_delta = timedelta(minutes=self.access_token_expire_minutes)
        expire = datetime.utcnow() + expires_delta

        to_encode = {"user_id": user.id, "email": user.email, "exp": expire}

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return Token(access_token=encoded_jwt)

    async def verify_token(self, token: str) -> Optional[TokenData]:
        """Проверить и декодировать JWT токен"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("user_id")
            email: str = payload.get("email")

            if user_id is None:
                return None

            return TokenData(user_id=user_id, email=email)
        except JWTError:
            return None

    async def get_current_user(self, token: str) -> Optional[UserInDB]:
        """Получить текущего пользователя по токену"""
        token_data = await self.verify_token(token)
        if token_data is None or token_data.user_id is None:
            return None

        user = await self.user_repository.get_user_by_id(token_data.user_id)
        return user

    async def authenticate_with_google(
        self,
        google_id: str,
        email: str,
        full_name: Optional[str] = None,
        picture: Optional[str] = None,
    ) -> tuple[UserInDB, Token]:
        """
        Аутентификация через Google OAuth.
        Если пользователь существует - возвращаем его, иначе создаем нового.
        """
        # Проверяем, существует ли пользователь
        user = await self.user_repository.get_user_by_google_id(google_id)

        if user is None:
            # Создаем нового пользователя
            from src.models.user import UserCreate

            user_create = UserCreate(
                email=email, google_id=google_id, full_name=full_name, picture=picture
            )
            user = await self.user_repository.create_user(user_create)
        else:
            # Обновляем информацию о пользователе
            update_data = {}
            if full_name and user.full_name != full_name:
                update_data["full_name"] = full_name
            if picture and user.picture != picture:
                update_data["picture"] = picture

            if update_data:
                user = await self.user_repository.update_user(user.id, update_data)

        # Создаем токен доступа
        token = self.create_access_token(user)

        return user, token

    async def register_user(
        self, email: str, password: str, full_name: Optional[str] = None
    ) -> tuple[UserInDB, Token]:
        """
        Регистрация нового пользователя с email и паролем
        """
        # Проверяем, не существует ли пользователь с таким email
        existing_user = await self.user_repository.get_user_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")

        # Хешируем пароль
        hashed_pwd = hash_password(password)

        # Создаем пользователя
        user = await self.user_repository.create_user_with_password(
            email=email, hashed_password=hashed_pwd, full_name=full_name
        )

        # Создаем токен
        token = self.create_access_token(user)

        return user, token

    async def authenticate_user(
        self, email: str, password: str
    ) -> Optional[tuple[UserInDB, Token]]:
        """
        Аутентификация пользователя по email и паролю
        """
        # Ищем пользователя
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            return None

        # Проверяем пароль
        if not user.hashed_password:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        # Создаем токен
        token = self.create_access_token(user)

        return user, token
