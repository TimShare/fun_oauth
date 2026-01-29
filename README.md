# FastAPI OAuth Application

FastAPI приложение с чистой архитектурой и авторизацией через Google OAuth 2.0.

## Архитектура

Проект следует принципам чистой архитектуры:

- **Models** (`src/models/`) - Pydantic модели для валидации данных
- **Repositories** (`src/repositories/`) - Слой доступа к данным (SQLAlchemy)
- **Services** (`src/services/`) - Бизнес-логика приложения
- **Routes** (`src/routes/`) - HTTP эндпоинты
- **Dependencies** (`src/dependencies/`) - Dependency Injection для FastAPI

## Установка

### 1. Переменные окружения

Создайте `.env` из `.env.example`:

```bash
cp .env.example .env
```

Обновите Google OAuth данные в `.env`:

```env
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 2. Зависимости

```bash
pip install -r requirements.txt
```

## Быстрый старт

### Тесты в Docker (рекомендуется)
```bash
./run_tests.sh
```
Запустит все 23 теста в Docker контейнере.

### Локальный запуск
```bash
./run_local.sh
```
Применит миграции БД и запустит приложение на `http://localhost:8000`

### Docker запуск
```bash
docker-compose up
```

## API Endpoints

### Публичные
- `GET /` - Информация о приложении
- `GET /health` - Проверка здоровья
- `GET /auth/google/login` - OAuth авторизация
- `GET /docs` - Swagger документация

### Защищенные (требуют Bearer токен)
- `GET /auth/me` - Информация о пользователе
- `POST /auth/logout` - Выход

## Миграции (Alembic)

После изменения моделей:

```bash
alembic revision --autogenerate -m "Описание"
alembic upgrade head
```

Просмотр истории:

```bash
alembic history
alembic current
```

## Технологии

- FastAPI 0.109.0
- SQLAlchemy 2.0 (ORM)
- Alembic (миграции)
- Pydantic (валидация)
- JWT (аутентификация)
- bcrypt (пароли)
- Google OAuth 2.0

## Тестирование

23 единичных теста покрывают:
- Аутентификацию (регистрация, вход)
- Google OAuth flow
- Защиту эндпоинтов
- Валидацию данных
- Обработку ошибок

Запуск:
```bash
./run_tests.sh              # В Docker (рекомендуется)
pytest tests/ -v            # Локально
```

## Production

Используйте PostgreSQL вместо SQLite:

```env
DATABASE_URL=postgresql://user:password@host/dbname
```

Остальные рекомендации:
- Установите DEBUG=False в production
- Обновите SECRET_KEY
- Используйте системный процесс-менеджер (systemd, supervisor)
- Настройте CORS для конкретных доменов
- Используйте HTTPS

## Лицензия

MIT
