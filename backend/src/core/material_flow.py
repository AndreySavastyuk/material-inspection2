"""
Движок управления потоком материалов с использованием state machine
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from transitions import Machine
from loguru import logger
import asyncio
import json

from src.models.material import Material, MaterialStatus
from src.models.workflow import WorkflowState, WorkflowTemplate, WorkflowRule


class MaterialFlowEngine:
    """
    Движок для управления состояниями материалов
    """

    # Определение состояний
    states = [
        {'name': 'received', 'on_enter': 'log_state_change'},
        {'name': 'quarantine', 'on_enter': ['log_state_change', 'start_quarantine_timer']},
        {'name': 'testing', 'on_enter': 'log_state_change'},
        {'name': 'approved', 'on_enter': ['log_state_change', 'notify_production']},
        {'name': 'rejected', 'on_enter': ['log_state_change', 'notify_supplier']},
        {'name': 'released', 'on_enter': 'log_state_change'}
    ]

    # Определение переходов
    transitions = [
        # Из состояния "received"
        {
            'trigger': 'to_quarantine',
            'source': 'received',
            'dest': 'quarantine',
            'conditions': 'can_quarantine'
        },
        {
            'trigger': 'to_testing',
            'source': 'received',
            'dest': 'testing',
            'conditions': 'can_start_testing'
        },
        {
            'trigger': 'quick_approve',
            'source': 'received',
            'dest': 'approved',
            'conditions': 'is_trusted_supplier'
        },

        # Из карантина
        {
            'trigger': 'end_quarantine',
            'source': 'quarantine',
            'dest': 'testing',
            'conditions': 'quarantine_period_passed'
        },

        # Из тестирования
        {
            'trigger': 'approve',
            'source': 'testing',
            'dest': 'approved',
            'conditions': 'all_tests_passed'
        },
        {
            'trigger': 'reject',
            'source': 'testing',
            'dest': 'rejected',
            'conditions': 'tests_failed'
        },

        # Из approved в производство
        {
            'trigger': 'release',
            'source': 'approved',
            'dest': 'released',
            'conditions': 'can_release'
        },

        # Возврат на повторное тестирование
        {
            'trigger': 'retest',
            'source': ['rejected', 'approved'],
            'dest': 'testing'
        },

        # Экстренная отмена из любого состояния
        {
            'trigger': 'emergency_reject',
            'source': '*',
            'dest': 'rejected',
            'unless': 'is_released'
        }
    ]

    def __init__(self, material: Material, template: Optional[WorkflowTemplate] = None):
        """
        Инициализация движка для конкретного материала

        Args:
            material: Объект материала
            template: Опциональный шаблон workflow
        """
        self.material = material
        self.template = template
        self.metadata: Dict[str, Any] = {}
        self.history: List[Dict] = []

        # Инициализация state machine
        self.machine = Machine(
            model=self,
            states=self.states,
            transitions=self.transitions,
            initial=material.status.value if material.status else 'received',
            send_event=True,
            auto_transitions=False,
            ignore_invalid_triggers=True
        )

        # Загрузка правил из шаблона
        if template:
            self.load_template_rules(template)

    def load_template_rules(self, template: WorkflowTemplate):
        """
        Загрузка правил из шаблона workflow
        """
        if template.transitions:
            template_data = template.transitions

            # Добавление дополнительных переходов из шаблона
            for transition in template_data.get('transitions', []):
                self.machine.add_transition(
                    trigger=f"template_{transition.get('from')}_{transition.get('to')}",
                    source=transition.get('from'),
                    dest=transition.get('to'),
                    conditions=transition.get('condition')
                )

    # Условия для переходов
    def can_quarantine(self, event):
        """Проверка возможности отправки в карантин"""
        # Проверяем, требуется ли карантин для данного типа материала
        return self.material.metadata.get('requires_quarantine', False)

    def can_start_testing(self, event):
        """Проверка возможности начала тестирования"""
        # Проверяем наличие необходимых документов
        has_certificate = bool(self.material.supplier_certificate_number)
        return has_certificate

    def is_trusted_supplier(self, event):
        """Проверка, является ли поставщик доверенным"""
        trusted_suppliers = self.metadata.get('trusted_suppliers', [])
        return self.material.supplier in trusted_suppliers

    def quarantine_period_passed(self, event):
        """Проверка окончания карантинного периода"""
        if 'quarantine_start' in self.metadata:
            quarantine_start = self.metadata['quarantine_start']
            quarantine_days = self.metadata.get('quarantine_days', 3)
            return (datetime.now() - quarantine_start).days >= quarantine_days
        return False

    def all_tests_passed(self, event):
        """Проверка прохождения всех тестов"""
        # Получаем результаты тестов из связанной таблицы
        if hasattr(self.material, 'test_results'):
            test_results = self.material.test_results
            if not test_results:
                return False
            return all(result.pass_fail == 'PASS' for result in test_results)
        return False

    def tests_failed(self, event):
        """Проверка провала тестов"""
        if hasattr(self.material, 'test_results'):
            test_results = self.material.test_results
            return any(result.pass_fail == 'FAIL' for result in test_results)
        return False

    def can_release(self, event):
        """Проверка возможности выпуска в производство"""
        # Проверяем наличие запроса от производства
        return self.metadata.get('production_request', False)

    def is_released(self, event):
        """Проверка, выпущен ли материал в производство"""
        return self.state == 'released'

    # Действия при входе в состояния
    def log_state_change(self, event):
        """Логирование изменения состояния"""
        logger.info(f"Material {self.material.material_code}: {event.transition.source} -> {event.transition.dest}")

        # Добавление в историю
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'from_state': event.transition.source,
            'to_state': event.transition.dest,
            'trigger': event.event.name,
            'user': event.kwargs.get('user_id'),
            'notes': event.kwargs.get('notes')
        })

    def start_quarantine_timer(self, event):
        """Запуск таймера карантина"""
        self.metadata['quarantine_start'] = datetime.now()
        self.metadata['quarantine_days'] = event.kwargs.get('quarantine_days', 3)
        logger.info(f"Quarantine started for {self.metadata['quarantine_days']} days")

    def notify_production(self, event):
        """Уведомление производства об одобрении материала"""
        logger.info(f"Notifying production: Material {self.material.material_code} approved")
        # Здесь будет интеграция с системой уведомлений

    def notify_supplier(self, event):
        """Уведомление поставщика об отклонении материала"""
        logger.info(f"Notifying supplier: Material {self.material.material_code} rejected")
        # Здесь будет интеграция с системой уведомлений

    async def process_auto_transitions(self):
        """
        Обработка автоматических переходов
        """
        # Проверка условий для автоматических переходов
        if self.state == 'quarantine' and self.quarantine_period_passed(None):
            self.end_quarantine()
            return True

        return False

    def get_available_transitions(self) -> List[str]:
        """
        Получение списка доступных переходов из текущего состояния
        """
        return [t for t in self.machine.get_triggers(self.state)]

    def get_state_info(self) -> Dict:
        """
        Получение информации о текущем состоянии
        """
        return {
            'current_state': self.state,
            'available_transitions': self.get_available_transitions(),
            'metadata': self.metadata,
            'history': self.history[-5:] if self.history else []  # Последние 5 записей
        }


class WorkflowOrchestrator:
    """
    Оркестратор для управления множественными workflow
    """

    def __init__(self):
        self.engines: Dict[str, MaterialFlowEngine] = {}
        self.templates: Dict[str, WorkflowTemplate] = {}

    def register_material(self, material: Material, template_name: Optional[str] = None) -> MaterialFlowEngine:
        """
        Регистрация материала в системе workflow
        """
        template = self.templates.get(template_name) if template_name else None
        engine = MaterialFlowEngine(material, template)
        self.engines[str(material.id)] = engine
        return engine

    def get_engine(self, material_id: str) -> Optional[MaterialFlowEngine]:
        """
        Получение движка для материала
        """
        return self.engines.get(material_id)

    async def process_all_auto_transitions(self):
        """
        Обработка автоматических переходов для всех материалов
        """
        results = []
        for material_id, engine in self.engines.items():
            try:
                changed = await engine.process_auto_transitions()
                if changed:
                    results.append(material_id)
            except Exception as e:
                logger.error(f"Error processing auto transitions for {material_id}: {e}")

        return results

    def load_template(self, template: WorkflowTemplate):
        """
        Загрузка шаблона workflow
        """
        self.templates[template.name] = template
        logger.info(f"Loaded workflow template: {template.name}")


# Глобальный экземпляр оркестратора
workflow_orchestrator = WorkflowOrchestrator()