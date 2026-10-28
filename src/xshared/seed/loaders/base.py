from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


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
