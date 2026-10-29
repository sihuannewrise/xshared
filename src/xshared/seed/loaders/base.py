from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from xshared.models import User
from xshared.seed.constants import SYSTEM_USER_EXTERNAL_ID


async def get_system_user_id(session: AsyncSession) -> int | None:
    """ID технической учётки для seed. None, если не создана (миграция не применена)."""
    return await session.scalar(
        select(User.id).where(User.external_id == SYSTEM_USER_EXTERNAL_ID)
    )


async def with_audit(data: dict, session: AsyncSession) -> dict:
    """Добавить created_by/updated_by = system user к словарю полей."""
    system_id = await get_system_user_id(session)
    return {**data, "created_by": system_id, "updated_by": system_id}


async def get_or_create(session: AsyncSession, model, defaults: dict | None = None, **filters):
    obj = await session.scalar(select(model).filter_by(**filters))
    if obj is not None:
        return obj, False
    obj = model(**filters, **(defaults or {}))
    session.add(obj)
    await session.flush()
    return obj, True

async def upsert_by_field(session: AsyncSession, model, field: str, value, data: dict):
    obj = await session.scalar(select(model).where(getattr(model, field) == value))
    if obj is None:
        obj = model(**{field: value, **data})
        session.add(obj)
        return obj, True
    for k, v in data.items():
        setattr(obj, k, v)
    return obj, False