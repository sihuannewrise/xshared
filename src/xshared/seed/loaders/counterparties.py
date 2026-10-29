import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from xshared.models import Counterparty, KPP, KppCaMapping
from xshared.seed.dadata import dd_find_by_id


DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


# ============================================================
# 1. DaData: парсинг и загрузка
# ============================================================

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
    return datetime.fromtimestamp(ts / 1000)


async def _load_dadata(inn: str) -> dict:
    """Получить данные из DaData (с кэшем)."""
    cache_file = CACHE_DIR / f"party_{inn}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))

    result = await dd_find_by_id("party", inn)
    if not result:
        raise ValueError(f"DaData: no data for INN {inn}")

    raw = result[0]
    cache_file.write_text(
        json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return raw


# ============================================================
# 2. Upsert контрагента и КПП
# ============================================================

async def _upsert_counterparty(
    session: AsyncSession, inn: str, data: dict
) -> Counterparty:
    """Создать или обновить контрагента по ИНН."""
    # kpp — не поле Counterparty, убираем
    cp_data = {k: v for k, v in data.items() if k != "kpp"}

    cp = await session.scalar(select(Counterparty).where(Counterparty.inn == inn))
    if cp is None:
        cp = Counterparty(inn=inn, **cp_data)
        session.add(cp)
        await session.flush()
    else:
        for k, v in cp_data.items():
            setattr(cp, k, v)
        await session.flush()
    return cp


async def _upsert_kpp_mapping(
    session: AsyncSession,
    counterparty: Counterparty,
    kpp_code: str,
    is_basic: bool = False,
) -> KppCaMapping:
    """Создать/обновить КПП и связь с контрагентом."""
    kpp = await session.scalar(select(KPP).where(KPP.name == kpp_code))
    if kpp is None:
        kpp = KPP(name=kpp_code)
        session.add(kpp)
        await session.flush()

    mapping = await session.scalar(
        select(KppCaMapping).where(
            KppCaMapping.counterparty_id == counterparty.id,
            KppCaMapping.kpp_id == kpp.id,
        )
    )
    if mapping is None:
        mapping = KppCaMapping(
            counterparty_id=counterparty.id,
            kpp_id=kpp.id,
            is_basic=is_basic,
        )
        session.add(mapping)
    else:
        mapping.is_basic = is_basic

    await session.flush()
    return mapping


async def _reset_basic_for_counterparty(
    session: AsyncSession, counterparty_id: int
) -> None:
    """Снять is_basic со всех КПП контрагента (если триггер не настроен)."""
    await session.execute(
        update(KppCaMapping)
        .where(
            KppCaMapping.counterparty_id == counterparty_id,
            KppCaMapping.is_basic.is_(True),
        )
        .values(is_basic=False)
    )
    await session.flush()


# ============================================================
# 3. Загрузка одного контрагента по ИНН (только DaData)
# ============================================================

async def load_counterparty(session: AsyncSession, inn: str) -> Counterparty:
    """
    Загрузить одного контрагента по ИНН из DaData.
    Обновляет только основной КПП из DaData.
    """
    raw = await _load_dadata(inn)
    data = _parse_dadata(raw)

    cp = await _upsert_counterparty(session, inn, data)

    dd_kpp = data.get("kpp")
    if dd_kpp:
        await _reset_basic_for_counterparty(session, cp.id)
        await _upsert_kpp_mapping(session, cp, dd_kpp, is_basic=True)

    return cp


# ============================================================
# 4. Загрузка из counterparties.json (DaData + КПП из JSON)
# ============================================================

async def load_counterparty_from_json(
    session: AsyncSession, row: dict
) -> Counterparty:
    """
    Загрузить одного контрагента из counterparties.json:
    1. DaData по ИНН — обновить реквизиты Counterparty.
    2. Основной КПП из DaData (is_basic=True).
    3. КПП из JSON (если отличается от DaData) — как дополнительный (is_basic=False).
    """
    inn = row["inn"]

    # 1. DaData
    raw = await _load_dadata(inn)
    data = _parse_dadata(raw)

    # 2. Counterparty
    cp = await _upsert_counterparty(session, inn, data)

    # 3. Основной КПП из DaData
    dd_kpp = data.get("kpp")
    json_kpp = row.get("kpp")

    if dd_kpp:
        await _reset_basic_for_counterparty(session, cp.id)
        await _upsert_kpp_mapping(session, cp, dd_kpp, is_basic=True)

    # 4. КПП из JSON — если отличается от DaData, добавить как дополнительный
    if json_kpp and json_kpp != dd_kpp:
        await _upsert_kpp_mapping(session, cp, json_kpp, is_basic=False)

    return cp


async def load_counterparties_from_json(
    session: AsyncSession,
    file_path: Path | None = None,
    *,
    use_savepoints: bool = True,
) -> dict[str, int | list[str]]:
    """
    Загрузить всех контрагентов из counterparties.json.

    :param file_path: путь к JSON (по умолчанию seed/data/counterparties.json)
    :param use_savepoints: если True — каждый контрагент в отдельном savepoint,
        ошибка одного не откатывает остальные.
    :return: {"ok": N, "fail": M, "errors": [...]}
    """
    path = file_path or (DATA_DIR / "counterparties.json")
    rows = json.loads(path.read_text(encoding="utf-8"))

    stats: dict[str, int | list[str]] = {"ok": 0, "fail": 0, "errors": []}

    for row in rows:
        inn = row.get("inn")
        if not inn:
            stats["fail"] += 1
            stats["errors"].append(f"no inn: {row}")
            continue

        try:
            if use_savepoints:
                async with session.begin_nested():
                    await load_counterparty_from_json(session, row)
            else:
                await load_counterparty_from_json(session, row)

            stats["ok"] += 1
            print(f"OK: {inn} ({row.get('name', '?')})")

        except Exception as e:
            stats["fail"] += 1
            stats["errors"].append(f"{inn}: {e}")
            print(f"FAIL: {inn}: {e}")

    return stats
