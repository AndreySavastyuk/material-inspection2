"""
Упрощенный API endpoints для работы с материалами
"""
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel

router = APIRouter()

# Временное хранилище данных (в памяти)
materials_db = {}


class MaterialSimple(BaseModel):
    """Упрощенная модель материала"""
    id: Optional[str] = None
    material_code: str
    name: str
    material_type: str
    supplier: str
    quantity: float
    unit: str = "kg"
    status: str = "received"
    created_at: Optional[datetime] = None


@router.get("/")
async def get_materials(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        status: Optional[str] = None,
        search: Optional[str] = None
):
    """Получение списка материалов"""
    # Фильтрация
    materials = list(materials_db.values())

    if status:
        materials = [m for m in materials if m["status"] == status]

    if search:
        materials = [m for m in materials if
                     search.lower() in m["name"].lower() or search.lower() in m["material_code"].lower()]

    # Пагинация
    total = len(materials)
    materials = materials[skip:skip + limit]

    return {
        "items": materials,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{material_id}")
async def get_material(material_id: str):
    """Получение информации о материале"""
    if material_id not in materials_db:
        raise HTTPException(status_code=404, detail="Material not found")

    return materials_db[material_id]


@router.post("/")
async def create_material(material: MaterialSimple):
    """Создание нового материала"""
    # Генерируем ID
    material_id = str(uuid4())

    # Создаем материал
    material_data = material.dict()
    material_data["id"] = material_id
    material_data["created_at"] = datetime.now().isoformat()

    # Сохраняем
    materials_db[material_id] = material_data

    return material_data


@router.patch("/{material_id}")
async def update_material(material_id: str, updates: Dict[str, Any]):
    """Обновление материала"""
    if material_id not in materials_db:
        raise HTTPException(status_code=404, detail="Material not found")

    materials_db[material_id].update(updates)
    return materials_db[material_id]


@router.delete("/{material_id}")
async def delete_material(material_id: str):
    """Удаление материала"""
    if material_id not in materials_db:
        raise HTTPException(status_code=404, detail="Material not found")

    del materials_db[material_id]
    return {"success": True, "message": "Material deleted"}


# Добавим тестовые данные
def init_test_data():
    """Инициализация тестовых данных"""
    test_materials = [
        {
            "id": str(uuid4()),
            "material_code": "MAT-2024-001",
            "name": "Лист стальной 09Г2С",
            "material_type": "steel_sheet",
            "supplier": "ООО МеталлПоставка",
            "quantity": 1500,
            "unit": "kg",
            "status": "received",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid4()),
            "material_code": "MAT-2024-002",
            "name": "Труба стальная 325х8",
            "material_type": "steel_pipe",
            "supplier": "АО СтальТрубПром",
            "quantity": 800,
            "unit": "kg",
            "status": "testing",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid4()),
            "material_code": "MAT-2024-003",
            "name": "Пруток стальной 40Х",
            "material_type": "steel_rod",
            "supplier": "ООО МеталлБаза",
            "quantity": 350,
            "unit": "kg",
            "status": "approved",
            "created_at": datetime.now().isoformat()
        }
    ]

    for material in test_materials:
        materials_db[material["id"]] = material


# Инициализируем тестовые данные при загрузке модуля
init_test_data()