"""
Material Service - бизнес-логика для работы с материалами
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from src.models.material import Material, MaterialStatus, MaterialType
from src.models.user import User, UserRole
from src.models.workflow import WorkflowState
from src.schemas.material import MaterialCreate, MaterialUpdate
from src.core.exceptions import (
    NotFoundException,
    BusinessLogicException,
    PermissionDeniedException
)


class MaterialService:
    """Сервис для работы с материалами"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_material(
            self,
            data: MaterialCreate,
            user_id: UUID
    ) -> Material:
        """
        Создание нового материала
        """
        # Проверяем уникальность кода материала
        existing = await self.db.execute(
            select(Material).where(Material.material_code == data.material_code)
        )
        if existing.scalar_one_or_none():
            raise BusinessLogicException(
                f"Material with code {data.material_code} already exists"
            )

        # Создаем материал
        material = Material(
            **data.dict(),
            status=MaterialStatus.RECEIVED,
            received_by=user_id,
            received_date=datetime.utcnow(),
            created_at=datetime.utcnow()
        )

        # Создаем начальное состояние workflow
        workflow_state = WorkflowState(
            material_id=material.id,
            status=MaterialStatus.RECEIVED,
            changed_by=user_id,
            notes="Материал принят на склад"
        )

        self.db.add(material)
        self.db.add(workflow_state)

        await self.db.commit()
        await self.db.refresh(material)

        return material

    async def get_material(self, material_id: UUID) -> Material:
        """
        Получение материала по ID
        """
        result = await self.db.execute(
            select(Material)
            .options(selectinload(Material.test_results))
            .where(Material.id == material_id)
        )
        material = result.scalar_one_or_none()

        if not material:
            raise NotFoundException(f"Material {material_id} not found")

        return material

    async def get_materials(
            self,
            skip: int = 0,
            limit: int = 100,
            status: Optional[MaterialStatus] = None,
            material_type: Optional[MaterialType] = None,
            supplier: Optional[str] = None,
            search: Optional[str] = None,
            user_role: Optional[UserRole] = None
    ) -> Dict[str, Any]:
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

        # Фильтрация по роли пользователя
        if user_role:
            role_status_map = {
                UserRole.WAREHOUSE_KEEPER: [
                    MaterialStatus.RECEIVED,
                    MaterialStatus.QUARANTINE
                ],
                UserRole.QUALITY_CONTROL: [
                    MaterialStatus.IN_INSPECTION,
                    MaterialStatus.APPROVED,
                    MaterialStatus.REJECTED
                ],
                UserRole.LAB_DESTRUCTIVE: [
                    MaterialStatus.LAB_TESTING
                ],
                UserRole.LAB_NON_DESTRUCTIVE: [
                    MaterialStatus.LAB_TESTING
                ],
                UserRole.PRODUCTION: [
                    MaterialStatus.APPROVED,
                    MaterialStatus.IN_PRODUCTION,
                    MaterialStatus.CONSUMED
                ]
            }

            if user_role in role_status_map:
                filters.append(Material.status.in_(role_status_map[user_role]))

        if filters:
            query = query.where(and_(*filters))

        # Получаем общее количество
        count_query = select(func.count()).select_from(Material)
        if filters:
            count_query = count_query.where(and_(*filters))

        total = await self.db.scalar(count_query)

        # Применяем пагинацию и сортировку
        query = query.order_by(Material.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        materials = result.scalars().all()

        return {
            "items": materials,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    async def update_material(
            self,
            material_id: UUID,
            data: MaterialUpdate,
            user_id: UUID
    ) -> Material:
        """
        Обновление материала
        """
        material = await self.get_material(material_id)

        # Обновляем только переданные поля
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(material, field, value)

        material.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(material)

        return material

    async def change_material_status(
            self,
            material_id: UUID,
            new_status: MaterialStatus,
            user_id: UUID,
            user_role: UserRole,
            notes: Optional[str] = None
    ) -> Material:
        """
        Изменение статуса материала с проверкой прав
        """
        material = await self.get_material(material_id)

        # Проверяем права на изменение статуса
        allowed_transitions = self._get_allowed_transitions(
            material.status,
            user_role
        )

        if new_status not in allowed_transitions:
            raise PermissionDeniedException(
                f"Transition from {material.status.value} to {new_status.value} "
                f"is not allowed for role {user_role.value}"
            )

        # Сохраняем историю изменения
        workflow_state = WorkflowState(
            material_id=material_id,
            status=new_status,
            previous_status=material.status,
            changed_by=user_id,
            notes=notes
        )

        # Обновляем статус
        material.status = new_status
        material.updated_at = datetime.utcnow()

        self.db.add(workflow_state)
        await self.db.commit()
        await self.db.refresh(material)

        return material

    async def assign_to_location(
            self,
            material_id: UUID,
            location: str,
            user_id: UUID
    ) -> Material:
        """
        Назначение местоположения материала
        """
        material = await self.get_material(material_id)

        # Сохраняем предыдущее местоположение в метаданных
        if material.current_location:
            if not material.metadata:
                material.metadata = {}

            if "location_history" not in material.metadata:
                material.metadata["location_history"] = []

            material.metadata["location_history"].append({
                "location": material.current_location,
                "moved_at": datetime.utcnow().isoformat(),
                "moved_by": str(user_id)
            })

        material.current_location = location
        material.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(material)

        return material

    async def check_availability(
            self,
            material_code: Optional[str] = None,
            grade: Optional[str] = None,
            min_quantity: Optional[float] = None
    ) -> List[Material]:
        """
        Проверка наличия материалов
        """
        query = select(Material).where(
            Material.status == MaterialStatus.APPROVED
        )

        if material_code:
            query = query.where(Material.material_code == material_code)

        if grade:
            query = query.where(Material.grade == grade)

        if min_quantity:
            query = query.where(Material.quantity >= min_quantity)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def reserve_material(
            self,
            material_id: UUID,
            quantity: float,
            user_id: UUID,
            purpose: str
    ) -> Material:
        """
        Резервирование материала для производства
        """
        material = await self.get_material(material_id)

        if material.status != MaterialStatus.APPROVED:
            raise BusinessLogicException(
                f"Material {material.material_code} is not approved for use"
            )

        if material.quantity < quantity:
            raise BusinessLogicException(
                f"Insufficient quantity. Available: {material.quantity}, "
                f"Requested: {quantity}"
            )

        # Обновляем количество и статус
        material.quantity -= quantity

        if material.quantity == 0:
            material.status = MaterialStatus.CONSUMED
        else:
            material.status = MaterialStatus.IN_PRODUCTION

        # Добавляем информацию о резервировании в метаданные
        if not material.metadata:
            material.metadata = {}

        if "reservations" not in material.metadata:
            material.metadata["reservations"] = []

        material.metadata["reservations"].append({
            "quantity": quantity,
            "reserved_by": str(user_id),
            "reserved_at": datetime.utcnow().isoformat(),
            "purpose": purpose
        })

        material.updated_at = datetime.utcnow()

        # Записываем в workflow
        workflow_state = WorkflowState(
            material_id=material_id,
            status=material.status,
            changed_by=user_id,
            notes=f"Reserved {quantity} {material.unit} for {purpose}"
        )

        self.db.add(workflow_state)
        await self.db.commit()
        await self.db.refresh(material)

        return material

    async def get_material_history(
            self,
            material_id: UUID
    ) -> List[WorkflowState]:
        """
        Получение истории изменений материала
        """
        result = await self.db.execute(
            select(WorkflowState)
            .where(WorkflowState.material_id == material_id)
            .order_by(WorkflowState.changed_at.asc())
        )

        return result.scalars().all()

    async def delete_material(
            self,
            material_id: UUID,
            user_id: UUID,
            user_role: UserRole
    ) -> bool:
        """
        Удаление материала (только для администратора)
        """
        if user_role != UserRole.ADMINISTRATOR:
            raise PermissionDeniedException(
                "Only administrators can delete materials"
            )

        material = await self.get_material(material_id)

        # Проверяем, можно ли удалить
        if material.status in [MaterialStatus.IN_PRODUCTION, MaterialStatus.CONSUMED]:
            raise BusinessLogicException(
                "Cannot delete material that is in production or consumed"
            )

        await self.db.delete(material)
        await self.db.commit()

        return True

    def _get_allowed_transitions(
            self,
            current_status: MaterialStatus,
            user_role: UserRole
    ) -> List[MaterialStatus]:
        """
        Получение разрешенных переходов статусов для роли
        """
        transitions_map = {
            UserRole.WAREHOUSE_KEEPER: {
                MaterialStatus.RECEIVED: [MaterialStatus.IN_INSPECTION, MaterialStatus.QUARANTINE],
                MaterialStatus.QUARANTINE: [MaterialStatus.IN_INSPECTION, MaterialStatus.REJECTED]
            },
            UserRole.QUALITY_CONTROL: {
                MaterialStatus.RECEIVED: [MaterialStatus.IN_INSPECTION],
                MaterialStatus.IN_INSPECTION: [MaterialStatus.LAB_TESTING, MaterialStatus.APPROVED,
                                               MaterialStatus.REJECTED],
                MaterialStatus.LAB_TESTING: [MaterialStatus.APPROVED, MaterialStatus.REJECTED]
            },
            UserRole.LAB_DESTRUCTIVE: {
                MaterialStatus.LAB_TESTING: [MaterialStatus.APPROVED, MaterialStatus.REJECTED]
            },
            UserRole.LAB_NON_DESTRUCTIVE: {
                MaterialStatus.LAB_TESTING: [MaterialStatus.APPROVED, MaterialStatus.REJECTED]
            },
            UserRole.PRODUCTION: {
                MaterialStatus.APPROVED: [MaterialStatus.IN_PRODUCTION],
                MaterialStatus.IN_PRODUCTION: [MaterialStatus.CONSUMED]
            },
            UserRole.ADMINISTRATOR: {
                # Администратор может делать любые переходы
                status: [s for s in MaterialStatus if s != status]
                for status in MaterialStatus
            }
        }

        role_transitions = transitions_map.get(user_role, {})
        return role_transitions.get(current_status, [])