from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import settings

# psycopg3 usa "postgresql+psycopg", psycopg2 usa "postgresql+psycopg2"
# Railway injeta DATABASE_URL como "postgresql://..." — corrigimos o prefixo aqui
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+psycopg://", "postgresql+psycopg://"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()