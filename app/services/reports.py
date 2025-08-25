from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.reports import ReportsRepository
from app.utils.numbering import format_doc_no
from app.utils.excel import ReportExcelBuilder


class ReportsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = ReportsRepository(session)

    async def get_rows(self, station_objects: list[str] | None, date_from, date_to):
        rows = await self.repo.fetch(station_objects, date_from, date_to)
        payload = []
        for (
            numeric,
            reg_date,
            doc_name,
            note,
            eq_type,
            factory_no,
            order_no,
            label,
            station_no,
            station_object,
            last_name,
            first_name,
            middle_name,
            department,
            username,
        ) in rows:
            payload.append(
                {
                    "doc_no": format_doc_no(numeric),
                    "reg_date": reg_date,
                    "doc_name": doc_name,
                    "note": note,
                    "eq_type": eq_type,
                    "factory_no": factory_no,
                    "order_no": order_no,
                    "label": label,
                    "station_no": station_no,
                    "station_object": station_object,
                    "last_name": last_name,
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "department": department,
                    "username_fallback": username if not any([last_name, first_name, middle_name, department]) else None,
                }
            )
        return payload

    async def get_rows_extended(
        self, 
        station_objects: list[str] | None, 
        station_no: str | None,
        label: str | None,
        factory_no: str | None,
        date_from, 
        date_to
    ):
        """Расширенный поиск с дополнительными фильтрами"""
        rows = await self.repo.fetch_extended(
            station_objects, station_no, label, factory_no, date_from, date_to
        )
        payload = []
        for (
            numeric,
            reg_date,
            doc_name,
            note,
            eq_type,
            factory_no,
            order_no,
            label,
            station_no,
            station_object,
            username,
        ) in rows:
            payload.append(
                {
                    "doc_no": format_doc_no(numeric),
                    "reg_date": reg_date.strftime('%d.%m.%Y %H:%M') if reg_date else '',
                    "doc_name": doc_name,
                    "note": note,
                    "eq_type": eq_type,
                    "factory_no": factory_no,
                    "order_no": order_no,
                    "label": label,
                    "station_no": station_no,
                    "station_object": station_object,
                    "username": username,
                }
            )
        return payload

    async def export_excel(self, station_objects: list[str] | None, date_from, date_to) -> str:
        data = await self.get_rows(station_objects, date_from, date_to)
        builder = ReportExcelBuilder()
        path = builder.build_report(data)
        return path

    async def export_excel_extended(
        self, 
        station_objects: list[str] | None, 
        station_no: str | None,
        label: str | None,
        factory_no: str | None,
        date_from, 
        date_to
    ) -> str:
        """Экспорт в Excel с расширенными фильтрами"""
        data = await self.get_rows_extended(
            station_objects, station_no, label, factory_no, date_from, date_to
        )
        builder = ReportExcelBuilder()
        path = builder.build_report_extended(data)
        return path


def start_of_week(dt: datetime | None = None) -> datetime:
    dt = dt or datetime.now()
    monday = dt - timedelta(days=dt.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)
