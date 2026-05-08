from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ComponentType(str, Enum):
    RDBMS = "RDBMS"
    CACHE = "CACHE"
    API = "API"
    QUEUE = "QUEUE"
    NOSQL = "NOSQL"
    MCP = "MCP"

class SignalPayload(BaseModel):
    component_id: str
    component_type: ComponentType
    error_code: str
    message: str
    latency_ms: Optional[float] = None
    timestamp: Optional[datetime] = None

class RCACreate(BaseModel):
    incident_start: datetime
    incident_end: datetime
    root_cause_category: str
    fix_applied: str = Field(..., min_length=10)
    prevention_steps: str = Field(..., min_length=10)

class StatusUpdate(BaseModel):
    status: str

class WorkItemResponse(BaseModel):
    id: str
    component_id: str
    component_type: str
    status: str
    priority: str
    title: str
    signal_count: float
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    mttr_minutes: Optional[float]
    has_rca: bool = False

    class Config:
        from_attributes = True
