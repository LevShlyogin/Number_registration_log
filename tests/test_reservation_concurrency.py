import asyncio
import pytest
from httpx import AsyncClient

from app.core.db import SessionLocal
from app.core.config import settings


@pytest.mark.asyncio
async def test_concurrent_reservation_no_duplicates(client: AsyncClient):
    # создадим одно оборудование
    resp = await client.post("/equipment", json={"eq_type": "EQ", "factory_no": None, "order_no": None, "label": None, "station_no": None, "station_object": None, "notes": None})
    eq = resp.json()
    # конкурентно резервируем
    async def reserve():
        r = await client.post("/sessions", json={"equipment_id": eq["id"], "requested_count": 5})
        return r.json()

    results = await asyncio.gather(*[reserve() for _ in range(5)])
    all_nums = [n for res in results for n in res["reserved_numbers"]]
    assert len(all_nums) == len(set(all_nums)), "Должны быть уникальные номера без дублей"
    # Проверим, что ни один не оканчивается на 00
    assert all(n % 100 != 0 for n in all_nums)