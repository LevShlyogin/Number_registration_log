from __future__ import annotations

from datetime import datetime
from pathlib import Path
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


class ReportExcelBuilder:
    columns = [
        "№ документа",
        "Дата регистрации",
        "Наименование документа",
        "Примечание",
        "Тип оборудования",
        "№ заводской",
        "№ заказа",
        "Маркировка",
        "№ станционный",
        "Станция / Объект",
        "Фамилия",
        "Имя",
        "Отчество",
        "Отдел",
    ]

    columns_extended = [
        "№ документа",
        "Дата регистрации",
        "Наименование документа",
        "Примечание",
        "Тип оборудования",
        "№ заводской",
        "№ заказа",
        "Маркировка",
        "№ станционный",
        "Станция / Объект",
        "Пользователь (создавший)",
    ]

    def build_report(self, rows: list[dict]) -> str:
        wb = Workbook()
        ws = wb.active
        ws.title = "Отчет"
        ws.append(self.columns)
        for r in rows:
            ws.append(
                [
                    r["doc_no"],
                    r["reg_date"],
                    r["doc_name"],
                    r["note"],
                    r["eq_type"],
                    r["factory_no"],
                    r["order_no"],
                    r["label"],
                    r["station_no"],
                    r["station_object"],
                    r["last_name"] or (r["username_fallback"] if r["username_fallback"] else ""),
                    r["first_name"] or "",
                    r["middle_name"] or "",
                    r["department"] or "",
                ]
            )
        # авто-ширина по заголовкам
        for i, col_name in enumerate(self.columns, start=1):
            ws.column_dimensions[get_column_letter(i)].width = max(len(col_name) + 2, 15)
        Path("var/exports").mkdir(parents=True, exist_ok=True)
        fname = f"var/exports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb.save(fname)
        return fname

    def build_report_extended(self, rows: list[dict]) -> str:
        """Создание расширенного отчета с колонкой пользователя"""
        wb = Workbook()
        ws = wb.active
        ws.title = "Отчет"
        ws.append(self.columns_extended)
        for r in rows:
            ws.append(
                [
                    r["doc_no"],
                    r["reg_date"],
                    r["doc_name"],
                    r["note"],
                    r["eq_type"],
                    r["factory_no"],
                    r["order_no"],
                    r["label"],
                    r["station_no"],
                    r["station_object"],
                    r["username"] or "",
                ]
            )
        # авто-ширина по заголовкам
        for i, col_name in enumerate(self.columns_extended, start=1):
            ws.column_dimensions[get_column_letter(i)].width = max(len(col_name) + 2, 15)
        Path("var/exports").mkdir(parents=True, exist_ok=True)
        fname = f"var/exports/report_extended_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        wb.save(fname)
        return fname
