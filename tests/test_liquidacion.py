import json
from datetime import datetime

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.crud import (
    agregar_item_db,
    calcular_alertas_item,
    marcar_liquidada_en_prokey,
    puede_liquidar,
    transicionar_requisicion,
)
from app.main import (
    detalle_requisicion,
    editar_prokey_ref_form,
    editar_prokey_ref_guardar,
    liquidar_en_prokey,
    liquidar_form,
    liquidar_guardar,
)
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
                Usuario(
                    username="jefe.bodega",
                    password=hash_password("pass123"),
                    nombre="Jefe Bodega",
                    rol="jefe_bodega",
                    departamento="Bodega",
                ),
                Usuario(
                    username="user.otro",
                    password=hash_password("pass123"),
                    nombre="Usuario Otro",
                    rol="user",
                    departamento="Operaciones",
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
        self.url = type("URL", (), {"path": "/liquidar/test"})()
        self.query_params: dict[str, str] = {}

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
        delivered_by=bode.id if estado in ("entregada", "liquidada", "liquidada_en_prokey") else None,
        delivered_at=datetime.now() if estado in ("entregada", "liquidada", "liquidada_en_prokey") else None,
        delivered_to="Cliente Test" if estado in ("entregada", "liquidada", "liquidada_en_prokey") else None,
        delivery_result=delivery_result if estado in ("entregada", "liquidada", "liquidada_en_prokey") else None,
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


def test_agregar_item_db_persiste_contexto_operacion(db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = Requisicion(
        folio=f"REQ-CTX-{datetime.now().timestamp()}",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Test contexto",
        created_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    item = agregar_item_db(
        db_session,
        req.id,
        descripcion="MOPA AZUL",
        cantidad=2,
        contexto_operacion="instalacion_inicial",
    )

    assert item.contexto_operacion == "instalacion_inicial"


@pytest.mark.anyio
async def test_liquidar_flujo_feliz_sin_alertas(db_session: Session):
    req = create_req_entregada(db_session, delivery_result="completa", cantidad=10)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "2",
                f"qty_used_{item.id}": "8",
                f"qty_left_{item.id}": "2",
                f"mode_{item.id}": "CONSUMIBLE",
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
    assert json.loads(item.liquidation_alerts) == []


@pytest.mark.anyio
async def test_liquidar_con_faltante(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "1",
                f"qty_used_{item.id}": "3",
                f"qty_left_{item.id}": "2",
                f"mode_{item.id}": "RETORNABLE",
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
    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "5",
                f"qty_used_{item.id}": "0",
                f"qty_left_{item.id}": "3",
                f"mode_{item.id}": "RETORNABLE",
                f"note_{item.id}": "",
                "prokey_ref": "PK-003",
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
    tipos = {a["type"] for a in json.loads(item.liquidation_alerts)}
    assert {"ALERTA_SOBRANTE", "ALERTA_RETORNO_EXTRA"}.issubset(tipos)


@pytest.mark.anyio
async def test_liquidar_salida_sin_soporte(db_session: Session):
    req = create_req_entregada(db_session, cantidad=2)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "3",
                f"qty_left_{item.id}": "0",
                f"mode_{item.id}": "RETORNABLE",
                f"note_{item.id}": "",
                "prokey_ref": "PK-004",
                "liquidation_comment": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    assert response.status_code == 200
    db_session.refresh(req)
    assert req.estado == "entregada"


def test_diferencia_retornable_cuadra(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    item.qty_used = 3
    item.qty_left_at_client = 2
    item.qty_returned_to_warehouse = 5
    item.liquidation_mode = "RETORNABLE"
    alertas = calcular_alertas_item(item)
    tipos = {a["type"] for a in alertas}
    assert "ALERTA_FALTANTE" not in tipos
    assert "ALERTA_SOBRANTE" not in tipos


def test_diferencia_retornable_retorno_extra(db_session: Session):
    req = create_req_entregada(db_session, cantidad=2)
    item = get_item(db_session, req)
    item.qty_used = 1
    item.qty_left_at_client = 1
    item.qty_returned_to_warehouse = 3
    item.liquidation_mode = "RETORNABLE"
    alertas = calcular_alertas_item(item)
    tipos = {a["type"] for a in alertas}
    assert {"ALERTA_SOBRANTE", "ALERTA_RETORNO_EXTRA"}.issubset(tipos)


def test_diferencia_consumible_cuadra(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    item.qty_used = 3
    item.qty_left_at_client = 2
    item.qty_returned_to_warehouse = 2
    item.liquidation_mode = "CONSUMIBLE"
    alertas = calcular_alertas_item(item)
    tipos = {a["type"] for a in alertas}
    assert "ALERTA_FALTANTE" not in tipos
    assert "ALERTA_SOBRANTE" not in tipos


def test_diferencia_consumible_faltante(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    item.qty_used = 3
    item.qty_left_at_client = 2
    item.qty_returned_to_warehouse = 1
    item.liquidation_mode = "CONSUMIBLE"
    alertas = calcular_alertas_item(item)
    assert any(a["type"] == "ALERTA_FALTANTE" and a["severity"] == "warn" for a in alertas)


def test_salida_sin_soporte(db_session: Session):
    req = create_req_entregada(db_session, cantidad=2)
    item = get_item(db_session, req)
    item.qty_used = 2
    item.qty_left_at_client = 1
    item.qty_returned_to_warehouse = 0
    item.liquidation_mode = "CONSUMIBLE"
    alertas = calcular_alertas_item(item)
    assert any(a["type"] == "ALERTA_SALIDA_SIN_SOPORTE" and a["severity"] == "high" for a in alertas)


def test_retornable_alerta_retorno_incompleto(db_session: Session):
    req = create_req_entregada(db_session, cantidad=3)
    item = get_item(db_session, req)
    item.qty_used = 2
    item.qty_left_at_client = 0
    item.qty_returned_to_warehouse = 2
    item.liquidation_mode = "RETORNABLE"
    alertas = calcular_alertas_item(item)
    assert any(a["type"] == "ALERTA_RETORNO_INCOMPLETO" and a["severity"] == "warn" for a in alertas)


def test_retorno_incompleto_no_aplica_en_instalacion_inicial(db_session: Session):
    req = create_req_entregada(db_session, cantidad=3)
    item = get_item(db_session, req)
    item.qty_used = 3
    item.qty_left_at_client = 0
    item.qty_returned_to_warehouse = 0
    item.liquidation_mode = "RETORNABLE"
    item.contexto_operacion = "instalacion_inicial"
    alertas = calcular_alertas_item(item)
    assert not any(a["type"] == "ALERTA_RETORNO_INCOMPLETO" for a in alertas)
    assert not any(a["type"] == "ALERTA_FALTANTE" for a in alertas)


@pytest.mark.anyio
async def test_detalle_liquidada_instalacion_inicial_retornable_no_marca_diferencia(db_session: Session):
    req = create_req_entregada(db_session, cantidad=2)
    item = get_item(db_session, req)
    item.contexto_operacion = "instalacion_inicial"
    db_session.commit()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "2",
                f"qty_not_used_{item.id}": "0",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )

    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    liq_item = payload["items"][0]
    assert liq_item["contexto_operacion"] == "instalacion_inicial"
    assert liq_item["expected_return"] == 0
    assert liq_item["difference"] == 0
    assert not any(alert["type"] == "ALERTA_FALTANTE" for alert in liq_item["liquidation_alerts"])


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
                f"qty_used_{item.id}": "5",
                f"qty_left_{item.id}": "0",
                f"mode_{item.id}": "RETORNABLE",
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
async def test_liquidar_permite_prokey_ref_vacio(db_session: Session):
    req = create_req_entregada(db_session)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "1",
                f"qty_used_{item.id}": "1",
                f"qty_left_{item.id}": "9",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada"
    assert req.prokey_ref is None


@pytest.mark.anyio
async def test_no_permite_liquidar_item_incompleto_entregado_gt_0(db_session: Session):
    req = create_req_entregada(db_session, cantidad=4)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "0",
                f"qty_not_used_{item.id}": "0",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )

    assert response.status_code == 200
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.liquidated_at is None


@pytest.mark.anyio
async def test_si_permite_cuando_delivered_es_0(db_session: Session):
    req = create_req_entregada(db_session, delivery_result="parcial", cantidad=3, cantidad_entregada=0)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "0",
                f"qty_not_used_{item.id}": "0",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada"


@pytest.mark.anyio
async def test_bloquea_si_no_cubre_entregado_retornable(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "3",
                f"qty_used_{item.id}": "3",
                f"qty_not_used_{item.id}": "0",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )

    assert response.status_code == 200
    db_session.refresh(req)
    assert req.estado == "entregada"


@pytest.mark.anyio
async def test_bloquea_si_no_cubre_entregado_consumible(db_session: Session):
    req = create_req_entregada(db_session, cantidad=10)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "8",
                f"qty_not_used_{item.id}": "0",
                f"mode_{item.id}": "CONSUMIBLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )

    assert response.status_code == 200
    db_session.refresh(req)
    assert req.estado == "entregada"


@pytest.mark.anyio
async def test_bloquea_consumible_si_regresa_distinto_de_no_usado(db_session: Session):
    req = create_req_entregada(db_session, cantidad=10)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "2",
                f"qty_used_{item.id}": "7",
                f"qty_not_used_{item.id}": "3",
                f"mode_{item.id}": "CONSUMIBLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )

    assert response.status_code == 200
    db_session.refresh(req)
    assert req.estado == "entregada"


@pytest.mark.anyio
async def test_permite_retornable_con_retorno_incompleto_pero_cobertura_ok(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "3",
                f"qty_used_{item.id}": "3",
                f"qty_not_used_{item.id}": "2",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    db_session.refresh(item)
    assert req.estado == "liquidada"
    assert any(a["type"] == "ALERTA_RETORNO_INCOMPLETO" for a in json.loads(item.liquidation_alerts))


@pytest.mark.anyio
async def test_permite_retornable_con_retorno_extra_no_bloquea_y_alerta(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "6",
                f"qty_used_{item.id}": "5",
                f"qty_not_used_{item.id}": "0",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    db_session.refresh(item)
    assert req.estado == "liquidada"
    tipos = {a["type"] for a in json.loads(item.liquidation_alerts)}
    assert "ALERTA_RETORNO_EXTRA" in tipos


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
                f"qty_left_{item.id}": "9",
                f"mode_{item.id}": "RETORNABLE",
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


@pytest.mark.anyio
async def test_detalle_liquidada_incluye_campos(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    item.contexto_operacion = "instalacion_inicial"
    db_session.commit()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "4",
                f"qty_used_{item.id}": "2",
                f"qty_left_{item.id}": "3",
                f"mode_{item.id}": "RETORNABLE",
                f"note_{item.id}": "Retiro de equipo",
                "prokey_ref": "PK-DET-01",
                "liquidation_comment": "Cierre liquidacion",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    db_session.refresh(req)
    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)

    assert payload["prokey_ref"] == "PK-DET-01"
    assert payload["liquidated_by_name"] == bodega.nombre
    assert payload["liquidated_at"] is not None
    assert any(t["evento"] == "Requisicion liquidada" for t in payload["timeline"])
    liq_item = payload["items"][0]
    assert "qty_returned_to_warehouse" in liq_item
    assert "qty_used" in liq_item
    assert "qty_left_at_client" in liq_item
    assert "item_liquidation_note" in liq_item
    assert "liquidation_alerts" in liq_item
    assert liq_item["contexto_operacion"] == "instalacion_inicial"


@pytest.mark.anyio
async def test_api_detalle_alertas_null_se_convierte_a_lista_vacia(db_session: Session):
    req = create_req_entregada(db_session, cantidad=10)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "2",
                f"qty_used_{item.id}": "8",
                f"qty_not_used_{item.id}": "2",
                f"mode_{item.id}": "CONSUMIBLE",
                "prokey_ref": "PK-DET-NULL-01",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    db_session.refresh(item)
    assert json.loads(item.liquidation_alerts) == []

    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    liq_item = payload["items"][0]
    assert isinstance(liq_item["liquidation_alerts"], list)
    assert liq_item["liquidation_alerts"] == []


@pytest.mark.anyio
async def test_api_detalle_incluye_retorno_incompleto(db_session: Session):
    req = create_req_entregada(db_session, cantidad=3)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "2",
                f"qty_used_{item.id}": "2",
                f"qty_not_used_{item.id}": "1",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "PK-DET-INC-01",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    db_session.refresh(item)
    db_alertas = json.loads(item.liquidation_alerts)
    assert any(a["type"] == "ALERTA_RETORNO_INCOMPLETO" for a in db_alertas)

    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    liq_item = payload["items"][0]
    assert any(a.get("type") == "ALERTA_RETORNO_INCOMPLETO" for a in liq_item["liquidation_alerts"])


@pytest.mark.anyio
async def test_detalle_liquidada_campos_derivados(db_session: Session):
    req = create_req_entregada(db_session, cantidad=10)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "3",
                f"qty_used_{item.id}": "4",
                f"qty_left_{item.id}": "6",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "PK-DET-02",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    payload = detalle_requisicion(req.id, current_user=bodega, db=db_session)
    liq_item = payload["items"][0]
    assert liq_item["qty_ocupo"] == 10
    assert liq_item["pk_ingreso_qty"] == 3
    assert liq_item["delta"] == 7


@pytest.mark.anyio
async def test_liquidada_es_solo_lectura(db_session: Session):
    req = create_req_entregada(db_session, cantidad=8)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "2",
                f"qty_used_{item.id}": "3",
                f"qty_left_{item.id}": "5",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "PK-DET-03",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    db_session.refresh(req)
    prev_ref = req.prokey_ref

    response = await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "0",
                f"qty_used_{item.id}": "8",
                f"qty_left_{item.id}": "0",
                "prokey_ref": "PK-NEW",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    assert response.status_code == 303
    assert "Ya+fue+liquidada" in response.headers["location"]
    db_session.refresh(req)
    assert req.prokey_ref == prev_ref


def test_liquidar_get_redirige_si_ya_liquidada(db_session: Session):
    req = create_req_entregada(db_session, estado="liquidada")
    req.prokey_ref = "PK-LIQ"
    db_session.commit()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    class ReqStub:
        session = {}

    response = liquidar_form(req.id, request=ReqStub(), current_user=bodega, db=db_session)
    assert response.status_code == 303
    assert "ya+fue+liquidada" in response.headers["location"].lower()


@pytest.mark.anyio
async def test_update_prokey_ref_permite_admin(db_session: Session):
    req = create_req_entregada(db_session, cantidad=5)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "2",
                f"qty_used_{item.id}": "2",
                f"qty_left_{item.id}": "3",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    db_session.refresh(item)
    original_qty_used = item.qty_used
    original_alerts = item.liquidation_alerts

    admin = db_session.query(Usuario).filter(Usuario.username == "admin.1").first()
    response = await editar_prokey_ref_guardar(
        req.id,
        DummyRequest({"prokey_ref": "PK-POST-001"}),
        current_user=admin,
        db=db_session,
    )
    assert response.status_code == 303
    db_session.refresh(req)
    db_session.refresh(item)
    assert req.estado == "liquidada"
    assert req.prokey_ref == "PK-POST-001"
    assert item.qty_used == original_qty_used
    assert item.liquidation_alerts == original_alerts


@pytest.mark.anyio
async def test_update_prokey_ref_permite_propietario(db_session: Session):
    req = create_req_entregada(db_session, cantidad=4)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    owner = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "1",
                f"qty_used_{item.id}": "2",
                f"qty_left_{item.id}": "2",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    response = await editar_prokey_ref_guardar(
        req.id,
        DummyRequest({"prokey_ref": "PK-OWNER-001"}),
        current_user=owner,
        db=db_session,
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.prokey_ref == "PK-OWNER-001"


@pytest.mark.anyio
async def test_update_prokey_ref_bloquea_no_propietario(db_session: Session):
    req = create_req_entregada(db_session, cantidad=3)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    otro = db_session.query(Usuario).filter(Usuario.username == "user.otro").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "1",
                f"qty_used_{item.id}": "1",
                f"qty_left_{item.id}": "2",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    with pytest.raises(HTTPException) as exc_info:
        await editar_prokey_ref_guardar(
            req.id,
            DummyRequest({"prokey_ref": "PK-NOPE-001"}),
            current_user=otro,
            db=db_session,
        )
    assert exc_info.value.status_code == 403


@pytest.mark.anyio
async def test_update_prokey_ref_requiere_estado_liquidada(db_session: Session):
    req = create_req_entregada(db_session, estado="entregada", cantidad=3)
    admin = db_session.query(Usuario).filter(Usuario.username == "admin.1").first()
    response = await editar_prokey_ref_guardar(
        req.id,
        DummyRequest({"prokey_ref": "PK-SHOULD-NOT-SAVE"}),
        current_user=admin,
        db=db_session,
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.prokey_ref is None


@pytest.mark.anyio
async def test_update_prokey_ref_no_permite_vacio(db_session: Session):
    req = create_req_entregada(db_session, cantidad=3)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    owner = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "1",
                f"qty_used_{item.id}": "1",
                f"qty_left_{item.id}": "2",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    response = await editar_prokey_ref_guardar(
        req.id,
        DummyRequest({"prokey_ref": "  "}),
        current_user=owner,
        db=db_session,
    )
    assert response.status_code == 303
    assert f"/requisiciones/{req.id}/prokey-ref" in response.headers["location"]
    db_session.refresh(req)
    assert req.prokey_ref is None


@pytest.mark.anyio
async def test_api_detalle_refleja_prokey_ref_actualizado(db_session: Session):
    req = create_req_entregada(db_session, cantidad=3)
    item = get_item(db_session, req)
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    admin = db_session.query(Usuario).filter(Usuario.username == "admin.1").first()
    await liquidar_guardar(
        req.id,
        DummyRequest(
            {
                f"qty_returned_{item.id}": "1",
                f"qty_used_{item.id}": "1",
                f"qty_left_{item.id}": "2",
                f"mode_{item.id}": "RETORNABLE",
                "prokey_ref": "",
            }
        ),
        current_user=bodega,
        db=db_session,
    )
    await editar_prokey_ref_guardar(
        req.id,
        DummyRequest({"prokey_ref": "PK-API-001"}),
        current_user=admin,
        db=db_session,
    )
    payload = detalle_requisicion(req.id, current_user=admin, db=db_session)
    assert payload["prokey_ref"] == "PK-API-001"


def test_update_prokey_ref_get_form_permitido(db_session: Session):
    req = create_req_entregada(db_session, estado="liquidada")
    owner = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()

    class ReqStub:
        session = {}
        url = type("URL", (), {"path": "/requisiciones/1/prokey-ref"})()
        query_params: dict[str, str] = {}

    response = editar_prokey_ref_form(req.id, request=ReqStub(), current_user=owner, db=db_session)
    assert response.status_code == 200


def test_marcar_liquidada_en_prokey_ok(db_session: Session):
    req = create_req_entregada(db_session, estado="liquidada")
    jefe = db_session.query(Usuario).filter(Usuario.username == "jefe.bodega").first()

    updated = marcar_liquidada_en_prokey(db_session, req.id, jefe.id)

    assert updated.estado == "liquidada_en_prokey"
    assert updated.prokey_liquidada_por == jefe.id
    assert updated.prokey_liquidada_at is not None


def test_marcar_liquidada_en_prokey_requiere_estado_liquidada(db_session: Session):
    req = create_req_entregada(db_session, estado="entregada")
    jefe = db_session.query(Usuario).filter(Usuario.username == "jefe.bodega").first()

    with pytest.raises(ValueError) as exc_info:
        marcar_liquidada_en_prokey(db_session, req.id, jefe.id)
    assert "estado liquidada" in str(exc_info.value).lower()


def test_marcar_liquidada_en_prokey_es_inmutable(db_session: Session):
    req = create_req_entregada(db_session, estado="liquidada")
    jefe = db_session.query(Usuario).filter(Usuario.username == "jefe.bodega").first()
    bode = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    marcar_liquidada_en_prokey(db_session, req.id, jefe.id)
    db_session.refresh(req)
    assert req.estado == "liquidada_en_prokey"

    with pytest.raises(ValueError):
        transicionar_requisicion(db_session, req, nuevo_estado="entregada", actor_id=bode.id)


def test_marcar_liquidada_en_prokey_permite_admin_y_jefe_bodega(db_session: Session):
    req = create_req_entregada(db_session, estado="liquidada")
    admin = db_session.query(Usuario).filter(Usuario.username == "admin.1").first()
    bode = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    aprob = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    response = liquidar_en_prokey(req.id, current_user=admin, db=db_session)
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "liquidada_en_prokey"

    req2 = create_req_entregada(db_session, estado="liquidada")

    with pytest.raises(HTTPException) as exc_bode:
        liquidar_en_prokey(req2.id, current_user=bode, db=db_session)
    assert exc_bode.value.status_code == 403

    with pytest.raises(HTTPException) as exc_aprob:
        liquidar_en_prokey(req2.id, current_user=aprob, db=db_session)
    assert exc_aprob.value.status_code == 403


def test_detalle_liquidada_en_prokey_incluye_campos(db_session: Session):
    req = create_req_entregada(db_session, estado="liquidada")
    jefe = db_session.query(Usuario).filter(Usuario.username == "jefe.bodega").first()
    owner = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()

    marcar_liquidada_en_prokey(db_session, req.id, jefe.id)
    payload = detalle_requisicion(req.id, current_user=owner, db=db_session)

    assert payload["estado"] == "liquidada_en_prokey"
    assert payload["prokey_liquidada_at"] is not None
    assert payload["prokey_liquidado_por_nombre"] == jefe.nombre
    assert any((e.get("evento") or "") == "Liquidada en Prokey" for e in payload.get("timeline", []))
