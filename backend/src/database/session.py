"""
Database session management
"""
from sqlalchemy.orm import Session
from src.database.base import SessionLocal, engine, Base

def create_tables():
    """
    Создание всех таблиц в базе данных
    """
    Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    """
    Получение синхронной сессии базы данных
    """
    return SessionLocal()