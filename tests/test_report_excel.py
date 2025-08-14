import os
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_report_excel(client: AsyncClient):
    eq = (await client.post("/equipment", json={"eq_type": "EQ", "factory_no": "F1", "order_no": "O1", "label": "L1", "station_no": "S1", "station_object": "ProjectA", "notes": None})).json()
    s = (await client.post("/sessions", json={"equipment_id": eq["id"], "requested_count": 1})).json()
    r1 = (await client.post("/documents/assign-one", json={"session_id": s["session_id"], "doc_name": "DocX", "note": "NoteX"}))
    assert r1.status_code == 200
    resp = await client.get("/reports/excel", params={"station_object": "ProjectA"})
    path = resp.json()["path"]
    assert os.path.exists(path), "Excel файл должен существовать"