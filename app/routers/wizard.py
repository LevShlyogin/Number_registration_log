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
            /* ### НОВЫЕ СТИЛИ для золотых номеров ### */
            .golden-number-list {
                max-height: 200px;
                overflow-y: auto;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 5px;
            }
            .golden-number-list .form-check-label {
                font-weight: bold;
                color: #b8860b;
            }
        </style>
    </head>
    <body>
        <div class="container mt-4">
            <h1>Регистрация номеров документов</h1>
            
            <!-- Кнопка для админской панели -->
            <div id="admin-panel-button" style="display: none; margin-bottom: 20px;">
                <button class="btn btn-danger" onclick="window.location.href='/admin-dashboard/dashboard'">
                    🔧 Админская панель
                </button>
            </div>
            
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
                                   placeholder="Например: 3">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Маркировка</label>
                            <input type="text" class="form-control" id="search-label" 
                                   placeholder="Например: Т-110">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">№ заводской</label>
                            <input type="text" class="form-control" id="search-factory-no" 
                                   placeholder="Например: 12345">
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">№ заказа</label>
                            <input type="text" class="form-control" id="search-order-no" 
                                   placeholder="Например: 12345-67-89876">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <label class="form-label">Поиск по тексту</label>
                            <input type="text" class="form-control" id="search-q" 
                                   placeholder="Введите текст для поиска по всем полям">
                        </div>
                    </div>
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

                <!-- ### НОВЫЙ БЛОК: Функционал для админа ### -->
                <div id="admin-golden-numbers-section" style="display: none; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd;">
                    <h4>Резерв золотых номеров (для админа)</h4>
                    <p class="text-muted">Этот блок виден только администраторам.</p>
                    <div class="mb-3">
                        <button class="btn btn-warning" onclick="suggestGoldenNumbers()">
                            Показать свободные золотые номера
                        </button>
                    </div>
                    <div id="golden-numbers-result" class="mb-3"></div>
                    <div id="golden-reserve-status"></div>
                </div>
                <!-- ### КОНЕЦ НОВОГО БЛОКА ### -->
                
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
                            <label class="form-label">Примечание (необязательно)</label>
                            <input type="text" class="form-control" id="doc-note" 
                                   placeholder="Введите примечание (можно оставить пустым)">
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
                                       placeholder="Например: 3">
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
                                       placeholder="Например: 12345">
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">№ заказа</label>
                                <input type="text" class="form-control" id="report-order-no" 
                                       placeholder="Например: 12345-67-89876">
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
                document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
                document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
                document.getElementById(`step-${step}`).classList.add('active');
                document.getElementById(`step-${step}-indicator`).classList.add('active');
                for (let i = 1; i < step; i++) {
                    document.getElementById(`step-${i}-indicator`).classList.add('completed');
                }
                currentStep = step;
            }
            
            function nextStep() { if (currentStep < 4) { showStep(currentStep + 1); } }
            function prevStep() { if (currentStep > 1) { showStep(currentStep - 1); } }
            
            function searchEquipment() {
                const params = new URLSearchParams();
                const fields = ['search-station-object', 'search-station-no', 'search-label', 'search-factory-no', 'search-order-no', 'search-q'];
                fields.forEach(id => {
                    const value = document.getElementById(id).value.trim();
                    if (value) {
                        const paramName = id.replace('search-', '');
                        params.append(paramName, value);
                    }
                });
                fetch(`/equipment/search?${params.toString()}`, { headers: { 'Hx-Request': 'true' } })
                    .then(response => response.text())
                    .then(html => { document.getElementById('search-results').innerHTML = html; })
                    .catch(error => { document.getElementById('search-results').innerHTML = `<div class="alert alert-danger">Ошибка поиска</div>`; });
            }
            
            function selectEquipment(id) {
                selectedEquipmentId = id;
                document.querySelectorAll('.equipment-item').forEach(item => item.classList.remove('selected'));
                const selectedItem = document.querySelector(`[data-equipment-id="${id}"]`);
                if (selectedItem) {
                    selectedItem.classList.add('selected');
                    const header = selectedItem.querySelector('.equipment-header').textContent;
                    document.getElementById('search-results').innerHTML = `<div class="alert alert-success">Выбрано: ${header}</div>`;
                } else {
                    document.getElementById('search-results').innerHTML = `<div class="alert alert-success">Выбрано оборудование с ID: ${id}</div>`;
                }
                document.getElementById('next-btn-1').disabled = false;
            }
            
            function showCreateForm() { document.getElementById('create-form').style.display = 'block'; }
            function hideCreateForm() { document.getElementById('create-form').style.display = 'none'; }
            
            function reserveNumbers() {
                if (!selectedEquipmentId) { alert('Сначала выберите оборудование'); return; }
                const count = document.getElementById('requested-count').value;
                const formData = new FormData();
                formData.append('equipment_id', selectedEquipmentId);
                formData.append('requested_count', count);
                fetch('/sessions', { method: 'POST', body: formData })
                    .then(response => response.json())
                    .then(data => {
                        const html = `<div class="alert alert-success"><strong>Сессия создана!</strong><br/>ID: ${data.session_id}<br/>Зарезервировано номеров: ${data.reserved_numbers.join(', ')}</div>`;
                        document.getElementById('reserve-result').innerHTML = html;
                        currentSessionId = data.session_id;
                        document.getElementById('next-btn-2').disabled = false;
                    })
                    .catch(error => { document.getElementById('reserve-result').innerHTML = `<div class="alert alert-danger">Ошибка при резерве номеров</div>`; });
            }

            // ### НОВАЯ ФУНКЦИЯ: Показать золотые номера ###
            function suggestGoldenNumbers() {
                const resultsDiv = document.getElementById('golden-numbers-result');
                resultsDiv.innerHTML = '<div class="alert alert-info">Поиск золотых номеров...</div>';
                fetch('/admin/golden-suggest?limit=20')
                    .then(response => response.json())
                    .then(data => {
                        const numbers = data.golden_numbers;
                        if (numbers.length === 0) {
                            resultsDiv.innerHTML = '<div class="alert alert-warning">Свободных золотых номеров не найдено.</div>';
                            return;
                        }
                        let html = '<div class="golden-number-list">';
                        numbers.forEach(num => {
                            const formattedNum = String(num).padStart(6, '0');
                            html += `<div class="form-check"><input class="form-check-input" type="checkbox" value="${num}" id="golden-${num}"><label class="form-check-label" for="golden-${num}">${formattedNum}</label></div>`;
                        });
                        html += '</div><button class="btn btn-success mt-3" onclick="reserveGoldenNumbers()">Зарезервировать выбранные</button>';
                        resultsDiv.innerHTML = html;
                    })
                    .catch(error => { resultsDiv.innerHTML = '<div class="alert alert-danger">Ошибка при поиске.</div>'; });
            }

            // ### НОВАЯ ФУНКЦИЯ: Зарезервировать выбранные золотые номера ###
            function reserveGoldenNumbers() {
                if (!selectedEquipmentId) { alert('Сначала выберите оборудование на Шаге 1.'); return; }
                const selectedCheckboxes = document.querySelectorAll('#golden-numbers-result input[type="checkbox"]:checked');
                const numbersToReserve = Array.from(selectedCheckboxes).map(cb => cb.value);
                if (numbersToReserve.length === 0) { alert('Выберите хотя бы один золотой номер.'); return; }
                const formData = new FormData();
                formData.append('equipment_id', selectedEquipmentId);
                formData.append('numbers', numbersToReserve.join(','));
                document.getElementById('golden-reserve-status').innerHTML = '<div class="alert alert-info">Резервирование...</div>';
                fetch('/admin/reserve-specific', { method: 'POST', body: formData })
                    .then(response => {
                        if (!response.ok) { return response.json().then(err => { throw new Error(err.detail || 'Ошибка сервера'); }); }
                        return response.json();
                    })
                    .then(data => {
                        const html = `<div class="alert alert-success"><strong>Сессия для золотых номеров создана!</strong><br/>ID: ${data.session_id}<br/>Зарезервировано: ${numbersToReserve.join(', ')}</div>`;
                        document.getElementById('golden-reserve-status').innerHTML = html;
                        document.getElementById('reserve-result').innerHTML = ''; // Прячем обычный блок
                        currentSessionId = data.session_id;
                        document.getElementById('next-btn-2').disabled = false;
                    })
                    .catch(error => { document.getElementById('golden-reserve-status').innerHTML = `<div class="alert alert-danger">Ошибка: ${error.message}</div>`; });
            }

            function assignNextNumber() {
                if (!currentSessionId) { alert('Сначала зарезервируйте номера'); return; }
                const docName = document.getElementById('doc-name').value;
                const docNote = document.getElementById('doc-note').value;
                if (!docName) { alert('Заполните наименование'); return; }
                const formData = new FormData();
                formData.append('session_id', currentSessionId);
                formData.append('doc_name', docName);
                if (docNote) formData.append('note', docNote);
                fetch('/documents/assign-one', { method: 'POST', headers: { 'Hx-Request': 'true' }, body: formData })
                    .then(response => response.text())
                    .then(html => { document.getElementById('documents-table').insertAdjacentHTML('beforeend', html); });
            }
            
            function completeSession() {
                if (!currentSessionId) { showStep(4); showReport(); return; }
                fetch(`/sessions/${currentSessionId}/complete`, { method: 'POST' })
                    .then(() => { showStep(4); showReport(); });
            }
            
            function showReport() {
                const params = new URLSearchParams();
                const fields = ['report-station-object', 'report-station-no', 'report-label', 'report-factory-no', 'report-order-no'];
                fields.forEach(id => {
                    const value = document.getElementById(id).value;
                    if (id === 'report-station-object' && value) {
                        const stations = value.split(',').map(s => s.trim()).filter(s => s);
                        stations.forEach(station => params.append('station_object', station));
                    } else if (value) {
                        const paramName = id.replace('report-', '');
                        params.append(paramName, value.trim());
                    }
                });
                document.getElementById('report-content').innerHTML = '<div class="alert alert-info">Отчет загружается...</div>';
                fetch(`/reports?${params.toString()}`, { headers: { 'Hx-Request': 'true' } })
                    .then(response => response.text())
                    .then(html => { document.getElementById('report-content').innerHTML = html; })
                    .catch(error => { document.getElementById('report-content').innerHTML = '<div class="alert alert-danger">Ошибка загрузки отчета</div>'; });
            }
            
            function exportExcel() {
                const params = new URLSearchParams();
                const fields = ['report-station-object', 'report-station-no', 'report-label', 'report-factory-no', 'report-order-no'];
                fields.forEach(id => {
                    const value = document.getElementById(id).value;
                    if (id === 'report-station-object' && value) {
                        const stations = value.split(',').map(s => s.trim()).filter(s => s);
                        stations.forEach(station => params.append('station_object', station));
                    } else if (value) {
                        const paramName = id.replace('report-', '');
                        params.append(paramName, value.trim());
                    }
                });
                window.open(`/reports/excel?${params.toString()}`, '_blank');
            }
            
            function restartWizard() {
                selectedEquipmentId = null;
                currentSessionId = null;
                reservedNumbers = [];
                showStep(1);
                const elementsToClear = ['search-results', 'reserve-result', 'documents-table', 'report-content', 'golden-numbers-result', 'golden-reserve-status'];
                elementsToClear.forEach(id => document.getElementById(id).innerHTML = '');
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
            
            // ### ИЗМЕНЕНО: Проверка прав админа ###
            document.addEventListener('DOMContentLoaded', function() {
                fetch('/admin/check-access')
                    .then(response => {
                        if (response.ok) {
                            // Показываем кнопку перехода в админ-панель
                            document.getElementById('admin-panel-button').style.display = 'block';
                            // Показываем секцию для резерва золотых номеров на шаге 2
                            document.getElementById('admin-golden-numbers-section').style.display = 'block';
                        }
                    })
                    .catch(() => { /* Игнорируем ошибки - просто не показываем админские элементы */ });
            });
        </script>
    </body>
    </html>
    """)
