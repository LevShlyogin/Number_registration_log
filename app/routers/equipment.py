from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, CurrentUser
from app.core.db import lifespan_session
from app.schemas.equipment import EquipmentCreate, EquipmentOut
from app.services.equipment import EquipmentService

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("/search")
async def search_equipment(
    request: Request,
    station_object: str | None = Query(None),
    station_no: str | None = Query(None),
    label: str | None = Query(None),
    factory_no: str | None = Query(None),
    q: str | None = Query(None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Поиск оборудования по различным критериям"""
    svc = EquipmentService(session)
    results = await svc.search(
        station_object=station_object,
        station_no=station_no,
        label=label,
        factory_no=factory_no,
        q=q
    )
    
    if request.headers.get("Hx-Request") == "true":
        if not results:
            html = """
            <div class="alert alert-info">
                <p>Ничего не найдено</p>
                <button class="btn btn-primary" onclick="showCreateForm()">
                    Создать новый объект
                </button>
            </div>
            """
        else:
            html = '<div class="equipment-list">'
            for eq in results:
                html += f"""
                <div class="equipment-item" data-equipment-id="{eq.id}">
                    <div class="equipment-header">
                        <strong>ID: {eq.id}</strong> - {eq.eq_type}
                    </div>
                    <div class="equipment-details">
                        <small>
                            {f'Станция: {eq.station_object}' if eq.station_object else ''}
                            {f' №{eq.station_no}' if eq.station_no else ''}
                            {f' Маркировка: {eq.label}' if eq.label else ''}
                            {f' Зав.№: {eq.factory_no}' if eq.factory_no else ''}
                        </small>
                    </div>
                    <button class="btn btn-sm btn-outline-primary" 
                            onclick="selectEquipment({eq.id})">
                        Выбрать
                    </button>
                </div>
                """
            html += '</div>'
        
        return HTMLResponse(html)
    else:
        return JSONResponse([EquipmentOut.model_validate(eq).model_dump() for eq in results])


@router.post("")
async def create_equipment(
    request: Request,
    eq_type: str = Form(...),
    factory_no: str | None = Form(None),
    order_no: str | None = Form(None),
    label: str | None = Form(None),
    station_no: str | None = Form(None),
    station_object: str | None = Form(None),
    notes: str | None = Form(None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    payload = EquipmentCreate(
        eq_type=eq_type,
        factory_no=factory_no,
        order_no=order_no,
        label=label,
        station_no=station_no,
        station_object=station_object,
        notes=notes,
    )
    svc = EquipmentService(session)
    eq = await svc.create(payload.model_dump())

    # Если запрос пришел из HTMX (форма в UI), вернем HTML-фрагмент,
    # иначе — JSON для API-клиентов (Postman/Bruno)
    if request.headers.get("Hx-Request") == "true":
        html = (
            f'<div class="badge badge-success">Создано оборудование: ID={eq.id}, '
            f'тип: <b>{eq.eq_type}</b></div>'
            f'<script>selectEquipment({eq.id});</script>'
        )
        return HTMLResponse(html)
    else:
        return JSONResponse(EquipmentOut.model_validate(eq).model_dump())