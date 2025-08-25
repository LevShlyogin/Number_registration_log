from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user, CurrentUser
from app.core.db import lifespan_session

router = APIRouter(prefix="/wizard", tags=["wizard"])


@router.get("")
async def wizard_ui(
    request: Request,
    session: AsyncSession = Depends(lifespan_session),
    user: CurrentUser = Depends(get_current_user),
):
    """Главная страница wizard"""
    return HTMLResponse(r"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Wizard - Регистрация номеров</title>
        <script src="https://unpkg.com/htmx.org@1.9.10"></script>
        <script src="https://unpkg.com/hyperscript.org@0.9.12"></script>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .wizard-step { display: none; }
            .wizard-step.active { display: block; }
            .equipment-item { 
                border: 1px solid #ddd; 
                padding: 10px; 
                margin: 5px 0; 
                border-radius: 5px; 
            }
            .equipment-item.selected { 
                background-color: #e3f2fd; 
                border-color: #2196f3; 
            }
            .document-table { margin-top: 20px; }
            .step-indicator { 
                display: flex; 
                justify-content: space-between; 
                margin-bottom: 30px; 
            }
            .step { 
                flex: 1; 
                text-align: center; 
                padding: 10px; 
                border-bottom: 3px solid #ddd; 
            }
            .step.active { border-color: #007bff; }
            .step.completed { border-color: #28a745; }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1>Регистрация номеров документов</h1>
            
            <div class="step-indicator">
                <div class="step active" id="step-1-indicator">
                    <strong>1. Поиск/Создание оборудования</strong>
                </div>
                <div class="step" id="step-2-indicator">
                    <strong>2. Резерв номеров</strong>
                </div>
                <div class="step" id="step-3-indicator">
                    <strong>3. Назначение номеров</strong>
                </div>
                <div class="step" id="step-4-indicator">
                    <strong>4. Отчет</strong>
                </div>
            </div>
            
            <!-- Шаг 1: Поиск/Создание оборудования -->
            <div class="wizard-step active" id="step-1">
                <h3>Поиск оборудования</h3>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Станция / Объект</label>
                            <input type="text" class="form-control" id="search-station-object" 
                                   placeholder="Например: Мосэнерго ТЭЦ-23">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">№ станционный</label>
                            <input type="text" class="form-control" id="search-station-no" 
                                   placeholder="Например: ст.3">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Маркировка</label>
                            <input type="text" class="form-control" id="search-label" 
                                   placeholder="Например: Т-110">
                        </div>
                        <div class="mb-3">
                            <label class="text">№ заводской</label>
                            <input type="text" class="form-control" id="search-factory-no" 
                                   placeholder="Например: 120-12,8-8МО">
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <label class="form-label">Поиск по тексту</label>
                    <input type="text" class="form-control" id="search-q" 
                           placeholder="Введите текст для поиска по всем полям">
                </div>
                
                <div class="mb-3">
                    <button class="btn btn-primary" onclick="searchEquipment()">
                        <i class="bi bi-search"></i> Поиск
                    </button>
                    <button class="btn btn-outline-secondary" onclick="showCreateForm()">
                        Создать новый объект
                    </button>
                </div>
                
                <div id="search-results"></div>
                
                <div id="create-form" style="display: none;">
                    <h4>Создание нового оборудования</h4>
                    <form hx-post="/equipment" hx-target="#create-result">
                        <div class="mb-3">
                            <label class="form-label">Тип оборудования *</label>
                            <select class="form-control" name="eq_type" required>
                                <option value="">Выберите тип</option>
                                <option value="Турбина">Турбина</option>
                                <option value="Вспомогательное оборудование">Вспомогательное оборудование</option>
                            </select>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Станция / Объект</label>
                                    <input type="text" class="form-control" name="station_object">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">№ станционный</label>
                                    <input type="text" class="form-control" name="station_no">
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Маркировка</label>
                                    <input type="text" class="form-control" name="label">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">№ заводской</label>
                                    <input type="text" class="form-control" name="factory_no">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">№ заказа</label>
                            <input type="text" class="form-control" name="order_no">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Примечания</label>
                            <textarea class="form-control" name="notes" rows="2"></textarea>
                        </div>
                        <button type="submit" class="btn btn-success">Создать</button>
                        <button type="button" class="btn btn-secondary" onclick="hideCreateForm()">Отмена</button>
                    </form>
                    <div id="create-result"></div>
                </div>
                
                <div class="mt-4">
                    <button class="btn btn-primary" onclick="nextStep()" id="next-btn-1" disabled>
                        Далее >
                    </button>
                </div>
            </div>
            
            <!-- Шаг 2: Резерв номеров -->
            <div class="wizard-step" id="step-2">
                <h3>Резерв номеров</h3>
                
                <div class="mb-3">
                    <label class="form-label">Количество номеров для резерва</label>
                    <input type="number" class="form-control" id="requested-count" 
                           min="1" max="100" value="1">
                </div>
                
                <div class="mb-3">
                    <button class="btn btn-primary" onclick="reserveNumbers()">
                        Резервировать
                    </button>
                </div>
                
                <div id="reserve-result"></div>
                
                <div class="mt-4">
                    <button class="btn btn-secondary" onclick="prevStep()">
                        < Назад
                    </button>
                    <button class="btn btn-primary" onclick="nextStep()" id="next-btn-2" disabled>
                        Далее >
                    </button>
                </div>
            </div>
            
            <!-- Шаг 3: Назначение номеров -->
            <div class="wizard-step" id="step-3">
                <h3>Назначение номеров</h3>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Наименование документа</label>
                            <input type="text" class="form-control" id="doc-name" 
                                   placeholder="Введите наименование"
                                   list="doc-names-list"
                                   oninput="suggestDocNames(this.value)">
                            <datalist id="doc-names-list"></datalist>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Примечание</label>
                            <input type="text" class="form-control" id="doc-note" 
                                   placeholder="Введите примечание"
                                   list="notes-list"
                                   oninput="suggestNotes(this.value)">
                            <datalist id="notes-list"></datalist>
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <button class="btn btn-primary" onclick="assignNextNumber()">
                        Назначить следующий номер
                    </button>
                </div>
                
                <div class="document-table">
                    <h4>Зарегистрированные номера</h4>
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>№ документа</th>
                                <th>Дата</th>
                                <th>Наименование</th>
                                <th>Примечание</th>
                                <th>Тип оборудования</th>
                                <th>№ зав.</th>
                                <th>№ заказа</th>
                                <th>Маркировка</th>
                                <th>№ станц.</th>
                                <th>Станция/объект</th>
                                <th>Пользователь</th>
                            </tr>
                        </thead>
                        <tbody id="documents-table">
                        </tbody>
                    </table>
                </div>
                
                <div class="mt-4">
                    <button class="btn btn-secondary" onclick="prevStep()">
                        < Назад
                    </button>
                    <button class="btn btn-success" onclick="completeSession()">
                        Завершить
                    </button>
                </div>
            </div>
            
            <!-- Шаг 4: Отчет -->
            <div class="wizard-step" id="step-4">
                <h3>Отчет</h3>
                
                <div class="mb-4">
                    <h4>Фильтры поиска</h4>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Станция / Объект (можно несколько через запятую)</label>
                                <input type="text" class="form-control" id="report-station-object" 
                                       placeholder="Например: Мосэнерго ТЭЦ-23, АСММ Наземный">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">№ станционный</label>
                                <input type="text" class="form-control" id="report-station-no" 
                                       placeholder="Например: ст.3">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Маркировка</label>
                                <input type="text" class="form-control" id="report-label" 
                                       placeholder="Например: Т-110">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">№ заводской</label>
                                <input type="text" class="form-control" id="report-factory-no" 
                                       placeholder="Например: 120-12,8-8МО">
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <button class="btn btn-primary" onclick="showReport()">
                        Показать
                    </button>
                    <button class="btn btn-success" onclick="exportExcel()">
                        Сохранить в Excel
                    </button>
                    <button class="btn btn-secondary" onclick="restartWizard()">
                        Вернуться в начало
                    </button>
                </div>
                
                <div id="report-content"></div>
            </div>
        </div>
        
        <script>
            let currentStep = 1;
            let selectedEquipmentId = null;
            let currentSessionId = null;
            let reservedNumbers = [];
            
            function showStep(step) {
                // Скрываем все шаги
                document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
                
                // Показываем нужный шаг
                document.getElementById(`step-${step}`).classList.add('active');
                document.getElementById(`step-${step}-indicator`).classList.add('active');
                
                // Обновляем индикаторы
                for (let i = 1; i < step; i++) {
                    document.getElementById(`step-${i}-indicator`).classList.add('completed');
                }
                
                currentStep = step;
            }
            
            function nextStep() {
                if (currentStep < 4) {
                    showStep(currentStep + 1);
                }
            }
            
            function prevStep() {
                if (currentStep > 1) {
                    showStep(currentStep - 1);
                }
            }
            
            function searchEquipment() {
                const params = new URLSearchParams();
                const stationObject = document.getElementById('search-station-object').value;
                const stationNo = document.getElementById('search-station-no').value;
                const label = document.getElementById('search-label').value;
                const factoryNo = document.getElementById('search-factory-no').value;
                const q = document.getElementById('search-q').value;
                
                if (stationObject) params.append('station_object', stationObject);
                if (stationNo) params.append('station_no', stationNo);
                if (label) params.append('label', label);
                if (factoryNo) params.append('factory_no', factoryNo);
                if (q) params.append('q', q);
                
                fetch(`/equipment/search?${params.toString()}`)
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('search-results').innerHTML = html;
                    });
            }
            
            function selectEquipment(id) {
                selectedEquipmentId = id;
                document.getElementById('next-btn-1').disabled = false;
                
                // Подсвечиваем выбранный элемент
                document.querySelectorAll('.equipment-item').forEach(item => {
                    item.classList.remove('selected');
                });
                document.querySelector(`[data-equipment-id="${id}"]`).classList.add('selected');
                
                // Показываем информацию о выбранном оборудовании
                const item = document.querySelector(`[data-equipment-id="${id}"]`);
                const header = item.querySelector('.equipment-header').textContent;
                document.getElementById('search-results').innerHTML = 
                    `<div class="alert alert-success">Выбрано: ${header}</div>`;
            }
            
            function showCreateForm() {
                document.getElementById('create-form').style.display = 'block';
            }
            
            function hideCreateForm() {
                document.getElementById('create-form').style.display = 'none';
            }
            
            function reserveNumbers() {
                if (!selectedEquipmentId) {
                    alert('Сначала выберите оборудование');
                    return;
                }
                
                const count = document.getElementById('requested-count').value;
                const formData = new FormData();
                formData.append('equipment_id', selectedEquipmentId);
                formData.append('requested_count', count);
                
                fetch('/sessions', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(html => {
                    document.getElementById('reserve-result').innerHTML = html;
                    // Извлекаем session_id и номера из ответа
                    const match = html.match(/Сессия: <b>([^<]+)<\/b>/);
                    if (match) {
                        currentSessionId = match[1];
                        document.getElementById('next-btn-2').disabled = false;
                    }
                });
            }
            
            function assignNextNumber() {
                if (!currentSessionId) {
                    alert('Сначала зарезервируйте номера');
                    return;
                }
                
                const docName = document.getElementById('doc-name').value;
                const docNote = document.getElementById('doc-note').value;
                
                if (!docName || !docNote) {
                    alert('Заполните наименование и примечание');
                    return;
                }
                
                const formData = new FormData();
                formData.append('session_id', currentSessionId);
                formData.append('doc_name', docName);
                formData.append('doc_note', docNote);
                
                fetch('/documents/assign-one', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.text())
                .then(html => {
                    // Добавляем новую строку в таблицу
                    const tbody = document.getElementById('documents-table');
                    tbody.insertAdjacentHTML('beforeend', html);
                });
            }
            
            function completeSession() {
                if (!currentSessionId) {
                    alert('Нет активной сессии');
                    return;
                }
                
                if (confirm('Завершить сессию?')) {
                    fetch(`/sessions/${currentSessionId}/complete`, {
                        method: 'POST'
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            nextStep();
                        }
                    });
                }
            }
            
            function showReport() {
                // Показываем отчет с фильтрами
                const params = new URLSearchParams();
                const stationObject = document.getElementById('report-station-object').value;
                const stationNo = document.getElementById('report-station-no').value;
                const label = document.getElementById('report-label').value;
                const factoryNo = document.getElementById('report-factory-no').value;
                
                if (stationObject) {
                    // Разбиваем на отдельные значения для множественного выбора
                    const stations = stationObject.split(',').map(s => s.trim()).filter(s => s);
                    stations.forEach(station => params.append('station_object', station));
                }
                if (stationNo) params.append('station_no', stationNo);
                if (label) params.append('label', label);
                if (factoryNo) params.append('factory_no', factoryNo);
                
                document.getElementById('report-content').innerHTML = 
                    '<div class="alert alert-info">Отчет загружается...</div>';
                
                fetch(`/reports?${params.toString()}`)
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('report-content').innerHTML = html;
                    })
                    .catch(error => {
                        document.getElementById('report-content').innerHTML = 
                            '<div class="alert alert-danger">Ошибка загрузки отчета</div>';
                    });
            }
            
            function exportExcel() {
                // Экспорт в Excel с фильтрами
                const params = new URLSearchParams();
                const stationObject = document.getElementById('report-station-object').value;
                const stationNo = document.getElementById('report-station-no').value;
                const label = document.getElementById('report-label').value;
                const factoryNo = document.getElementById('report-factory-no').value;
                
                if (stationObject) {
                    const stations = stationObject.split(',').map(s => s.trim()).filter(s => s);
                    stations.forEach(station => params.append('station_object', station));
                }
                if (stationNo) params.append('station_no', stationNo);
                if (label) params.append('label', label);
                if (factoryNo) params.append('factory_no', factoryNo);
                
                window.open(`/reports/excel?${params.toString()}`, '_blank');
            }
            
            function restartWizard() {
                // Сброс всех данных и возврат к первому шагу
                selectedEquipmentId = null;
                currentSessionId = null;
                reservedNumbers = [];
                showStep(1);
                document.getElementById('search-results').innerHTML = '';
                document.getElementById('reserve-result').innerHTML = '';
                document.getElementById('documents-table').innerHTML = '';
                document.getElementById('report-content').innerHTML = '';
                document.getElementById('next-btn-1').disabled = true;
                document.getElementById('next-btn-2').disabled = true;
            }
            
            function suggestDocNames(query) {
                if (query.length < 2) return;
                
                fetch(`/suggest/doc-names?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(suggestions => {
                        const datalist = document.getElementById('doc-names-list');
                        datalist.innerHTML = '';
                        suggestions.forEach(suggestion => {
                            const option = document.createElement('option');
                            option.value = suggestion;
                            datalist.appendChild(option);
                        });
                    });
            }
            
            function suggestNotes(query) {
                if (query.length < 2) return;
                
                fetch(`/suggest/notes?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(suggestions => {
                        const datalist = document.getElementById('notes-list');
                        datalist.innerHTML = '';
                        suggestions.forEach(suggestion => {
                            const option = document.createElement('option');
                            option.value = suggestion;
                            datalist.appendChild(option);
                        });
                    });
            }
        </script>
    </body>
    </html>
    """)
