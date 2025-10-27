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

    async def assign_one(self, *, session_id: str, user_id: int, doc_name: str, note: str | None, is_admin: bool,
                         numeric: int) -> dict:
        print("\n" + "=" * 50)
        print(f"-> assign_one_service: Начало назначения для сессии {session_id}")
        print(f"   - Пользователь ID: {user_id}, Админ: {is_admin}")
        print(f"   - Запрошенный номер (от фронтенда): {numeric}")

        reserved_orm = await self.numbers_repo.get_reserved_for_session(session_id)
        reserved_numerics = [r.numeric for r in reserved_orm]

        print(f"   - Номера, считающиеся 'reserved' в БД для этой сессии: {reserved_numerics}")

        if not reserved_orm:
            print(f"<- assign_one_service: ВЫХОД. Причина: Нет зарезервированных номеров в сессии.")
            print("=" * 50 + "\n")
            return {"created": None, "message": "Нет зарезервированных номеров в сессии."}

        candidate_row = next((row for row in reserved_orm if row.numeric == numeric), None)

        if candidate_row is None:
            print(f"<- assign_one_service: ВЫХОД. Причина: Номер {numeric} не найден в списке 'reserved' номеров.")
            print("=" * 50 + "\n")
            return {"created": None, "message": f"Номер {numeric} не найден или уже назначен в текущей сессии."}

        if is_golden(candidate_row.numeric) and not is_admin:
            print(f"<- assign_one_service: ВЫХОД. Причина: Не-админ пытается назначить золотой номер {numeric}.")
            print("=" * 50 + "\n")
            return {"created": None, "message": f"Номер {numeric} является 'золотым' и недоступен для назначения."}

        try:
            session_obj = await self.sessions_repo.get(session_id)
            if not session_obj:
                print(f"<- assign_one_service: ВЫХОД. Причина: Сессия {session_id} не найдена.")
                print("=" * 50 + "\n")
                return {"created": None, "message": "Сессия не найдена."}

            doc = await self.docs_repo.create(
                {
                    "numeric": numeric,
                    "doc_name": doc_name,
                    "note": note,
                    "equipment_id": session_obj.equipment_id,
                    "user_id": user_id,
                }
            )
            await self.numbers_repo.mark_assigned([numeric])
            await self.session.commit()

            print(f"   - УСПЕХ: Документ с номером {numeric} создан и закоммичен.")
            print(f"<- assign_one_service: Успешное завершение.")
            print("=" * 50 + "\n")

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
            print(f"<- assign_one_service: ВЫХОД. Причина: IntegrityError (дубликат документа).")
            print("=" * 50 + "\n")
            await self.session.rollback()
            raise ValueError("Такой документ уже зарегистрирован для данного объекта.")

    async def edit_document_admin(self, *, document_id: int, username: str, data: AdminDocumentUpdate) -> dict:
        """
        Обновляет данные документа и связанного с ним оборудования,
        сохраняя аудит всех изменений.
        """
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
