"""
Metal Inspection System - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger

from src.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    # Startup
    logger.info("Starting Metal Inspection System...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Пока используем упрощенную версию без БД
    logger.info("Using in-memory storage (development mode)")

    yield

    # Shutdown
    logger.info("Shutting down Metal Inspection System...")


# Создание приложения FastAPI
app = FastAPI(
    title="Metal Inspection System",
    description="Система приемки и входного контроля металла",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Импортируем роутеры после создания app
from src.api.v1 import materials_simple as materials
from src.api.v1 import workflows, certificates, users

# Подключение роутеров
app.include_router(
    materials.router,
    prefix="/api/v1/materials",
    tags=["Materials"]
)

app.include_router(
    workflows.router,
    prefix="/api/v1/workflows",
    tags=["Workflows"]
)

app.include_router(
    certificates.router,
    prefix="/api/v1/certificates",
    tags=["Certificates"]
)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["Users"]
)

# Главная страница API
@app.get("/")
async def root():
    return {
        "message": "Metal Inspection System API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "storage": "in-memory"
    }