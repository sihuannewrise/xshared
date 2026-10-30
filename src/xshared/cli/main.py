import asyncio
import typer

from pathlib import Path
from typing import Annotated

from xshared.db.session import session_scope
from xshared.seed.loaders.counterparties import (
    CACHE_DIR, load_counterparty, load_counterparties_from_json
)


app = typer.Typer(help="xshared CLI")


@app.command()
def seed_cpt(
    inns: Annotated[list[str], typer.Argument(help="ИНН контрагентов")],
    refresh: Annotated[
        bool,
        typer.Option("--refresh", help="Очистить кэш DaData"),
    ] = False,
):
    """
    Seed counterparty by INN (one or list).
    Добавить/обновить данные контрагента из кэш-файла,
    если кэша нет, сделать запрос в DaData.
    """
    if refresh:
        for inn in inns:
            cache_file = CACHE_DIR / f"party_{inn}.json"
            if cache_file.exists():
                cache_file.unlink()
        print("Cache cleared for provided INNs")

    async def _run():
        for inn in inns:
            try:
                async with session_scope() as session:
                    cp = await load_counterparty(session, inn)
                    print(f"OK: {inn} -> {cp.id} ({cp.name})")
            except Exception as e:
                print(f"FAIL: {inn}: {e}")

    asyncio.run(_run())


@app.command()
def seed_cpt_json(
    file: Annotated[
        Path | None,
        typer.Option(help="JSON-файл (по умолчанию seed/data/counterparties.json)"),
    ] = None,
    offset: Annotated[
        int,
        typer.Option(help="Пропустить первые N записей"),
    ] = 0,
    limit: Annotated[
        int | None,
        typer.Option(help="Загрузить не более N записей (None - все)"),
    ] = None,
    delay: Annotated[
        float,
        typer.Option(help="Пауза между запросами к DaData в секундах"),
    ] = 0.2,
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
            stats = await load_counterparties_from_json(
                session, file, offset=offset, limit=limit, delay_seconds=delay
            )
            print(f"\nDone: ok={stats['ok']}, fail={stats['fail']} (total processed: {stats['total']})")
            if stats["errors"]:
                print("Errors:")
                for err in stats["errors"]:
                    print(f"  - {err}")
    asyncio.run(_run())


if __name__ == "__main__":
    app()