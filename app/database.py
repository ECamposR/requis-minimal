import os
import logging
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
logger = logging.getLogger(__name__)


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

    # Ensure base tables exist before applying incremental ALTER TABLE statements.
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        tables = {
            row[0]
            for row in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        }

        if "usuarios" in tables:
            user_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(usuarios)")).fetchall()
            }
            if "activo" not in user_columns:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN activo BOOLEAN NOT NULL DEFAULT 1"))

        if "requisiciones" in tables:
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
            if "cliente_ruta_principal" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN cliente_ruta_principal VARCHAR(4)"))
            if "approval_comment" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN approval_comment TEXT"))
            if "rejection_comment" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN rejection_comment TEXT"))
            if "delivery_result" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN delivery_result VARCHAR(20)"))
            if "delivery_comment" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN delivery_comment TEXT"))

        if "items" in tables:
            item_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(items)")).fetchall()
            }
            if "cantidad_entregada" not in item_columns:
                conn.execute(text("ALTER TABLE items ADD COLUMN cantidad_entregada FLOAT"))

        liq_migrations = [
            "ALTER TABLE requisiciones ADD COLUMN prokey_ref TEXT",
            "ALTER TABLE requisiciones ADD COLUMN liquidation_comment TEXT",
            "ALTER TABLE requisiciones ADD COLUMN liquidated_by INTEGER REFERENCES usuarios(id)",
            "ALTER TABLE requisiciones ADD COLUMN liquidated_at TIMESTAMP",
            "ALTER TABLE items ADD COLUMN qty_returned_to_warehouse INTEGER",
            "ALTER TABLE items ADD COLUMN qty_used INTEGER",
            "ALTER TABLE items ADD COLUMN qty_left_at_client INTEGER",
            "ALTER TABLE items ADD COLUMN liquidation_mode TEXT",
            "ALTER TABLE items ADD COLUMN item_liquidation_note TEXT",
            "ALTER TABLE items ADD COLUMN liquidation_alerts TEXT",
        ]

        for sql in liq_migrations:
            try:
                conn.execute(text(sql))
            except Exception as e:
                err_msg = str(e).lower()
                if "duplicate column" in err_msg or "already exists" in err_msg:
                    continue
                logger.error("Error en migracion de liquidacion: %s -> %s", sql, e)
                raise

        # Backfill baseline de entrega para historicos de entrega completa.
        try:
            conn.execute(
                text(
                    """
                    UPDATE items SET cantidad_entregada = cantidad
                    WHERE cantidad_entregada IS NULL
                    AND requisicion_id IN (
                        SELECT id FROM requisiciones
                        WHERE estado = 'entregada' AND delivery_result = 'completa'
                    )
                    """
                )
            )
        except Exception as e:
            logger.warning("Backfill cantidad_entregada: %s", e)
