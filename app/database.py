import os
import logging
import json
import hashlib
import sqlite3
import tempfile
import zipfile
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .catalog_types import catalog_item_allows_decimal, classify_catalog_item_type

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./requisiciones.db")
BACKUP_FORMAT_VERSION = "requisiciones-backup-v1"

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


def is_sqlite_database() -> bool:
    return DATABASE_URL.startswith("sqlite")


def get_sqlite_database_path() -> Path:
    if not is_sqlite_database():
        raise RuntimeError("La funcionalidad de respaldo solo soporta SQLite")
    url = make_url(DATABASE_URL)
    database = url.database
    if not database:
        raise RuntimeError("DATABASE_URL no apunta a una base SQLite valida")
    path = Path(database)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def get_backup_directory() -> Path:
    configured = os.getenv("BACKUPS_DIR", "backups")
    path = Path(configured)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path


def _local_now() -> datetime:
    tz_name = os.getenv("TZ", "America/El_Salvador")
    try:
        return datetime.now(ZoneInfo(tz_name))
    except Exception:
        return datetime.now()


def _backup_timestamp_slug() -> str:
    return _local_now().strftime("%Y%m%d_%H%M%S")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sanitize_database_url() -> str:
    if not is_sqlite_database():
        return DATABASE_URL
    return f"sqlite:///{get_sqlite_database_path().name}"


def _collect_sqlite_tables() -> list[str]:
    with engine.begin() as conn:
        rows = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        ).fetchall()
    return [row[0] for row in rows]


def read_backup_manifest(archive_path: Path) -> dict[str, object]:
    with zipfile.ZipFile(archive_path, "r") as zf:
        try:
            raw = zf.read("manifest.json")
        except KeyError as exc:
            raise ValueError("El respaldo no contiene manifest.json") from exc
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ValueError("No se pudo leer el manifest del respaldo") from exc
    if manifest.get("backup_format") != BACKUP_FORMAT_VERSION:
        raise ValueError("Formato de respaldo no soportado")
    return manifest


