"""
Модель пользователей с полем для пароля
"""
from sqlalchemy import Column, String, DateTime, Boolean, JSON, Enum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from src.core.database import Base


class UserRole(str, enum.Enum):
    """Роли пользователей"""
    WAREHOUSE_KEEPER = "warehouse_keeper"  # Кладовщик
    QUALITY_CONTROL = "quality_control"  # ОТК
    LAB_DESTRUCTIVE = "lab_destructive"  # ЦЗЛ (разрушающий контроль)
    LAB_NON_DESTRUCTIVE = "lab_non_destructive"  # ЦЗЛ (неразрушающий контроль)
    PRODUCTION = "production"  # Производство
    ADMINISTRATOR = "administrator"  # Администратор


class User(Base):
    """
    Модель пользователя
    """
    __tablename__ = "users"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)

    # Поле для хранения хешированного пароля
    password_hash = Column(String(255), nullable=False)

    # Роль и права
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Дополнительная информация
    department = Column(String(100))  # Отдел/подразделение
    position = Column(String(100))  # Должность
    phone = Column(String(20))

    # Настройки и предпочтения
    preferences = Column(JSON, default=dict)

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))

    # Связи
    created_materials = relationship(
        "Material",
        back_populates="creator",
        foreign_keys="Material.created_by"
    )
    updated_materials = relationship(
        "Material",
        back_populates="updater",
        foreign_keys="Material.updated_by"
    )
    workflow_changes = relationship(
        "WorkflowState",
        back_populates="user",
        foreign_keys="WorkflowState.changed_by"
    )
    test_results = relationship(
        "TestResult",
        back_populates="tester",
        foreign_keys="TestResult.tested_by"
    )
    issued_certificates = relationship(
        "Certificate",
        back_populates="issuer",
        foreign_keys="Certificate.issued_by"
    )

    def __repr__(self):
        return f"<User {self.username}: {self.role.value}>"

    @property
    def role_display_name(self) -> str:
        """Отображаемое название роли"""
        role_names = {
            UserRole.WAREHOUSE_KEEPER: "Кладовщик",
            UserRole.QUALITY_CONTROL: "ОТК",
            UserRole.LAB_DESTRUCTIVE: "ЦЗЛ (разрушающий контроль)",
            UserRole.LAB_NON_DESTRUCTIVE: "ЦЗЛ (неразрушающий контроль)",
            UserRole.PRODUCTION: "Производство",
            UserRole.ADMINISTRATOR: "Администратор"
        }
        return role_names.get(self.role, self.role.value)

    def has_permission(self, permission: str) -> bool:
        """
        Проверка наличия разрешения у пользователя
        """
        # Администратор имеет все права
        if self.is_superuser or self.role == UserRole.ADMINISTRATOR:
            return True

        # Права по ролям
        permissions = {
            UserRole.WAREHOUSE_KEEPER: [
                "material.create",
                "material.read",
                "material.update_location",
                "workflow.receive"
            ],
            UserRole.QUALITY_CONTROL: [
                "material.read",
                "material.inspect",
                "workflow.approve",
                "workflow.reject",
                "test.create_visual"
            ],
            UserRole.LAB_DESTRUCTIVE: [
                "material.read",
                "test.create_destructive",
                "test.read",
                "test.update",
                "certificate.create"
            ],
            UserRole.LAB_NON_DESTRUCTIVE: [
                "material.read",
                "test.create_non_destructive",
                "test.read",
                "test.update",
                "certificate.create"
            ],
            UserRole.PRODUCTION: [
                "material.read",
                "material.request",
                "workflow.release"
            ]
        }

        user_permissions = permissions.get(self.role, [])
        return permission in user_permissions

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "id": str(self.id),
            "username": self.username,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role.value if self.role else None,
            "role_display": self.role_display_name,
            "department": self.department,
            "position": self.position,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }