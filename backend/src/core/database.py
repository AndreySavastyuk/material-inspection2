"""
Настройка и инициализация базы данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from loguru import logger

from src.core.config import settings

# Преобразование DATABASE_URL для async
if settings.DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
elif settings.DATABASE_URL.startswith("sqlite:///"):
    DATABASE_URL = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
else:
    DATABASE_URL = settings.DATABASE_URL


# Создание асинхронного движка с учетом типа БД
if DATABASE_URL.startswith("sqlite"):
    # Для SQLite не используем настройки пула
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DB_ECHO,
        future=True,
    )
else:
    # Для PostgreSQL используем настройки пула
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DB_ECHO,
        future=True,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
    )

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Базовый класс для моделей
Base = declarative_base()

# Dependency для получения сессии БД
async def get_db():
    """
    Dependency для получения сессии базы данных
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

async def init_db():
    """
    Инициализация базы данных (создание таблиц)
    """
    async with engine.begin() as conn:
        # Импортируем все модели, чтобы они были зарегистрированы
        from src.models import material, user, workflow, certificate

        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")

async def close_db():
    """
    Закрытие соединения с базой данных
    """
    await engine.dispose()
    logger.info("Database connection closed")