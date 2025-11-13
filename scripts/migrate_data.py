# -*- coding: utf-8 -*-
"""
Excel -> PostgreSQL migration
Run: poetry run python scripts/migrate_data.py
"""

import os
import sys
import re
import logging
from pathlib import Path
from typing import Dict, Tuple

from sqlalchemy import text

import pandas as pd
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

# Project path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Models
from app.models.user import User
from app.models.equipment import Equipment
from app.models.document import Document

# Logging
log_file = project_root / "scripts" / "migration.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file, mode="w"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def resolve_db_url() -> str:
    """Get sync SQLAlchemy URL. Prefer DATABASE_URL; fallback to POSTGRES_*."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url.replace("+asyncpg", "")
    host = os.getenv("POSTGRES_SERVER") or os.getenv("POSTGRES_HOST") or "localhost"
    port = os.getenv("POSTGRES_PORT") or "5432"
    user = os.getenv("POSTGRES_USER")
    pwd = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    if not all([user, pwd, db]):
        raise RuntimeError(
            "Missing DB env. Set DATABASE_URL or POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB"
        )
    return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"


def normalize_int_str(value: object) -> str:
    """Return clean integer string from messy excel cell like '21501', '21501.0', ' 21501 '."""
    s = str(value).strip()
    if not s or s.lower() in ("nan", "none"):
        return ""
    # Try float -> int -> str
    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
    except Exception:
        pass
    # Fallback to first digit sequence
    m = re.search(r"\d+", s)
    return m.group(0) if m else ""


def normalize_factory_no(value: object) -> str:
    """Нормализация заводского номера для оборудования/документов."""
    s = normalize_int_str(value)
    # все «пустые» и '0' приводим к единому плейсхолдеру '00000'
    if s in ("", "0"):
        return "00000"
    return s


def load_users(session: Session, path: str) -> None:
    logger.info(f"Loading users from {path}")
    # engine=xlrd for .xls
    df = pd.read_excel(path, dtype=str, engine="xlrd").fillna("")
    col_map = {
        "Имя пользователя": "username",
        "Фамилия": "last_name",
        "Имя": "first_name",
        "Отчество": "middle_name",
        "Отдел": "department",
    }
    df = df.rename(columns=col_map)
    for c in ["username", "last_name", "first_name", "middle_name", "department"]:
        if c not in df.columns:
            df[c] = ""
    df["username"] = df["username"].str.strip().str.lower()

    records = df[["username", "last_name", "first_name", "middle_name", "department"]].to_dict("records")
    # Default migration user
    records.append(
        {
            "username": "migration_user",
            "last_name": "System",
            "first_name": "Migration",
            "middle_name": "",
            "department": "IT",
        }
    )
    if not records:
        logger.warning("No users to insert")
        return

    stmt = insert(User).values(records).on_conflict_do_nothing(index_elements=["username"])
    res = session.execute(stmt)
    session.commit()
    logger.info(f"Users processed: {len(records)}, inserted: {res.rowcount}")


def build_orders_map_from_excel(xlsx_path: str) -> Dict[str, str]:
    """Собирает map: последние 5 цифр -> полный номер заказа. Не включает '00000'."""
    xl = pd.ExcelFile(xlsx_path)
    # ищем лист по точному совпадению или по подстроке
    sheet = next((s for s in xl.sheet_names if s.strip().lower() == 'номер заказов' or 'заказ' in s.lower()), None)
    if not sheet:
        logger.warning("Orders sheet not found, skip orders mapping")
        return {}

    df = xl.parse(sheet, dtype=str).fillna('')
    # ищем колонку с номером заказа
    col = next((c for c in df.columns if '№ производственного заказа' in c.lower() or 'заказ' in c.lower()), None)
    if not col:
        logger.warning("Orders column not found, skip orders mapping")
        return {}

    df = df.rename(columns={col: 'order_no'})

    orders: Dict[str, str] = {}
    pat = re.compile(r'(\d{5})\D*$')  # последние 5 цифр перед концом строки
    for _, r in df.iterrows():
        order = str(r.get('order_no', '')).strip()
        if not order:
            continue
        m = pat.search(order)
        if m:
            last5 = m.group(1)
            if last5 == "00000":  # не присваиваем заказы плейсхолдеру
                continue
            orders[last5] = order
    return orders

def update_order_numbers(session: Session, xlsx_path: str, overwrite_incorrect: bool = True) -> Tuple[int, int]:
    """
    Обновляет equipment.order_no по последним 5 цифрам заказа.
    - overwrite_incorrect=True: очистит order_no, где последние 5 цифр не совпадают с factory_no
    Возвращает: (updated, cleaned)
    """
    orders = build_orders_map_from_excel(xlsx_path)
    if not orders:
        return (0, 0)

    updated = 0
    for last5, full in orders.items():
        res = session.execute(
            text("""
                UPDATE equipment
                SET order_no = :order
                WHERE factory_no = :last5
            """),
            {"order": full, "last5": last5},
        )
        updated += res.rowcount

    cleaned = 0
    if overwrite_incorrect:
        res = session.execute(
            text("""
                UPDATE equipment
                SET order_no = NULL
                WHERE order_no IS NOT NULL
                  AND substring(order_no from '(\d{5})\\D*$') <> factory_no
            """)
        )
        cleaned = res.rowcount

    session.commit()
    return (updated, cleaned)

def unify_placeholder_equipment(session: Session) -> Tuple[int, int]:
    """
    Переводит все ссылки с equipment.factory_no='0' на '00000' и удаляет '0'.
    Возвращает: (docs_relinked, eq_deleted)
    """
    # id '00000'
    q = session.execute(select(Equipment.id).where(Equipment.factory_no == "00000"))
    id_00000 = q.scalar_one_or_none()

    # id '0'
    q = session.execute(select(Equipment.id).where(Equipment.factory_no == "0"))
    id_zero = q.scalar_one_or_none()

    if not id_zero:
        return (0, 0)

    if not id_00000:
        # если нет 00000 — просто переименуем '0' -> '00000'
        session.execute(text("UPDATE equipment SET factory_no='00000' WHERE id=:id"), {"id": id_zero})
        session.commit()
        return (0, 0)

    # есть обе записи: переназначаем документы и удаляем '0'
    res = session.execute(text("UPDATE documents SET equipment_id=:to_id WHERE equipment_id=:from_id"),
                          {"to_id": id_00000, "from_id": id_zero})
    docs = res.rowcount or 0

    # если у вас есть таблица sessions с FK на equipment — тоже переназначьте при необходимости:
    try:
        res = session.execute(text("UPDATE sessions SET equipment_id=:to_id WHERE equipment_id=:from_id"),
                              {"to_id": id_00000, "from_id": id_zero})
    except Exception:
        pass

    session.execute(text("DELETE FROM equipment WHERE id=:id"), {"id": id_zero})
    session.commit()

    return (docs, 1)

def load_equipment(session: Session, path: str) -> None:
    logger.info(f"Loading equipment from {path}")

    df_t = pd.read_excel(path, sheet_name="Турбины УТЗ", dtype=str).fillna("")
    df_t = df_t.rename(columns={
        "Зав№": "factory_no",
        "Маркировка турбины": "label",
        "Наименование станции": "station_object",
        "Станц. №": "station_no",
    })
    df_t["factory_no"] = df_t["factory_no"].map(normalize_factory_no)
    df_t["eq_type"] = "Турбина"

    # входные дубли по factory_no -> удаляем
    df_t = df_t.drop_duplicates(subset=["factory_no"])

    # существующие в БД
    existing_fns = {fn for (fn,) in session.execute(select(Equipment.factory_no)).all() if fn}

    # собираем к вставке только новые factory_no
    eq_records = []
    for _, r in df_t.iterrows():
        fn = (r.get("factory_no") or "").strip()
        if not fn or fn in existing_fns:
            continue
        eq_records.append({
            "factory_no": fn,
            "label": r.get("label") or None,
            "station_object": r.get("station_object") or None,
            "station_no": r.get("station_no") or None,
            "eq_type": "Турбина",
            "notes": None,
        })

    # плейсхолдер 00000 (если нет)
    if "00000" not in existing_fns and not any(x["factory_no"] == "00000" for x in eq_records):
        eq_records.append({
            "factory_no": "00000",
            "eq_type": "Вспомогательное оборудование",
            "label": "General/Unlinked",
            "station_object": None,
            "station_no": None,
            "notes": "Auto-created for documents without factory_no",
        })

    inserted = 0
    if eq_records:
        res = session.execute(insert(Equipment).values(eq_records))
        session.commit()
        inserted = res.rowcount or 0

    logger.info(f"Equipment processed: {len(df_t)}, inserted: {inserted}")

    # после вставки: проставим/исправим orders для всех
    updated, cleaned = update_order_numbers(session, path, overwrite_incorrect=True)
    logger.info(f"Orders updated: {updated}, cleaned mismatches: {cleaned}")

    # почистим '0' -> '00000' (если вдруг осталось от прошлых запусков)
    docs_relinked, eq_deleted = unify_placeholder_equipment(session)
    if docs_relinked or eq_deleted:
        logger.info(f"Unified placeholder equipment: docs relinked={docs_relinked}, eq_deleted={eq_deleted}")


def load_documents(session: Session, path: str) -> None:
    import re
    logger.info(f"Loading documents from {path}")
    df = pd.read_excel(path, dtype=str).fillna("")

    # кеш уже существующих numeric (int)
    existing_nums = {n for (n,) in session.execute(select(Document.numeric)).all()}

    # equipment cache
    rows = session.execute(select(Equipment.id, Equipment.factory_no)).all()
    eq_cache: Dict[str, int] = {fn: eid for (eid, fn) in rows if fn}

    # default user
    default_user_id = session.execute(
        select(User.id).where(User.username == "migration_user")
    ).scalar_one_or_none()
    if not default_user_id:
        raise RuntimeError("migration_user is not found")

    to_add = []
    skipped = 0
    virt_created = 0

    for idx, row in df.iterrows():
        # 1) Обозначение -> извлекаем цифры: УТЗ-300031 -> 300031
        designation = str(row.get("Обозначение", "")).strip()
        m = re.search(r"(\d+)", designation)
        if not m:
            skipped += 1
            continue
        numeric = int(m.group(1))
        if numeric in existing_nums:
            skipped += 1
            continue

        # 2) Наименование -> в doc_name
        title = str(row.get("Наименование", "")).strip()
        doc_name = title or f"DOC-{numeric}"

        # 3) Примечание -> в note (только примечание)
        prim = str(row.get("Примечание", "")).strip()
        note = prim or None

        # 4) Привязка к оборудованию
        factory_raw = row.get("Зав.№ турбины первичного применения", "")
        factory_no = normalize_int_str(factory_raw)

        eq_id = None
        if factory_no and factory_no != "00000":
            eq_id = eq_cache.get(factory_no)
        if not eq_id:
            # запасной путь: плейсхолдер "00000"
            eq_id = eq_cache.get("00000")
            if not eq_id:
                virt_no = f"VIRT-DOC-{numeric}"
                if virt_no not in eq_cache:
                    veq = Equipment(
                        eq_type="Вспомогательное оборудование",
                        factory_no=virt_no,
                        label=f"Virtual for {doc_name}",
                        notes=f"Created for document #{numeric}",
                    )
                    session.add(veq)
                    session.flush()
                    eq_cache[virt_no] = veq.id
                    virt_created += 1
                eq_id = eq_cache[virt_no]

        to_add.append(
            {
                "numeric": numeric,
                "doc_name": doc_name,
                "note": note,
                "equipment_id": eq_id,
                "user_id": default_user_id,
            }
        )

    if to_add:
        # игнорируем любой уникальный конфликт (и по numeric, и по составному UQ)
        stmt = insert(Document).values(to_add).on_conflict_do_nothing()
        res = session.execute(stmt)
        session.commit()
        logger.info(
            f"Documents prepared: {len(to_add)}, inserted: {res.rowcount}, "
            f"skipped: {skipped}, virtual_eq_created: {virt_created}"
        )
    else:
        logger.info("No documents to insert")
        
        
from sqlalchemy import func

def bump_counter_after_import(session: Session) -> int:
    """Сдвигает счётчик на первое безопасное значение после импортированных документов."""
    max_num = session.execute(select(func.max(Document.numeric))).scalar()
    if not max_num:
        # в базе ещё нет документов — ничего не делаем
        return 0

    next_start = int(max_num) + 1
    # избегаем “золотых”
    if next_start % 100 == 0:
        next_start += 1

    # гарантированно создаём/обновляем строку счётчика с id=1
    session.execute(text("""
        INSERT INTO doc_counter (id, base_start, next_normal_start)
        VALUES (1, :n, :n)
        ON CONFLICT (id) DO UPDATE
        SET base_start = EXCLUDED.base_start,
            next_normal_start = EXCLUDED.next_normal_start
    """), {"n": next_start})
    session.commit()
    logger.info(f"DocCounter set to {next_start}")
    return next_start


def main() -> int:
    files = {
        "users": project_root / "data" / "Копия Актуальный список пользователей СКБт.xls",
        "equipment": project_root / "data" / "Копия Паровые Турбины.xlsx",
        "documents": project_root / "data" / "Копия Номера до 20к.xlsx",
    }
    # Check files exist
    for name, p in files.items():
        if not p.exists():
            print(f"ERROR: missing file {p}")
            return 1

    db_url = resolve_db_url()
    engine = create_engine(db_url, pool_pre_ping=True)

    with Session(engine) as session:
        load_users(session, str(files["users"]))
        load_equipment(session, str(files["equipment"]))
        load_documents(session, str(files["documents"]))
        bump_counter_after_import(session)

    print("Migration finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())