from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.schemas.reports import ReportFilter
from app.services.reports import ReportsService, start_of_week

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[dict])
async def report_json(
    station_object: list[str] | None = Query(default=None, alias="station_object"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = ReportsService(session)
    if date_from is None and date_to is not None:
        date_from = start_of_week()
    if date_from and not date_to:
        date_to = datetime.now()
    rows = await svc.get_rows(station_object, date_from, date_to)
    return rows


@router.get("/excel", response_model=dict)
async def report_excel(
    station_object: list[str] | None = Query(default=None, alias="station_object"),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = ReportsService(session)
    if date_from is None and date_to is not None:
        date_from = start_of_week()
    if date_from and not date_to:
        date_to = datetime.now()
    path = await svc.export_excel(station_object, date_from, date_to)
    return {"path": path}
