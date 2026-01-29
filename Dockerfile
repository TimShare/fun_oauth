FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Применяем миграции при запуске и затем запускаем приложение
CMD ["sh", "-c", "alembic upgrade head && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"]
