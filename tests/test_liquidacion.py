import json
from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.crud import puede_liquidar
from app.main import liquidar_guardar
from app.models import Base, Item, Requisicion, Usuario

TEST_DB_URL = "sqlite://"


@pytest.fixture
def test_engine():
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with testing_session_local() as seed_db:
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
                Usuario(
                    username="admin.1",
                    password=hash_password("pass123"),
                    nombre="Admin Uno",
                    rol="admin",
                    departamento="Admon",
                ),
            ]
        )
        seed_db.commit()

    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def db_session(test_engine):
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()


class DummyRequest:
    def __init__(self, data: dict[str, str]):
        self._data = data

    async def form(self):
        return self._data


@pytest.fixture
def anyio_backend():
    return "asyncio"


def create_req_entregada(
    db_session: Session,
    *,
    delivery_result: str = "completa",
    estado: str = "entregada",
    cantidad: float = 10.0,
    cantidad_entregada: float | None = None,
) -> Requisicion:
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprob = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bode = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    req = Requisicion(
        folio=f"REQ-LIQ-{datetime.now().timestamp()}",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado=estado,
        justificacion="Test liquidacion",
        approved_by=aprob.id,
        approved_at=datetime.now(),
        delivered_by=bode.id if estado in ("entregada", "liquidada") else None,
        delivered_at=datetime.now() if estado in ("entregada", "liquidada") else None,
        delivered_to="Cliente Test" if estado in ("entregada", "liquidada") else None,
        delivery_result=delivery_result if estado in ("entregada", "liquidada") else None,
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)
    db_session.add(
        Item(
            requisicion_id=req.id,
            descripcion="Item Test",
            cantidad=cantidad,
            cantidad_entregada=cantidad if cantidad_entregada is None else cantidad_entregada,
            unidad="unidad",
        )
    )
    db_session.commit()
    db_session.refresh(req)
    return req


def get_item(db_session: Session, req: Requisicion) -> Item:
    return db_session.query(Item).filter(Item.requisicion_id == req.id).first()


def test_puede_liquidar_requisicion_entregada_completa(db_session: Session):
    req = create_req_entregada(db_session, delivery_result="completa")
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    assert puede_liquidar(req, bodega) is True


def test_puede_liquidar_rechaza_estado_aprobada(db_session: Session):
    req = create_req_entregada(db_session, estado="aprobada")
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    assert puede_liquidar(req, bodega) is False


def test_puede_liquidar_rechaza_no_entregada(db_session: Session):
    req = create_req_entregada(db_session, delivery_result="no_entregada")
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    assert puede_liquidar(req, bodega) is False


def test_puede_liquidar_rechaza_rol_user(db_session: Session):
    req = create_req_entregada(db_session, delivery_result="completa")
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    assert puede_liquidar(req, user) is False


@pytest.mark.anyio
async def test_liquidar_flujo_feliz_sin_alertas(db_session: Session):
    req = create_req_entregada(db_session, delivery_result="completa", cantidad=10)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "3",
                f"qty_used_{item.id}": "5",
                f"qty_left_{item.id}": "2",
                f"note_{item.id}": "",
                "prokey_ref": "PK-001",
                "liquidation_comment": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    assert response.status_code == 303
    db_session.refresh(req)
    db_session.refresh(item)
    assert req.estado == "liquidada"
    assert req.prokey_ref == "PK-001"
    assert item.liquidation_alerts is None


@pytest.mark.anyio
async def test_liquidar_con_faltante(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "3",
                f"qty_left_{item.id}": "0",
                f"note_{item.id}": "",
                "prokey_ref": "PK-002",
                "liquidation_comment": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    db_session.refresh(item)
    alertas = json.loads(item.liquidation_alerts)
    assert any(a["type"] == "ALERTA_FALTANTE" and a["severity"] == "warn" for a in alertas)


@pytest.mark.anyio
async def test_liquidar_con_retorno_extra(db_session: Session):
    req = create_req_entregada(db_session, cantidad=3)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "5",
                f"qty_used_{item.id}": "0",
                f"qty_left_{item.id}": "0",
                f"note_{item.id}": "",
                "prokey_ref": "PK-003",
                "liquidation_comment": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    db_session.refresh(item)
    alertas = json.loads(item.liquidation_alerts)
    types = {a["type"] for a in alertas}
    severities = {a["severity"] for a in alertas}
    assert {"ALERTA_SOBRANTE", "ALERTA_RETORNO_EXTRA"}.issubset(types)
    assert {"warn", "high"}.issubset(severities)


@pytest.mark.anyio
async def test_liquidar_salida_sin_soporte(db_session: Session):
    req = create_req_entregada(db_session, cantidad=2)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "3",
                f"qty_left_{item.id}": "0",
                f"note_{item.id}": "",
                "prokey_ref": "PK-004",
                "liquidation_comment": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    db_session.refresh(item)
    alertas = json.loads(item.liquidation_alerts)
    types = {a["type"] for a in alertas}
    severities = {a["severity"] for a in alertas}
    assert {"ALERTA_SOBRANTE", "ALERTA_SALIDA_SIN_SOPORTE"}.issubset(types)
    assert {"warn", "high"}.issubset(severities)


@pytest.mark.anyio
async def test_liquidar_no_bloquea_por_delta(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "1",
                f"qty_left_{item.id}": "0",
                "prokey_ref": "PK-005",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada"


@pytest.mark.anyio
async def test_liquidar_requiere_prokey_ref(db_session: Session):
    req = create_req_entregada(db_session)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "1",
                f"qty_used_{item.id}": "1",
                f"qty_left_{item.id}": "1",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    assert response.status_code == 303
    assert f"/liquidar/{req.id}" in response.headers["location"]
    db_session.refresh(req)
    assert req.estado == "entregada"


@pytest.mark.anyio
async def test_liquidar_inmutable_no_reliquidar(db_session: Session):
    req = create_req_entregada(db_session)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    first = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "1",
                f"qty_used_{item.id}": "1",
                f"qty_left_{item.id}": "8",
                "prokey_ref": "PK-006",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    assert first.status_code == 303
    db_session.refresh(req)
    first_ref = req.prokey_ref

    second = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "10",
                f"qty_left_{item.id}": "0",
                "prokey_ref": "PK-CHANGED",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    assert second.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada"
    assert req.prokey_ref == first_ref


@pytest.mark.anyio
async def test_liquidar_rechaza_rol_no_permitido(db_session: Session):
    req = create_req_entregada(db_session)
    item = get_item(db_session, req)
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    with pytest.raises(HTTPException) as exc_info:
        await liquidar_guardar(
            req.id,
            DummyRequest(
                {
                    f"qty_returned_{item.id}": "0",
                    f"qty_used_{item.id}": "1",
                    f"qty_left_{item.id}": "1",
                    "prokey_ref": "PK-007",
                }
            ),
            current_user=user,
            db=db_session,
        )
    assert exc_info.value.status_code == 403
