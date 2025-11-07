#!/usr/bin/env python3
"""Проверка результатов миграции"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

def check_data():
    db_url = settings.DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        print("\n📊 ПРОВЕРКА ДАННЫХ В БД\n")
        print("="*60)
        
        # Общая статистика
        for table in ['users', 'equipment', 'documents']:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"Таблица {table:15} : {count:6} записей")
        
        print("\n" + "="*60)
        print("📝 ПРИМЕРЫ ДАННЫХ:\n")
        
        # Примеры пользователей
        result = conn.execute(text("""
            SELECT username, last_name, first_name, department 
            FROM users 
            ORDER BY id DESC
            LIMIT 3
        """))
        print("Последние добавленные пользователи:")
        for row in result:
            print(f"  • {row[0]:20} : {row[1]} {row[2]} ({row[3]})")
        
        # Примеры турбин
        result = conn.execute(text("""
            SELECT factory_no, label, station_object 
            FROM equipment 
            WHERE eq_type = 'Турбина'
            ORDER BY id DESC
            LIMIT 3
        """))
        print("\nПоследние добавленные турбины:")
        for row in result:
            print(f"  • Зав.№ {row[0]:10} : {row[1]} - {row[2]}")
        
        # Примеры документов
        result = conn.execute(text("""
            SELECT d.numeric, d.doc_name, e.factory_no 
            FROM documents d
            JOIN equipment e ON d.equipment_id = e.id
            ORDER BY d.id DESC
            LIMIT 3
        """))
        print("\nПоследние добавленные документы:")
        for row in result:
            print(f"  • №{row[0]:5} : {row[1]:20} (Оборудование: {row[2]})")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    check_data()