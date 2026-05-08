from sqlalchemy import Column, String, DateTime, Text, Enum, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
import enum
from datetime import datetime

class WorkItemStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class Priority(str, enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"

class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    component_id = Column(String, nullable=False, index=True)
    component_type = Column(String, nullable=False)
    status = Column(Enum(WorkItemStatus), default=WorkItemStatus.OPEN, nullable=False)
    priority = Column(Enum(Priority), nullable=False)
    title = Column(String, nullable=False)
    signal_count = Column(Float, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    mttr_minutes = Column(Float, nullable=True)
    rca = relationship("RCARecord", back_populates="work_item", uselist=False)

class RCARecord(Base):
    __tablename__ = "rca_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    work_item_id = Column(String, ForeignKey("work_items.id"), nullable=False)
    incident_start = Column(DateTime, nullable=False)
    incident_end = Column(DateTime, nullable=False)
    root_cause_category = Column(String, nullable=False)
    fix_applied = Column(Text, nullable=False)
    prevention_steps = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    work_item = relationship("WorkItem", back_populates="rca")
