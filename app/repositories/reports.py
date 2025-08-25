from __future__ import annotations

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.equipment import Equipment
from app.models.user import User


class ReportsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch(self, station_objects: list[str] | None, date_from, date_to):
        stmt = (
            select(
                Document.numeric,
                Document.reg_date,
                Document.doc_name,
                Document.note,
                Equipment.eq_type,
                Equipment.factory_no,
                Equipment.order_no,
                Equipment.label,
                Equipment.station_no,
                Equipment.station_object,
                User.last_name,
                User.first_name,
                User.middle_name,
                User.department,
                User.username,
            )
            .join(Equipment, Equipment.id == Document.equipment_id)
            .join(User, User.id == Document.user_id)
        )
        where = []
        if station_objects:
            where.append(Equipment.station_object.in_(station_objects))
        if date_from:
            where.append(Document.reg_date >= date_from)
        if date_to:
            where.append(Document.reg_date <= date_to)
        if where:
            stmt = stmt.where(and_(*where))
        stmt = stmt.order_by(Document.reg_date.asc(), Document.numeric.asc())
        res = await self.session.execute(stmt)
        return res.fetchall()

    async def fetch_extended(
        self, 
        station_objects: list[str] | None, 
        station_no: str | None,
        label: str | None,
        factory_no: str | None,
        date_from, 
        date_to
    ):
        """Расширенный поиск с дополнительными фильтрами"""
        stmt = (
            select(
                Document.numeric,
                Document.reg_date,
                Document.doc_name,
                Document.note,
                Equipment.eq_type,
                Equipment.factory_no,
                Equipment.order_no,
                Equipment.label,
                Equipment.station_no,
                Equipment.station_object,
                User.username,
            )
            .join(Equipment, Equipment.id == Document.equipment_id)
            .join(User, User.id == Document.user_id)
        )
        where = []
        if station_objects:
            where.append(Equipment.station_object.in_(station_objects))
        if station_no:
            where.append(Equipment.station_no.ilike(f"%{station_no}%"))
        if label:
            where.append(Equipment.label.ilike(f"%{label}%"))
        if factory_no:
            where.append(Equipment.factory_no.ilike(f"%{factory_no}%"))
        if date_from:
            where.append(Document.reg_date >= date_from)
        if date_to:
            where.append(Document.reg_date <= date_to)
        if where:
            stmt = stmt.where(and_(*where))
        stmt = stmt.order_by(Document.reg_date.asc(), Document.numeric.asc())
        res = await self.session.execute(stmt)
        return res.fetchall()
