from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.sql_models import WorkItem, RCARecord, WorkItemStatus
from app.models.schemas import RCACreate, WorkItemResponse, StatusUpdate
from app.services.state_machine import transition_state, get_state
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/", response_model=list[WorkItemResponse])
async def list_incidents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorkItem).order_by(WorkItem.created_at.desc())
    )
    items = result.scalars().all()
    response = []
    for item in items:
        rca_result = await db.execute(select(RCARecord).where(RCARecord.work_item_id == item.id))
        has_rca = rca_result.scalars().first() is not None
        response.append(WorkItemResponse(
            id=item.id,
            component_id=item.component_id,
            component_type=item.component_type,
            status=item.status,
            priority=item.priority,
            title=item.title,
            signal_count=item.signal_count,
            created_at=item.created_at,
            updated_at=item.updated_at,
            resolved_at=item.resolved_at,
            mttr_minutes=item.mttr_minutes,
            has_rca=has_rca
        ))
    return response

@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkItem).where(WorkItem.id == incident_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Incident not found")
    rca_result = await db.execute(select(RCARecord).where(RCARecord.work_item_id == incident_id))
    rca = rca_result.scalars().first()
    return {
        "incident": item,
        "rca": rca
    }

@router.patch("/{incident_id}/status")
async def update_status(incident_id: str, update: StatusUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkItem).where(WorkItem.id == incident_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Incident not found")

    new_status = transition_state(item.status)

    # Enforce RCA before CLOSED
    if new_status == "CLOSED":
        rca_result = await db.execute(select(RCARecord).where(RCARecord.work_item_id == incident_id))
        rca = rca_result.scalars().first()
        if not rca:
            raise HTTPException(
                status_code=400,
                detail="❌ Cannot close incident without a complete RCA. Please submit RCA first."
            )

    item.status = new_status
    item.updated_at = datetime.utcnow()

    if new_status == "RESOLVED":
        item.resolved_at = datetime.utcnow()
        delta = (item.resolved_at - item.created_at).total_seconds() / 60
        item.mttr_minutes = round(delta, 2)

    await db.commit()
    logger.info(f"✅ Incident {incident_id} transitioned to {new_status}")
    return {"status": new_status, "mttr_minutes": item.mttr_minutes}

@router.post("/{incident_id}/rca")
async def submit_rca(incident_id: str, rca_data: RCACreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkItem).where(WorkItem.id == incident_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Check if RCA already exists
    existing = await db.execute(select(RCARecord).where(RCARecord.work_item_id == incident_id))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="RCA already submitted for this incident.")

    rca = RCARecord(
        work_item_id=incident_id,
        incident_start=rca_data.incident_start,
        incident_end=rca_data.incident_end,
        root_cause_category=rca_data.root_cause_category,
        fix_applied=rca_data.fix_applied,
        prevention_steps=rca_data.prevention_steps
    )
    db.add(rca)
    await db.commit()
    logger.info(f"✅ RCA submitted for incident {incident_id}")
    return {"message": "RCA submitted successfully", "incident_id": incident_id}
