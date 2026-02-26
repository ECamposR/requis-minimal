from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.crud import agregar_item_db, crear_requisicion_db, transicionar_requisicion
from app.main import detalle_requisicion, liquidar_form, liquidar_guardar
from app.models import Base, Requisicion, Usuario


class DummyRequest:
    def __init__(self, data: dict[str, str] | None = None):
        self._data = data or {}
        self.session: dict[str, str] = {}

    async def form(self):
        return self._data


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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

    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def alert_types(item_payload: dict) -> set[str]:
    return {a.get("type") for a in item_payload.get("liquidation_alerts", [])}


def build_req(db: Session, items: list[tuple[str, int]]) -> Requisicion:
    user = db.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = crear_requisicion_db(
        db=db,
        solicitante_id=user.id,
        departamento=user.departamento,
        cliente_codigo="C123",
        cliente_nombre="Cliente Test",
        cliente_ruta_principal="RA01",
        justificacion="Flujo integracion liquidacion",
    )
    for desc, qty in items:
        agregar_item_db(db, req.id, desc, qty)
    db.refresh(req)
    return req


def aprobar_req(db: Session, req: Requisicion) -> None:
    aprob = db.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    transicionar_requisicion(
        db,
        req,
        nuevo_estado="aprobada",
        actor_id=aprob.id,
        approval_comment="Aprobado integracion",
    )


def entregar_completa_req(db: Session, req: Requisicion) -> None:
    bode = db.query(Usuario).filter(Usuario.username == "bodega.1").first()
    for item in req.items:
        item.cantidad_entregada = item.cantidad
    transicionar_requisicion(
        db,
        req,
        nuevo_estado="entregada",
        actor_id=bode.id,
        delivered_to="Recibe Cliente",
        delivery_result="completa",
        delivery_comment="Entrega completa integracion",
    )


async def liquidar(
    db: Session,
    req: Requisicion,
    payload_by_item_id: dict[int, dict[str, str]],
    prokey_ref: str,
):
    bode = db.query(Usuario).filter(Usuario.username == "bodega.1").first()
    form_data: dict[str, str] = {"prokey_ref": prokey_ref, "liquidation_comment": "Liquidacion integracion"}
    for item_id, values in payload_by_item_id.items():
        form_data[f"qty_returned_{item_id}"] = values.get("returned", "0")
        form_data[f"qty_used_{item_id}"] = values.get("used", "0")
        form_data[f"qty_left_{item_id}"] = values.get("left", "0")
        form_data[f"mode_{item_id}"] = values.get("mode", "RETORNABLE")
        form_data[f"note_{item_id}"] = values.get("note", "")
    return await liquidar_guardar(req.id, DummyRequest(form_data), current_user=bode, db=db)


