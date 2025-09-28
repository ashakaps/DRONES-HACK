from sqlmodel import SQLModel, create_engine, Session
import os

# Для PostgreSQL используем asyncpg или psycopg2
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    # Для SQLite оставляем старые настройки
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Для PostgreSQL
    engine = create_engine(DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session