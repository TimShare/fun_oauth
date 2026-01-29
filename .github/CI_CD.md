# CI/CD Pipeline

Проект использует GitHub Actions для автоматизации тестирования и развертывания.

## Workflows

### 1. Tests (`.github/workflows/tests.yml`)

Запускается при каждом push и pull request в ветки `main` и `develop`:

- ✅ Сборка Docker образа
- ✅ Применение миграций
- ✅ Запуск 23 единичных тестов
- ✅ Проверка health endpoint

**Условия:**
- Все тесты должны пройти
- Health endpoint должен быть доступен

### 2. Code Quality (`.github/workflows/quality.yml`)

Проверяет качество кода:

- ✅ Форматирование (Black)
- ✅ Сортировка импортов (isort)
- ✅ Линтинг (flake8)

**Условия:**
- Код должен соответствовать стилю Black
- Импорты должны быть отсортированы
- Не должно быть синтаксических ошибок

Исправить код автоматически:
```bash
black src/ tests/
isort src/ tests/
```

### 3. Build Docker Image (`.github/workflows/build.yml`)

Собирает и публикует Docker образ при push в main:

- ✅ Сборка Docker образа
- ✅ Публикация в Docker Hub (требует секреты)
- ✅ Тегирование (branch, semver, sha)

**Требуется:**
```
DOCKER_USERNAME
DOCKER_PASSWORD
```

Добавить в GitHub Settings → Secrets and variables → Actions

## Локальная разработка

Перед push убедитесь что код проходит проверки:

```bash
# Форматирование
black src/ tests/
isort src/ tests/

# Линтинг
flake8 src/ tests/

# Тесты
./run_tests.sh
```

## Tags и Releases

При создании tag версии (v1.0.0, v1.1.0):
1. GitHub Actions автоматически собирает Docker образ
2. Образ публикуется с тегом версии
3. Создается Release на GitHub

```bash
git tag v1.0.0
git push origin v1.0.0
```

## Troubleshooting

### Тесты не проходят в CI но проходят локально

Это может быть из-за разных зависимостей. Пересоберите образ:

```bash
docker-compose build --no-cache
./run_tests.sh
```

### Docker образ не публикуется

Проверьте что добавлены secrets в Settings → Secrets and variables

### Миграции не применяются

Убедитесь что в `alembic/versions/` есть файлы миграций
