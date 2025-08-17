"""
Модели сертификатов и результатов тестирования
"""
from sqlalchemy import Column, String, DateTime, Float, Text, JSON, Enum, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from src.core.database import Base


class TestType(str, enum.Enum):
    """Типы тестов"""
    VISUAL = "visual"  # Визуальный осмотр
    DIMENSIONAL = "dimensional"  # Контроль размеров
    CHEMICAL = "chemical"  # Химический анализ
    HARDNESS = "hardness"  # Испытание на твердость
    TENSILE = "tensile"  # Испытание на растяжение
    IMPACT = "impact"  # Испытание на удар
    ULTRASONIC = "ultrasonic"  # Ультразвуковой контроль
    RADIOGRAPHIC = "radiographic"  # Радиографический контроль
    MAGNETIC = "magnetic"  # Магнитный контроль
    PENETRANT = "penetrant"  # Капиллярный контроль


class TestCategory(str, enum.Enum):
    """Категории тестов"""
    DESTRUCTIVE = "destructive"  # Разрушающий контроль
    NON_DESTRUCTIVE = "non_destructive"  # Неразрушающий контроль
    VISUAL_CHECK = "visual_check"  # Визуальная проверка


class TestResult(Base):
    """
    Результаты тестирования материалов
    """
    __tablename__ = "test_results"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)

    # Информация о тесте
    test_type = Column(Enum(TestType), nullable=False)
    test_category = Column(Enum(TestCategory), nullable=False)
    test_method = Column(String(100))  # Метод/стандарт тестирования

    # Результаты
    pass_fail = Column(String(10), nullable=False)  # PASS/FAIL
    numeric_results = Column(JSON)  # Численные результаты
    # Пример структуры numeric_results:
    # {
    #     "tensile_strength": 450.5,
    #     "yield_strength": 320.0,
    #     "elongation": 22.5,
    #     "units": {
    #         "tensile_strength": "MPa",
    #         "yield_strength": "MPa",
    #         "elongation": "%"
    #     }
    # }

    # Дополнительная информация
    test_conditions = Column(JSON)  # Условия проведения теста
    equipment_used = Column(String(200))  # Используемое оборудование
    notes = Column(Text)
    attachments = Column(JSON, default=list)  # Пути к файлам с результатами

    # Кто и когда проводил тест
    tested_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    tested_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime(timezone=True))

    # Связь с сертификатом
    certificate_id = Column(Integer, ForeignKey("certificates.id"))

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    material = relationship("Material", back_populates="test_results")
    tester = relationship("User", back_populates="test_results", foreign_keys=[tested_by])
    verifier = relationship("User", foreign_keys=[verified_by])
    certificate = relationship("Certificate", back_populates="test_results")

    def __repr__(self):
        return f"<TestResult {self.test_type.value}: {self.pass_fail}>"


class Certificate(Base):
    """
    Сертификаты качества материалов
    """
    __tablename__ = "certificates"

    # Основные поля
    id = Column(Integer, primary_key=True, index=True)
    certificate_number = Column(String(50), unique=True, nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)

    # Тип сертификата
    certificate_type = Column(String(50), default="quality")  # quality, compliance, test

    # Информация о сертификате
    issued_date = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True))
    issued_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Содержимое сертификата
    summary = Column(Text)  # Краткое описание
    conclusions = Column(Text)  # Заключения
    recommendations = Column(Text)  # Рекомендации

    # Файлы
    pdf_path = Column(String(500))  # Путь к PDF файлу
    original_certificate_path = Column(String(500))  # Путь к оригинальному сертификату поставщика

    # Метаданные для поиска
    certificate_metadata = Column(JSON, default=dict)
    # Пример структуры certificate_metadata:
    # {
    #     "keywords": ["сталь", "лист", "09Г2С"],
    #     "standards": ["ГОСТ 19281-2014"],
    #     "customer": "ООО Производство",
    #     "project": "Проект А-123"
    # }

    # Цифровая подпись
    digital_signature = Column(Text)
    signature_timestamp = Column(DateTime(timezone=True))

    # Статус
    is_valid = Column(Boolean, default=True)
    invalidation_reason = Column(Text)
    invalidated_at = Column(DateTime(timezone=True))

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Связи
    material = relationship("Material", back_populates="certificates")
    issuer = relationship("User", back_populates="issued_certificates")
    test_results = relationship("TestResult", back_populates="certificate")

    def __repr__(self):
        return f"<Certificate {self.certificate_number}>"

    @property
    def is_expired(self) -> bool:
        """Проверка истечения срока действия"""
        if not self.valid_until:
            return False
        from datetime import datetime
        return datetime.now(self.valid_until.tzinfo) > self.valid_until

    def to_dict(self):
        """Преобразование в словарь"""
        return {
            "id": str(self.id),
            "certificate_number": self.certificate_number,
            "material_id": str(self.material_id),
            "certificate_type": self.certificate_type,
            "issued_date": self.issued_date.isoformat() if self.issued_date else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "is_valid": self.is_valid,
            "is_expired": self.is_expired,
            "summary": self.summary,
            "pdf_path": self.pdf_path,
            "certificate_metadata": self.certificate_metadata
        }