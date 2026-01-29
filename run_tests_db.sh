#!/bin/bash
# Интеграционные тесты с PostgreSQL в Docker

set -e

echo "🐳 Запуск PostgreSQL контейнера..."
docker compose -f docker-compose.test.yml up -d

echo "⏳ Ожидание готовности PostgreSQL..."
for i in {1..30}; do
  status=$(docker inspect --format='{{.State.Health.Status}}' oauth-postgres-test 2>/dev/null || true)
  if [ "$status" = "healthy" ]; then
    break
  fi
  sleep 1
done

if [ "$status" != "healthy" ]; then
  echo "❌ PostgreSQL не готов"
  docker compose -f docker-compose.test.yml down -v
  exit 1
fi

export DATABASE_URL="postgresql+psycopg2://oauth_test:oauth_test@localhost:5433/oauth_test"
export SECRET_KEY="test-secret-key"
export GOOGLE_CLIENT_ID="test-client-id"
export GOOGLE_CLIENT_SECRET="test-client-secret"
export GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback"

alembic upgrade head
python -m pytest tests/ -v --tb=short

echo "🧹 Остановка контейнеров..."
docker compose -f docker-compose.test.yml down -v
