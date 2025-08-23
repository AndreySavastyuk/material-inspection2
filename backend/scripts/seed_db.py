#!/usr/bin/env python
"""
Seed database with test data
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Добавляем корневую директорию в path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, func
from src.core.database import AsyncSessionLocal, engine, Base
from src.models.material import Material, MaterialStatus, MaterialType
from src.models.user import User, UserRole
from src.models.workflow import WorkflowState, WorkflowTemplate
from src.models.certificate import TestResult, TestType, TestCategory

# Временная функция для хеширования паролей
# Если импорт не работает, используем локальную версию
try:
    from src.core.security import get_password_hash
except ImportError:
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def get_password_hash(password: str) -> str:
        """Получение хеша пароля"""
        return pwd_context.hash(password)


async def create_users(session: AsyncSession):
    """Создание тестовых пользователей"""
    print("Creating users...")

    users_data = [
        {
            "username": "admin",
            "email": "admin@metal.com",
            "full_name": "Администратор Системы",
            "role": UserRole.ADMINISTRATOR,
            "password_hash": get_password_hash("admin123")
        },
        {
            "username": "warehouse",
            "email": "warehouse@metal.com",
            "full_name": "Иванов Иван Иванович",
            "role": UserRole.WAREHOUSE_KEEPER,
            "password_hash": get_password_hash("warehouse123")
        },
        {
            "username": "quality",
            "email": "quality@metal.com",
            "full_name": "Петрова Мария Сергеевна",
            "role": UserRole.QUALITY_CONTROL,
            "password_hash": get_password_hash("quality123")
        },
        {
            "username": "lab_destructive",
            "email": "lab_d@metal.com",
            "full_name": "Сидоров Петр Петрович",
            "role": UserRole.LAB_DESTRUCTIVE,
            "password_hash": get_password_hash("lab123")
        },
        {
            "username": "lab_nondestructive",
            "email": "lab_nd@metal.com",
            "full_name": "Козлова Анна Викторовна",
            "role": UserRole.LAB_NON_DESTRUCTIVE,
            "password_hash": get_password_hash("lab123")
        },
        {
            "username": "production",
            "email": "production@metal.com",
            "full_name": "Николаев Николай Николаевич",
            "role": UserRole.PRODUCTION,
            "password_hash": get_password_hash("production123")
        }
    ]

    users = []
    for user_data in users_data:
        user = User(**user_data)
        session.add(user)
        users.append(user)

    await session.commit()
    print(f"[OK] Created {len(users)} users")
    return users


async def create_materials(session: AsyncSession, users: list):
    """Создание тестовых материалов"""
    print("Creating materials...")

    materials_data = [
        # Листовой прокат
        {
            "batch_number": "MAT-2024-001",
            "material_type": MaterialType.STEEL,
            "grade": "09Г2С",
            "specification": "ГОСТ 19281-2014, 10х1500х6000",
            "quantity": 25.0,
            "unit": "шт",
            "supplier": "ООО МеталлПоставка",
            "supplier_certificate": "СК-2024-1234",
            "status": MaterialStatus.RECEIVED,
            "location": "Склад А, ряд 1",
            "created_by": users[1].id  # warehouse
        },
        {
            "batch_number": "MAT-2024-002",
            "material_type": MaterialType.STEEL,
            "grade": "08пс",
            "specification": "ГОСТ 19904-90, 2х1250х2500",
            "quantity": 50.0,
            "unit": "шт",
            "supplier": "АО СтальТрейд",
            "supplier_certificate": "СТ-2024-5678",
            "status": MaterialStatus.TESTING,
            "location": "Зона ОТК",
            "created_by": users[1].id
        },
        # Трубы
        {
            "batch_number": "MAT-2024-003",
            "material_type": MaterialType.STEEL,
            "grade": "Ст3сп",
            "specification": "ГОСТ 10704-91, 108х4х6000",
            "quantity": 30.0,
            "unit": "шт",
            "supplier": "ООО ТрубПром",
            "supplier_certificate": "ТП-2024-9012",
            "status": MaterialStatus.TESTING,
            "location": "ЦЗЛ",
            "created_by": users[1].id
        },
        # Профиль
        {
            "batch_number": "MAT-2024-004",
            "material_type": MaterialType.STEEL,
            "grade": "09Г2С",
            "specification": "ГОСТ 8509-93, 75х75х6х6000",
            "quantity": 40.0,
            "unit": "шт",
            "supplier": "ООО МеталлПрофиль",
            "supplier_certificate": "МП-2024-3456",
            "status": MaterialStatus.APPROVED,
            "location": "Склад Б, ряд 3",
            "created_by": users[1].id
        },
        # Круг
        {
            "batch_number": "MAT-2024-005",
            "material_type": MaterialType.ALLOY_STEEL,
            "grade": "40Х",
            "specification": "ГОСТ 4543-2016, ф50х3000",
            "quantity": 20.0,
            "unit": "шт",
            "supplier": "ООО СпецСталь",
            "supplier_certificate": "СС-2024-7890",
            "status": MaterialStatus.RELEASED,
            "location": "Цех №2",
            "created_by": users[1].id
        },
        # Проволока
        {
            "batch_number": "MAT-2024-006",
            "material_type": MaterialType.STEEL,
            "grade": "Св-08Г2С",
            "specification": "ГОСТ 2246-70, ф1.2",
            "quantity": 10.0,
            "unit": "кг",
            "supplier": "АО ПроволокаПлюс",
            "supplier_certificate": "ПП-2024-1122",
            "status": MaterialStatus.APPROVED,
            "location": "Склад расходных",
            "created_by": users[1].id
        }
    ]

    materials = []
    for i, mat_data in enumerate(materials_data):
        # Добавляем временные метки
        mat_data["received_date"] = datetime.now() - timedelta(days=random.randint(1, 30))
        mat_data["created_at"] = mat_data["received_date"]

        # Добавляем метаданные
        mat_data["material_metadata"] = {
            "invoice_number": f"INV-2024-{1000 + i}",
            "batch_number": f"BATCH-{random.randint(1000, 9999)}",
            "temperature_storage": "15-25°C",
            "humidity_requirements": "<60%"
        }

        material = Material(**mat_data)
        session.add(material)
        materials.append(material)

    await session.commit()
    print(f"[OK] Created {len(materials)} materials")
    return materials


async def create_test_results(session: AsyncSession, materials: list, users: list):
    """Создание результатов испытаний"""
    print("Creating test results...")

    test_results = []

    # Для материалов в статусе LAB_TESTING и APPROVED
    for material in materials:
        if material.status in [MaterialStatus.TESTING, MaterialStatus.APPROVED, MaterialStatus.RELEASED]:
            # Химический анализ
            chem_test = TestResult(
                material_id=material.id,
                test_type=TestType.CHEMICAL,
                test_category=TestCategory.DESTRUCTIVE,
                tested_by=users[3].id,  # lab_destructive
                tested_at=material.received_date + timedelta(days=1),
                pass_fail="PASS",
                numeric_results={
                    "C": 0.12,
                    "Mn": 1.45,
                    "Si": 0.55,
                    "P": 0.025,
                    "S": 0.020,
                    "Cr": 0.30,
                    "Ni": 0.30,
                    "Cu": 0.30,
                    "units": {"C": "%", "Mn": "%", "Si": "%", "P": "%", "S": "%"}
                },
                notes="Химический состав соответствует требованиям"
            )
            session.add(chem_test)
            test_results.append(chem_test)

            # Механические испытания
            mech_test = TestResult(
                material_id=material.id,
                test_type=TestType.TENSILE,
                test_category=TestCategory.DESTRUCTIVE,
                tested_by=users[3].id,
                tested_at=material.received_date + timedelta(days=2),
                pass_fail="PASS",
                numeric_results={
                    "yield_strength": 345,
                    "tensile_strength": 490,
                    "elongation": 21,
                    "reduction_area": 65,
                    "units": {
                        "yield_strength": "MPa",
                        "tensile_strength": "MPa",
                        "elongation": "%",
                        "reduction_area": "%"
                    }
                },
                notes="Механические свойства в норме"
            )
            session.add(mech_test)
            test_results.append(mech_test)

            # Ультразвуковой контроль для листов и труб
            if material.material_type in [MaterialType.STEEL, MaterialType.ALLOY_STEEL]:
                ut_test = TestResult(
                    material_id=material.id,
                    test_type=TestType.ULTRASONIC,
                    test_category=TestCategory.NON_DESTRUCTIVE,
                    tested_by=users[4].id,  # lab_nondestructive
                    tested_at=material.received_date + timedelta(days=1),
                    pass_fail="PASS",
                    numeric_results={
                        "defects_found": 0,
                        "max_defect_size": 0,
                        "scanned_area": 100,
                        "units": {
                            "max_defect_size": "mm",
                            "scanned_area": "%"
                        }
                    },
                    notes="Дефекты не обнаружены"
                )
                session.add(ut_test)
                test_results.append(ut_test)

    await session.commit()
    print(f"[OK] Created {len(test_results)} test results")
    return test_results


async def create_workflow_templates(session: AsyncSession):
    """Создание шаблонов workflow"""
    print("Creating workflow templates...")

    templates_data = [
        {
            "name": "Стандартный процесс приемки",
            "description": "Полный цикл приемки с контролем качества",
            "is_active": True,
            "transitions": {
                "states": ["received", "testing", "approved", "released"],
                "transitions": [
                    {"from": "received", "to": "testing", "condition": "quality_check_passed"},
                    {"from": "testing", "to": "approved", "condition": "all_tests_passed"},
                    {"from": "approved", "to": "released", "condition": "production_ready"}
                ],
                "auto_transitions": []
            }
        },
        {
            "name": "Упрощенный процесс",
            "description": "Для проверенных поставщиков",
            "is_active": True,
            "transitions": {
                "states": ["received", "approved", "released"],
                "transitions": [
                    {"from": "received", "to": "approved", "condition": "trusted_supplier"},
                    {"from": "approved", "to": "released", "condition": "production_ready"}
                ],
                "auto_transitions": ["trusted_supplier"]
            }
        }
    ]

    templates = []
    for template_data in templates_data:
        template = WorkflowTemplate(**template_data)
        session.add(template)
        templates.append(template)

    await session.commit()
    print(f"[OK] Created {len(templates)} workflow templates")
    return templates


async def main():
    """Основная функция"""
    print("\n" + "=" * 50)
    print("Starting database seeding...")
    print("=" * 50 + "\n")

    try:
        # Пересоздаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSessionLocal() as session:
            # Проверяем, не заполнена ли уже БД
            result = await session.execute(
                select(func.count()).select_from(User)
            )
            existing_users = result.scalar()

            if existing_users > 0:
                print("[WARNING] Database already contains data!")
                response = input("Do you want to clear and reseed? (y/n): ")
                if response.lower() != 'y':
                    print("Aborted.")
                    return

                # Очищаем таблицы
                print("Clearing existing data...")
                await session.execute(text("DELETE FROM test_results"))
                await session.execute(text("DELETE FROM certificates"))
                await session.execute(text("DELETE FROM workflow_states"))
                await session.execute(text("DELETE FROM materials"))
                await session.execute(text("DELETE FROM workflow_templates"))
                await session.execute(text("DELETE FROM users"))
                await session.commit()

            # Создаем данные
            users = await create_users(session)
            materials = await create_materials(session, users)
            test_results = await create_test_results(session, materials, users)
            templates = await create_workflow_templates(session)

            print("\n" + "=" * 50)
            print("[SUCCESS] Database seeding completed successfully!")
            print("=" * 50)

            print("\nSummary:")
            print(f"  • Users: {len(users)}")
            print(f"  • Materials: {len(materials)}")
            print(f"  • Test Results: {len(test_results)}")
            print(f"  • Workflow Templates: {len(templates)}")

            print("\nTest credentials:")
            print("  Admin: admin / admin123")
            print("  Warehouse: warehouse / warehouse123")
            print("  Quality: quality / quality123")
            print("  Lab: lab_destructive / lab123")
            print("  Production: production / production123")

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
