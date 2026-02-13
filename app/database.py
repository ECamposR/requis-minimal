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
            if "liquidated_by" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN liquidated_by INTEGER"))
            if "liquidated_at" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN liquidated_at DATETIME"))

            req_sql = conn.execute(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name='requisiciones'")
            ).scalar()
            needs_rebuild = req_sql and (
                "'liquidada'" not in str(req_sql)
                or "liquidated_by" not in str(req_sql)
                or "liquidated_at" not in str(req_sql)
            )
            if needs_rebuild:
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                conn.execute(
                    text(
                        """
                        CREATE TABLE requisiciones_new (
                            id INTEGER NOT NULL PRIMARY KEY,
                            folio VARCHAR(30) NOT NULL UNIQUE,
                            solicitante_id INTEGER NOT NULL,
                            departamento VARCHAR(80) NOT NULL,
                            cliente_codigo VARCHAR(40),
                            cliente_nombre VARCHAR(160),
                            cliente_ruta_principal VARCHAR(4),
                            estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
                            justificacion TEXT NOT NULL,
                            created_at DATETIME NOT NULL,
                            approved_at DATETIME,
                            approved_by INTEGER,
                            approval_comment TEXT,
                            delivered_at DATETIME,
                            delivered_by INTEGER,
                            delivered_to VARCHAR(120),
                            delivery_result VARCHAR(20),
                            delivery_comment TEXT,
                            liquidated_at DATETIME,
                            liquidated_by INTEGER,
                            rejected_at DATETIME,
                            rejected_by INTEGER,
                            rejection_reason TEXT,
                            rejection_comment TEXT,
                            CONSTRAINT ck_requisiciones_estado CHECK (
                                estado in ('pendiente', 'aprobada', 'rechazada', 'entregada', 'liquidada')
                            ),
                            FOREIGN KEY(solicitante_id) REFERENCES usuarios(id),
                            FOREIGN KEY(approved_by) REFERENCES usuarios(id),
                            FOREIGN KEY(rejected_by) REFERENCES usuarios(id),
                            FOREIGN KEY(delivered_by) REFERENCES usuarios(id),
                            FOREIGN KEY(liquidated_by) REFERENCES usuarios(id)
                        )
                        """
                    )
                )
                conn.execute(
                    text(
                        """
                        INSERT INTO requisiciones_new (
                            id, folio, solicitante_id, departamento, cliente_codigo, cliente_nombre, cliente_ruta_principal,
                            estado, justificacion, created_at, approved_at, approved_by, approval_comment, delivered_at,
                            delivered_by, delivered_to, delivery_result, delivery_comment, liquidated_at, liquidated_by,
                            rejected_at, rejected_by,
                            rejection_reason, rejection_comment
                        )
                        SELECT
                            id, folio, solicitante_id, departamento, cliente_codigo, cliente_nombre, cliente_ruta_principal,
                            estado, justificacion, created_at, approved_at, approved_by, approval_comment, delivered_at,
                            delivered_by, delivered_to, delivery_result, delivery_comment, liquidated_at, liquidated_by,
                            rejected_at, rejected_by,
                            rejection_reason, rejection_comment
                        FROM requisiciones
                        """
                    )
                )
                conn.execute(text("DROP TABLE requisiciones"))
                conn.execute(text("ALTER TABLE requisiciones_new RENAME TO requisiciones"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_requisiciones_id ON requisiciones (id)"))
                conn.execute(text("PRAGMA foreign_keys=ON"))

        if "items" in tables:
            item_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(items)")).fetchall()
            }
            if "cantidad_entregada" not in item_columns:
                conn.execute(text("ALTER TABLE items ADD COLUMN cantidad_entregada FLOAT"))
            if "cantidad_usada" not in item_columns:
                conn.execute(text("ALTER TABLE items ADD COLUMN cantidad_usada INTEGER NOT NULL DEFAULT 0"))
            if "cantidad_devuelta_sin_usar" not in item_columns:
                conn.execute(
                    text("ALTER TABLE items ADD COLUMN cantidad_devuelta_sin_usar INTEGER NOT NULL DEFAULT 0")
                )
            if "cantidad_devuelta_danada" not in item_columns:
                conn.execute(
                    text("ALTER TABLE items ADD COLUMN cantidad_devuelta_danada INTEGER NOT NULL DEFAULT 0")
                )
            if "pk_register" not in item_columns:
                conn.execute(text("ALTER TABLE items ADD COLUMN pk_register BOOLEAN NOT NULL DEFAULT 0"))
            if "pk_qty_override" not in item_columns:
                conn.execute(text("ALTER TABLE items ADD COLUMN pk_qty_override INTEGER"))

        if "catalogo_items" in tables:
            catalogo_columns = {
                row[1]
                for row in conn.execute(text("PRAGMA table_info(catalogo_items)")).fetchall()
            }
            if "es_servicio" not in catalogo_columns:
                conn.execute(text("ALTER TABLE catalogo_items ADD COLUMN es_servicio BOOLEAN NOT NULL DEFAULT 0"))
