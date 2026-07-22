from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from app.core.config import settings


def _build_engine():
    url = settings.DATABASE_URL
    if url.startswith("sqlite"):
        return create_async_engine(
            url,
            echo=settings.APP_ENV == "development",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    connect_args: dict = {}
    if settings.DATABASE_SSL:
        # Railway Postgres requires TLS
        connect_args["ssl"] = True

    return create_async_engine(
        url,
        echo=settings.APP_ENV == "development",
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = _build_engine()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
