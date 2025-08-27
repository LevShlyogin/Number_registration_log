from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.repositories.doc_numbers import DocNumbersRepository
from app.repositories.documents import DocumentsRepository
from app.repositories.sessions import SessionsRepository
from app.repositories.audit import AuditRepository
from app.repositories.equipment import EquipmentRepository
from app.repositories.users import UsersRepository
from app.models.session import SessionStatus
from app.utils.numbering import format_doc_no, is_golden
# ### ИСПРАВЛЕНО: Правильный импорт ###
from app.schemas.admin import AdminDocumentUpdate


class DocumentsService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.numbers_repo = DocNumbersRepository(session)
        self.docs_repo = DocumentsRepository(session)
        self.sessions_repo = SessionsRepository(session)
        self.audit_repo = AuditRepository(session)
        self.equipment_repo = EquipmentRepository(session)
        self.users_repo = UsersRepository(session)

    async def assign_one(self, *, session_id: str, user_id: int, doc_name: str, note: str | None, is_admin: bool) -> dict:
        # берем наименьший зарезервированный номер
        reserved = await self.numbers_repo.get_reserved_for_session(session_id)
        if not reserved:
            return {"created": None, "message": "Нет зарезервированных номеров в сессии."}
        candidate = None
        for row in reserved:
            if is_golden(row.numeric) and not is_admin:
                continue
            candidate = row.numeric
            break
        if candidate is None:
            return {"created": None, "message": "В пуле только номера ХХХХ00, недоступные обычному пользователю."}

        # создаем документ
        try:
            doc = await self.docs_repo.create(
                {
                    "numeric": candidate,
                    "doc_name": doc_name,
                    "note": note,
                    "equipment_id": (await self.sessions_repo.get(session_id)).equipment_id,
                    "user_id": user_id,
                }
            )
            await self.numbers_repo.mark_assigned([candidate])
            # если больше номеров нет — закрываем сессию
            rest = await self.numbers_repo.get_reserved_for_session(session_id)
            if not any((not is_golden(r.numeric) or is_admin) for r in rest):
                await self.sessions_repo.set_status(session_id, SessionStatus.completed)
            await self.session.commit()
            
            # Получаем дополнительную информацию для wizard
            equipment = await self.equipment_repo.get(doc.equipment_id)
            user = await self.users_repo.get(doc.user_id)
            
            return {
                "created": {
                    "id": doc.id,
                    "numeric": doc.numeric,
                    "formatted_no": format_doc_no(doc.numeric),
                    "doc_name": doc.doc_name,
                    "note": doc.note,
                    "reg_date": doc.reg_date,
                    "equipment": equipment,
                    "user": user,
                },
                "message": "Документ создан.",
            }
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Такой документ уже зарегистрирован.")

    async def edit_document_admin(self, *, document_id: int, username: str, data: AdminDocumentUpdate) -> dict:
        """
        Обновляет данные документа и связанного с ним оборудования,
        сохраняя аудит всех изменений.
        """
        # Получаем документ
        doc = await self.docs_repo.get(document_id)
        if not doc:
            raise ValueError("Документ не найден.")
        
        equipment = doc.equipment
        if not equipment:
            raise ValueError("Связанное оборудование для документа не найдено.")

        changed = {}

        # 1. Проверяем изменения в полях документа (Document)
        if data.doc_name is not None and data.doc_name != doc.doc_name:
            changed["Наименование документа"] = [doc.doc_name, data.doc_name]
            doc.doc_name = data.doc_name
        
        if data.note is not None and data.note != doc.note:
            changed["Примечание"] = [doc.note, data.note]
            doc.note = data.note

        # 2. Проверяем изменения в полях оборудования (Equipment)
        if data.eq_type is not None and data.eq_type != equipment.eq_type:
            changed["Тип оборудования"] = [equipment.eq_type, data.eq_type]
            equipment.eq_type = data.eq_type
        
        if data.station_object is not None and data.station_object != equipment.station_object:
            changed["Станция/Объект"] = [equipment.station_object, data.station_object]
            equipment.station_object = data.station_object

        if data.station_no is not None and data.station_no != equipment.station_no:
            changed["№ станционный"] = [equipment.station_no, data.station_no]
            equipment.station_no = data.station_no

        if data.factory_no is not None and data.factory_no != equipment.factory_no:
            changed["№ заводской"] = [equipment.factory_no, data.factory_no]
            equipment.factory_no = data.factory_no

        if data.order_no is not None and data.order_no != equipment.order_no:
            changed["№ заказа"] = [equipment.order_no, data.order_no]
            equipment.order_no = data.order_no

        if data.label is not None and data.label != equipment.label:
            changed["Маркировка"] = [equipment.label, data.label]
            equipment.label = data.label

        # 3. Если изменений нет, выходим
        if not changed:
            return {"message": "Изменений нет."}

        # 4. Сохраняем изменения и аудит
        try:
            await self.session.flush()
        except IntegrityError:
            await self.session.rollback()
            raise ValueError("Такой документ уже зарегистрирован (конфликт уникальности).")
        
        await self.audit_repo.add(document_id=doc.id, doc_number=doc.numeric, username=username, diff=changed)
        await self.session.commit()
        
        return {"message": "Изменения сохранены.", "diff": changed}