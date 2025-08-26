from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Form, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.core.db import lifespan_session
from app.core.auth import get_current_user, CurrentUser
from app.services.admin import AdminService
from app.services.reservation import ReservationService
from app.services.reports import ReportsService
from app.services.equipment import EquipmentService
from app.core.config import settings
from app.schemas.admin import GoldenSuggestOut

router = APIRouter(prefix="/admin-dashboard", tags=["admin-dashboard"])


@router.get("/dashboard")
async def admin_dashboard(
    request: Request,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Админская панель с расширенным функционалом"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    
    return HTMLResponse(r"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Админская панель</title>
        <script src="https://unpkg.com/htmx.org@1.9.10"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .admin-section { margin-bottom: 30px; }
            .filter-row { margin-bottom: 20px; }
            .table-responsive { margin-top: 20px; }
            .edit-form { display: none; }
            .golden-number { color: #ffc107; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container-fluid mt-4">
            <div class="row">
                <div class="col-12">
                    <h1><i class="bi bi-shield-lock"></i> Админская панель</h1>
                    <p class="text-muted">Расширенное управление документами и номерами</p>
                    
                    <div class="mb-3">
                        <a href="/wizard" class="btn btn-secondary">
                            <i class="bi bi-arrow-left"></i> Вернуться к Wizard
                        </a>
                    </div>
                </div>
            </div>
            
            <!-- Фильтры для поиска -->
            <div class="admin-section">
                <h3>Фильтры поиска</h3>
                <div class="row filter-row">
                    <div class="col-md-2">
                        <label class="form-label">Станция/Объект</label>
                        <input type="text" class="form-control" id="filter-station-object" 
                               placeholder="Например: Мосэнерго">
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">№ станционный</label>
                        <input type="text" class="form-control" id="filter-station-no" 
                               placeholder="Например: 3">
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Маркировка</label>
                        <input type="text" class="form-control" id="filter-label" 
                               placeholder="Например: Т-110">
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">№ заводской</label>
                        <input type="text" class="form-control" id="filter-factory-no" 
                               placeholder="Например: 12345">
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">№ заказа</label>
                        <input type="text" class="form-control" id="filter-order-no" 
                               placeholder="Например: 12345-67">
                    </div>
                    <div class="col-md-2">
                        <label class="form-label">Пользователь</label>
                        <input type="text" class="form-control" id="filter-username" 
                               placeholder="Имя пользователя">
                    </div>
                </div>
                
                <div class="row filter-row">
                    <div class="col-md-3">
                        <label class="form-label">Дата от</label>
                        <input type="date" class="form-control" id="filter-date-from">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Дата до</label>
                        <input type="date" class="form-control" id="filter-date-to">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Тип оборудования</label>
                        <select class="form-control" id="filter-eq-type">
                            <option value="">Все типы</option>
                            <option value="Турбина">Турбина</option>
                            <option value="Вспомогательное оборудование">Вспомогательное оборудование</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <button class="btn btn-primary" onclick="searchDocuments()" style="margin-top: 32px;">
                            <i class="bi bi-search"></i> Поиск
                        </button>
                        <button class="btn btn-success" onclick="exportToExcel()" style="margin-top: 32px;">
                            <i class="bi bi-file-earmark-excel"></i> Excel
                        </button>
                    </div>
                </div>
            </div>
            
            <!-- Результаты поиска -->
            <div class="admin-section">
                <h3>Результаты поиска</h3>
                <div id="search-results">
                    <div class="alert alert-info">Используйте фильтры для поиска документов</div>
                </div>
            </div>
            
            <!-- Управление золотыми номерами -->
            <div class="admin-section">
                <h3>Управление золотыми номерами</h3>
                <div class="row">
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label class="form-label">Оборудование</label>
                            <select class="form-control" id="golden-equipment">
                                <option value="">Выберите оборудование</option>
                            </select>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <label class="form-label">Количество номеров</label>
                            <input type="number" class="form-control" id="golden-count" 
                                   min="1" max="50" value="10">
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="mb-3">
                            <button class="btn btn-warning" onclick="suggestGoldenNumbers()" style="margin-top: 32px;">
                                <i class="bi bi-star"></i> Показать золотые
                            </button>
                        </div>
                    </div>
                </div>
                
                <div id="golden-results"></div>
            </div>
        </div>
        
        <script>
            // Поиск документов с расширенными фильтрами
            function searchDocuments() {
                const params = new URLSearchParams();
                
                // Собираем все фильтры
                const filters = [
                    'filter-station-object', 'filter-station-no', 'filter-label', 
                    'filter-factory-no', 'filter-order-no', 'filter-username',
                    'filter-date-from', 'filter-date-to', 'filter-eq-type'
                ];
                
                filters.forEach(filterId => {
                    const value = document.getElementById(filterId).value;
                    if (value) {
                        const paramName = filterId.replace('filter-', '');
                        if (paramName === 'station-object') {
                            // Поддержка множественного выбора для станций
                            const stations = value.split(',').map(s => s.trim()).filter(s => s);
                            stations.forEach(station => params.append('station_object', station));
                        } else {
                            params.append(paramName, value);
                        }
                    }
                });
                
                document.getElementById('search-results').innerHTML = 
                    '<div class="alert alert-info">Поиск...</div>';
                
                fetch(`/admin-dashboard/documents?${params.toString()}`, {
                    headers: { 'Hx-Request': 'true' }
                })
                .then(response => response.text())
                .then(html => {
                    document.getElementById('search-results').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('search-results').innerHTML = 
                        '<div class="alert alert-danger">Ошибка поиска</div>';
                });
            }
            
            // Экспорт в Excel
            function exportToExcel() {
                const params = new URLSearchParams();
                const filters = [
                    'filter-station-object', 'filter-station-no', 'filter-label', 
                    'filter-factory-no', 'filter-order-no', 'filter-username',
                    'filter-date-from', 'filter-date-to', 'filter-eq-type'
                ];
                
                filters.forEach(filterId => {
                    const value = document.getElementById(filterId).value;
                    if (value) {
                        const paramName = filterId.replace('filter-', '');
                        if (paramName === 'station-object') {
                            const stations = value.split(',').map(s => s.trim()).filter(s => s);
                            stations.forEach(station => params.append('station_object', station));
                        } else {
                            params.append(paramName, value);
                        }
                    }
                });
                
                window.open(`/admin-dashboard/documents/excel?${params.toString()}`, '_blank');
            }
            
            // Предложение золотых номеров
            function suggestGoldenNumbers() {
                const equipmentId = document.getElementById('golden-equipment').value;
                const count = document.getElementById('golden-count').value;
                
                if (!equipmentId) {
                    alert('Выберите оборудование');
                    return;
                }
                
                document.getElementById('golden-results').innerHTML = 
                    '<div class="alert alert-info">Поиск золотых номеров...</div>';
                
                fetch(`/admin/golden-suggest?limit=${count}`, {
                    headers: { 'Hx-Request': 'true' }
                })
                .then(response => response.text())
                .then(html => {
                    document.getElementById('golden-results').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('golden-results').innerHTML = 
                        '<div class="alert alert-danger">Ошибка поиска золотых номеров</div>';
                });
            }
            
            // Загрузка списка оборудования при загрузке страницы
            document.addEventListener('DOMContentLoaded', function() {
                // Загружаем список оборудования для выбора золотых номеров
                fetch('/admin-dashboard/equipment?limit=100')
                .then(response => response.json())
                .then(equipment => {
                    const select = document.getElementById('golden-equipment');
                    equipment.forEach(eq => {
                        const option = document.createElement('option');
                        option.value = eq.id;
                        option.textContent = `${eq.eq_type} - ${eq.station_object || 'N/A'} (${eq.factory_no || 'N/A'})`;
                        select.appendChild(option);
                    });
                });
                
                // Устанавливаем даты по умолчанию (последние 30 дней)
                const today = new Date();
                const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000));
                
                document.getElementById('filter-date-from').value = thirtyDaysAgo.toISOString().split('T')[0];
                document.getElementById('filter-date-to').value = today.toISOString().split('T')[0];
            });
        </script>
    </body>
    </html>
    """)


@router.get("/equipment")
async def admin_equipment(
    limit: int = 100,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Получение списка оборудования для админской панели"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    
    svc = EquipmentService(session)
    equipment = await svc.get_all(limit=limit)
    
    return JSONResponse([{
        "id": eq.id,
        "eq_type": eq.eq_type,
        "station_object": eq.station_object,
        "factory_no": eq.factory_no,
        "order_no": eq.order_no,
        "label": eq.label,
        "station_no": eq.station_no
    } for eq in equipment])


@router.get("/documents")
async def admin_documents(
    request: Request,
    station_object: list[str] | None = Query(default=None),
    station_no: str | None = Query(default=None),
    label: str | None = Query(default=None),
    factory_no: str | None = Query(default=None),
    order_no: str | None = Query(default=None),
    username: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    eq_type: str | None = Query(default=None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Расширенный поиск документов для админов"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    
    svc = ReportsService(session)
    
    # Парсим даты
    df = None
    dt = None
    if date_from:
        try:
            df = datetime.fromisoformat(date_from)
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.fromisoformat(date_to + " 23:59:59")
        except ValueError:
            pass
    
    # Получаем данные с расширенными фильтрами
    rows = await svc.get_rows_extended_admin(
        station_objects=station_object,
        station_no=station_no,
        label=label,
        factory_no=factory_no,
        order_no=order_no,
        username=username,
        date_from=df,
        date_to=dt,
        eq_type=eq_type
    )
    
    if request.headers.get("Hx-Request") == "true":
        if not rows:
            return HTMLResponse('<div class="alert alert-warning">Документы не найдены</div>')
        
        html = """
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead class="table-dark">
                    <tr>
                        <th>№ документа</th>
                        <th>Дата регистрации</th>
                        <th>Наименование</th>
                        <th>Примечание</th>
                        <th>Тип оборудования</th>
                        <th>№ заводской</th>
                        <th>№ заказа</th>
                        <th>Маркировка</th>
                        <th>№ станционный</th>
                        <th>Станция/Объект</th>
                        <th>Пользователь</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for row in rows:
            html += f"""
            <tr>
                <td>{row['doc_no']}</td>
                <td>{row['reg_date']}</td>
                <td>{row['doc_name']}</td>
                <td>{row['note'] or '-'}</td>
                <td>{row['eq_type']}</td>
                <td>{row['factory_no'] or '-'}</td>
                <td>{row['order_no'] or '-'}</td>
                <td>{row['label'] or '-'}</td>
                <td>{row['station_no'] or '-'}</td>
                <td>{row['station_object'] or '-'}</td>
                <td>{row['username']}</td>
                <td>
                    <button class="btn btn-sm btn-primary" onclick="editDocument({row['id']})">
                        <i class="bi bi-pencil"></i> Изменить
                    </button>
                </td>
            </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        return HTMLResponse(html)
    
    return JSONResponse(rows)


@router.get("/documents/excel")
async def admin_documents_excel(
    station_object: list[str] | None = Query(default=None),
    station_no: str | None = Query(default=None),
    label: str | None = Query(default=None),
    factory_no: str | None = Query(default=None),
    order_no: str | None = Query(default=None),
    username: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    eq_type: str | None = Query(default=None),
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Экспорт документов в Excel для админов"""
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Только админ.")
    
    svc = ReportsService(session)
    
    # Парсим даты
    df = None
    dt = None
    if date_from:
        try:
            df = datetime.fromisoformat(date_from)
        except ValueError:
            pass
    if date_to:
        try:
            dt = datetime.fromisoformat(date_to + " 23:59:59")
        except ValueError:
            pass
    
    # Экспортируем в Excel
    fname = await svc.export_excel_extended_admin(
        station_objects=station_object,
        station_no=station_no,
        label=label,
        factory_no=factory_no,
        order_no=order_no,
        username=username,
        date_from=df,
        date_to=dt,
        eq_type=eq_type
    )
    
    from fastapi.responses import FileResponse
    from starlette.background import BackgroundTask
    import os
    
    return FileResponse(
        path=fname,
        filename=os.path.basename(fname),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        background=BackgroundTask(lambda: os.remove(fname))
    )
