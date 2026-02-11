import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./requisiciones.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def run_migrations() -> None:
    """Minimal incremental migrations for SQLite local MVP."""
    if not DATABASE_URL.startswith("sqlite"):
        return

    with engine.begin() as conn:
        user_columns = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(usuarios)")).fetchall()
        }
        if "activo" not in user_columns:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN activo BOOLEAN NOT NULL DEFAULT 1"))

        columns = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(requisiciones)")).fetchall()
        }
        if "rejected_at" not in columns:
            conn.execute(text("ALTER TABLE requisiciones ADD COLUMN rejected_at DATETIME"))
        if "rejected_by" not in columns:
            conn.execute(text("ALTER TABLE requisiciones ADD COLUMN rejected_by INTEGER"))
        if "cliente_codigo" not in columns:
            conn.execute(text("ALTER TABLE requisiciones ADD COLUMN cliente_codigo VARCHAR(40)"))
        if "cliente_nombre" not in columns:
            conn.execute(text("ALTER TABLE requisiciones ADD COLUMN cliente_nombre VARCHAR(160)"))
        if "approval_comment" not in columns:
            conn.execute(text("ALTER TABLE requisiciones ADD COLUMN approval_comment TEXT"))
        if "rejection_comment" not in columns:
            conn.execute(text("ALTER TABLE requisiciones ADD COLUMN rejection_comment TEXT"))
        if "delivery_result" not in columns:
            conn.execute(text("ALTER TABLE requisiciones ADD COLUMN delivery_result VARCHAR(20)"))
        if "delivery_comment" not in columns:
            conn.execute(text("ALTER TABLE requisiciones ADD COLUMN delivery_comment TEXT"))

        item_columns = {
            row[1]
            for row in conn.execute(text("PRAGMA table_info(items)")).fetchall()
        }
        if "cantidad_entregada" not in item_columns:
            conn.execute(text("ALTER TABLE items ADD COLUMN cantidad_entregada FLOAT"))
