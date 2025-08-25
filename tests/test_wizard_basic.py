import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.equipment import Equipment
from app.models.user import User


@pytest.mark.asyncio
async def test_wizard_ui_access(async_client: AsyncClient, test_user: User):
    """Тест доступа к wizard UI"""
    response = await async_client.get("/wizard")
    assert response.status_code == 200
    assert "Регистрация номеров документов" in response.text


@pytest.mark.asyncio
async def test_equipment_search(async_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Тест поиска оборудования"""
    # Создаем тестовое оборудование
    equipment = Equipment(
        eq_type="Турбина",
        station_object="Мосэнерго ТЭЦ-23",
        station_no="ст.3",
        label="Т-110",
        factory_no="120-12,8-8МО"
    )
    test_session.add(equipment)
    await test_session.commit()
    
    # Тестируем поиск
    response = await async_client.get(
        "/equipment/search",
        params={"q": "Мосэнерго"}
    )
    assert response.status_code == 200
    
    # Проверяем, что оборудование найдено
    data = response.json()
    assert len(data) > 0
    assert any(eq["station_object"] == "Мосэнерго ТЭЦ-23" for eq in data)


@pytest.mark.asyncio
async def test_equipment_creation_duplicate_check(async_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Тест проверки дублей при создании оборудования"""
    # Создаем первое оборудование
    equipment1 = Equipment(
        eq_type="Турбина",
        station_object="ТЭЦ-1",
        station_no="ст.1",
        label="Т-100",
        factory_no="100-10"
    )
    test_session.add(equipment1)
    await test_session.commit()
    
    # Пытаемся создать дубль
    response = await async_client.post(
        "/equipment",
        data={
            "eq_type": "Турбина",
            "station_object": "ТЭЦ-1",
            "station_no": "ст.1",
            "label": "Т-100",
            "factory_no": "100-10"
        }
    )
    
    # Должна быть ошибка 409 (дубль)
    assert response.status_code == 409
    assert "Объект с такими атрибутами уже существует" in response.text


@pytest.mark.asyncio
async def test_suggest_endpoints(async_client: AsyncClient, test_user: User, test_session: AsyncSession):
    """Тест эндпоинтов автодополнения"""
    # Тестируем автодополнение для doc-names
    response = await async_client.get("/suggest/doc-names")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Тестируем автодополнение для notes
    response = await async_client.get("/suggest/notes")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
