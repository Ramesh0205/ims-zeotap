import asyncio
import json
import logging
from datetime import datetime
from app.core.database import signals_collection, redis_client, AsyncSessionLocal
from app.models.schemas import SignalPayload
from app.models.sql_models import WorkItem
from app.services.alert_strategy import get_alert_strategy
from app.core.metrics import record_signal

logger = logging.getLogger(__name__)

# In-memory buffer for backpressure handling
signal_buffer = asyncio.Queue(maxsize=50000)

async def buffer_signal(signal: SignalPayload):
    """Put signal in memory buffer immediately - never blocks the API"""
    record_signal()
    try:
        signal_buffer.put_nowait(signal.dict())
    except asyncio.QueueFull:
        logger.warning("⚠️ Signal buffer full! Dropping oldest signal.")
        signal_buffer.get_nowait()
        signal_buffer.put_nowait(signal.dict())

async def signal_processor():
    """Background worker that drains the buffer and persists signals"""
    while True:
        try:
            signal_data = await signal_buffer.get()
            await process_single_signal(signal_data)
        except Exception as e:
            logger.error(f"Error processing signal: {e}")

async def process_single_signal(signal_data: dict):
    component_id = signal_data["component_id"]
    component_type = signal_data["component_type"]

    # Store raw signal in MongoDB (audit log)
    signal_data["ingested_at"] = datetime.utcnow().isoformat()
    await signals_collection.insert_one(signal_data)

    # Debounce key
    debounce_key = f"debounce:{component_id}"
    count = await redis_client.incr(debounce_key)

    if count == 1:
        # First signal - set expiry window
        await redis_client.expire(debounce_key, 10)

    if count == 1:
        # Create new Work Item
        await create_work_item(component_id, component_type)
    else:
        # Increment signal count on existing work item
        await increment_signal_count(component_id)

async def create_work_item(component_id: str, component_type: str):
    strategy = get_alert_strategy(component_type)
    async with AsyncSessionLocal() as session:
        work_item = WorkItem(
            component_id=component_id,
            component_type=component_type,
            priority=strategy.get_priority(),
            title=strategy.get_title(component_id),
        )
        session.add(work_item)
        await session.commit()
        await session.refresh(work_item)
        # Cache in Redis
        await redis_client.setex(
            f"incident:{component_id}",
            300,
            json.dumps({"id": work_item.id, "status": work_item.status, "priority": work_item.priority})
        )
        logger.info(f"✅ Work Item created for {component_id} with priority {work_item.priority}")

async def increment_signal_count(component_id: str):
    from sqlalchemy import update
    from app.models.sql_models import WorkItem
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(WorkItem)
            .where(WorkItem.component_id == component_id)
            .order_by(WorkItem.created_at.desc())
        )
        work_item = result.scalars().first()
        if work_item:
            work_item.signal_count += 1
            await session.commit()
