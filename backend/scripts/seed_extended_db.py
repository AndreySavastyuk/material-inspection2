#!/usr/bin/env python3
"""
Расширенный скрипт для заполнения базы данных тестовыми данными
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import AsyncSessionLocal
from src.models.material import Material, MaterialStatus, MaterialType
from src.models.user import User, UserRole
from src.models.certificate import TestResult, TestType, TestCategory, Certificate
from src.models.workflow import WorkflowState

# Расширенные тестовые данные
MATERIAL_NAMES = {
    MaterialType.STEEL: [
        "Лист стальной горячекатаный",
        "Лист стальной холоднокатаный",
        "Уголок равнополочный",
        "Уголок неравнополочный",
        "Швеллер горячекатаный",
        "Балка двутавровая",
        "Труба стальная электросварная",
        "Труба стальная бесшовная",
        "Арматура А500С",
        "Арматура А400"
    ],
    MaterialType.STAINLESS_STEEL: [
        "Лист нержавеющий AISI 304",
        "Лист нержавеющий AISI 316",
        "Труба нержавеющая AISI 304",
        "Проволока нержавеющая",
        "Уголок нержавеющий"
    ],
    MaterialType.ALUMINUM: [
        "Лист алюминиевый АМг3",
        "Профиль алюминиевый",
        "Труба алюминиевая",
        "Проволока алюминиевая",
        "Уголок алюминиевый"
    ],
    MaterialType.COPPER: [
        "Лист медный М1",
        "Труба медная",
        "Проволока медная",
        "Шина медная",
        "Пруток медный"
    ],
    MaterialType.BRASS: [
        "Лист латунный Л63",
        "Труба латунная",
        "Проволока латунная",
        "Пруток латунный",
        "Профиль латунный"
    ],
    MaterialType.CARBON_STEEL: [
        "Лист углеродистый Ст3",
        "Профиль углеродистый",
        "Труба углеродистая",
        "Арматура углеродистая",
        "Проволока углеродистая"
    ],
    MaterialType.ALLOY_STEEL: [
        "Лист легированный 09Г2С",
        "Профиль легированный",
        "Труба легированная",
        "Арматура легированная",
        "Проволока легированная"
    ],
    MaterialType.OTHER: [
        "Материал специальный",
        "Сплав специальный",
        "Композитный материал",
        "Биметаллический материал",
        "Материал экспериментальный"
    ]
}

GRADES = [
    "Ст3", "Ст3сп", "Ст3пс", "09Г2С", "10ХСНД", "15ХСНД",
    "20", "35", "45", "40Х", "30ХГСА", "65Г",
    "12Х18Н10Т", "08Х18Н10", "AISI 304", "AISI 316", "AISI 321",
    "АМг2", "АМг3", "АМг5", "АД31", "Д16Т",
    "Л63", "Л68", "ЛС59-1", "М1", "М2", "М3"
]

STANDARDS = [
    "ГОСТ 19903-2015", "ГОСТ 19904-90", "ГОСТ 14637-89",
    "ГОСТ 8509-93", "ГОСТ 8510-86", "ГОСТ 8240-97",
    "ГОСТ 26020-83", "ГОСТ 10704-91", "ГОСТ 8732-78",
    "ГОСТ 8734-75", "ГОСТ 5781-82", "ГОСТ 34028-2016",
    "ГОСТ 380-2005", "ГОСТ 1050-2013", "ГОСТ 4543-2016",
    "ТУ 14-1-5521-2008", "ТУ 14-3-1128-2000"
]

SUPPLIERS = [
    {"name": "ООО 'МеталлСервис'", "city": "Москва", "trusted": True},
    {"name": "АО 'СтальИнвест'", "city": "Челябинск", "trusted": True},
    {"name": "ООО 'ПромМеталл'", "city": "Екатеринбург", "trusted": False},
    {"name": "ПАО 'Северсталь'", "city": "Череповец", "trusted": True},
    {"name": "ООО 'МеталлоТорг'", "city": "Санкт-Петербург", "trusted": False},
    {"name": "АО 'НЛМК'", "city": "Липецк", "trusted": True},
    {"name": "ООО 'УралМет'", "city": "Нижний Тагил", "trusted": False},
    {"name": "ПАО 'ММК'", "city": "Магнитогорск", "trusted": True},
    {"name": "ООО 'СибирьМеталл'", "city": "Новосибирск", "trusted": False},
    {"name": "АО 'Мечел'", "city": "Челябинск", "trusted": True}
]

DIMENSIONS = {
    MaterialType.STEEL: [
        "3x1250x2500", "4x1500x3000", "5x1500x6000", "6x2000x6000",
        "50x50x5", "63x63x6", "75x75x8", "100x100x10",
        "57x3.5", "76x3.5", "89x4", "108x4", "Ø6", "Ø8", "Ø10", "Ø12"
    ],
    MaterialType.STAINLESS_STEEL: [
        "3x1250x2500", "4x1500x3000", "50x50x5", "63x63x6",
        "57x3.5", "76x3.5", "Ø1.2", "Ø1.6", "Ø2.0"
    ],
    MaterialType.ALUMINUM: [
        "2x1250x2500", "3x1500x3000", "40x40x3", "50x50x4",
        "25x25", "30x30", "Ø1.0", "Ø1.5", "Ø2.0"
    ],
    MaterialType.COPPER: [
        "1x1000x2000", "2x1250x2500", "20x20", "25x25",
        "15x15", "20x20", "Ø0.8", "Ø1.0", "Ø1.2"
    ],
    MaterialType.BRASS: [
        "1x1000x2000", "2x1250x2500", "15x15", "20x20",
        "10x10", "15x15", "Ø0.5", "Ø0.8", "Ø1.0"
    ],
    MaterialType.CARBON_STEEL: [
        "5x1500x6000", "8x2000x6000", "60x60x6", "75x75x8",
        "89x4", "108x4", "Ø8", "Ø10", "Ø12"
    ],
    MaterialType.ALLOY_STEEL: [
        "10x2000x6000", "12x2000x6000", "80x80x8", "100x100x10",
        "114x4.5", "159x4.5", "Ø10", "Ø12", "Ø16"
    ],
    MaterialType.OTHER: [
        "Стандартный", "По заказу", "Специальный",
        "Нестандартный", "Экспериментальный"
    ]
}

STORAGE_LOCATIONS = [
    "Склад 1 - Зона А - Ряд 1", "Склад 1 - Зона А - Ряд 2",
    "Склад 1 - Зона Б - Ряд 1", "Склад 1 - Зона Б - Ряд 2",
    "Склад 2 - Зона А - Ряд 1", "Склад 2 - Зона А - Ряд 2",
    "Склад 2 - Зона Б - Ряд 1", "Склад 2 - Зона Б - Ряд 2",
    "Карантинная зона - Секция 1", "Карантинная зона - Секция 2",
    "Зона временного хранения", "Открытая площадка - Сектор А"
]


def generate_random_notes(status: MaterialStatus, trusted_supplier: bool) -> str:
    """Генерация случайных примечаний в зависимости от статуса"""
    notes_templates = {
        MaterialStatus.RECEIVED: [
            "Материал поступил в полном объеме",
            "Требуется дополнительная проверка документации",
            "Визуальный осмотр без замечаний",
            "Упаковка частично повреждена, материал не пострадал"
        ],
        MaterialStatus.QUARANTINE: [
            "Помещен в карантин до получения результатов испытаний",
            "Карантин по требованию ОТК",
            "Ожидание результатов входного контроля",
            "Новый поставщик, требуется полная проверка"
        ],
        MaterialStatus.TESTING: [
            "Образцы переданы в лабораторию",
            "Проводятся механические испытания",
            "Химический анализ в процессе",
            "Ожидание результатов разрушающего контроля"
        ],
        MaterialStatus.APPROVED: [
            "Все испытания пройдены успешно",
            "Соответствует требованиям ГОСТ",
            "Одобрено для использования в производстве",
            "Качество подтверждено, можно выдавать"
        ],
        MaterialStatus.RELEASED: [
            "Выдано в производство по заявке",
            "Передано в цех №1",
            "Использовано для заказа №12345",
            "Частичная выдача, остаток на складе"
        ],
        MaterialStatus.REJECTED: [
            "Не соответствует химическому составу",
            "Механические свойства ниже требуемых",
            "Обнаружены критические дефекты",
            "Возврат поставщику"
        ]
    }

    base_note = random.choice(notes_templates.get(status, ["Стандартная приемка"]))

    if not trusted_supplier and status in [MaterialStatus.RECEIVED, MaterialStatus.QUARANTINE]:
        base_note += ". Требуется усиленный контроль (новый поставщик)"

    return base_note


def generate_special_requirements(mat_type: MaterialType) -> str:
    """Генерация специальных требований для хранения"""
    requirements = {
        MaterialType.STEEL: "Хранить горизонтально на стеллажах. Избегать прямого контакта с влагой.",
        MaterialType.STAINLESS_STEEL: "Хранить в сухом помещении. Избегать контакта с углеродистой сталью.",
        MaterialType.ALUMINUM: "Хранить на подкладках. Обеспечить вентиляцию между рядами.",
        MaterialType.COPPER: "Хранить в сухом помещении. Защитить от окисления.",
        MaterialType.BRASS: "Хранить в сухом помещении. Избегать механических повреждений.",
        MaterialType.CARBON_STEEL: "Хранить на пирамидах с ограничителями. Защитить торцы от загрязнения.",
        MaterialType.ALLOY_STEEL: "Хранить в бухтах вертикально. Защитить от механических повреждений.",
        MaterialType.OTHER: "Хранить на открытой площадке. Обеспечить отвод воды."
    }
    return requirements.get(mat_type, "Стандартные условия хранения")


def generate_status_dates(received_date: datetime, current_status: MaterialStatus) -> dict:
    """Генерация дат изменения статусов"""
    dates = {"received": received_date.isoformat()}

    if current_status == MaterialStatus.QUARANTINE:
        dates["quarantine"] = (received_date + timedelta(hours=random.randint(1, 24))).isoformat()
    elif current_status == MaterialStatus.TESTING:
        dates["quarantine"] = (received_date + timedelta(hours=random.randint(1, 24))).isoformat()
        dates["testing"] = (received_date + timedelta(days=random.randint(1, 3))).isoformat()
    elif current_status == MaterialStatus.APPROVED:
        dates["quarantine"] = (received_date + timedelta(hours=random.randint(1, 24))).isoformat()
        dates["testing"] = (received_date + timedelta(days=random.randint(1, 3))).isoformat()
        dates["approved"] = (received_date + timedelta(days=random.randint(3, 7))).isoformat()
    elif current_status == MaterialStatus.RELEASED:
        dates["quarantine"] = (received_date + timedelta(hours=random.randint(1, 24))).isoformat()
        dates["testing"] = (received_date + timedelta(days=random.randint(1, 3))).isoformat()
        dates["approved"] = (received_date + timedelta(days=random.randint(3, 7))).isoformat()
        dates["released"] = (received_date + timedelta(days=random.randint(7, 30))).isoformat()
    elif current_status == MaterialStatus.REJECTED:
        dates["testing"] = (received_date + timedelta(days=random.randint(1, 3))).isoformat()
        dates["rejected"] = (received_date + timedelta(days=random.randint(3, 5))).isoformat()

    return dates


async def create_extended_materials(session: AsyncSession, users: List[User]) -> List[Material]:
    """Создание расширенного набора материалов"""
    print("Creating extended materials dataset...")

    materials = []
    material_counter = 1

    # Создаем материалы для каждого типа
    for mat_type in MaterialType:
        material_names = MATERIAL_NAMES.get(mat_type, ["Материал"])
        dimensions_list = DIMENSIONS.get(mat_type, ["Стандартный"])

        # Создаем по несколько материалов каждого наименования
        for name in material_names:
            # Создаем 2-3 варианта каждого материала с разными параметрами
            for variant in range(random.randint(2, 3)):
                # Определяем статус материала
                status_weights = {
                    MaterialStatus.RECEIVED: 0.15,
                    MaterialStatus.QUARANTINE: 0.10,
                    MaterialStatus.TESTING: 0.15,
                    MaterialStatus.APPROVED: 0.35,
                    MaterialStatus.RELEASED: 0.20,
                    MaterialStatus.REJECTED: 0.05
                }
                status = random.choices(
                    list(status_weights.keys()),
                    weights=list(status_weights.values())
                )[0]

                # Генерируем дату поступления
                days_ago = random.randint(0, 180)
                received_date = datetime.now() - timedelta(days=days_ago)

                # Выбираем поставщика
                supplier = random.choice(SUPPLIERS)

                # Генерируем код материала
                year = received_date.year
                material_code = f"MAT-{year}-{str(material_counter).zfill(5)}"
                material_counter += 1

                # Создаем материал
                import time
                timestamp = int(time.time() * 1000) % 100000  # Последние 5 цифр timestamp
                material_data = {
                    "batch_number": f"BATCH-{received_date.strftime('%Y%m%d')}-{timestamp}-{random.randint(1000, 9999)}",
                    "material_type": mat_type.value,
                    "grade": random.choice(GRADES) if random.random() > 0.3 else None,
                    "specification": random.choice(STANDARDS) if random.random() > 0.2 else None,
                    "quantity": round(random.uniform(10, 5000), 2),
                    "unit": "кг" if mat_type in [MaterialType.STEEL, MaterialType.CARBON_STEEL, MaterialType.ALLOY_STEEL] else "м" if "труба" in name.lower() else "шт",
                    "supplier": supplier["name"],
                    "supplier_certificate": f"СК-{received_date.year}-{random.randint(1000, 9999)}",
                    "status": status.value,
                    "location": random.choice(STORAGE_LOCATIONS),
                    "received_date": received_date,
                    "created_by": random.choice(users).id,
                    "notes": generate_random_notes(status, supplier["trusted"]),
                    "material_metadata": {
                        "material_code": f"MAT-{year}-{str(material_counter).zfill(5)}",
                        "dimensions": random.choice(dimensions_list),
                        "heat_number": f"П-{random.randint(100000, 999999)}" if mat_type in [MaterialType.STEEL, MaterialType.CARBON_STEEL, MaterialType.ALLOY_STEEL] else None,
                        "invoice_number": f"INV-{received_date.year}-{random.randint(10000, 99999)}",
                        "supplier_city": supplier["city"],
                        "trusted_supplier": supplier["trusted"],
                        "requires_quarantine": not supplier["trusted"] and random.random() > 0.5,
                        "urgent": random.random() > 0.8,
                        "temperature_storage": "15-25°C",
                        "humidity_requirements": "<60%",
                        "special_requirements": generate_special_requirements(mat_type),
                        "contract_number": f"К-{received_date.year}-{random.randint(100, 999)}",
                        "delivery_method": random.choice(["Авто", "Ж/Д", "Авиа", "Самовывоз"]),
                        "customs_declaration": f"ГТД-{random.randint(1000000, 9999999)}" if random.random() > 0.7 else None
                    }
                }

                # Добавляем временные метки для разных статусов
                if status != MaterialStatus.RECEIVED:
                    material_data["material_metadata"]["status_dates"] = generate_status_dates(received_date, status)

                material = Material(**material_data)
                session.add(material)
                materials.append(material)

    await session.commit()
    print(f"[OK] Created {len(materials)} materials")
    return materials


async def create_extended_test_results(session: AsyncSession, materials: List[Material], users: List[User]):
    """Создание расширенных результатов испытаний"""
    print("Creating extended test results...")

    test_results = []
    lab_users = [u for u in users if u.role in [UserRole.LAB_DESTRUCTIVE, UserRole.LAB_NON_DESTRUCTIVE, UserRole.QUALITY_CONTROL]]

    for material in materials:
        # Создаем тесты только для материалов в соответствующих статусах
        if material.status in [MaterialStatus.TESTING.value, MaterialStatus.APPROVED.value, MaterialStatus.RELEASED.value]:
            # Химический анализ (для металлов)
            if material.material_type in [MaterialType.STEEL.value, MaterialType.CARBON_STEEL.value, MaterialType.ALLOY_STEEL.value, MaterialType.STAINLESS_STEEL.value]:
                chem_results = generate_chemical_composition(material.grade)
                chem_test = TestResult(
                    material_id=material.id,
                    test_type=TestType.CHEMICAL,
                    test_category=TestCategory.DESTRUCTIVE,
                    tested_by=random.choice(lab_users).id,
                    tested_at=material.received_date + timedelta(days=random.randint(1, 3)),
                    pass_fail="PASS" if material.status != MaterialStatus.REJECTED.value else "FAIL",
                    numeric_results=chem_results,
                    notes=f"Химический состав {'соответствует' if material.status != MaterialStatus.REJECTED.value else 'не соответствует'} требованиям"
                )
                session.add(chem_test)
                test_results.append(chem_test)

            # Механические испытания
            if material.material_type in [MaterialType.STEEL.value, MaterialType.CARBON_STEEL.value, MaterialType.ALLOY_STEEL.value]:
                mech_results = generate_mechanical_properties(material.material_type)
                mech_test = TestResult(
                    material_id=material.id,
                    test_type=TestType.TENSILE,
                    test_category=TestCategory.DESTRUCTIVE,
                    tested_by=random.choice(lab_users).id,
                    tested_at=material.received_date + timedelta(days=random.randint(2, 4)),
                    pass_fail="PASS" if material.status != MaterialStatus.REJECTED.value else "FAIL",
                    numeric_results=mech_results,
                    notes="Механические свойства проверены"
                )
                session.add(mech_test)
                test_results.append(mech_test)

            # Измерение твердости
            if random.random() > 0.5:
                hardness_test = TestResult(
                    material_id=material.id,
                    test_type=TestType.HARDNESS,
                    test_category=TestCategory.NON_DESTRUCTIVE,
                    tested_by=random.choice(lab_users).id,
                    tested_at=material.received_date + timedelta(days=random.randint(1, 2)),
                    pass_fail="PASS",
                    numeric_results={
                        "HB": random.randint(150, 350),
                        "measurement_points": 5,
                        "average": random.randint(200, 300),
                        "units": "HB"
                    },
                    notes="Измерение твердости по Бринеллю"
                )
                session.add(hardness_test)
                test_results.append(hardness_test)

            # Визуальный контроль
            visual_test = TestResult(
                material_id=material.id,
                test_type=TestType.VISUAL,
                test_category=TestCategory.NON_DESTRUCTIVE,
                tested_by=random.choice(lab_users).id,
                tested_at=material.received_date + timedelta(hours=random.randint(1, 8)),
                pass_fail="PASS" if material.status != MaterialStatus.REJECTED.value else "FAIL",
                notes="Визуальный осмотр: " + random.choice([
                    "Поверхность без видимых дефектов",
                    "Обнаружены незначительные царапины, не влияющие на качество",
                    "Геометрические размеры соответствуют заявленным",
                    "Маркировка четкая, соответствует документации"
                ]) if material.status != MaterialStatus.REJECTED.value else "Обнаружены критические дефекты поверхности. Визуальный контроль выполнен согласно ГОСТ"
            )
            session.add(visual_test)
            test_results.append(visual_test)

            # Ультразвуковой контроль (для толстых материалов)
            if material.material_type == MaterialType.STEEL.value and random.random() > 0.6:
                ut_test = TestResult(
                    material_id=material.id,
                    test_type=TestType.ULTRASONIC,
                    test_category=TestCategory.NON_DESTRUCTIVE,
                    tested_by=random.choice(lab_users).id,
                    tested_at=material.received_date + timedelta(days=random.randint(1, 3)),
                    pass_fail="PASS",
                    notes="УЗК: Внутренние дефекты не обнаружены. Контроль выполнен на установке УД2-70"
                )
                session.add(ut_test)
                test_results.append(ut_test)

    await session.commit()
    print(f"[OK] Created {len(test_results)} test results")
    return test_results


async def create_certificates(session: AsyncSession, materials: List[Material], users: List[User]):
    """Создание сертификатов для одобренных материалов"""
    print("Creating certificates...")

    certificates = []
    qc_users = [u for u in users if u.role == UserRole.QUALITY_CONTROL]

    for material in materials:
        if material.status in [MaterialStatus.APPROVED.value, MaterialStatus.RELEASED.value]:
            # Получаем название материала из metadata
            material_name = material.material_metadata.get('material_code', f'Материал {material.batch_number}')

            cert = Certificate(
                certificate_number=f"CERT-{datetime.now().year}-{random.randint(10000, 99999)}",
                material_id=material.id,
                certificate_type="quality",
                issued_date=material.received_date + timedelta(days=random.randint(3, 7)),
                valid_until=material.received_date + timedelta(days=365),
                issued_by=random.choice(qc_users).id,
                summary=f"Материал {material_name} соответствует требованиям {material.specification or 'технических условий'}",
                conclusions="Материал пригоден для использования в производстве",
                recommendations="Соблюдать условия хранения согласно требованиям",
                certificate_metadata={
                    "test_protocol_numbers": [f"ПИ-{random.randint(1000, 9999)}" for _ in range(random.randint(1, 3))],
                    "laboratory": "Центральная заводская лаборатория",
                    "accreditation": "РОСС RU.0001.21МТ52"
                }
            )
            session.add(cert)
            certificates.append(cert)

    await session.commit()
    print(f"[OK] Created {len(certificates)} certificates")
    return certificates


def generate_chemical_composition(grade: str = None) -> dict:
    """Генерация химического состава в зависимости от марки стали"""
    if grade and grade.startswith("09Г2С"):
        return {
            "C": round(random.uniform(0.09, 0.12), 3),
            "Mn": round(random.uniform(1.3, 1.7), 3),
            "Si": round(random.uniform(0.5, 0.8), 3),
            "P": round(random.uniform(0.01, 0.035), 3),
            "S": round(random.uniform(0.01, 0.04), 3),
            "Cr": round(random.uniform(0.0, 0.3), 3),
            "Ni": round(random.uniform(0.0, 0.3), 3),
            "Cu": round(random.uniform(0.0, 0.3), 3),
            "units": "%"
        }
    elif grade and "Х18Н10" in grade:
        return {
            "C": round(random.uniform(0.08, 0.12), 3),
            "Cr": round(random.uniform(17.0, 19.0), 3),
            "Ni": round(random.uniform(9.0, 11.0), 3),
            "Mn": round(random.uniform(1.0, 2.0), 3),
            "Si": round(random.uniform(0.0, 0.8), 3),
            "P": round(random.uniform(0.01, 0.035), 3),
            "S": round(random.uniform(0.01, 0.02), 3),
            "Ti": round(random.uniform(0.4, 0.7), 3) if "Т" in grade else 0,
            "units": "%"
        }
    else:
        # Обычная углеродистая сталь
        return {
            "C": round(random.uniform(0.14, 0.22), 3),
            "Mn": round(random.uniform(0.4, 0.65), 3),
            "Si": round(random.uniform(0.15, 0.35), 3),
            "P": round(random.uniform(0.01, 0.04), 3),
            "S": round(random.uniform(0.01, 0.05), 3),
            "Cr": round(random.uniform(0.0, 0.25), 3),
            "Ni": round(random.uniform(0.0, 0.25), 3),
            "Cu": round(random.uniform(0.0, 0.25), 3),
            "units": "%"
        }


def generate_mechanical_properties(mat_type: str) -> dict:
    """Генерация механических свойств"""
    # Для арматуры и высокопрочных сталей
    if "арматура" in str(mat_type).lower() or mat_type in [MaterialType.ALLOY_STEEL.value, MaterialType.CARBON_STEEL.value]:
        return {
            "yield_strength": random.randint(400, 600),
            "tensile_strength": random.randint(500, 700),
            "elongation": random.randint(14, 25),
            "units": {"yield_strength": "МПа", "tensile_strength": "МПа", "elongation": "%"}
        }
    else:
        return {
            "yield_strength": random.randint(235, 355),
            "tensile_strength": random.randint(360, 510),
            "elongation": random.randint(20, 30),
            "impact_strength": random.randint(27, 40),
            "units": {
                "yield_strength": "МПа",
                "tensile_strength": "МПа",
                "elongation": "%",
                "impact_strength": "Дж/см²"
            }
        }


async def create_workflow_history(session: AsyncSession, materials: List[Material], users: List[User]):
    """Создание истории workflow для материалов"""
    print("Creating workflow history...")

    workflow_states = []

    for material in materials:
        # Создаем историю изменений статуса
        if material.status != MaterialStatus.RECEIVED.value:
            # Начальное состояние - получен
            state = WorkflowState(
                material_id=material.id,
                state_name=MaterialStatus.RECEIVED.value,
                previous_state=None,
                changed_by=material.created_by,
                changed_at=material.received_date,
                reason="Материал поступил на склад",
                notes="Первичная приемка"
            )
            session.add(state)
            workflow_states.append(state)

            # Промежуточные состояния
            if material.status in [MaterialStatus.TESTING.value, MaterialStatus.APPROVED.value, MaterialStatus.RELEASED.value]:
                # Карантин (если требовался)
                if material.material_metadata.get("requires_quarantine"):
                    state = WorkflowState(
                        material_id=material.id,
                        state_name=MaterialStatus.QUARANTINE.value,
                        previous_state=MaterialStatus.RECEIVED.value,
                        changed_by=random.choice(users).id,
                        changed_at=material.received_date + timedelta(hours=random.randint(1, 24)),
                        reason="Требуется карантинное хранение",
                        notes="Новый поставщик"
                    )
                    session.add(state)
                    workflow_states.append(state)

                # Тестирование
                if material.status != MaterialStatus.QUARANTINE.value:
                    state = WorkflowState(
                        material_id=material.id,
                        state_name=MaterialStatus.TESTING.value,
                        previous_state=MaterialStatus.QUARANTINE.value if material.material_metadata.get(
                            "requires_quarantine") else MaterialStatus.RECEIVED.value,
                        changed_by=random.choice([u for u in users if u.role == UserRole.QUALITY_CONTROL]).id,
                        changed_at=material.received_date + timedelta(days=random.randint(1, 3)),
                        reason="Направлен на испытания",
                        notes="Полный комплекс испытаний"
                    )
                    session.add(state)
                    workflow_states.append(state)

            # Финальное состояние
            if material.status == MaterialStatus.APPROVED.value:
                state = WorkflowState(
                    material_id=material.id,
                    state_name=MaterialStatus.APPROVED.value,
                    previous_state=MaterialStatus.TESTING.value,
                    changed_by=random.choice([u for u in users if u.role == UserRole.QUALITY_CONTROL]).id,
                    changed_at=material.received_date + timedelta(days=random.randint(3, 7)),
                    reason="Все испытания пройдены успешно",
                    notes="Материал соответствует требованиям"
                )
                session.add(state)
                workflow_states.append(state)
            elif material.status == MaterialStatus.RELEASED.value:
                # Сначала одобрение
                state = WorkflowState(
                    material_id=material.id,
                    state_name=MaterialStatus.APPROVED.value,
                    previous_state=MaterialStatus.TESTING.value,
                    changed_by=random.choice([u for u in users if u.role == UserRole.QUALITY_CONTROL]).id,
                    changed_at=material.received_date + timedelta(days=random.randint(3, 7)),
                    reason="Все испытания пройдены успешно",
                    notes="Материал соответствует требованиям"
                )
                session.add(state)
                workflow_states.append(state)

                # Затем выдача
                state = WorkflowState(
                    material_id=material.id,
                    state_name=MaterialStatus.RELEASED.value,
                    previous_state=MaterialStatus.APPROVED.value,
                    changed_by=random.choice(
                        [u for u in users if u.role in [UserRole.WAREHOUSE_KEEPER, UserRole.PRODUCTION]]).id,
                    changed_at=material.received_date + timedelta(days=random.randint(7, 30)),
                    reason="Выдано в производство",
                    notes=f"Заявка №{random.randint(1000, 9999)}"
                )
                session.add(state)
                workflow_states.append(state)
            elif material.status == MaterialStatus.REJECTED.value:
                state = WorkflowState(
                    material_id=material.id,
                    state_name=MaterialStatus.REJECTED.value,
                    previous_state=MaterialStatus.TESTING.value,
                    changed_by=random.choice([u for u in users if u.role == UserRole.QUALITY_CONTROL]).id,
                    changed_at=material.received_date + timedelta(days=random.randint(3, 5)),
                    reason="Не соответствует требованиям",
                    notes="Возврат поставщику"
                )
                session.add(state)
                workflow_states.append(state)

    await session.commit()
    print(f"[OK] Created {len(workflow_states)} workflow states")
    return workflow_states


async def main():
    """Основная функция"""
    print("=" * 50)
    print("Extended Database Seeding Script")
    print("=" * 50)

    async with AsyncSessionLocal() as session:
        try:
            # Получаем существующих пользователей
            from sqlalchemy import select
            result = await session.execute(select(User))
            users = result.scalars().all()

            if not users:
                print("[ERROR] No users found. Please run init_db.py first")
                return

            print(f"[OK] Found {len(users)} users")

            # Создаем расширенный набор материалов
            materials = await create_extended_materials(session, users)

            # Создаем результаты испытаний
            test_results = await create_extended_test_results(session, materials, users)

            # Создаем сертификаты
            certificates = await create_certificates(session, materials, users)

            # Создаем историю workflow
            workflow_states = await create_workflow_history(session, materials, users)

            print("=" * 50)
            print("Extended seeding completed successfully!")
            print(f"Total materials created: {len(materials)}")
            print(f"Total test results: {len(test_results)}")
            print(f"Total certificates: {len(certificates)}")
            print(f"Total workflow states: {len(workflow_states)}")
            print("=" * 50)

        except Exception as e:
            print(f"[ERROR] {str(e)}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())