from sqlalchemy import Column, String, Text, DateTime, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base
from enum import Enum


class MaterialStatus(str, Enum):
    RECEIVED = "received"
    QUARANTINE = "quarantine"
    TESTING = "testing"
    APPROVED = "approved"
    REJECTED = "rejected"
    RELEASED = "released"


class MaterialType(str, Enum):
    STEEL = "steel"
    ALUMINUM = "aluminum"
    COPPER = "copper"
    BRASS = "brass"
    STAINLESS_STEEL = "stainless_steel"
    CARBON_STEEL = "carbon_steel"
    ALLOY_STEEL = "alloy_steel"
    OTHER = "other"


class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(100), unique=True, nullable=False, index=True)
    material_type = Column(String(50), nullable=False)
    grade = Column(String(100), nullable=True)
    specification = Column(String(200), nullable=True)
    quantity = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False, default="kg")
    supplier = Column(String(200), nullable=False)
    supplier_certificate = Column(String(500), nullable=True)

    # Переименовано с metadata на material_metadata
    material_metadata = Column(JSON, nullable=True, default=dict)

    status = Column(String(20), nullable=False, default=MaterialStatus.RECEIVED.value)
    location = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)

    # Даты
    received_date = Column(DateTime(timezone=True), server_default=func.now())
    production_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)

    # Аудит
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Отношения
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_materials")
    updater = relationship("User", foreign_keys=[updated_by], back_populates="updated_materials")
    workflow_states = relationship("WorkflowState", back_populates="material")
    test_results = relationship("TestResult", back_populates="material")
    certificates = relationship("Certificate", back_populates="material")

    def __repr__(self):
        return f"<Material(id={self.id}, batch_number='{self.batch_number}', type='{self.material_type}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "batch_number": self.batch_number,
            "material_type": self.material_type,
            "grade": self.grade,
            "specification": self.specification,
            "quantity": self.quantity,
            "unit": self.unit,
            "supplier": self.supplier,
            "supplier_certificate": self.supplier_certificate,
            "material_metadata": self.material_metadata,
            "status": self.status,
            "location": self.location,
            "notes": self.notes,
            "received_date": self.received_date.isoformat() if self.received_date else None,
            "production_date": self.production_date.isoformat() if self.production_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by
        }