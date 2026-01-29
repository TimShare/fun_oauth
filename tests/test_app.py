"""
Тесты для FastAPI OAuth приложения
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Фикстура для создания тестового клиента"""
    return TestClient(app)


class TestHealth:
    """Тесты здоровья приложения"""

    def test_health_check(self, client):
        """Проверка здоровья приложения"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_root_endpoint(self, client):
        """Проверка корневого эндпоинта"""
        response = client.get("/")
        assert response.status_code == 200


class TestAuthRegistration:
    """Тесты регистрации пользователя"""

    def test_register_invalid_email(self, client):
        """Регистрация с невалидным email"""
        response = client.post(
            "/auth/register", json={"email": "invalid-email", "password": "password123"}
        )
        assert response.status_code == 422  # Validation error

    def test_register_missing_fields(self, client):
        """Регистрация без обязательных полей"""
        response = client.post("/auth/register", json={})
        assert response.status_code == 422


class TestAuthLogin:
    """Тесты входа пользователя"""

    def test_login_wrong_password(self, client):
        """Вход с неправильным паролем"""
        response = client.post(
            "/auth/login",
            json={"email": "user@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Вход несуществующего пользователя"""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "password123"},
        )
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]

    def test_login_invalid_email_format(self, client):
        """Вход с невалидным форматом email"""
        response = client.post(
            "/auth/login", json={"email": "invalid-email", "password": "password123"}
        )
        assert response.status_code == 422


class TestProtectedEndpoints:
    """Тесты защищенных эндпоинтов"""

    def test_get_profile_no_token(self, client):
        """Получение профиля без токена"""
        response = client.get("/auth/me")
        assert response.status_code == 403  # Forbidden

    def test_get_profile_invalid_token(self, client):
        """Получение профиля с невалидным токеном"""
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    def test_get_profile_expired_token(self, client):
        """Получение профиля с истекшим токеном"""
        # Используем токен с истекшим сроком
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjAwMDAwMDAwfQ.invalid"

        response = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    def test_logout_no_token(self, client):
        """Выход без токена"""
        response = client.post("/auth/logout")
        assert response.status_code == 403


class TestGoogleOAuth:
    """Тесты Google OAuth"""

    def test_google_login_redirect(self, client):
        """Проверка редиректа на Google"""
        response = client.get("/auth/google/login", follow_redirects=False)
        assert response.status_code == 307
        assert "accounts.google.com" in response.headers["location"]

    def test_google_callback_missing_code(self, client):
        """Callback без кода авторизации"""
        response = client.get("/auth/google/callback")
        assert response.status_code == 422  # Missing required parameter


class TestAPIDocumentation:
    """Тесты API документации"""

    def test_swagger_docs_available(self, client):
        """Проверка что Swagger документация доступна"""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_available(self, client):
        """Проверка что OpenAPI схема доступна"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "openapi" in response.json()


class TestStaticFiles:
    """Тесты статических файлов"""

    def test_static_css_available(self, client):
        """Проверка что CSS доступен"""
        response = client.get("/static/css/style.css")
        assert response.status_code == 200

    def test_static_js_available(self, client):
        """Проверка что JavaScript доступен"""
        response = client.get("/static/js/app.js")
        assert response.status_code == 200


class TestErrorHandling:
    """Тесты обработки ошибок"""

    def test_404_not_found(self, client):
        """Проверка 404 ошибки"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404

    def test_method_not_allowed(self, client):
        """Проверка что неправильный метод запроса возвращает ошибку"""
        response = client.get("/auth/login")  # Должен быть POST
        assert response.status_code == 405  # Method Not Allowed


class TestPasswordValidation:
    """Тесты валидации паролей"""

    def test_register_requires_email(self, client):
        """Регистрация требует email"""
        response = client.post("/auth/register", json={"password": "password123"})
        assert response.status_code == 422

    def test_register_requires_password(self, client):
        """Регистрация требует пароль"""
        response = client.post("/auth/register", json={"email": "test@example.com"})
        assert response.status_code == 422


class TestSecurityHeaders:
    """Тесты безопасности"""

    def test_health_endpoint_public(self, client):
        """Health endpoint должен быть публичным"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_auth_endpoints_exist(self, client):
        """Проверка что эндпоинты авторизации существуют"""
        # GET на эндпоинты которые требуют POST должны вернуть 405
        response = client.get("/auth/register")
        assert response.status_code == 405

        response = client.get("/auth/login")
        assert response.status_code == 405
