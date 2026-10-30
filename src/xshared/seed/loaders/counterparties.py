import asyncio
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from xshared.models import Counterparty, KPP, KppCaMapping
from xshared.seed.dadata import dd_find_by_id
from xshared.seed.loaders.base import get_system_user_id
from xshared.seed.constants import MANAGED_COMPANY_POST_TITLE

DATA_DIR = Path(__file__).parent.parent / "data"
CACHE_DIR = DATA_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def _is_cached(inn: str) -> bool:
    """Проверяет, есть ли файл кэша для указанного ИНН."""
    cache_file = CACHE_DIR / f"party_{inn}.json"
    return cache_file.exists()

# ============================================================
# 1. DaData: парсинг и загрузка
# ============================================================

def _parse_dadata(data: dict) -> dict:
    """Преобразовать ответ DaData в поля Counterparty."""
    opf_full = data["data"]["opf"]["full"]
    name_full = data["data"]["name"]["full"]
    name_full_with_opf = f'{opf_full} "{name_full}"'

    # Безопасное извлечение адреса
    addr = data["data"].get("address") or {}
    addr_data = addr.get("data") or {}

    mgmt = data["data"].get("management") or {}

    result = {
        "name": name_full,
        "name_full_with_opf": name_full_with_opf,
        "opf_short": data["data"]["opf"]["short"],
        "status": data["data"]["state"]["status"],
        "ogrn": data["data"]["ogrn"],
        "ogrn_date": _ts_to_dt(data["data"]["ogrn_date"]),
        "actuality_date": _ts_to_dt(data["data"]["state"]["actuality_date"]),
        "registration_date": _ts_to_dt(data["data"]["state"]["registration_date"]),
        "liquidation_date": _ts_to_dt(data["data"]["state"]["liquidation_date"]),
        "management_start_date": _ts_to_dt(mgmt.get("start_date")),
        "postal_code": addr_data.get("postal_code"),
        "address": addr.get("value"),
        "address_full": addr_data.get("source"),
        "counterparty_type": data["data"]["type"],
        "branch_type": data["data"]["branch_type"],
        "kpp": data["data"]["kpp"],
        "email": data["data"].get("emails"),
    }

    # --- Руководитель (для юрлиц) ---
    if mgmt:
        mgmt_name = (mgmt.get("name") or "").strip()
        mgmt_post = (mgmt.get("post") or "").strip()

        result["management_name"] = mgmt_name if mgmt_name else None
        result["management_disqualified"] = mgmt.get("disqualified")

        if _is_legal_entity_name(mgmt_name):
            result["management_post"] = MANAGED_COMPANY_POST_TITLE
        else:
            result["management_post"] = mgmt_post.capitalize() if mgmt_post else None

            if mgmt_name:
                parts = mgmt_name.split()
                if len(parts) == 1:
                    result["fio_surname"] = parts[0]
                elif len(parts) == 2:
                    result["fio_surname"] = parts[0]
                    result["fio_name"] = parts[1]
                elif len(parts) >= 3:
                    result["fio_surname"] = parts[0]
                    result["fio_name"] = parts[1]
                    result["fio_patronymic"] = " ".join(parts[2:])

    # --- ИП (физлица) ---
    fio = data["data"].get("fio")
    if fio:
        result["fio_surname"] = fio.get("surname")
        result["fio_name"] = fio.get("name")
        result["fio_patronymic"] = fio.get("patronymic")

    return result


def _is_legal_entity_name(name: str) -> bool:
    """Проверяет, является ли строка названием юрлица (есть кавычки)."""
    return bool(name) and any(q in name for q in ('"', '«', '»'))


def _ts_to_dt(ts):
    if ts is None:
        return None
    return datetime.fromtimestamp(ts / 1000)


async def _load_dadata(inn: str) -> dict:
    """Получить данные из кэша, если кэша нет - создать его с данными из DaData."""
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
# 2. Вставка контрагента с КПП
# ============================================================

