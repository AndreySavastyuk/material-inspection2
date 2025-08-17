"""Users API endpoints"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    return {"message": "Users endpoint"}

@router.get("/roles")
async def get_roles():
    return {
        "roles": [
            {"id": "warehouse_keeper", "name": "Кладовщик"},
            {"id": "quality_control", "name": "ОТК"},
            {"id": "lab_destructive", "name": "ЦЗЛ (разрушающий контроль)"},
            {"id": "lab_non_destructive", "name": "ЦЗЛ (неразрушающий контроль)"},
            {"id": "production", "name": "Производство"},
            {"id": "administrator", "name": "Администратор"}
        ]
    }