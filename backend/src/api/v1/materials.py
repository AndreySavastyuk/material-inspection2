"""
API endpoints для работы с материалами
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime
from uuid import UUID

from src.core.database import get_db
from src.models.material import Material, MaterialStatus, MaterialType
from src.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialResponse,
    MaterialListResponse
)
from src.core.material_flow import workflow_orchestrator

router = APIRouter()


@router.get("/", response_model=MaterialListResponse)
async def get_materials(
        db: AsyncSession = Depends(get_db),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        status: Optional[MaterialStatus] = None,
        material_type: Optional[MaterialType] = None,
        supplier: Optional[str] = None,
        search: Optional[str] = None,
        role: Optional[str] = Query(None, description="User role for filtering")
):
    """
    Получение списка материалов с фильтрацией
    """
    query = select(Material)

    # Применяем фильтры
    filters = []
    if status:
        filters.append(Material.status == status)
    if material_type:
        filters.append(Material.material_type == material_type)
    if supplier:
        filters.append(Material.supplier.ilike(f"%{supplier}%"))
    if search:
        filters.append(
            or_(
                Material.material_code.ilike(f"%{search}%"),
                Material.name.ilike(f"%{search}%"),
                Material.grade.ilike(f"%{search}%")
            )
        )

    # Фильтрация по роли
    if role:
        role_filters = {
            "warehouse_keeper": [MaterialStatus.RECEIVED, MaterialStatus.QUARANTINE],
            "quality_control": [MaterialStatus.RECEIVED, MaterialStatus.QUARANTINE, MaterialStatus.TESTING],
            "lab_destructive": [MaterialStatus.TESTING],
            "lab_non_destructive": [MaterialStatus.TESTING],
            "production": [MaterialStatus.APPROVED, MaterialStatus.RELEASED],
        }
        if role in role_filters:
            filters.append(Material.status.in_(role_filters[role]))

    if filters:
        query = query.where(and_(*filters))

    # Сортировка и пагинация
    query = query.order_by(Material.created_at.desc())
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    materials = result.scalars().all()

    # Подсчет общего количества
    count_query = select(func.count()).select_from(Material)
    if filters:
        count_query = count_query.where(and_(*filters))
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    return MaterialListResponse(
        items=[MaterialResponse.from_orm(m) for m in materials],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
        material_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о конкретном материале
    """
    query = select(Material).where(Material.id == material_id)
    result = await db.execute(query)
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Получаем информацию о workflow
    engine = workflow_orchestrator.get_engine(str(material_id))
    workflow_info = engine.get_state_info() if engine else None

    response = MaterialResponse.from_orm(material)
    if workflow_info:
        response.workflow_info = workflow_info

    return response


@router.post("/", response_model=MaterialResponse)
async def create_material(
        material_data: MaterialCreate,
        db: AsyncSession = Depends(get_db),
        user_id: Optional[UUID] = None  # В production это будет из JWT токена
):
    """
    Создание нового материала (приёмка)
    """
    # Проверяем уникальность кода материала
    existing_query = select(Material).where(Material.material_code == material_data.material_code)
    existing = await db.execute(existing_query)
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Material code already exists")

    # Создаем материал
    material = Material(
        **material_data.dict(),
        received_by=user_id,
        status=MaterialStatus.RECEIVED
    )

    db.add(material)
    await db.commit()
    await db.refresh(material)

    # Регистрируем в workflow
    workflow_orchestrator.register_material(material)

    return MaterialResponse.from_orm(material)


@router.patch("/{material_id}", response_model=MaterialResponse)
async def update_material(
        material_id: UUID,
        material_update: MaterialUpdate,
        db: AsyncSession = Depends(get_db)
):
    """
    Обновление информации о материале
    """
    query = select(Material).where(Material.id == material_id)
    result = await db.execute(query)
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Обновляем поля
    update_data = material_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(material, field, value)

    material.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(material)

    return MaterialResponse.from_orm(material)


@router.post("/{material_id}/transition")
async def transition_material(
        material_id: UUID,
        transition: str = Body(..., description="Transition trigger name"),
        notes: Optional[str] = Body(None),
        user_id: Optional[UUID] = Body(None),
        db: AsyncSession = Depends(get_db)
):
    """
    Изменение состояния материала в workflow
    """
    # Получаем материал
    query = select(Material).where(Material.id == material_id)
    result = await db.execute(query)
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Получаем движок workflow
    engine = workflow_orchestrator.get_engine(str(material_id))
    if not engine:
        engine = workflow_orchestrator.register_material(material)

    # Проверяем доступность перехода
    available_transitions = engine.get_available_transitions()
    if transition not in available_transitions:
        raise HTTPException(
            status_code=400,
            detail=f"Transition '{transition}' not available. Available: {available_transitions}"
        )

    # Выполняем переход
    try:
        trigger = getattr(engine, transition)
        success = trigger(user_id=user_id, notes=notes)

        if success:
            # Обновляем статус в БД
            material.status = MaterialStatus(engine.state)
            await db.commit()

            return {
                "success": True,
                "new_state": engine.state,
                "available_transitions": engine.get_available_transitions()
            }
        else:
            return {
                "success": False,
                "message": "Transition conditions not met",
                "current_state": engine.state
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{material_id}/workflow")
async def get_material_workflow(
        material_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Получение информации о текущем состоянии workflow материала
    """
    # Проверяем существование материала
    query = select(Material).where(Material.id == material_id)
    result = await db.execute(query)
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Получаем движок workflow
    engine = workflow_orchestrator.get_engine(str(material_id))
    if not engine:
        engine = workflow_orchestrator.register_material(material)

    return engine.get_state_info()


@router.delete("/{material_id}")
async def delete_material(
        material_id: UUID,
        db: AsyncSession = Depends(get_db)
):
    """
    Удаление материала (только для администратора)
    """
    query = select(Material).where(Material.id == material_id)
    result = await db.execute(query)
    material = result.scalar_one_or_none()

    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Проверяем, можно ли удалить
    if material.status not in [MaterialStatus.REJECTED, MaterialStatus.RECEIVED]:
        raise HTTPException(
            status_code=400,
            detail="Can only delete materials in RECEIVED or REJECTED status"
        )

    await db.delete(material)
    await db.commit()

    return {"success": True, "message": "Material deleted"}


# Дополнительный импорт для подсчета
from sqlalchemy import func