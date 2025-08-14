--- README.md
# Журнал регистрации УТЗ

Стек: FastAPI (async), SQLAlchemy 2.0 (async), PostgreSQL 15+, Alembic, Pydantic v2, pydantic-settings, Jinja2+HTMX, openpyxl, APScheduler. Контейнеризация — Docker + docker-compose. Poetry.

## Запуск

1) Установите Docker и Docker Compose.
2) Склонируйте репозиторий. Создайте .env из шаблона:
```
cp .env.example .env
```
3) Поднимите окружение:
```
docker-compose up --build
```
4) Примените миграции (автоматически применяются при старте тестов; для ручного запуска внутри контейнера):
```
docker-compose exec api alembic upgrade head
```
5) Откройте http://localhost:8000 и передавайте заголовок X-User (например, через расширение/инструмент). В браузере можно использовать DevTools → Network → Request headers.

- Админы: vgrubtsov, yuaalekseeva, lrshlyogin, pyagavrilov.
- Пользователи: любые другие X-User.

UI:
- /ui/equipment — создание оборудования.
- /ui/session — резерв номеров и поштучное назначение документов.
- /ui/admin — подсказки по “золотым” и резерв конкретных номеров (для админа).
- /ui/reports — отчеты (фильтр по “Станция / Объект”, период опционально).

API (примеры):
- POST /equipment
- POST /sessions
- POST /sessions/{id}/cancel
- POST /documents/assign-one
- PATCH /documents/{id} (только админ)
- GET /reports (JSON), GET /reports/excel (Excel)
- GET /admin/golden-suggest, POST /admin/reserve-specific
- GET /suggest/doc-names, GET /suggest/equipment/{field}
- POST /import/excel (только админ)

## Нумерация
- Формат: `УТЗ-` + 6 цифр.
- “Золотые” номера: оканчиваются на “00” (numeric % 100 == 0).
- Обычные пользователи не могут резервировать “00” — они пропускаются.
- Админ может выбрать любые номера; отдельная подсказка свободных “00”.

## Резервы и TTL
- При старте сессии указывается N (по умолчанию 1) и TTL (по умолчанию 30 минут).
- Система резервирует пул из N номеров транзакционно. Параллельные запросы корректно конкурируют (SELECT FOR UPDATE, SKIP LOCKED).
- По отмене или TTL — номера освобождаются (released) и могут быть зарезервированы снова.

## Уникальность документов
- Уникальный индекс: (doc_name, note, equipment_id) на CITEXT-полях — регистронезависимо.
- При нарушении — сообщение: “Такой документ уже зарегистрирован”.

## Импорт из Excel
- POST /import/excel (multipart/form-data), только админ.
- После импорта doc_counter.base_start и next_normal_start = max(numeric)+1, “дыры” в истории не заполняются.
- Импорт ожидает русские заголовки колонок (см. ТЗ). Формат дат: dd.mm.yyyy или ISO.

## Отчеты
- Фильтр по списку “Станция / Объект” и/или периоду (если задан; иначе — по умолчанию: от начала недели до текущего времени).
- Excel с колонками: как в ТЗ + ФИО/Отдел (иначе username).

## Тесты
Запуск (локально в контейнере):
```
docker-compose exec api pytest -q
```

## Коллекция Postman/Bruno
Файл postman_collection.json в корне. Включает основные эндпоинты. Не забудьте добавить заголовок X-User в окружении коллекции.

