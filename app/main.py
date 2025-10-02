import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

from app.core.config import settings
from app.core import db
from app.tasks.cleanup import start_scheduler, stop_scheduler
from app.routers import equipment, documents, sessions, reports, suggest, admin, importer, users

api_router = APIRouter()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"/api/v1/openapi.json"
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(equipment.router, prefix="/equipment", tags=["equipment"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(suggest.router, prefix="/suggest", tags=["suggest"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(importer.router, prefix="/import", tags=["import"])

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup():
    start_scheduler(db.SessionLocal)
    logger.info("Application startup complete.")


@app.on_event("shutdown")
async def on_shutdown():
    stop_scheduler()
    logger.info("Application shutdown complete.")


@app.get("/api/health-check")
def health_check():
    return {"status": "ok"}