async def _upsert_counterparty(
    session: AsyncSession, inn: str, data: dict
) -> Counterparty:
    """Создать или обновить контрагента по ИНН (с аудитом от system user)."""
    system_id = await get_system_user_id(session)
    cp_data = {k: v for k, v in data.items() if k not in ("kpp", "inn")}

    cp = await session.scalar(select(Counterparty).where(Counterparty.inn == inn))
    if cp is None:
        cp = Counterparty(
            inn=inn,
            **cp_data,
            created_by=system_id,
            updated_by=system_id,
        )
        session.add(cp)
        await session.flush()
    else:
        for k, v in cp_data.items():
            setattr(cp, k, v)
        cp.updated_by = system_id
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
    """Снять is_basic со всех КПП контрагента."""
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
# 3. Универсальная загрузка (DaData + опционально JSON)
# ============================================================

async def load_counterparty(
    session: AsyncSession,
    inn: str,
    kpps: list[str] | None = None,
    force_db_update: bool = False,
) -> Counterparty:
    """
    Загрузить контрагента по ИНН из DaData.
    Если передан kpps (список КПП), они добавляются как дополнительные.

    :param force_db_update: Если False, обновляет БД только если контрагента там нет.
                            Если True, перезаписывает данные из DaData.
    """
    cp = await session.scalar(select(Counterparty).where(Counterparty.inn == inn))

    if cp is not None and not force_db_update:
        # Если контрагент уже есть и мы не форсируем обновление — пропускаем
        # (но можно опционально дописать связи КПП, если их не было)
        # print(f"SKIP: {inn} (already in DB)")

        # Опционально: если контрагент есть, но у него нет связей КПП, добавим их из JSON
        if kpps:
            for kpp in kpps:
                await _upsert_kpp_mapping(session, cp, kpp, is_basic=False)

        return cp

    # 2. Если контрагента нет ИЛИ force_db_update=True — берем данные из DaData/кэша
    raw = await _load_dadata(inn)
    data = _parse_dadata(raw)

    cp = await _upsert_counterparty(session, inn, data)

    dd_kpp = data.get("kpp")

    if dd_kpp:
        await _reset_basic_for_counterparty(session, cp.id)
        await _upsert_kpp_mapping(session, cp, dd_kpp, is_basic=True)

    if kpps:
        for kpp in kpps:
            if kpp != dd_kpp:
                await _upsert_kpp_mapping(session, cp, kpp, is_basic=False)

    return cp


async def load_counterparties_from_json(
    session: AsyncSession,
    file_path: Path | None = None,
    *,
    offset: int = 0,
    limit: int | None = None,
    delay_seconds: float = 0.2,
    use_savepoints: bool = True,
    force_db_update: bool = False,
    skip_if_cached: bool = False,
) -> dict[str, int | list[str]]:
    """
    Загрузить контрагентов из counterparties.json порциями.
    Формат JSON: [{"inn": "...", "kpps": ["...", "..."]}, ...]

    :param skip_if_cached: Если True, пропускать ИНН, для которых уже есть файл кэша.
    """
    path = file_path or (DATA_DIR / "counterparties.json")
    items = json.loads(path.read_text(encoding="utf-8"))

    items_to_process = items[offset : offset + limit if limit else None]
    stats = {"ok": 0, "fail": 0, "skipped": 0, "errors": [], "total": len(items_to_process)}

    for item in items_to_process:
        inn = item.get("inn")
        kpps = item.get("kpps")

        if not inn:
            stats["fail"] += 1
            stats["errors"].append(f"no inn: {item}")
            continue

        if skip_if_cached and _is_cached(inn):
            stats["skipped"] += 1
            print(f"SKIP: {inn} (cached)")
            continue

        try:
            if use_savepoints:
                async with session.begin_nested():
                    await load_counterparty(session, inn, kpps, force_db_update=force_db_update)
            else:
                await load_counterparty(session, inn, kpps, force_db_update=force_db_update)

            stats["ok"] += 1
            print(f"OK: {inn}")

            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

        except Exception as e:
            stats["fail"] += 1
            stats["errors"].append(f"{inn}: {e}")
            print(f"FAIL: {inn}: {e}")
            if session.in_transaction():
                await session.rollback()

    return stats
