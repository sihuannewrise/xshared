import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer

from xshared.db.session import session_scope
from xshared.seed.loaders.counterparties import load_counterparty

app = typer.Typer(help="xshared CLI")


@app.command()
def seed_counterparties(
    inns: Annotated[list[str], typer.Argument(help="ИНН контрагентов")],
):
    """Заполнить контрагентов из DaData по ИНН."""
    async def _run():
        async with session_scope() as session:
            for inn in inns:
                try:
                    cp = await load_counterparty(session, inn)
                    print(f"OK: {inn} -> {cp.id} ({cp.name})")
                except Exception as e:
                    print(f"FAIL: {inn}: {e}")
    asyncio.run(_run())


@app.command()
def seed_from_json(
    file: Annotated[Path, typer.Argument(help="JSON-файл с данными")],
    model: Annotated[str, typer.Option(help="Имя модели: counterparty, kpp, company")],
):
    """Заполнить справочник из JSON (без DaData)."""
    ...


if __name__ == "__main__":
    app()
