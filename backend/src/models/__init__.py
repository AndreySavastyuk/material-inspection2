"""
Database models initialization
"""

# Импортируем все модели для регистрации в Base.metadata
from src.models.material import Material, MaterialStatus, MaterialType
from src.models.user import User, UserRole
from src.models.workflow import WorkflowState, WorkflowTemplate, WorkflowRule
from src.models.certificate import Certificate, TestResult, TestType, TestCategory

__all__ = [
    'Material',
    'MaterialStatus',
    'MaterialType',
    'User',
    'UserRole',
    'WorkflowState',
    'WorkflowTemplate',
    'WorkflowRule',
    'Certificate',
    'TestResult',
    'TestType',
    'TestCategory'
]