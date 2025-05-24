from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from pathlib import Path
import os

# Load from .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DB_HOST = os.environ.getenv("DB_HOST")
DB_PORT = os.environ.getenv("DB_PORT")
DB_NAME = os.environ.getenv("DB_NAME")
DB_USER = os.environ.getenv("DB_USER")
DB_PASSWORD = os.environ.getenv("DB_PASSWORD")

# postgresql+asyncpg://postgres:postgres@localhost:5432/equitytracker_db
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

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
