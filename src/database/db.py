import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Get database configuration from environment variables with defaults
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "postgres")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(
    url=DATABASE_URL,
    pool_size=20,
    max_overflow=30
)

new_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)