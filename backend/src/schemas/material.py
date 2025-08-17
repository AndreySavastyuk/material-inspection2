"""
Pydantic схемы для материалов
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator

from src.models.material import MaterialStatus, MaterialType


class MaterialBase(BaseModel):
    """Базовая схема материала"""
    material_code: str = Field(..., min_length=1, max_length=50)
    material_type: MaterialType
    name: str = Field(..., min_length=1, max_length=200)
    grade: Optional[str] = Field(None, max_length=50)
    standard: Optional[str] = Field(None, max_length=50)
    dimensions: Optional[str] = Field(None, max_length=100)
    supplier: str = Field(..., min_length=1, max_length=200)
    supplier_certificate_number: Optional[str] = Field(None, max_length=100)
    batch_number: Optional[str] = Field(None, max_length=50)
    heat_number: Optional[str] = Field(None, max_length=50)
    quantity: float = Field(..., gt=0)
    unit: str = Field(default="kg", max_length=20)
    total_weight: Optional[float] = Field(None, ge=0)
    current_location: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MaterialCreate(MaterialBase):
    """Схема для создания материала"""

    @validator('material_code')
    def validate_material_code(cls, v):
        """Валидация кода материала"""
        if not v or not v.strip():
            raise ValueError('Material code cannot be empty')
        # Можно добавить проверку формата, например: MAT-2024-001
        return v.strip().upper()

    @validator('quantity')
    def validate_quantity(cls, v):
        """Валидация количества"""
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v


class MaterialUpdate(BaseModel):
    """Схема для обновления материала"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    grade: Optional[str] = Field(None, max_length=50)
    standard: Optional[str] = Field(None, max_length=50)
    dimensions: Optional[str] = Field(None, max_length=100)
    quantity: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, max_length=20)
    total_weight: Optional[float] = Field(None, ge=0)
    current_location: Optional[str] = Field(None, max_length=100)
    status: Optional[MaterialStatus] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MaterialResponse(MaterialBase):
    """Схема ответа с информацией о материале"""
    id: UUID
    status: MaterialStatus
    received_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    received_by: Optional[UUID]

    # Дополнительная информация
    workflow_info: Optional[Dict[str, Any]] = None
    test_results_count: Optional[int] = 0
    certificates_count: Optional[int] = 0

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            UUID: lambda v: str(v)
        }


class MaterialListResponse(BaseModel):
    """Схема ответа со списком материалов"""
    items: List[MaterialResponse]
    total: int
    skip: int
    limit: int

    class Config:
        orm_mode = True


class MaterialStatistics(BaseModel):
    """Статистика по материалам"""
    total_count: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_supplier: Dict[str, int]
    recent_receipts: int  # За последние 7 дней
    pending_tests: int
    approved_this_month: int


class MaterialWorkflowRequest(BaseModel):
    """Запрос на изменение workflow"""
    transition: str = Field(..., description="Название перехода")
    notes: Optional[str] = Field(None, description="Примечания")
    user_id: Optional[UUID] = Field(None, description="ID пользователя")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MaterialWorkflowResponse(BaseModel):
    """Ответ с информацией о workflow"""
    current_state: str
    available_transitions: List[str]
    history: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    can_auto_transition: bool = False


class MaterialSearchRequest(BaseModel):
    """Запрос на поиск материалов"""
    search_term: Optional[str] = None
    status: Optional[List[MaterialStatus]] = None
    material_type: Optional[List[MaterialType]] = None
    supplier: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    grade: Optional[str] = None
    has_certificate: Optional[bool] = None
    location: Optional[str] = None

    # Сортировка
    sort_by: str = Field(default="created_at", pattern="^(created_at|material_code|name|status)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")

    # Пагинация
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)