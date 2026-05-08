import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.db.postgres import init_db
from app.routers import signals, workitems, health
from app.services.metrics import metrics_reporter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting IMS backend...")
    await init_db()
    asyncio.create_task(metrics_reporter())
    yield
    logger.info("Shutting down IMS backend...")

app = FastAPI(
    title="Incident Management System",
    description="Mission-Critical IMS for Zeotap SRE Assignment",
    version="1.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])
app.include_router(workitems.router, prefix="/api/workitems", tags=["Work Items"])
app.include_router(health.router, tags=["Health"])

@app.get("/")
async def root():
    return {"message": "IMS API is running", "docs": "/docs"}
