"""
Скрипт миграции данных из Excel файлов в БД
Запускать из корня проекта: python scripts/migrate_data.py
"""

import sys
import os
from pathlib import Path

# Добавляем корень проекта в path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import logging
from datetime import datetime
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from typing import Dict, Optional
import re

# Импортируем модели из проекта
from app.models.user import User
from app.models.equipment import Equipment
from app.models.document import Document
from app.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ExcelDataMigration:
    def __init__(self):
        """Инициализация с использованием настроек проекта"""
        # Используем синхронное подключение для миграции (убираем +asyncpg)
        db_url = settings.DATABASE_URL.replace("+asyncpg", "")
        self.engine = create_engine(db_url, echo=False)
        self.users_cache: Dict[str, int] = {}
        self.equipment_cache: Dict[str, int] = {}
        
        # Проверяем подключение
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                version = result.scalar()
                logger.info(f"✅ Подключено к PostgreSQL: {version[:30]}...")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к БД: {e}")
            raise

    def load_users(self, file_path: str) -> None:
        """Загрузка пользователей из Excel"""
        if not Path(file_path).exists():
            logger.error(f"Файл не найден: {file_path}")
            return
            
        logger.info(f"📥 Загрузка пользователей из {file_path}")
        
        try:
            df_users = pd.read_excel(file_path)
            logger.info(f"  Найдено {len(df_users)} записей")
            
            with Session(self.engine) as session:
                users_added = 0
                users_updated = 0
                users_skipped = 0
                
                for idx, row in df_users.iterrows():
                    username = str(row['Имя пользователя']).strip().lower()
                    
                    existing_user = session.execute(
                        select(User).where(User.username == username)
                    ).scalar_one_or_none()
                    
                    if not existing_user:
                        user = User(
                            username=username,
                            last_name=str(row['Фамилия']).strip() if pd.notna(row['Фамилия']) else None,
                            first_name=str(row['Имя']).strip() if pd.notna(row['Имя']) else None,
                            middle_name=str(row['Отчество']).strip() if pd.notna(row['Отчество']) else None,
                            department=str(row['Отдел']).strip() if pd.notna(row['Отдел']) else None
                        )
                        session.add(user)
                        users_added += 1
                        logger.debug(f"  + Добавлен: {username}")
                    else:
                        # Обновляем информацию если нужно
                        updated = False
                        if pd.notna(row['Фамилия']) and not existing_user.last_name:
                            existing_user.last_name = str(row['Фамилия']).strip()
                            updated = True
                        if pd.notna(row['Имя']) and not existing_user.first_name:
                            existing_user.first_name = str(row['Имя']).strip()
                            updated = True
                        if pd.notna(row['Отдел']) and not existing_user.department:
                            existing_user.department = str(row['Отдел']).strip()
                            updated = True
                        
                        if updated:
                            users_updated += 1
                            logger.debug(f"  ~ Обновлен: {username}")
                        else:
                            users_skipped += 1
                
                session.commit()
                
                # Кэшируем пользователей
                all_users = session.execute(select(User)).scalars().all()
                self.users_cache = {u.username: u.id for u in all_users}
                
                logger.info(f"  ✅ Результат: добавлено {users_added}, обновлено {users_updated}, пропущено {users_skipped}")
                logger.info(f"  📊 Всего пользователей в БД: {len(self.users_cache)}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке пользователей: {e}")
            raise

    def load_equipment(self, turbines_file: str) -> None:
        """Загрузка оборудования из Excel"""
        if not Path(turbines_file).exists():
            logger.error(f"Файл не найден: {turbines_file}")
            return
            
        logger.info(f"📥 Загрузка турбин из {turbines_file}")
        
        try:
            # Читаем турбины
            df_turbines = pd.read_excel(turbines_file, sheet_name='Турбины УТЗ')
            logger.info(f"  Найдено {len(df_turbines)} турбин")
            
            # Читаем заказы
            orders_map = {}
            try:
                df_orders = pd.read_excel(turbines_file, sheet_name='Номер Заказов')
                logger.info(f"  Найдено {len(df_orders)} заказов")
                
                for _, row in df_orders.iterrows():
                    if pd.notna(row.iloc[0]):
                        order_no = str(row.iloc[0]).strip()
                        # Извлекаем последние 5 цифр для маппинга
                        match = re.search(r'(\d{5})(?:\D|$)', order_no)
                        if match:
                            orders_map[match.group(1)] = order_no
                
                logger.info(f"  Создан маппинг для {len(orders_map)} заказов")
            except Exception as e:
                logger.warning(f"  ⚠️  Не удалось загрузить заказы: {e}")
            
            with Session(self.engine) as session:
                equipment_added = 0
                equipment_skipped = 0
                
                for _, row in df_turbines.iterrows():
                    factory_no = str(int(row['Зав№'])) if pd.notna(row['Зав№']) else None
                    if not factory_no:
                        continue
                    
                    existing = session.execute(
                        select(Equipment).where(Equipment.factory_no == factory_no)
                    ).scalar_one_or_none()
                    
                    if not existing:
                        # Пытаемся найти номер заказа
                        order_no = orders_map.get(factory_no, None)
                        
                        equipment = Equipment(
                            eq_type="Турбина",
                            factory_no=factory_no,
                            order_no=order_no,
                            label=str(row['Маркировка турбины']).strip() if pd.notna(row['Маркировка турбины']) else None,
                            station_no=str(row['Станц. №']).strip() if pd.notna(row['Станц. №']) else None,
                            station_object=str(row['Наименование станции']).strip() if pd.notna(row['Наименование станции']) else None,
                            notes=None
                        )
                        session.add(equipment)
                        equipment_added += 1
                        logger.debug(f"  + Турбина {factory_no}: {equipment.label}")
                    else:
                        equipment_skipped += 1
                
                session.commit()
                
                # Кэшируем оборудование
                all_equipment = session.execute(select(Equipment)).scalars().all()
                self.equipment_cache = {e.factory_no: e.id for e in all_equipment if e.factory_no}
                
                logger.info(f"  ✅ Результат: добавлено {equipment_added}, пропущено {equipment_skipped}")
                logger.info(f"  📊 Всего оборудования в БД: {len(self.equipment_cache)}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке оборудования: {e}")
            raise

    def load_documents(self, documents_file: str, default_username: str = "yuvabramov") -> None:
        """Загрузка документов из Excel"""
        if not Path(documents_file).exists():
            logger.error(f"Файл не найден: {documents_file}")
            return
            
        logger.info(f"📥 Загрузка документов из {documents_file}")
        
        try:
            df_docs = pd.read_excel(documents_file)
            logger.info(f"  Найдено {len(df_docs)} документов")
            
            # Получаем ID дефолтного пользователя
            default_user_id = self.users_cache.get(default_username)
            if not default_user_id:
                logger.error(f"  ❌ Пользователь {default_username} не найден!")
                if self.users_cache:
                    default_username = list(self.users_cache.keys())[0]
                    default_user_id = self.users_cache[default_username]
                    logger.info(f"  Используем первого доступного пользователя: {default_username}")
                else:
                    logger.error("  ❌ Нет пользователей в БД!")
                    return
            
            with Session(self.engine) as session:
                documents_added = 0
                documents_skipped = 0
                virtual_equipment_created = 0
                
                for idx, row in df_docs.iterrows():
                    try:
                        # Получаем numeric
                        numeric = int(row['№ п/п']) if pd.notna(row['№ п/п']) else idx + 1
                        
                        # Проверяем существование по numeric
                        existing = session.execute(
                            select(Document).where(Document.numeric == numeric)
                        ).scalar_one_or_none()
                        
                        if existing:
                            documents_skipped += 1
                            continue
                        
                        # Извлекаем данные
                        doc_name = str(row['Обозначение']).strip() if pd.notna(row['Обозначение']) else f"DOC-{numeric}"
                        doc_title = str(row['Наименование']).strip() if pd.notna(row['Наименование']) else ""
                        note_text = str(row.get('Примечание', '')).strip() if pd.notna(row.get('Примечание')) else ""
                        
                        # Формируем note
                        note_parts = []
                        if doc_title:
                            note_parts.append(doc_title)
                        if note_text and note_text not in ['nan', '']:
                            note_parts.append(note_text)
                        note = ". ".join(note_parts) if note_parts else None
                        
                        # Определяем equipment_id
                        factory_no_raw = row.get('Зав.№ турбины первичного применения', '')
                        factory_no = str(int(factory_no_raw)) if pd.notna(factory_no_raw) and str(factory_no_raw) not in ['00000', '0'] else None
                        
                        equipment_id = None
                        if factory_no:
                            equipment_id = self.equipment_cache.get(factory_no)
                        
                        # Если нет оборудования, создаем виртуальное
                        if not equipment_id:
                            # Ищем номер заказа в примечании
                            order_match = re.search(r'К-(\d+)', note_text) if note_text else None
                            if order_match:
                                virtual_no = f"VIRT-K-{order_match.group(1)}"
                            else:
                                virtual_no = f"VIRT-DOC-{numeric}"
                            
                            if virtual_no not in self.equipment_cache:
                                virtual_eq = Equipment(
                                    eq_type="Вспомогательное оборудование",
                                    factory_no=virtual_no,
                                    order_no=order_match.group(0) if order_match else None,
                                    label=f"Виртуальное для {doc_name}",
                                    notes=f"Создано для документа №{numeric}"
                                )
                                session.add(virtual_eq)
                                session.flush()
                                self.equipment_cache[virtual_no] = virtual_eq.id
                                virtual_equipment_created += 1
                            
                            equipment_id = self.equipment_cache[virtual_no]
                        
                        # Создаем документ
                        document = Document(
                            numeric=numeric,
                            reg_date=datetime.now(),
                            doc_name=doc_name,
                            note=note,
                            equipment_id=equipment_id,
                            user_id=default_user_id
                        )
                        session.add(document)
                        documents_added += 1
                        
                        if documents_added % 100 == 0:
                            session.commit()
                            logger.info(f"    Обработано {documents_added} документов...")
                            
                    except Exception as e:
                        logger.warning(f"  ⚠️  Ошибка в строке {idx}: {e}")
                        continue
                
                session.commit()
                
                logger.info(f"  ✅ Результат: добавлено {documents_added}, пропущено {documents_skipped}")
                logger.info(f"  📊 Создано виртуального оборудования: {virtual_equipment_created}")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при загрузке документов: {e}")
            raise

    def get_statistics(self) -> None:
        """Вывод статистики БД"""
        with Session(self.engine) as session:
            stats = {
                'users': session.query(User).count(),
                'equipment': session.query(Equipment).count(),
                'equipment_turbines': session.query(Equipment).filter(Equipment.eq_type == "Турбина").count(),
                'equipment_virtual': session.query(Equipment).filter(Equipment.factory_no.like('VIRT%')).count(),
                'documents': session.query(Document).count()
            }
            
            print("\n" + "="*60)
            print("📊 СТАТИСТИКА БАЗЫ ДАННЫХ:")
            print("="*60)
            print(f"👤 Пользователей: {stats['users']}")
            print(f"⚙️  Всего оборудования: {stats['equipment']}")
            print(f"   - Турбин: {stats['equipment_turbines']}")
            print(f"   - Виртуального: {stats['equipment_virtual']}")
            print(f"📄 Документов: {stats['documents']}")
            print("="*60 + "\n")