@pytest.mark.anyio
async def test_flujo_completo_liquidacion_sin_alertas(db_session: Session):
    req = build_req(db_session, [("Item A", 10), ("Item B", 5)])
    aprobar_req(db_session, req)
    entregar_completa_req(db_session, req)
    items = list(req.items)
    response = await liquidar(
        db_session,
        req,
        {
            items[0].id: {"returned": "2", "used": "5", "left": "2", "mode": "CONSUMIBLE"},
            items[1].id: {"returned": "2", "used": "2", "left": "2", "mode": "CONSUMIBLE"},
        },
        "PK-INT-001",
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada"
    assert req.prokey_ref == "PK-INT-001"

    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    assert payload["estado"] == "liquidada"
    assert payload["prokey_ref"] == "PK-INT-001"
    total_alerts = sum(len(item.get("liquidation_alerts", [])) for item in payload["items"])
    assert total_alerts == 0


@pytest.mark.anyio
async def test_flujo_completo_con_faltante(db_session: Session):
    req = build_req(db_session, [("Item A", 5)])
    aprobar_req(db_session, req)
    entregar_completa_req(db_session, req)
    item = req.items[0]

    response = await liquidar(
        db_session,
        req,
        {item.id: {"returned": "0", "used": "3", "left": "0"}},
        "PK-INT-002",
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada"

    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    liq_item = payload["items"][0]
    assert liq_item["delta"] == 2
    assert "ALERTA_FALTANTE" in alert_types(liq_item)
    assert any(a.get("severity") == "warn" for a in liq_item["liquidation_alerts"])


@pytest.mark.anyio
async def test_flujo_completo_con_retorno_extra(db_session: Session):
    req = build_req(db_session, [("Item A", 3)])
    aprobar_req(db_session, req)
    entregar_completa_req(db_session, req)
    item = req.items[0]
    response = await liquidar(
        db_session,
        req,
        {item.id: {"returned": "5", "used": "0", "left": "0"}},
        "PK-INT-003",
    )
    assert response.status_code == 303

    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    liq_item = payload["items"][0]
    assert liq_item["delta"] == -2
    assert {"ALERTA_SOBRANTE", "ALERTA_RETORNO_EXTRA"}.issubset(alert_types(liq_item))


@pytest.mark.anyio
async def test_flujo_completo_salida_sin_soporte(db_session: Session):
    req = build_req(db_session, [("Item A", 2)])
    aprobar_req(db_session, req)
    entregar_completa_req(db_session, req)
    item = req.items[0]
    response = await liquidar(
        db_session,
        req,
        {item.id: {"returned": "0", "used": "3", "left": "0"}},
        "PK-INT-004",
    )
    assert response.status_code == 303

    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    liq_item = payload["items"][0]
    assert liq_item["delta"] == -1
    assert {"ALERTA_FALTANTE", "ALERTA_SALIDA_SIN_SOPORTE"}.issubset(alert_types(liq_item))


@pytest.mark.anyio
async def test_liquidar_sin_prokey_ref_guarda_null(db_session: Session):
    req = build_req(db_session, [("Item A", 4)])
    aprobar_req(db_session, req)
    entregar_completa_req(db_session, req)
    item = req.items[0]
    response = await liquidar(
        db_session,
        req,
        {item.id: {"returned": "1", "used": "2", "left": "1"}},
        "",
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada"
    assert req.prokey_ref is None
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    assert payload["prokey_ref"] is None


@pytest.mark.anyio
async def test_no_liquidar_no_entregada(db_session: Session):
    req = build_req(db_session, [("Item A", 4)])
    aprobar_req(db_session, req)
    item = req.items[0]
    response = await liquidar(
        db_session,
        req,
        {item.id: {"returned": "1", "used": "2", "left": "1"}},
        "PK-INT-005",
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "aprobada"


@pytest.mark.anyio
async def test_no_liquidar_delivery_no_entregada(db_session: Session):
    req = build_req(db_session, [("Item A", 4)])
    aprobar_req(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    transicionar_requisicion(
        db_session,
        req,
        nuevo_estado="entregada",
        actor_id=bodega.id,
        delivered_to=None,
        delivery_result="no_entregada",
        delivery_comment="Sin inventario",
    )
    item = req.items[0]
    response = await liquidar(
        db_session,
        req,
        {item.id: {"returned": "0", "used": "0", "left": "0"}},
        "PK-INT-006",
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.delivery_result == "no_entregada"


@pytest.mark.anyio
async def test_liquidada_inmutable(db_session: Session):
    req = build_req(db_session, [("Item A", 6)])
    aprobar_req(db_session, req)
    entregar_completa_req(db_session, req)
    item = req.items[0]

    first = await liquidar(
        db_session,
        req,
        {item.id: {"returned": "2", "used": "2", "left": "2"}},
        "PK-INT-007",
    )
    assert first.status_code == 303
    db_session.refresh(req)
    original_ref = req.prokey_ref

    second = await liquidar(
        db_session,
        req,
        {item.id: {"returned": "0", "used": "6", "left": "0"}},
        "PK-CHANGED",
    )
    assert second.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada"
    assert req.prokey_ref == original_ref


@pytest.mark.anyio
async def test_timeline_incluye_liquidacion(db_session: Session):
    req = build_req(db_session, [("Item A", 4)])
    aprobar_req(db_session, req)
    entregar_completa_req(db_session, req)
    item = req.items[0]
    await liquidar(
        db_session,
        req,
        {item.id: {"returned": "1", "used": "2", "left": "1"}},
        "PK-INT-008",
    )

    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    eventos = payload.get("timeline", [])
    evento_liq = [e for e in eventos if "liquidada" in (e.get("evento") or "").lower()]
    assert evento_liq
    assert any((e.get("actor") or "") == "Bodega Uno" for e in evento_liq)


def test_get_liquidar_redirige_si_ya_liquidada(db_session: Session):
    req = build_req(db_session, [("Item A", 1)])
    req.estado = "liquidada"
    req.prokey_ref = "PK-INT-009"
    req.liquidated_at = datetime.now()
    db_session.commit()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    response = liquidar_form(req.id, request=DummyRequest(), current_user=bodega, db=db_session)
    assert response.status_code == 303
    assert "liquidada" in response.headers["location"].lower()
