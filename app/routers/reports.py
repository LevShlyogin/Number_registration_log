from fastapi import APIRouter, Depends, Query
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.services.reports import ReportsService, start_of_week

router = APIRouter(prefix="/reports", tags=["reports"])


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


@router.get("", response_model=list[dict])
async def report_json(
    station_object: list[str] | None = Query(default=None, alias="station_object"),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = ReportsService(session)
    df = _parse_dt(date_from)
    dt = _parse_dt(date_to)
    if df is None and dt is not None:
        df = start_of_week()
    if df is not None and dt is None:
        dt = datetime.now()
    rows = await svc.get_rows(station_object, df, dt)
    return rows


@router.get("/excel", response_model=dict)
async def report_excel(
    station_object: list[str] | None = Query(default=None, alias="station_object"),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = ReportsService(session)
    df = _parse_dt(date_from)
    dt = _parse_dt(date_to)
    if df is None and dt is not None:
        df = start_of_week()
    if df is not None and dt is None:
        dt = datetime.now()
    path = await svc.export_excel(station_object, df, dt)
    return {"path": path}