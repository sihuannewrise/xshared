import ssl
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from xshared.config import settings


def build_ssl_context() -> ssl.SSLContext | None:
    """SSL-контекст для asyncpg (Traefik терминирует TLS)."""
    if not settings.db_ssl_enabled:
        return None

    if settings.db_ssl_ca_path:
        return ssl.create_default_context(cafile=settings.db_ssl_ca_path)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


def build_connect_args() -> dict[str, Any]:
    """connect_args для create_async_engine / async_engine_from_config."""
    ssl_ctx = build_ssl_context()
    return {"ssl": ssl_ctx} if ssl_ctx is not None else {}


def create_engine(
    *,
    pool_size: int = 5,
    max_overflow: int = 10,
    pool_pre_ping: bool = True,
    echo: bool = False,
) -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        connect_args=build_connect_args(),
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_pre_ping=pool_pre_ping,
        echo=echo,
    )


engine: AsyncEngine = create_engine(
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    echo=settings.db_echo,
)

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@asynccontextmanager
async def session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    Контекстный менеджер для скриптов, фоновых задач и тестов.

    Использование:
        async with session_scope() as session:
            result = await session.execute(...)
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """Закрыть пул соединений (вызывать при остановке приложения)."""
    await engine.dispose()