import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core import db
from app.tasks.cleanup import start_scheduler, stop_scheduler
from app.routers import equipment, documents, sessions, reports, suggest, admin, importer, users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код, который выполняется при старте
    start_scheduler(db.SessionLocal)
    logger.info("Scheduler started.")
    yield
    # Код, который выполняется при остановке
    stop_scheduler()
    logger.info("Scheduler stopped.")

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(suggest.router, prefix="/suggest", tags=["suggest"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(importer.router, prefix="/import", tags=["import"])

app.include_router(api_router, prefix="/api/v1")

@app.get("/api/health-check")
def health_check():
    return {"status": "ok"}