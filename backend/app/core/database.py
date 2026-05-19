from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from redis.asyncio import Redis
from app.core.config import settings
import logging
import asyncio

logger = logging.getLogger(__name__)

Base = declarative_base()

# MongoDB
mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
mongo_db = mongo_client["ims_signals"]
signals_collection = mongo_db["raw_signals"]

# PostgreSQL
engine = create_async_engine(settings.POSTGRES_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Redis
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

async def init_db():
    from app.models.sql_models import Base as SQLBase
    # Retry logic - wait for PostgreSQL to be ready
    for attempt in range(10):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(SQLBase.metadata.create_all)
            break
        except Exception as e:
            logger.warning(f"DB not ready, attempt {attempt+1}/10. Retrying in 3s... {e}")
            await asyncio.sleep(3)
    await signals_collection.create_index("component_id")
    await signals_collection.create_index("timestamp")
    logger.info("✅ Databases initialized successfully")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
