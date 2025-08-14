# Архитектура проекта

Проект: Журнал регистрации УТЗ  
Стек: FastAPI (async), SQLAlchemy 2.0 (async) + asyncpg, PostgreSQL 15+, Alembic, Pydantic v2, pydantic-settings, Jinja2 + HTMX, openpyxl, APScheduler. Контейнеризация: Docker + docker-compose. Управление зависимостями: Poetry.

- Слои: routers → services → repositories → models → db
- Валидация: Pydantic-схемы + ограничения БД (UNIQUE, FK, CHECK, ENUM)
- Идентификация: заголовок X-User; RBAC: список админов в конфиге
- Нумерация: таблицы doc_counter + doc_numbers; пропуск “золотых” (XX00) для обычных
- Конкурентность: SELECT FOR UPDATE, SKIP LOCKED, транзакции
- TTL резерва: освобождение фоном (APScheduler) или вручную

## Дерево каталогов

```text
.
├── app/
│   ├── core/                    # Базовая конфигурация приложения
│   │   ├── auth.py              # Идентификация по X-User, определение роли admin
│   │   ├── config.py            # pydantic-settings (.env)
│   │   └── db.py                # Async engine/session, фабрики сессий
│   ├── models/                  # ORM-модели SQLAlchemy
│   │   ├── base.py              # Declarative base, TimestampMixin
│   │   ├── user.py              # Пользователи (CITEXT username)
│   │   ├── equipment.py         # Оборудование
│   │   ├── counter.py           # DocCounter: base_start, next_normal_start
│   │   ├── session.py           # Сессии резервов (TTL, статус)
│   │   ├── doc_number.py        # doc_numbers: статусная модель резервов/использования
│   │   ├── document.py          # Документы (UNIQUE doc_name+note+equipment_id)
│   │   └── audit.py             # Аудит-лог изменений документов (JSONB diff)
│   ├── repositories/            # Доступ к БД (CRUD/квартеты запросов)
│   │   ├── users.py
│   │   ├── equipment.py
│   │   ├── counter.py
│   │   ├── sessions.py
│   │   ├── doc_numbers.py
│   │   ├── documents.py
│   │   ├── audit.py
│   │   └── reports.py
│   ├── schemas/                 # Pydantic v2 схемы (вход/выход API)
│   │   ├── common.py
│   │   ├── equipment.py
│   │   ├── sessions.py
│   │   ├── documents.py
│   │   ├── admin.py
│   │   └── reports.py
│   ├── services/                # Бизнес-логика и транзакции
│   │   ├── users.py
│   │   ├── equipment.py
│   │   ├── reservation.py       # Резервирование с пулом, skip golden, SELECT FOR UPDATE
│   │   ├── documents.py         # Назначение номера, уникальность, аудит
│   │   ├── admin.py             # Подсказки по “золотым”, резерв конкретных номеров
│   │   ├── reports.py           # Отчеты JSON/Excel
│   │   └── importer.py          # Импорт из Excel и установка base_start/next_normal_start
│   ├── utils/                   # Вспомогательные утилиты
│   │   ├── numbering.py         # Формат номера, проверка “золотого”
│   │   └── excel.py             # Генерация Excel (openpyxl)
│   ├── tasks/
│   │   └── cleanup.py           # Фоновая очистка TTL (APScheduler)
│   ├── routers/                 # FastAPI роутеры (слой API)
│   │   ├── equipment.py
│   │   ├── sessions.py
│   │   ├── documents.py
│   │   ├── admin.py
│   │   ├── reports.py
│   │   ├── suggest.py           # Подсказки (autocomplete)
│   │   └── importer.py          # Загрузка Excel (админ)
│   ├── templates/               # Минимальный UI (Jinja2 + HTMX)
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── equipment.html
│   │   ├── session.html
│   │   ├── admin.html
│   │   └── reports.html
│   ├── routers/ui.py            # Роуты UI-страниц
│   ├── scripts/
│   │   └── import_excel.py      # CLI-импорт Excel (typer)
│   └── main.py                  # FastAPI app, middleware, включение роутеров, старт задач
├── alembic/
│   ├── versions/
│   │   └── 0001_init.py         # Начальная миграция: все таблицы, ENUM, CITEXT, индексы
│   ├── env.py                   # Конфиг Alembic, URL из .env
│   └── script.py.mako           # Шаблон миграций
├── tests/                       # Pytest-тесты критичных сценариев
│   ├── conftest.py
│   ├── test_reservation_concurrency.py
│   ├── test_uniqueness.py
│   ├── test_golden.py
│   ├── test_ttl_release.py
│   └── test_report_excel.py
├── postman_collection.json      # Коллекция запросов Postman/Bruno
├── Dockerfile                   # Образ API (Poetry)
├── docker-compose.yml           # Сервисы: api + postgres
├── pyproject.toml               # Poetry, deps, black/isort/ruff конфиги
├── .env.example                 # Пример окружения (DATABASE_URL, TTL и пр.)
├── README.md                    # Инструкции по запуску и использованию
└── (runtime) var/exports/       # Папка для экспортируемых Excel (создается на лету)
```

