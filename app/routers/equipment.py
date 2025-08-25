from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, Query, HTTPException
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
    order_no: str | None = Query(None),
    q: str | None = Query(None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = EquipmentService(session)
    results = await svc.search(
        station_object=station_object, station_no=station_no, label=label, 
        factory_no=factory_no, order_no=order_no, q=q
    )
    
    if request.headers.get("Hx-Request") == "true":
        # Для HTMX возвращаем HTML с кнопками выбора
        if not results:
            html = """
            <div class="alert alert-info">
                Ничего не найдено. 
                <button class="btn btn-outline-primary btn-sm" onclick="showCreateForm()">
                    Создать новый объект
                </button>
            </div>
            """
        else:
            html = '<div class="mb-3"><strong>Найденные объекты:</strong></div>'
            for eq in results:
                html += f"""
                <div class="equipment-item" data-equipment-id="{eq.id}">
                    <div class="equipment-header">
                        <strong>{eq.eq_type}</strong> - {eq.station_object or 'N/A'} 
                        {eq.station_no and f'(ст.{eq.station_no})' or ''} 
                        {eq.label and f'[{eq.label}]' or ''}
                    </div>
                    <div class="equipment-details">
                        <small class="text-muted">
                            ID: {eq.id} | 
                            Заводской: {eq.factory_no or 'N/A'} | 
                            Заказ: {eq.order_no or 'N/A'}
                        </small>
                    </div>
                    <button class="btn btn-primary btn-sm mt-2" onclick="selectEquipment({eq.id})">
                        Выбрать
                    </button>
                </div>
                """
        return HTMLResponse(html)
    else:
        # Для API возвращаем JSON
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
    
    try:
        svc = EquipmentService(session)
        eq = await svc.create(payload.model_dump())

        # Если запрос пришел из HTMX (форма в UI), вернем HTML-фрагмент,
        # иначе — JSON для API-клиентов (Postman/Bruno)
        if request.headers.get("Hx-Request") == "true":
            html = (
                f'<div class="alert alert-success">Создано оборудование: ID={eq.id}, '
                f'тип: <b>{eq.eq_type}</b></div>'
                f'<script>selectEquipment({eq.id});</script>'
            )
            return HTMLResponse(html)
        else:
            return JSONResponse(EquipmentOut.model_validate(eq).model_dump())
            
    except HTTPException as e:
        # Обрабатываем ошибки валидации
        if request.headers.get("Hx-Request") == "true":
            html = f'<div class="alert alert-danger">Ошибка: {e.detail}</div>'
            return HTMLResponse(html, status_code=e.status_code)
        else:
            raise e
    except Exception as e:
        # Обрабатываем неожиданные ошибки
        if request.headers.get("Hx-Request") == "true":
            html = f'<div class="alert alert-danger">Ошибка создания: {str(e)}</div>'
            return HTMLResponse(html, status_code=500)
        else:
            raise HTTPException(status_code=500, detail=f"Ошибка создания: {str(e)}")