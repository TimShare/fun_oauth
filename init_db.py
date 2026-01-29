#!/usr/bin/env python3
"""
Скрипт инициализации базы данных используя Alembic миграции.

Использование:
    python init_db.py

Вместо этого рекомендуется использовать Alembic команды напрямую:
    alembic upgrade head    - Применить все миграции
    alembic downgrade -1    - Откатить одну миграцию
    alembic history        - Просмотреть историю миграций
"""

import subprocess
import sys
from pathlib import Path


def run_alembic_command(args):
    """Запустить команду alembic"""
    cmd = ["alembic"] + args
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode == 0


def main():
    """Инициализация базы данных через Alembic миграции"""
    print("🔄 Применение миграций базы данных...")
    print()
    
    try:
        # Применяем все миграции
        if not run_alembic_command(["upgrade", "head"]):
            print("❌ Ошибка при применении миграций")
            sys.exit(1)
        
        print()
        print("✅ База данных успешно инициализирована!")
        print()
        print("📝 Полезные команды Alembic:")
        print("  alembic upgrade head        - Применить все миграции")
        print("  alembic downgrade -1        - Откатить одну миграцию")
        print("  alembic history             - Просмотреть историю миграций")
        print("  alembic current             - Посмотреть текущую версию")
        print("  alembic revision --autogenerate -m 'message' - Создать новую миграцию")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