def list_backup_archives() -> list[dict[str, object]]:
    backup_dir = get_backup_directory()
    if not backup_dir.exists():
        return []
    backups: list[dict[str, object]] = []
    for archive_path in sorted(backup_dir.glob("*.zip"), key=lambda item: item.stat().st_mtime, reverse=True):
        item = {
            "filename": archive_path.name,
            "size_bytes": archive_path.stat().st_size,
            "modified_at": datetime.fromtimestamp(archive_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "generated_at": None,
            "database_sha256": None,
            "backup_format": None,
        }
        try:
            manifest = read_backup_manifest(archive_path)
        except Exception:
            backups.append(item)
            continue
        item["generated_at"] = manifest.get("generated_at")
        item["database_sha256"] = manifest.get("database_sha256")
        item["backup_format"] = manifest.get("backup_format")
        backups.append(item)
    return backups


def resolve_backup_archive(filename: str) -> Path:
    safe_name = Path(filename).name
    if safe_name != filename or not safe_name.endswith(".zip"):
        raise ValueError("Nombre de respaldo invalido")
    archive_path = get_backup_directory() / safe_name
    if not archive_path.exists():
        raise FileNotFoundError("Respaldo no encontrado")
    return archive_path


def create_backup_archive(prefix: str = "backup") -> Path:
    db_path = get_sqlite_database_path()
    if not db_path.exists():
        raise FileNotFoundError("No se encontro la base de datos operativa")

    backup_dir = get_backup_directory()
    backup_dir.mkdir(parents=True, exist_ok=True)
    archive_name = f"{prefix}_{_backup_timestamp_slug()}.zip"
    archive_path = backup_dir / archive_name

    with tempfile.TemporaryDirectory(prefix="req-backup-") as temp_dir:
        temp_dir_path = Path(temp_dir)
        snapshot_path = temp_dir_path / db_path.name
        with sqlite3.connect(str(db_path), timeout=30) as source_db:
            source_db.execute("PRAGMA busy_timeout = 5000")
            with sqlite3.connect(str(snapshot_path), timeout=30) as snapshot_db:
                source_db.backup(snapshot_db)
        manifest = {
            "backup_format": BACKUP_FORMAT_VERSION,
            "generated_at": _local_now().strftime("%Y-%m-%d %H:%M:%S"),
            "database_filename": db_path.name,
            "database_sha256": _sha256_file(snapshot_path),
            "database_size_bytes": snapshot_path.stat().st_size,
            "database_url_sanitized": _sanitize_database_url(),
            "app_name": os.getenv("APP_NAME", "Sistema de Requisiciones MVP"),
            "app_version": os.getenv("APP_VERSION", "local"),
            "tables": _collect_sqlite_tables(),
            "secret_key_present": bool(os.getenv("SECRET_KEY")),
        }
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(snapshot_path, arcname=db_path.name)
            archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    return archive_path


def restore_backup_archive(archive_path: Path) -> dict[str, object]:
    db_path = get_sqlite_database_path()
    if not db_path.exists():
        raise FileNotFoundError("No se encontro la base de datos operativa")

    manifest = read_backup_manifest(archive_path)
    safety_backup = create_backup_archive(prefix="pre_restore")

    with tempfile.TemporaryDirectory(prefix="req-restore-") as temp_dir:
        temp_dir_path = Path(temp_dir)
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(temp_dir_path)

        extracted_db = temp_dir_path / str(manifest.get("database_filename") or db_path.name)
        if not extracted_db.exists():
            db_candidates = list(temp_dir_path.glob("*.db"))
            if not db_candidates:
                raise ValueError("El respaldo no contiene una base SQLite valida")
            extracted_db = db_candidates[0]

        with sqlite3.connect(str(extracted_db), timeout=30) as source_db:
            source_db.execute("SELECT name FROM sqlite_master LIMIT 1")

        engine.dispose()
        with sqlite3.connect(str(extracted_db), timeout=30) as source_db:
            source_db.execute("PRAGMA busy_timeout = 5000")
            with sqlite3.connect(str(db_path), timeout=30) as target_db:
                target_db.execute("PRAGMA busy_timeout = 5000")
                source_db.backup(target_db)
        engine.dispose()
        run_migrations()

    return {
        "manifest": manifest,
        "safety_backup": safety_backup.name,
    }


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
            conn.execute(text("UPDATE usuarios SET rol = 'logistica' WHERE rol = 'auditor'"))

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
            if "prepared_at" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN prepared_at DATETIME"))
            if "prepared_by" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN prepared_by INTEGER REFERENCES usuarios(id)"))
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
            if "receptor_designado_id" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE requisiciones "
                        "ADD COLUMN receptor_designado_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL"
                    )
                )
            if "motivo_requisicion" not in columns:
                conn.execute(text("ALTER TABLE requisiciones ADD COLUMN motivo_requisicion TEXT"))

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
                "prokey_no_aplica": "ALTER TABLE requisiciones ADD COLUMN prokey_no_aplica BOOLEAN NOT NULL DEFAULT 0",
                "prokey_ref_actualizada_at": "ALTER TABLE requisiciones ADD COLUMN prokey_ref_actualizada_at TIMESTAMP",
                "prokey_ref_actualizada_por": "ALTER TABLE requisiciones ADD COLUMN prokey_ref_actualizada_por INTEGER REFERENCES usuarios(id)",
                "liquidation_comment": "ALTER TABLE requisiciones ADD COLUMN liquidation_comment TEXT",
                "liquidated_by": "ALTER TABLE requisiciones ADD COLUMN liquidated_by INTEGER REFERENCES usuarios(id)",
                "liquidated_at": "ALTER TABLE requisiciones ADD COLUMN liquidated_at TIMESTAMP",
                "prokey_liquidada_at": "ALTER TABLE requisiciones ADD COLUMN prokey_liquidada_at TIMESTAMP",
                "prokey_liquidada_por": "ALTER TABLE requisiciones ADD COLUMN prokey_liquidada_por INTEGER REFERENCES usuarios(id)",
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

            # SQLite no permite ALTER CHECK constraint; si la tabla historica quedó
            # con CHECK de estado antiguo, reconstruimos tabla para incluir
            # estados operativos recientes y evitar fallos de commit/filtros.
            table_sql_row = conn.execute(
                text("SELECT sql FROM sqlite_master WHERE type='table' AND name='requisiciones'")
            ).fetchone()
            table_sql = (table_sql_row[0] or "").lower() if table_sql_row else ""
            if table_sql and (
                "liquidada_en_prokey" not in table_sql
                or "preparado" not in table_sql
                or "no_entregada" not in table_sql
                or "pendiente_prokey" not in table_sql
                or "finalizada_sin_prokey" not in table_sql
            ):
                logger.warning(
                    "Detectado CHECK antiguo en requisiciones.estado; reconstruyendo tabla para incluir estados operativos y finales nuevos"
                )
                conn.execute(text("PRAGMA foreign_keys=OFF"))
                try:
                    conn.execute(text("ALTER TABLE requisiciones RENAME TO requisiciones_old"))
                    conn.execute(
                        text(
                            """
                            CREATE TABLE requisiciones (
                                id INTEGER NOT NULL PRIMARY KEY,
                                folio VARCHAR(30) NOT NULL UNIQUE,
                                solicitante_id INTEGER NOT NULL REFERENCES usuarios(id),
                                departamento VARCHAR(80) NOT NULL,
                                cliente_codigo VARCHAR(40),
                                cliente_nombre VARCHAR(160),
                                cliente_ruta_principal VARCHAR(4),
                                estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
                                motivo_requisicion VARCHAR(80),
                                justificacion TEXT NOT NULL,
                                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                                approved_at DATETIME,
                                approved_by INTEGER REFERENCES usuarios(id),
                                approval_comment TEXT,
                                prepared_at DATETIME,
                                prepared_by INTEGER REFERENCES usuarios(id),
                                delivered_at DATETIME,
                                delivered_by INTEGER REFERENCES usuarios(id),
                                recibido_por_id INTEGER REFERENCES usuarios(id),
                                delivered_to VARCHAR(120),
                                recibido_at TEXT,
                                delivery_result VARCHAR(20),
                                delivery_comment TEXT,
                                receptor_designado_id INTEGER REFERENCES usuarios(id) ON DELETE SET NULL,
                                prokey_ref TEXT,
                                prokey_no_aplica BOOLEAN NOT NULL DEFAULT 0,
                                prokey_ref_actualizada_at TIMESTAMP,
                                prokey_ref_actualizada_por INTEGER REFERENCES usuarios(id),
                                liquidation_comment TEXT,
                                liquidated_by INTEGER REFERENCES usuarios(id),
                                liquidated_at TIMESTAMP,
                                prokey_liquidada_at TIMESTAMP,
                                prokey_liquidada_por INTEGER REFERENCES usuarios(id),
                                rejected_at DATETIME,
                                rejected_by INTEGER,
                                rejection_reason TEXT,
                                rejection_comment TEXT,
                                CONSTRAINT ck_requisiciones_estado CHECK (
                                    estado in ('pendiente', 'aprobada', 'preparado', 'rechazada', 'entregada', 'no_entregada', 'liquidada', 'pendiente_prokey', 'finalizada_sin_prokey', 'liquidada_en_prokey')
                                )
                            )
                            """
                        )
                    )
                    conn.execute(
                        text(
                            """
                            INSERT INTO requisiciones (
                                id, folio, solicitante_id, departamento, cliente_codigo, cliente_nombre, cliente_ruta_principal,
                                estado, motivo_requisicion, justificacion, created_at, approved_at, approved_by, approval_comment,
                                prepared_at, prepared_by,
                                delivered_at, delivered_by, recibido_por_id, delivered_to, recibido_at, delivery_result,
                                delivery_comment, receptor_designado_id, prokey_ref, prokey_no_aplica, prokey_ref_actualizada_at, prokey_ref_actualizada_por, liquidation_comment, liquidated_by,
                                liquidated_at, prokey_liquidada_at, prokey_liquidada_por, rejected_at, rejected_by,
                                rejection_reason, rejection_comment
                            )
                            SELECT
                                id, folio, solicitante_id, departamento, cliente_codigo, cliente_nombre, cliente_ruta_principal,
                                estado, motivo_requisicion, justificacion, created_at, approved_at, approved_by, approval_comment,
                                prepared_at, prepared_by,
                                delivered_at, delivered_by, recibido_por_id, delivered_to, recibido_at, delivery_result,
                                delivery_comment, receptor_designado_id, prokey_ref, 0, prokey_ref_actualizada_at, prokey_ref_actualizada_por, liquidation_comment, liquidated_by,
                                liquidated_at, prokey_liquidada_at, prokey_liquidada_por, rejected_at, rejected_by,
                                rejection_reason, rejection_comment
                            FROM requisiciones_old
                            """
                        )
                    )
                    conn.execute(text("DROP TABLE requisiciones_old"))
                finally:
                    conn.execute(text("PRAGMA foreign_keys=ON"))

            conn.execute(
                text(
                    """
                    UPDATE requisiciones
                    SET estado = 'no_entregada'
                    WHERE estado = 'entregada' AND delivery_result = 'no_entregada'
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE requisiciones
                    SET prokey_no_aplica = 1
                    WHERE estado IN ('liquidada', 'finalizada_sin_prokey')
                      AND EXISTS (
                        SELECT 1
                        FROM items
                        WHERE items.requisicion_id = requisiciones.id
                      )
                      AND NOT EXISTS (
                        SELECT 1
                        FROM items
                        WHERE items.requisicion_id = requisiciones.id
                          AND COALESCE(items.qty_used, 0) > 0
                      )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE requisiciones
                    SET estado = 'finalizada_sin_prokey'
                    WHERE estado = 'liquidada' AND COALESCE(prokey_no_aplica, 0) = 1
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE requisiciones
                    SET estado = 'pendiente_prokey'
                    WHERE estado = 'liquidada' AND COALESCE(prokey_no_aplica, 0) = 0
                    """
                )
            )

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
            if "permite_decimal" not in catalog_columns:
                conn.execute(text("ALTER TABLE catalogo_items ADD COLUMN permite_decimal INTEGER NOT NULL DEFAULT 0"))
            catalog_rows = conn.execute(
                text("SELECT id, nombre, tipo_item, permite_decimal FROM catalogo_items")
            ).fetchall()
            for item_id, nombre, tipo_item, permite_decimal in catalog_rows:
                if tipo_item is not None:
                    pass
                else:
                    computed = classify_catalog_item_type(nombre or "")
                    if computed is not None:
                        conn.execute(
                            text("UPDATE catalogo_items SET tipo_item = :tipo_item WHERE id = :item_id"),
                            {"tipo_item": computed, "item_id": item_id},
                        )
                expected_decimal = 1 if catalog_item_allows_decimal(nombre or "") else 0
                if permite_decimal != expected_decimal:
                    conn.execute(
                        text("UPDATE catalogo_items SET permite_decimal = :permite_decimal WHERE id = :item_id"),
                        {"permite_decimal": expected_decimal, "item_id": item_id},
                    )
