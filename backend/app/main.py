import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import signals, incidents, health
from app.core.database import init_db
from app.core.metrics import metrics_reporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    asyncio.create_task(metrics_reporter())
    yield

app = FastAPI(title="Incident Management System", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["Health"])
app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["Incidents"])
