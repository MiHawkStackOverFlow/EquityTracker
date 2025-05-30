from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# postgresql+asyncpg://postgres:postgres@localhost:5432/equitytracker_db
DATABASE_URL = os.environ.get("DATABASE_URL")

# Async engine
print("Loaded DB URL:", DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=True)

# Session factory
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()

# Dependency: get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
