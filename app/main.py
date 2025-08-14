from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import equipment, sessions, documents, admin, reports, suggest, importer, ui
from app.core.db import SessionLocal
from app.tasks.cleanup import start_scheduler

app = FastAPI(title="Журнал регистрации УТЗ", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(ui.router)
app.include_router(equipment.router)
app.include_router(sessions.router)
app.include_router(documents.router)
app.include_router(admin.router)
app.include_router(reports.router)
app.include_router(suggest.router)
app.include_router(importer.router)


@app.on_event("startup")
async def on_startup():
    # запуск планировщика очистки TTL
    start_scheduler(SessionLocal)
