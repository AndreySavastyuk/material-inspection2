"""
Модель состояний workflow
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.core.database import Base


class WorkflowState(Base):
    """
    История состояний материала в workflow
    """
    __tablename__ = "workflow_states"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)

    # Информация о состоянии
    state_name = Column(String(50), nullable=False)
    previous_state = Column(String(50))

    # Кто и когда изменил состояние
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Дополнительная информация
    reason = Column(Text)  # Причина изменения
    notes = Column(Text)  # Примечания
    extra_data = Column(JSON, default=dict)  # Дополнительные данные (было metadata)

    # Связи
    material = relationship("Material", back_populates="workflow_states")
    user = relationship("User", back_populates="workflow_changes")

    def __repr__(self):
        return f"<WorkflowState {self.state_name} for Material {self.material_id}>"


class WorkflowTemplate(Base):
    """
    Шаблоны workflow для разных типов материалов
    """
    __tablename__ = "workflow_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)

    # Тип материала, к которому применяется шаблон
    material_type = Column(String(50))

    # JSON структура с описанием переходов
    transitions = Column(JSON, nullable=False)
    # Пример структуры:
    # {
    #     "states": ["received", "quarantine", "testing", "approved", "released"],
    #     "transitions": [
    #         {"from": "received", "to": "quarantine", "condition": "needs_quarantine"},
    #         {"from": "quarantine", "to": "testing", "condition": "quarantine_period_passed"},
    #         {"from": "testing", "to": "approved", "condition": "all_tests_passed"},
    #         {"from": "approved", "to": "released", "condition": "production_request"}
    #     ],
    #     "auto_transitions": ["quarantine_period_passed"]
    # }

    # Настройки
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)  # Использовать по умолчанию для типа
    priority = Column(Integer, default=0)  # Приоритет при выборе шаблона

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    rules = relationship("WorkflowRule", back_populates="template", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<WorkflowTemplate {self.name}>"


class WorkflowRule(Base):
    """
    Правила автоматических переходов в workflow
    """
    __tablename__ = "workflow_rules"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("workflow_templates.id"), nullable=False)

    # Описание правила
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Условия правила
    from_state = Column(String(50), nullable=False)
    to_state = Column(String(50), nullable=False)

    # Тип правила
    rule_type = Column(String(50), nullable=False)  # time_based, condition_based, approval_based

    # Параметры правила в JSON
    conditions = Column(JSON, nullable=False)
    # Примеры:
    # Для time_based: {"hours": 24, "business_days_only": true}
    # Для condition_based: {"field": "test_results", "operator": "all_passed"}
    # Для approval_based: {"required_roles": ["quality_control"], "min_approvals": 1}

    # Действия при срабатывании
    actions = Column(JSON, default=dict)
    # Пример: {"notify": ["quality_control"], "auto_assign": true}

    # Настройки
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Связи
    template = relationship("WorkflowTemplate", back_populates="rules")

    def __repr__(self):
        return f"<WorkflowRule {self.name}: {self.from_state} -> {self.to_state}>"