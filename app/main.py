import logging
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core import db
from app.tasks.cleanup import start_scheduler, stop_scheduler
from app.routers import equipment, documents, sessions, reports, suggest, admin, importer, users
from app.middleware.log_requests import LogRequestsMiddleware

# Основной логгер
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Логгер для использования API, который будет писать в отдельный файл
api_usage_logger = logging.getLogger("api_usage")
api_usage_logger.setLevel(logging.INFO)
# Добавляем обработчик, который пишет в файл 'api_usage.log' с ротацией
# maxBytes=5MB, 3 бэкап-файла
handler = RotatingFileHandler("api_usage.log", maxBytes=5*1024*1024, backupCount=3)
api_usage_logger.addHandler(handler)
api_usage_logger.propagate = False # Не передавать сообщения в основной логгер

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler(db.SessionLocal)
    logger.info("Scheduler started.")
    yield
    stop_scheduler()
    logger.info("Scheduler stopped.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# --- Подключаем Middleware ---
app.add_middleware(LogRequestsMiddleware)

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