from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from ..config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

engine = None


def get_engine() -> AsyncEngine:
    global engine

    if engine is None:
        try:
            engine = create_async_engine(
                f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}",
                echo=True,
            )
        except Exception as e:
            print("An internal occured while establishing engine connection")
    return engine


SessionLocal = async_sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session():
    async with SessionLocal() as session:
        yield session
