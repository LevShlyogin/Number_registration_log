import pytest
from httpx import AsyncClient

from app.core.config import settings


@pytest.mark.asyncio
async def test_skip_golden_for_user_and_allow_for_admin(client: AsyncClient):
    # user reserves near a golden
    eq = (await client.post("/equipment", json={"eq_type": "EQ", "factory_no": None, "order_no": None, "label": None, "station_no": None, "station_object": None, "notes": None})).json()
    # обычный
    s = (await client.post("/sessions", json={"equipment_id": eq["id"], "requested_count": 3})).json()
    nums = s["reserved_numbers"]
    assert all(n % 100 != 0 for n in nums)
    # админ получает список и резервирует конкретный "00"
    admin_headers = {"X-User": "vgrubtsov"}
    from httpx import AsyncClient as Client2
    async with Client2(app=client._transport.app, base_url="http://test", headers=admin_headers) as admin:
      glist = (await admin.get("/admin/golden-suggest?limit=1")).json()
      assert glist["golden_numbers"], "Должен быть список золотых"
      golden = glist["golden_numbers"][0]
      r = await admin.post("/admin/reserve-specific", json={"equipment_id": eq["id"], "numbers": [golden]})
      assert r.status_code == 200