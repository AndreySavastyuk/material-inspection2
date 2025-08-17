"""
Скрипт для инициализации базы данных и создания первоначальных данных
"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from sqlalchemy import create_engine
from src.core.config import settings
from src.core.database import Base, init_db

# Импортируем все модели
from src.models import material, user, workflow, certificate


def create_tables():
    """
    Создание таблиц в базе данных (синхронно для Alembic)
    """
    # Получаем URL для синхронного подключения
    db_url = settings.DATABASE_URL

    # Преобразуем асинхронные URL в синхронные
    if db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://")
    elif db_url.startswith("sqlite+aiosqlite://"):
        db_url = db_url.replace("sqlite+aiosqlite://", "sqlite://")

    print(f"Creating database tables...")
    print(f"Database URL: {db_url}")

    try:
        # Создаем движок
        if db_url.startswith("sqlite://"):
            # Для SQLite убираем настройки пула соединений
            engine = create_engine(db_url, echo=True)
        else:
            # Для PostgreSQL с настройками пула
            engine = create_engine(
                db_url,
                echo=True,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True
            )

        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)

        print("[SUCCESS] Database tables created successfully!")

        # Закрываем соединение
        engine.dispose()

    except Exception as e:
        print(f"[ERROR] Error creating database tables: {e}")
        print(f"   Make sure the database server is running and accessible.")
        raise


async def init_database():
    """
    Асинхронная инициализация базы данных
    """
    print("Initializing database...")
    print(f"Database URL: {settings.DATABASE_URL}")

    try:
        await init_db()
        print("[SUCCESS] Database initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        print(f"   Make sure the database server is running and accessible.")
        raise


def check_config():
    """
    Проверка конфигурации
    """
    print("Checking configuration...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Debug mode: {settings.DEBUG}")

    # Проверяем наличие .env файла
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print(f"[OK] .env file found: {env_file}")
    else:
        print(f"[WARNING] .env file not found: {env_file}")
        print("   Using default configuration")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        "--sync",
        action="store_true",
        help="Use synchronous table creation (for initial setup)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check configuration only"
    )

    args = parser.parse_args()

    # Проверяем конфигурацию
    check_config()

    if args.check:
        print("Configuration check completed.")
        sys.exit(0)

    try:
        if args.sync:
            create_tables()
        else:
            asyncio.run(init_database())
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize database: {e}")
        print("\nTroubleshooting:")
        print("1. Check if the database server is running")
        print("2. Verify database connection settings in .env file")
        print("3. Try using --sync flag for synchronous initialization")
        print("4. For SQLite, ensure the directory exists and is writable")
        sys.exit(1)
