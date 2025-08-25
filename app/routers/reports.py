from __future__ import annotations

from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
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


def _parse_stations(station_object: list[str] | None, station_raw: str | None) -> list[str] | None:
    # поддерживаем и повтор параметра, и CSV-строку из одного поля формы
    if station_object and len(station_object) > 0:
        return station_object
    if station_raw:
        parts = [p.strip() for p in station_raw.split(",") if p.strip()]
        return parts or None
    return None


@router.get("", response_class=HTMLResponse)
async def report_json(
    request: Request,
    station_object: list[str] | None = Query(default=None, alias="station_object"),
    station_object_raw: str | None = Query(default=None, alias="station_object"),
    station_no: str | None = Query(default=None),
    label: str | None = Query(default=None),
    factory_no: str | None = Query(default=None),
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
    stations = _parse_stations(station_object, station_object_raw)
    rows = await svc.get_rows_extended(
        stations, station_no, label, factory_no, df, dt
    )

    if request.headers.get("Hx-Request") == "true":
        # мини‑таблица для HTMX
        if not rows:
            return HTMLResponse('<div class="badge">Нет данных</div>')
        header = (
            "<tr><th>№</th><th>Дата</th><th>Наименование</th><th>Примечание</th>"
            "<th>Тип</th><th>Заводской</th><th>Заказ</th><th>Маркировка</th>"
            "<th>Станц. №</th><th>Станция/Объект</th><th>Пользователь</th></tr>"
        )
        body = "".join(
            f"<tr><td>{r['doc_no']}</td><td>{r['reg_date']}</td><td>{r['doc_name']}</td><td>{r['note']}</td>"
            f"<td>{r['eq_type']}</td><td>{r['factory_no'] or ''}</td><td>{r['order_no'] or ''}</td>"
            f"<td>{r['label'] or ''}</td><td>{r['station_no'] or ''}</td><td>{r['station_object'] or ''}</td>"
            f"<td>{r.get('username', '')}</td></tr>"
            for r in rows
        )
        return HTMLResponse(f"<table>{header}{body}</table>")
    return JSONResponse(rows)


@router.get("/excel")
async def report_excel(
    request: Request,
    station_object: list[str] | None = Query(default=None, alias="station_object"),
    station_object_raw: str | None = Query(default=None, alias="station_object"),
    station_no: str | None = Query(default=None),
    label: str | None = Query(default=None),
    factory_no: str | None = Query(default=None),
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
    stations = _parse_stations(station_object, station_object_raw)
    path = await svc.export_excel_extended(
        stations, station_no, label, factory_no, df, dt
    )
    return JSONResponse({"path": path})