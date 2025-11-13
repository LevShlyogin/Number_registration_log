import pytest
from httpx import AsyncClient
from faker import Faker

# Инициализируем Faker для генерации случайных, но правдоподобных данных
fake = Faker("ru_RU")

@pytest.mark.asyncio
class TestAuthAndUsers:
    """Тесты, связанные с аутентификацией и пользователями."""
    
    async def test_get_me_as_admin(self, client: AsyncClient, default_admin_headers: dict):
        response = await client.get("/users/me", headers=default_admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test_admin"
        assert data["is_admin"] is True

    async def test_get_me_as_user(self, client: AsyncClient, default_user_headers: dict):
        response = await client.get("/users/me", headers=default_user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test_user"
        assert data["is_admin"] is False

    async def test_admin_check_access_for_admin(self, client: AsyncClient, default_admin_headers: dict):
        response = await client.get("/admin/check-access", headers=default_admin_headers)
        assert response.status_code == 200
        assert response.json() == {"is_admin": True}

    async def test_admin_check_access_for_user(self, client: AsyncClient, default_user_headers: dict):
        response = await client.get("/admin/check-access", headers=default_user_headers)
        assert response.status_code == 403


@pytest.mark.asyncio
class TestEquipmentAPI:
    """Тесты для эндпоинтов /equipment."""

    async def test_create_equipment_as_admin_succeeds(self, client: AsyncClient, default_admin_headers: dict):
        payload = {
            "eq_type": fake.word().capitalize(),
            "factory_no": fake.numerify(text="#####"),
            "order_no": fake.numerify(text="#####-##-#####")
        }
        response = await client.post("/equipment", json=payload, headers=default_admin_headers)
        assert response.status_code == 201
        data = response.json()
        assert data["factory_no"] == payload["factory_no"]

    async def test_create_equipment_as_user_fails(self, client: AsyncClient, default_user_headers: dict):
        payload = {"eq_type": "Denied Device", "factory_no": "00000"}
        response = await client.post("/equipment", json=payload, headers=default_user_headers)
        assert response.status_code == 403

    async def test_create_equipment_with_invalid_factory_no_fails(self, client: AsyncClient, default_admin_headers: dict):
        payload = {"eq_type": "Invalid Device", "factory_no": "ABCDE"}
        response = await client.post("/equipment", json=payload, headers=default_admin_headers)
        assert response.status_code == 422
        assert "Заводской номер должен содержать только цифры" in response.text
    
    async def test_create_duplicate_equipment_fails(self, client: AsyncClient, default_admin_headers: dict):
        payload = {"eq_type": "Duplicated Device", "factory_no": "54321"}
        response1 = await client.post("/equipment", json=payload, headers=default_admin_headers)
        assert response1.status_code == 201
        
        response2 = await client.post("/equipment", json=payload, headers=default_admin_headers)
        assert response2.status_code == 409
        assert "уже существует" in response2.json()["detail"]

    async def test_search_equipment(self, client: AsyncClient, default_user_headers: dict, default_equipment: dict):
        factory_no = default_equipment.factory_no
        response = await client.get(f"/equipment/search?factory_no={factory_no}", headers=default_user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["factory_no"] == factory_no


@pytest.mark.asyncio
class TestGoldenNumberReservation:
    """Тесты для задачи №7: резервирование 'золотых' номеров."""

    async def test_reserve_golden_as_admin_succeeds(self, client: AsyncClient, default_admin_headers: dict, default_equipment: dict):
        equipment_id = default_equipment.id
        payload = {"quantity": 2, "equipment_id": equipment_id, "ttl_seconds": 60}
        
        response = await client.post("/documents/reserve-golden", json=payload, headers=default_admin_headers)
        
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert len(data["reserved_numbers"]) == 2
        assert data["reserved_numbers"][0] % 100 == 0
        assert data["reserved_numbers"][1] % 100 == 0

    async def test_reserve_golden_as_user_fails(self, client: AsyncClient, default_user_headers: dict, default_equipment: dict):
        equipment_id = default_equipment.id
        payload = {"quantity": 1, "equipment_id": equipment_id}
        
        response = await client.post("/documents/reserve-golden", json=payload, headers=default_user_headers)
        
        assert response.status_code == 403
        assert "Эта операция доступна только администраторам" in response.json()["detail"]

    async def test_reserve_golden_not_enough_numbers_fails(self, client: AsyncClient, default_admin_headers: dict, default_equipment: dict):
        equipment_id = default_equipment.id
        payload = {"quantity": 99999, "equipment_id": equipment_id} # Заведомо недостижимое количество
        
        response = await client.post("/documents/reserve-golden", json=payload, headers=default_admin_headers)
        
        assert response.status_code == 409
        assert "Не удалось найти" in response.json()["detail"]

    async def test_reserve_golden_invalid_quantity_fails(self, client: AsyncClient, default_admin_headers: dict, default_equipment: dict):
        equipment_id = default_equipment.id
        payload = {"quantity": 0, "equipment_id": equipment_id}
        
        response = await client.post("/documents/reserve-golden", json=payload, headers=default_admin_headers)
        
        assert response.status_code == 422


@pytest.mark.asyncio
class TestSessionsAndDocumentsFlow:
    """Тесты, проверяющие полный цикл: резервирование -> назначение."""

    async def test_full_workflow_succeeds(self, client: AsyncClient, default_user_headers: dict, default_equipment: dict):
        equipment_id = default_equipment.id
        reserve_payload = {"equipment_id": equipment_id, "requested_count": 1}
        
        reserve_response = await client.post("/sessions/reserve", json=reserve_payload, headers=default_user_headers)
        assert reserve_response.status_code == 200
        
        reserve_data = reserve_response.json()
        session_id = reserve_data["session_id"]
        reserved_number = reserve_data["reserved_numbers"][0]

        assign_payload = {
            "session_id": session_id,
            "doc_name": "Тестовый документ",
            "numeric": reserved_number
        }
        assign_response = await client.post("/documents/assign-one", json=assign_payload, headers=default_user_headers)

        assert assign_response.status_code == 200
        assign_data = assign_response.json()
        
        assert assign_data["message"] == "Документ создан."
        assert assign_data["created"]["numeric"] == reserved_number
        assert assign_data["created"]["equipment"]["id"] == equipment_id