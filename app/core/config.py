from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_env: str = Field(default="dev", alias="APP_ENV")
    database_url: str = Field(alias="DATABASE_URL")
    default_ttl_seconds: int = Field(default=1800, alias="DEFAULT_TTL_SECONDS")
    admin_users: list[str] = ["vgrubtsov", "yuaalekseeva", "lrshlyogin", "pyagavrilov"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()



--- tests/test_report_excel.py
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