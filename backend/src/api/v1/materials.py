"""
API endpoints для работы с материалами
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.core.database import get_db
from src.models.material import MaterialStatus, MaterialType
from src.models.user import User, UserRole
from src.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    MaterialListResponse,
    MaterialStatusChange
)
from src.services.material_service import MaterialService
from src.core.auth import get_current_user

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/", response_model=MaterialListResponse)
async def get_materials(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[MaterialStatus] = None,
    material_type: Optional[MaterialType] = None,
    supplier: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка материалов с фильтрацией

    - **skip**: количество записей для пропуска
    - **limit**: максимальное количество записей
    - **status**: фильтр по статусу
    - **material_type**: фильтр по типу материала
    - **supplier**: фильтр по поставщику
    - **search**: поиск по коду, названию или марке
    """
    service = MaterialService(db)
    result = await service.get_materials(
        skip=skip,
        limit=limit,
        status=status,
        material_type=material_type,
        supplier=supplier,
        search=search,
        user_role=current_user.role if current_user else None
    )
    return result


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    material_data: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание нового материала

    Доступно только для ролей: WAREHOUSE_KEEPER, ADMINISTRATOR
    """
    # Проверка прав доступа
    if current_user.role not in [UserRole.WAREHOUSE_KEEPER, UserRole.ADMINISTRATOR]:
        raise PermissionDeniedException(
            "Only warehouse keepers and administrators can create materials"
        )

    service = MaterialService(db)
    material = await service.create_material(
        data=material_data,
        user_id=current_user.id
    )
    return material


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение материала по ID
    """
    service = MaterialService(db)
    material = await service.get_material(material_id)
    return material


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: UUID,
    material_data: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление данных материала

    Доступно для: WAREHOUSE_KEEPER, QUALITY_CONTROL, ADMINISTRATOR
    """
    # Проверка прав доступа
    allowed_roles = [
        UserRole.WAREHOUSE_KEEPER,
        UserRole.QUALITY_CONTROL,
        UserRole.ADMINISTRATOR
    ]
    if current_user.role not in allowed_roles:
        raise PermissionDeniedException(
            "You don't have permission to update materials"
        )

    service = MaterialService(db)
    material = await service.update_material(
        material_id=material_id,
        data=material_data,
        user_id=current_user.id
    )
    return material


@router.post("/{material_id}/status", response_model=MaterialResponse)
async def change_material_status(
    material_id: UUID,
    status_change: MaterialStatusChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Изменение статуса материала

    Переходы статусов контролируются в зависимости от роли пользователя
    """
    service = MaterialService(db)
    material = await service.change_material_status(
        material_id=material_id,
        new_status=status_change.new_status,
        user_id=current_user.id,
        user_role=current_user.role,
        notes=status_change.notes
    )
    return material


@router.post("/{material_id}/location", response_model=MaterialResponse)
async def assign_location(
    material_id: UUID,
    location: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Назначение местоположения материала

    Доступно для: WAREHOUSE_KEEPER, ADMINISTRATOR
    """
    if current_user.role not in [UserRole.WAREHOUSE_KEEPER, UserRole.ADMINISTRATOR]:
        raise PermissionDeniedException(
            "Only warehouse keepers can assign locations"
        )

    service = MaterialService(db)
    material = await service.assign_to_location(
        material_id=material_id,
        location=location,
        user_id=current_user.id
    )
    return material


@router.post("/{material_id}/reserve", response_model=MaterialResponse)
async def reserve_material(
    material_id: UUID,
    quantity: float = Body(..., gt=0),
    purpose: str = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Резервирование материала для производства

    Доступно для: PRODUCTION, ADMINISTRATOR
    """
    if current_user.role not in [UserRole.PRODUCTION, UserRole.ADMINISTRATOR]:
        raise PermissionDeniedException(
            "Only production staff can reserve materials"
        )

    service = MaterialService(db)
    material = await service.reserve_material(
        material_id=material_id,
        quantity=quantity,
        user_id=current_user.id,
        purpose=purpose
    )
    return material


@router.get("/{material_id}/history")
async def get_material_history(
    material_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение истории изменений материала
    """
    service = MaterialService(db)
    history = await service.get_material_history(material_id)
    return history


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление материала

    Доступно только для: ADMINISTRATOR
    """
    service = MaterialService(db)
    await service.delete_material(
        material_id=material_id,
        user_id=current_user.id,
        user_role=current_user.role
    )
    return None


@router.get("/availability/check")
async def check_availability(
    material_code: Optional[str] = None,
    grade: Optional[str] = None,
    min_quantity: Optional[float] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Проверка наличия материалов на складе
    """
    service = MaterialService(db)
    materials = await service.check_availability(
        material_code=material_code,
        grade=grade,
        min_quantity=min_quantity
    )
    return materials


# Импорт исключений
from src.core.exceptions import PermissionDeniedException