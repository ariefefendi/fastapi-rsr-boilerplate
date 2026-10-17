import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Pakai env yang sama dengan docker-compose (.env)
DATABASE_URL = URL.create(
    drivername="mysql+mysqldb",  # mysqlclient, sudah ada di Dockerfile
    username=os.getenv("DB_USERNAME", "djangocore_app"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "db"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_DATABASE", "djangocore"),
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
