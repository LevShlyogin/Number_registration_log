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
            /* Стили для золотых номеров */
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
                <!-- ... Индикаторы шагов без изменений ... -->
            </div>
            
            <!-- Шаг 1: Поиск/Создание оборудования (без изменений) -->
            <div class="wizard-step active" id="step-1">
                 <!-- ... HTML Шага 1 остается без изменений ... -->
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
            
            <!-- Шаг 3: Назначение номеров (без изменений) -->
            <div class="wizard-step" id="step-3">
                <!-- ... HTML Шага 3 остается без изменений ... -->
            </div>
            
            <!-- Шаг 4: Отчет (без изменений) -->
            <div class="wizard-step" id="step-4">
                <!-- ... HTML Шага 4 остается без изменений ... -->
            </div>
        </div>
        
        <script>
            let currentStep = 1;
            let selectedEquipmentId = null;
            let currentSessionId = null;
            let reservedNumbers = [];
            
            // ... Функции showStep, nextStep, prevStep, searchEquipment, selectEquipment, etc. остаются без изменений ...

            function reserveNumbers() {
                // ... Логика обычного резерва остается без изменений ...
            }

            // ### НОВАЯ ФУНКЦИЯ: Показать золотые номера ###
            function suggestGoldenNumbers() {
                const resultsDiv = document.getElementById('golden-numbers-result');
                resultsDiv.innerHTML = '<div class="alert alert-info">Поиск золотых номеров...</div>';

                fetch('/admin/golden-suggest?limit=20') // Запрашиваем 20 номеров для выбора
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
                            html += `
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" value="${num}" id="golden-${num}">
                                    <label class="form-check-label" for="golden-${num}">
                                        ${formattedNum}
                                    </label>
                                </div>
                            `;
                        });
                        html += '</div>';
                        html += '<button class="btn btn-success mt-3" onclick="reserveGoldenNumbers()">Зарезервировать выбранные</button>';
                        
                        resultsDiv.innerHTML = html;
                    })
                    .catch(error => {
                        resultsDiv.innerHTML = '<div class="alert alert-danger">Ошибка при поиске золотых номеров.</div>';
                    });
            }

            // ### НОВАЯ ФУНКЦИЯ: Зарезервировать выбранные золотые номера ###
            function reserveGoldenNumbers() {
                if (!selectedEquipmentId) {
                    alert('Сначала выберите оборудование на Шаге 1.');
                    return;
                }

                const selectedCheckboxes = document.querySelectorAll('#golden-numbers-result input[type="checkbox"]:checked');
                const numbersToReserve = Array.from(selectedCheckboxes).map(cb => cb.value);

                if (numbersToReserve.length === 0) {
                    alert('Выберите хотя бы один золотой номер для резерва.');
                    return;
                }

                const formData = new FormData();
                formData.append('equipment_id', selectedEquipmentId);
                formData.append('numbers', numbersToReserve.join(',')); // Отправляем как строку через запятую

                document.getElementById('golden-reserve-status').innerHTML = '<div class="alert alert-info">Резервирование...</div>';
                
                fetch('/admin/reserve-specific', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(err => { throw new Error(err.detail || 'Ошибка сервера'); });
                    }
                    return response.json();
                })
                .then(data => {
                    const html = `
                        <div class="alert alert-success">
                            <strong>Сессия для золотых номеров создана!</strong><br/>
                            ID: ${data.session_id}<br/>
                            Зарезервировано: ${numbersToReserve.join(', ')}
                        </div>
                    `;
                    document.getElementById('golden-reserve-status').innerHTML = html;
                    
                    // Прячем обычный блок резерва, чтобы не было путаницы
                    document.getElementById('reserve-result').innerHTML = '';

                    // Сохраняем session_id и активируем кнопку "Далее"
                    currentSessionId = data.session_id;
                    document.getElementById('next-btn-2').disabled = false;
                })
                .catch(error => {
                    document.getElementById('golden-reserve-status').innerHTML = 
                        `<div class="alert alert-danger">Ошибка при резерве: ${error.message}</div>`;
                });
            }
            
            // ... (остальные JS-функции: assignNextNumber, completeSession, etc. без изменений) ...

            // ### ИЗМЕНЕНО: Проверка прав админа ###
            document.addEventListener('DOMContentLoaded', function() {
                // Проверяем, является ли пользователь админом через API
                fetch('/admin/check-access')
                    .then(response => {
                        if (response.ok) {
                            // Показываем кнопку перехода в админ-панель
                            document.getElementById('admin-panel-button').style.display = 'block';
                            // Показываем секцию для резерва золотых номеров на шаге 2
                            document.getElementById('admin-golden-numbers-section').style.display = 'block';
                        }
                    })
                    .catch(() => {
                        // Игнорируем ошибки - просто не показываем админские элементы
                    });
            });
        </script>
    </body>
    </html>
    """)
