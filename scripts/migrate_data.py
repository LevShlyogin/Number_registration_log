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


def load_equipment(session: Session, path: str) -> None:
    logger.info(f"Loading equipment from {path}")
    df_t = pd.read_excel(path, sheet_name="Турбины УТЗ", dtype=str).fillna("")
    df_t = df_t.rename(
        columns={
            "Зав№": "factory_no",
            "Маркировка турбины": "label",
            "Наименование станции": "station_object",
            "Станц. №": "station_no",
        }
    )
    df_t["factory_no"] = df_t["factory_no"].map(normalize_int_str)
    df_t["eq_type"] = "Турбина"

    eq_records = df_t[["factory_no", "label", "station_object", "station_no", "eq_type"]].to_dict("records")

    # Placeholder for docs without factory_no
    eq_records.append(
        {
            "factory_no": "00000",
            "eq_type": "Вспомогательное оборудование",
            "label": "General/Unlinked",
            "station_object": None,
            "station_no": None,
            "notes": "Auto-created for documents without factory_no",
        }
    )

    # Orders mapping: last 5 digits -> order_no
    try:
        df_o = pd.read_excel(path, sheet_name="Номер Заказов", dtype=str).fillna("")
        df_o = df_o.rename(columns={"№ производственного заказа": "order_no"})
        orders_map: Dict[str, str] = {}
        for _, r in df_o.iterrows():
            order = str(r.get("order_no", "")).strip()
            if not order:
                continue
            m = re.search(r"(\d{5})(?:\D|$)", order)
            if m:
                orders_map[m.group(1)] = order
        for item in eq_records:
            fn = (item.get("factory_no") or "").strip()
            if fn in orders_map:
                item["order_no"] = orders_map[fn]
    except Exception as e:
        logger.warning(f"Orders sheet not applied: {e}")

    stmt = insert(Equipment).values(eq_records).on_conflict_do_nothing(index_elements=["factory_no"])
    res = session.execute(stmt)
    session.commit()
    logger.info(f"Equipment processed: {len(eq_records)}, inserted: {res.rowcount}")


def load_documents(session: Session, path: str) -> None:
    logger.info(f"Loading documents from {path}")
    df = pd.read_excel(path, dtype=str).fillna("")

    existing_nums = {n for (n,) in session.execute(select(Document.numeric)).all()}
    rows = session.execute(select(Equipment.id, Equipment.factory_no)).all()
    eq_cache: Dict[str, int] = {fn: eid for (eid, fn) in rows if fn}

    default_user_id = session.execute(
        select(User.id).where(User.username == "migration_user")
    ).scalar_one_or_none()
    if not default_user_id:
        raise RuntimeError("migration_user is not found")

    to_add = []
    skipped = 0
    virt_created = 0

    for idx, row in df.iterrows():
        raw_num = str(row.get("№ п/п", "")).strip()
        if not raw_num.isdigit():
            skipped += 1
            continue
        numeric = int(raw_num)
        if numeric in existing_nums:
            skipped += 1
            continue

        doc_name = str(row.get("Обозначение", "")).strip() or f"DOC-{numeric}"
        title = str(row.get("Наименование", "")).strip()
        note_extra = str(row.get("Примечание", "")).strip()
        note = " | ".join([p for p in [title, note_extra] if p]) or None

        factory_raw = row.get("Зав.№ турбины первичного применения", "")
        factory_no = normalize_int_str(factory_raw)

        eq_id = None
        if factory_no and factory_no != "00000":
            eq_id = eq_cache.get(factory_no)

        if not eq_id:
            # Try placeholder
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
        stmt = insert(Document).values(to_add).on_conflict_do_nothing(index_elements=["numeric"])
        res = session.execute(stmt)
        session.commit()
        logger.info(
            f"Documents prepared: {len(to_add)}, inserted: {res.rowcount}, "
            f"skipped: {skipped}, virtual_eq_created: {virt_created}"
        )
    else:
        logger.info("No documents to insert")


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

    print("Migration finished")
    return 0


if __name__ == "__main__":
    sys.exit(main())