--- postman_collection.json
{
  "info": {
    "name": "UTZ Journal API",
    "_postman_id": "e7a1b89d-5b1a-4f9d-9b8b-111122223333",
    "description": "Коллекция запросов к API Журнала регистрации",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Create Equipment",
      "request": {
        "method": "POST",
        "header": [{ "key": "X-User", "value": "tester" }],
        "url": { "raw": "http://localhost:8000/equipment", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["equipment"] },
        "body": { "mode": "raw", "raw": "{\"eq_type\":\"EQ\"}", "options": { "raw": { "language": "json" } } }
      }
    },
    {
      "name": "Start Session",
      "request": {
        "method": "POST",
        "header": [{ "key": "X-User", "value": "tester" }],
        "url": { "raw": "http://localhost:8000/sessions", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["sessions"] },
        "body": { "mode": "raw", "raw": "{\"equipment_id\":1,\"requested_count\":3}" }
      }
    },
    {
      "name": "Assign One",
      "request": {
        "method": "POST",
        "header": [{ "key": "X-User", "value": "tester" }],
        "url": { "raw": "http://localhost:8000/documents/assign-one", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["documents", "assign-one"] },
        "body": { "mode": "raw", "raw": "{\"session_id\":\"<fill>\",\"doc_name\":\"Док\",\"note\":\"Прим\"}" }
      }
    },
    {
      "name": "Admin Golden Suggest",
      "request": {
        "method": "GET",
        "header": [{ "key": "X-User", "value": "vgrubtsov" }],
        "url": { "raw": "http://localhost:8000/admin/golden-suggest?limit=5", "protocol": "http", "host": ["localhost"], "port": "8000", "path": ["admin", "golden-suggest"], "query": [{ "key": "limit", "value": "5" }] }
      }
    }
  ]
}

Проверка (демо‑сценарий)
- Импорт Excel:
  - Команда: docker-compose exec api python app/scripts/import_excel.py run var/imports/sample.xlsx
  - Ожидаемо: {"imported": X, "next_start": max_numeric+1}. Таблица doc_counter обновлена, новые номера продолжаются от next_start, “дыры” из истории не трогаются.

- Резерв обычным пользователем N=3, где встречается ХХХХ00:
  - Предварительно установите next_normal_start=…99 (после импорта либо несколькими резервами). Затем:
    - POST /sessions {equipment_id: <id>, requested_count: 3} (X-User: любой не-админ).
    - Вернется session_id и три числа, не оканчивающиеся на 00. Если в диапазоне попадал ХХХХ00, он пропущен.

- Админ получает список ближайших свободных ХХХХ00 и занимает один:
  - GET /admin/golden-suggest?limit=5 (X-User: vgrubtsov).
  - POST /admin/reserve-specific {equipment_id: <id>, numbers: [<какой-то ХХХХ00>]}.
  - Вернется session_id админской сессии с резервом.

- Попытка дублирования:
  - Создайте документ с doc_name="A", note="B", equipment_id=E.
  - Повторите assign-one с теми же значениями: ответ 409, “Такой документ уже зарегистрирован”.

- Экспорт отчета в Excel:
  - GET /reports/excel?station_object=Проект1
  - Ответ: {"path":"var/exports/report_YYYYMMDD_HHMMSS.xlsx"}
  - Колонки: в нужном порядке согласно ТЗ (см. utils/excel.py).

Допущения и ограничения
- TTL по умолчанию — 30 минут (конфигurable через DEFAULT_TTL_SECONDS). Планировщик подчищает каждые 60 секунд.
- В рамках одной сессии операция assign-one назначает один документ (следующий зарезервированный номер). Это связано с требованием уникальности (doc_name, note, equipment_id): массовое создание N документов с одинаковой комбинацией приведет к нарушению уникальности. Для создания нескольких документов используйте повторные вызовы assign-one с разными значениями doc_name/note.
- Импорт Excel ожидает русские заголовки, даты в dd.mm.yyyy или ISO. Недостающие ФИО/отдел — подставляется username.
- Поля таблиц в БД названы на английском; русские названия используются в UI, отчетах и сообщениях.
- Для простоты в импорте оборудование создается новой записью для каждой строки (не выполняется сложный поиск дублей по комбинации полей).
- Подсказки для оборудования реализованы минимально (distinct + ILIKE) и каскадно по station_object -> station_no/label; UI-примеры используют HTMX.
- Документы редактировать может только админ; изменения логируются в audit_logs (JSONB diff).
- Тесты покрывают ключевые сценарии и ориентированы на контейнерное окружение PostgreSQL.