## Роли и взаимодействие слоев

- routers: определяют HTTP-контракты, парсят входные данные (Pydantic), вызывают сервисы, формируют ответы/коды ошибок.
- services: инкапсулируют бизнес-правила, транзакции, последовательность вызовов репозиториев и проверок, обрабатывают ограничения уникальности и доменные ошибки.
- repositories: обращаются к БД (SQLAlchemy Core/ORM), выполняют SELECT/INSERT/UPDATE с нужными блокировками и опциями конкуренции (FOR UPDATE, SKIP LOCKED).
- models: ORM-сущности, типы и ограничения на уровне БД (UNIQUE, FK, CHECK/ENUM, CITEXT).
- core: конфигурация (.env), создание engine/session, упрощенная авторизация (X-User).
- tasks: фоновая очистка просроченных резервов (перевод sessions → expired, doc_numbers → released).
- utils: форматирование номера (УТЗ-******), работа с Excel.

## Ключевые сущности

- doc_counter: одна строка со смещениями нумерации:
  - base_start — база после импорта (max(existing)+1)
  - next_normal_start — указатель для монотонной нумерации новых не-“00” номеров
- doc_numbers: статусный реестр номеров (reserved/assigned/released) с привязкой к пользователю/сессии/TTL.
- documents: фактические записи журнала; UNIQUE по (lower(doc_name), lower(note), equipment_id); numeric уникален.
- sessions: сессии резервирования, TTL и статус (active/cancelled/completed/expired).
- audit_logs: история изменений полей документа (JSONB diff).

## Транзакционный сценарий резерва

- POST /sessions:
  - Release expired (doc_numbers), expire sessions — предшаг.
  - SELECT doc_counter FOR UPDATE.
  - Забираем released номера (SKIP LOCKED), для обычных — фильтруем ХХХХ00.
  - Если не хватило — создаем новые записи doc_numbers от next_normal_start, пропуская ХХХХ00 для обычных; двигаем next_normal_start.
  - Коммит.
- Обычным пользователям номера с окончанием “00” не попадают в пул; админам доступны (и отдельный эндпоинт выбора конкретных).

Наглядно:

```mermaid
sequenceDiagram
  participant U as User
  participant API as FastAPI (sessions)
  participant S as ReservationService
  participant DB as PostgreSQL

  U->>API: POST /sessions {equipment_id, N}
  API->>S: start_session()
  S->>DB: release expired
  S->>DB: expire sessions
  S->>DB: SELECT doc_counter FOR UPDATE
  S->>DB: SELECT released SKIP LOCKED
  alt not enough numbers
    S->>DB: INSERT doc_numbers (reserved)
    Note right of S: Skip ХХХХ00 for regular users
    S->>DB: UPDATE doc_counter.next_normal_start
  end
  S-->>API: session_id, reserved_numbers
  API-->>U: 200 OK
```

## RBAC и идентификация

- X-User обязателен. Пользователь создается автоматически при первом запросе.
- Роль admin — если username входит в список настроек (config.admin_users).
- Обычные не видят/не могут занять ХХХХ00; админы — могут, дополнительно получают подсказку ближайших свободных.

## Настройки окружения

- DATABASE_URL — postgresql+asyncpg://user:pass@host:port/db
- DEFAULT_TTL_SECONDS — дефолтный TTL резервов (например, 1800)
- APP_ENV — dev/prod

Файл .env.example — шаблон.

## Как добавить новый функционал (чек-лист)

1) Модель/миграция (при необходимости):
   - Добавить ORM-модель в app/models
   - Сгенерировать миграцию Alembic и применить

2) Схемы Pydantic:
   - app/schemas/<feature>.py

3) Репозиторий и сервис:
   - app/repositories/<feature>.py
   - app/services/<feature>.py (транзакции, бизнес-правила)

4) Роутер:
   - app/routers/<feature>.py и включить в app.main

5) Тесты:
   - tests/test_<feature>.py

6) Документация/UI (по необходимости):
   - app/templates/*.html (HTMX-фрагменты)
   - README/architecture.md — обновить при изменениях.

## Ключевые инварианты домена

- Формат номера: "УТЗ-" + zfill(6)
- “Золотые” номера: numeric % 100 == 0
- Монотонность нумерации после импорта: next_normal_start всегда двигается вперед; “дыры” истории не дозаполняем.
- Уникальность документа: (lower(doc_name), lower(note), equipment_id)
- Отчеты: фильтр по “Станция / Объект” (список), даты — опционально (по умолчанию: от начала недели до текущего момента).
- Excel-экспорт — с ФИО/Отдел, иначе fallback к username.

## Полезные пути

- UI: /ui/equipment, /ui/session, /ui/admin, /ui/reports
- API: /equipment, /sessions, /documents/assign-one, /admin/golden-suggest, /admin/reserve-specific, /reports, /reports/excel, /suggest/*, /import/excel
- Экспортируемые файлы: var/exports/*.xlsx (создается автоматически)

Если нужны дополнительные разделы (например, схема ER или sequence для редактирования документа), добавлю их сюда.
