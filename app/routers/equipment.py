from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, CurrentUser
from app.core.db import lifespan_session
from app.schemas.equipment import EquipmentCreate, EquipmentOut
from app.services.equipment import EquipmentService

router = APIRouter(prefix="/equipment", tags=["equipment"])


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
            f'<div class="badge">Создано оборудование: ID={eq.id}, '
            f'тип: <b>{eq.eq_type}</b></div>'
        )
        return HTMLResponse(html)
    else:
        return JSONResponse(EquipmentOut.model_validate(eq).model_dump())