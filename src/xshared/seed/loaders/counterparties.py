import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from xshared.models import Counterparty, KPP, CaKppMapping
from xshared.seed.dadata import dd_find_by_id
from xshared.seed.loaders.base import get_or_create

CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def _parse_dadata(data: dict) -> dict:
    """Преобразовать ответ DaData в поля Counterparty."""
    return {
        "name": data["data"]["name"]["full"],
        "opf_short": data["data"]["opf"]["short"],
        "name_full_with_opf": data["data"]["name"]["full_with_opf"],
        "status": data["data"]["state"]["status"],
        "inn": data["data"]["inn"],
        "ogrn": data["data"]["ogrn"],
        "ogrn_date": _ts_to_dt(data["data"]["ogrn_date"]),
        "actuality_date": _ts_to_dt(data["data"]["state"]["actuality_date"]),
        "registration_date": _ts_to_dt(data["data"]["state"]["registration_date"]),
        "liquidation_date": _ts_to_dt(data["data"]["state"]["liquidation_date"]),
        "address": data["data"]["address"]["value"],
        "address_full": data["data"]["address"]["data"]["source"],
        "counterparty_type": data["data"]["type"],
        "branch_type": data["data"].get("branch_type"),
        "kpp": data["data"].get("kpp"),
    }


def _ts_to_dt(ts):
    if ts is None:
        return None
    from datetime import datetime
    return datetime.fromtimestamp(ts / 1000)


async def load_counterparty(session: AsyncSession, inn: str) -> Counterparty:
    # 1. Кэш
    cache_file = CACHE_DIR / f"party_{inn}.json"
    if cache_file.exists():
        raw = json.loads(cache_file.read_text(encoding="utf-8"))
    else:
        result = await dd_find_by_id("party", inn)
        if not result:
            raise ValueError(f"DaData: no data for INN {inn}")
        raw = result[0]
        cache_file.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    data = _parse_dadata(raw)

    # 2. Upsert
    counterparty, created = await get_or_create(
        session, Counterparty, defaults=data, inn=inn,
    )
    if not created:
        for k, v in data.items():
            setattr(counterparty, k, v)

    # 3. KPP из ответа
    dd_kpp = data.get("kpp")
    if dd_kpp:
        kpp, _ = await get_or_create(session, KPP, defaults={}, name=dd_kpp)
        mapping, created = await get_or_create(
            session, CaKppMapping,
            defaults={"is_basic": True},
            counterparty_id=counterparty.id,
            kpp_id=kpp.id,
        )
        if not created:
            mapping.is_basic = True

    return counterparty
