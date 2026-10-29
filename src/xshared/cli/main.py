# src/xshared/cli/main.py
import asyncio
from pathlib import Path
from typing import Annotated

import typer

from xshared.db.session import session_scope
from xshared.seed.loaders.counterparties import (
    CACHE_DIR,
    load_counterparties_from_json,
    load_counterparty,
)


app = typer.Typer(help="xshared CLI")


@app.command()
def seed_counterparties(
    inns: Annotated[list[str], typer.Argument(help="ИНН контрагентов")],
):
    """Заполнить контрагентов из DaData по ИНН (только основной КПП)."""
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
def seed_counterparties_json(
    file: Annotated[
        Path | None,
        typer.Option(help="JSON-файл (по умолчанию seed/data/counterparties.json)"),
    ] = None,
    refresh: Annotated[
        bool,
        typer.Option("--refresh", help="Игнорировать кэш DaData"),
    ] = False,
):
    """Заполнить контрагентов из counterparties.json (DaData + КПП из JSON)."""
    if refresh:
        for f in CACHE_DIR.glob("party_*.json"):
            f.unlink()
        print("Cache cleared")

    async def _run():
        async with session_scope() as session:
            stats = await load_counterparties_from_json(session, file)
            print(f"\nDone: ok={stats['ok']}, fail={stats['fail']}")
            if stats["errors"]:
                print("Errors:")
                for err in stats["errors"]:
                    print(f"  - {err}")
    asyncio.run(_run())


if __name__ == "__main__":
    app()
