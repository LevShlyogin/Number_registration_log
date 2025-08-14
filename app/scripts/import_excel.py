from __future__ import annotations

import asyncio
import typer

from app.core.db import SessionLocal
from app.services.importer import ExcelImporterService

cli = typer.Typer()


@cli.command()
def run(path: str):
    async def _do():
        async with SessionLocal() as session:
            svc = ExcelImporterService(session)
            res = await svc.import_file(path)
            print(res)

    asyncio.run(_do())


if __name__ == "__main__":
    cli()