from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.services.importer import ExcelImporterService

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/excel", response_model=dict)
async def import_excel(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ может импортировать Excel.")
    path = Path("var/uploads")
    path.mkdir(parents=True, exist_ok=True)
    fpath = path / file.filename
    with open(fpath, "wb") as f:
        f.write(await file.read())
    svc = ExcelImporterService(session)
    result = await svc.import_file(str(fpath))
    return result
