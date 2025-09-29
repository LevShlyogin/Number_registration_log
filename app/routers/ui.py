from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.auth import get_current_user, CurrentUser

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["ui"])


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, user: CurrentUser = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "username": user.username, "year": datetime.now().year})


@router.get("/ui/equipment", response_class=HTMLResponse)
async def ui_equipment(request: Request, user: CurrentUser = Depends(get_current_user)):
    return templates.TemplateResponse("equipment.html", {"request": request, "username": user.username, "year": datetime.now().year})


@router.get("/ui/session", response_class=HTMLResponse)
async def ui_session(request: Request, user: CurrentUser = Depends(get_current_user)):
    return templates.TemplateResponse("session.html", {"request": request, "username": user.username, "year": datetime.now().year})


@router.get("/ui/admin", response_class=HTMLResponse)
async def ui_admin(request: Request, user: CurrentUser = Depends(get_current_user)):
    return templates.TemplateResponse("admin.html", {"request": request, "username": user.username, "year": datetime.now().year})


@router.get("/ui/reports", response_class=HTMLResponse)
async def ui_reports(request: Request, user: CurrentUser = Depends(get_current_user)):
    return templates.TemplateResponse("reports.html", {"request": request, "username": user.username, "year": datetime.now().year})