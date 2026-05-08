from fastapi import APIRouter, Depends, BackgroundTasks
from app.models.schemas import SignalPayload
from app.services.signal_service import buffer_signal, signal_processor
from app.core.rate_limiter import rate_limiter
import asyncio

router = APIRouter()
_processor_started = False

@router.on_event("startup")
async def start_processor():
    global _processor_started
    if not _processor_started:
        asyncio.create_task(signal_processor())
        _processor_started = True

@router.post("/ingest")
async def ingest_signal(
    signal: SignalPayload,
    _=Depends(rate_limiter.check)
):
    await buffer_signal(signal)
    return {"status": "accepted", "component_id": signal.component_id}

@router.post("/ingest/bulk")
async def ingest_bulk(
    signals: list[SignalPayload],
    _=Depends(rate_limiter.check)
):
    for signal in signals:
        await buffer_signal(signal)
    return {"status": "accepted", "count": len(signals)}

@router.get("/raw/{component_id}")
async def get_raw_signals(component_id: str, limit: int = 50):
    from app.core.database import signals_collection
    cursor = signals_collection.find(
        {"component_id": component_id},
        {"_id": 0}
    ).sort("ingested_at", -1).limit(limit)
    signals = await cursor.to_list(length=limit)
    return signals
