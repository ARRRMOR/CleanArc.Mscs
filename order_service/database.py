from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base


DATABASE_URL = "postgresql+asyncpg://user:password@order_db:5432/order_db"


Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)
LocalSession = async_sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with LocalSession() as session:
        yield session



































































