def main():
    """Основная функция миграции"""
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    # Файлы данных
    files = {
        'users': DATA_DIR / "Копия Актуальный список пользователей СКБт.xls",
        'turbines': DATA_DIR / "Копия Паровые Турбины.xlsx",
        'documents': DATA_DIR / "Копия Номера до 20к.xlsx"
    }
    
    # Проверяем наличие файлов
    print("\n🔍 Проверка файлов данных:")
    all_files_exist = True
    for name, path in files.items():
        if path.exists():
            print(f"  ✅ {name}: {path.name}")
        else:
            print(f"  ❌ {name}: НЕ НАЙДЕН ({path})")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Загрузите все необходимые файлы в папку data/")
        return 1
    
    print("\n" + "="*60)
    print("🚀 НАЧАЛО МИГРАЦИИ ДАННЫХ")
    print("="*60)
    
    try:
        migration = ExcelDataMigration()
        
        # Миграция по этапам
        print("\n📥 ЭТАП 1: Загрузка пользователей...")
        migration.load_users(str(files['users']))
        
        print("\n📥 ЭТАП 2: Загрузка оборудования...")
        migration.load_equipment(str(files['turbines']))
        
        print("\n📥 ЭТАП 3: Загрузка документов...")
        migration.load_documents(str(files['documents']))
        
        # Статистика
        migration.get_statistics()
        
        print("✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!\n")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        print(f"\n❌ МИГРАЦИЯ ПРЕРВАНА: {e}\n")
        return 1

if __name__ == "__main__":
    exit(main())