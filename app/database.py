import os
import logging
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .catalog_types import classify_catalog_item_type

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
            if "pin_hash" not in user_columns:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN pin_hash TEXT"))
            if "puede_iniciar_sesion" not in user_columns:
                conn.execute(text("ALTER TABLE usuarios ADD COLUMN puede_iniciar_sesion INTEGER NOT NULL DEFAULT 1"))

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
            if "recibido_por_id" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN recibido_por_id INTEGER REFERENCES usuarios(id)"))
            if "recibido_at" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN recibido_at TEXT"))

        if "items" in tables:
            item_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(items)")).fetchall()
            }
            if "cantidad_entregada" not in item_columns:
                conn.execute(text("ALTER TABLE items ADD COLUMN cantidad_entregada FLOAT"))

        if "requisiciones" in tables:
            req_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(requisiciones)")).fetchall()
            }
            req_migrations = {
                "prokey_ref": "ALTER TABLE requisiciones ADD COLUMN prokey_ref TEXT",
                "liquidation_comment": "ALTER TABLE requisiciones ADD COLUMN liquidation_comment TEXT",
                "liquidated_by": "ALTER TABLE requisiciones ADD COLUMN liquidated_by INTEGER REFERENCES usuarios(id)",
                "liquidated_at": "ALTER TABLE requisiciones ADD COLUMN liquidated_at TIMESTAMP",
            }
            for column, sql in req_migrations.items():
                if column in req_columns:
                    continue
                try:
                    conn.execute(text(sql))
                except Exception as e:
                    err_msg = str(e).lower()
                    if "duplicate column" in err_msg or "already exists" in err_msg:
                        continue
                    logger.error("Error en migracion de liquidacion requisiciones: %s -> %s", sql, e)
                    raise

        if "items" in tables:
            item_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(items)")).fetchall()
            }
            item_migrations = {
                "qty_returned_to_warehouse": "ALTER TABLE items ADD COLUMN qty_returned_to_warehouse INTEGER",
                "qty_used": "ALTER TABLE items ADD COLUMN qty_used INTEGER",
                "qty_left_at_client": "ALTER TABLE items ADD COLUMN qty_left_at_client INTEGER",
                "liquidation_mode": "ALTER TABLE items ADD COLUMN liquidation_mode TEXT",
                "contexto_operacion": "ALTER TABLE items ADD COLUMN contexto_operacion TEXT",
                "es_demo": "ALTER TABLE items ADD COLUMN es_demo INTEGER NOT NULL DEFAULT 0",
                "item_liquidation_note": "ALTER TABLE items ADD COLUMN item_liquidation_note TEXT",
                "liquidation_alerts": "ALTER TABLE items ADD COLUMN liquidation_alerts TEXT",
            }
            for column, sql in item_migrations.items():
                if column in item_columns:
                    continue
                try:
                    conn.execute(text(sql))
                except Exception as e:
                    err_msg = str(e).lower()
                    if "duplicate column" in err_msg or "already exists" in err_msg:
                        continue
                    logger.error("Error en migracion de liquidacion items: %s -> %s", sql, e)
                    raise

        if "items" in tables and "requisiciones" in tables:
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

        if "catalogo_items" in tables:
            catalog_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(catalogo_items)")).fetchall()
            }
            if "tipo_item" not in catalog_columns:
                conn.execute(text("ALTER TABLE catalogo_items ADD COLUMN tipo_item VARCHAR(20)"))
            catalog_rows = conn.execute(text("SELECT id, nombre, tipo_item FROM catalogo_items")).fetchall()
            for item_id, nombre, tipo_item in catalog_rows:
                if tipo_item is not None:
                    continue
                computed = classify_catalog_item_type(nombre or "")
                if computed is None:
                    continue
                conn.execute(
                    text("UPDATE catalogo_items SET tipo_item = :tipo_item WHERE id = :item_id"),
                    {"tipo_item": computed, "item_id": item_id},
                )
