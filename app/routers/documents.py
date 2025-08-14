from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.schemas.documents import DocumentAssignOne, DocumentOut
from app.services.documents import DocumentsService
from app.utils.numbering import format_doc_no

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/assign-one", response_model=dict)
async def assign_one(
    payload: DocumentAssignOne,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    svc = DocumentsService(session)
    try:
        res = await svc.assign_one(
            session_id=payload.session_id, user_id=user.id, doc_name=payload.doc_name, note=payload.note, is_admin=user.is_admin
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return res


@router.patch("/{document_id}", response_model=dict)
async def edit_document_admin(
    document_id: int,
    payload: dict,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ может редактировать документ.")
    doc_name = payload.get("doc_name")
    note = payload.get("note")
    svc = DocumentsService(session)
    try:
        res = await svc.edit_document_admin(document_id=document_id, username=user.username, doc_name=doc_name, note=note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=409, detail="Такой документ уже зарегистрирован.")
    return res
