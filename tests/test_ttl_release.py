import asyncio
import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_ttl_release(client: AsyncClient):
    eq = (await client.post("/equipment", json={"eq_type": "EQ", "factory_no": None, "order_no": None, "label": None, "station_no": None, "station_object": None, "notes": None})).json()
    # маленький TTL
    s = (await client.post("/sessions", json={"equipment_id": eq["id"], "requested_count": 2, "ttl_seconds": 1})).json()
    await asyncio.sleep(2)
    # новая сессия должна мочь взять эти номера (или новые); главное — не упасть
    s2 = (await client.post("/sessions", json={"equipment_id": eq["id"], "requested_count": 2})).json()
    assert "session_id" in s2