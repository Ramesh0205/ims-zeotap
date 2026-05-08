from fastapi import APIRouter
from app.core.database import redis_client, mongo_client, engine
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    status = {"status": "healthy", "timestamp": time.time(), "services": {}}
    try:
        await redis_client.ping()
        status["services"]["redis"] = "✅ connected"
    except Exception as e:
        status["services"]["redis"] = f"❌ error: {str(e)}"
        status["status"] = "degraded"
    try:
        await mongo_client.admin.command("ping")
        status["services"]["mongodb"] = "✅ connected"
    except Exception as e:
        status["services"]["mongodb"] = f"❌ error: {str(e)}"
        status["status"] = "degraded"
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__('sqlalchemy').text("SELECT 1"))
        status["services"]["postgresql"] = "✅ connected"
    except Exception as e:
        status["services"]["postgresql"] = f"❌ error: {str(e)}"
        status["status"] = "degraded"
    return status
