from datetime import datetime
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

import app.database as database_module
from app.auth import hash_password
from app.database import run_migrations
from app.crud import transicionar_requisicion
from app.models import Base, Item, Requisicion, Usuario

TEST_DB_URL = "sqlite:///./test_liquidacion_model.db"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as seed_db:
        seed_db.add_all(
            [
                Usuario(
                    username="user.ops",
                    password=hash_password("pass123"),
                    nombre="Usuario Ops",
                    rol="user",
                    departamento="Operaciones",
                ),
                Usuario(
                    username="aprob.ops",
                    password=hash_password("pass123"),
                    nombre="Aprobador Ops",
                    rol="aprobador",
                    departamento="Operaciones",
                ),
                Usuario(
                    username="bodega.1",
                    password=hash_password("pass123"),
                    nombre="Bodega Uno",
                    rol="bodega",
                    departamento="Bodega",
                ),
            ]
        )
        seed_db.commit()

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_estado_liquidada_es_valido(db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = Requisicion(
        folio="REQ-LIQ-0001",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="liquidada",
        justificacion="Prueba estado liquidada",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)
    assert req.estado == "liquidada"


def test_campos_liquidacion_item_nullable(db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = Requisicion(
        folio="REQ-LIQ-0002",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Prueba nullables item",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    item = Item(requisicion_id=req.id, descripcion="Mopa", cantidad=1, unidad="unidad")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    assert item.qty_returned_to_warehouse is None
    assert item.qty_used is None
    assert item.qty_left_at_client is None
    assert item.item_liquidation_note is None
    assert item.liquidation_alerts is None


def test_campos_liquidacion_requisicion_nullable(db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = Requisicion(
        folio="REQ-LIQ-0003",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Prueba nullables requisicion",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    assert req.prokey_ref is None
    assert req.liquidation_comment is None
    assert req.liquidated_by is None
    assert req.liquidated_at is None


def test_backfill_entrega_completa(db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-LIQ-0004",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Entrega completa",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)
    db_session.add_all(
        [
            Item(requisicion_id=req.id, descripcion="Item A", cantidad=2, unidad="unidad"),
            Item(requisicion_id=req.id, descripcion="Item B", cantidad=3, unidad="unidad"),
        ]
    )
    db_session.commit()

    for item in req.items:
        if item.cantidad_entregada is None:
            item.cantidad_entregada = item.cantidad
    transicionar_requisicion(
        db_session,
        req,
        nuevo_estado="entregada",
        actor_id=bodega.id,
        delivered_to="Juan Perez",
        delivery_result="completa",
        delivery_comment="Entrega total",
    )
    db_session.refresh(req)
    assert req.estado == "entregada"
    for item in req.items:
        assert item.cantidad_entregada == item.cantidad


def test_entrega_parcial_no_se_sobreescribe(db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-LIQ-0005",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Entrega parcial",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    item = Item(requisicion_id=req.id, descripcion="Item C", cantidad=1, unidad="unidad")
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    item.cantidad_entregada = 0.5

    transicionar_requisicion(
        db_session,
        req,
        nuevo_estado="entregada",
        actor_id=bodega.id,
        delivered_to="Juan Perez",
        delivery_result="parcial",
        delivery_comment="Faltante parcial",
    )
    db_session.refresh(item)
    assert item.cantidad_entregada == 0.5


@pytest.fixture
def isolated_migration_engine(tmp_path: Path):
    original_url = database_module.DATABASE_URL
    original_engine = database_module.engine
    original_sessionlocal = database_module.SessionLocal

    db_path = tmp_path / "migration_liquidacion.db"
    url = f"sqlite:///{db_path}"
    test_engine = create_engine(url, connect_args={"check_same_thread": False})

    database_module.DATABASE_URL = url
    database_module.engine = test_engine
    database_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    try:
        yield test_engine
    finally:
        test_engine.dispose()
        database_module.DATABASE_URL = original_url
        database_module.engine = original_engine
        database_module.SessionLocal = original_sessionlocal


def test_migracion_no_falla_en_db_nueva(isolated_migration_engine):
    run_migrations()
    with isolated_migration_engine.connect() as conn:
        req_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(requisiciones)")).fetchall()}
        item_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(items)")).fetchall()}

    assert {"prokey_ref", "liquidation_comment", "liquidated_by", "liquidated_at"}.issubset(req_cols)
    assert {
        "qty_returned_to_warehouse",
        "qty_used",
        "qty_left_at_client",
        "item_liquidation_note",
        "liquidation_alerts",
    }.issubset(item_cols)


def test_migracion_idempotente(isolated_migration_engine):
    run_migrations()
    run_migrations()
    with isolated_migration_engine.connect() as conn:
        req_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(requisiciones)")).fetchall()}
    assert "liquidated_at" in req_cols


def test_migracion_convierte_liquidada_a_estados_semanticos(isolated_migration_engine):
    with isolated_migration_engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE usuarios (
                    id INTEGER NOT NULL PRIMARY KEY,
                    username VARCHAR(80) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    nombre VARCHAR(120) NOT NULL,
                    rol VARCHAR(20) NOT NULL,
                    departamento VARCHAR(80) NOT NULL,
                    activo BOOLEAN NOT NULL DEFAULT 1,
                    pin_hash VARCHAR(255),
                    puede_iniciar_sesion BOOLEAN NOT NULL DEFAULT 1
                )
                """
            )
        )
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
                        estado in ('pendiente', 'aprobada', 'preparado', 'rechazada', 'entregada', 'no_entregada', 'liquidada', 'liquidada_en_prokey')
                    )
                )
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE TABLE items (
                    id INTEGER NOT NULL PRIMARY KEY,
                    requisicion_id INTEGER NOT NULL REFERENCES requisiciones(id) ON DELETE CASCADE,
                    descripcion TEXT NOT NULL,
                    cantidad FLOAT NOT NULL,
                    cantidad_entregada FLOAT,
                    qty_returned_to_warehouse FLOAT,
                    qty_used FLOAT,
                    qty_left_at_client FLOAT,
                    liquidation_mode VARCHAR(20),
                    contexto_operacion VARCHAR(30),
                    es_demo BOOLEAN NOT NULL DEFAULT 0,
                    item_liquidation_note VARCHAR,
                    liquidation_alerts VARCHAR,
                    unidad VARCHAR(40) NOT NULL,
                    CONSTRAINT ck_items_cantidad_positive CHECK (cantidad > 0)
                )
                """
            )
        )
        conn.execute(
            text(
                "INSERT INTO usuarios (id, username, password, nombre, rol, departamento, activo, puede_iniciar_sesion) "
                "VALUES (1, 'user.ops', 'hash', 'Usuario Ops', 'user', 'Operaciones', 1, 1)"
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO requisiciones (id, folio, solicitante_id, departamento, estado, justificacion)
                VALUES
                    (1, 'REQ-MIG-001', 1, 'Operaciones', 'liquidada', 'Debe pasar a pendiente_prokey'),
                    (2, 'REQ-MIG-002', 1, 'Operaciones', 'liquidada', 'Debe pasar a finalizada_sin_prokey')
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO items (requisicion_id, descripcion, cantidad, cantidad_entregada, qty_used, qty_left_at_client, qty_returned_to_warehouse, unidad)
                VALUES
                    (1, 'Item 1', 3, 3, 1, 2, 3, 'unidad'),
                    (2, 'Item 2', 4, 4, 0, 4, 4, 'unidad')
                """
            )
        )

    run_migrations()

    with isolated_migration_engine.connect() as conn:
        rows = conn.execute(
            text("SELECT folio, estado, prokey_no_aplica FROM requisiciones ORDER BY id")
        ).fetchall()

    assert rows[0] == ("REQ-MIG-001", "pendiente_prokey", 0)
    assert rows[1] == ("REQ-MIG-002", "finalizada_sin_prokey", 1)
