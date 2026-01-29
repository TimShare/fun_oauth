from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
import httpx

from src.config import get_settings
from src.models.user import Token, User, UserRegister, UserLogin
from src.services.auth_service import AuthService
from src.dependencies.auth import get_auth_service, get_current_user
from src.models.user import UserInDB


router = APIRouter(prefix="/auth", tags=["authentication"])

# Настройка OAuth
settings = get_settings()
oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/google/login")
async def google_login():
    """
    Перенаправление на страницу авторизации Google.
    Пользователь будет перенаправлен на Google для входа.
    """
    redirect_uri = settings.google_redirect_uri
    return RedirectResponse(
        url=f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&"
        f"access_type=offline"
    )


@router.get("/google/callback")
async def google_callback(
    code: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Обработка callback от Google после успешной авторизации.
    Обменивает код авторизации на токены и создает/обновляет пользователя.
    """
    try:
        # Обмен кода на токены
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            token_data = token_response.json()

            if "error" in token_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=token_data.get("error_description", "Failed to get token")
                )

            # Получение информации о пользователе
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            user_info = user_response.json()

        # Аутентификация/создание пользователя
        user, token = await auth_service.authenticate_with_google(
            google_id=user_info["id"],
            email=user_info["email"],
            full_name=user_info.get("name"),
            picture=user_info.get("picture"),
        )

        # Перенаправление на frontend с токеном
        frontend_url = settings.frontend_url
        return RedirectResponse(
            url=f"{frontend_url}/?token={token.access_token}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.get("/me", response_model=User)
async def get_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Получить информацию о текущем авторизованном пользователе.
    Требует Bearer токен в заголовке Authorization.
    """
    return User(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        picture=current_user.picture,
        is_active=current_user.is_active
    )


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    """
    Выход из системы (в данной реализации просто подтверждение).
    Клиент должен удалить токен на своей стороне.
    """
    return {"message": "Successfully logged out"}


@router.post("/register", response_model=Token)
async def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Регистрация нового пользователя с email и паролем.
    Возвращает JWT токен для последующей аутентификации.
    """
    try:
        user, token = await auth_service.register_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Вход пользователя с email и паролем.
    Возвращает JWT токен.
    """
    result = await auth_service.authenticate_user(
        email=user_data.email,
        password=user_data.password
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    user, token = result
    return token
