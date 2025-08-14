import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_uniqueness_same_name_note_equipment(client: AsyncClient):
    # оборудование
    eq = (await client.post("/equipment", json={"eq_type": "EQ", "factory_no": None, "order_no": None, "label": None, "station_no": None, "station_object": None, "notes": None})).json()
    # сессия и назначение первого документа
    s = (await client.post("/sessions", json={"equipment_id": eq["id"], "requested_count": 1})).json()
    r1 = (await client.post("/documents/assign-one", json={"session_id": s["session_id"], "doc_name": "Doc", "note": "Note"}))
    assert r1.status_code == 200
    # новая сессия и попытка создать дубликат с теми же полями
    s2 = (await client.post("/sessions", json={"equipment_id": eq["id"], "requested_count": 1})).json()
    r2 = await client.post("/documents/assign-one", json={"session_id": s2["session_id"], "doc_name": "Doc", "note": "Note"})
    assert r2.status_code == 409
    assert "уже зарегистрирован" in r2.text
