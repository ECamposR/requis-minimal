from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.database import get_db
from app.main import app
from app.models import Base, CatalogoItem, Item, Requisicion, Usuario

TEST_DB_URL = "sqlite:///./test_requisiciones.db"


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
        seed_db.add_all(
            [
                CatalogoItem(nombre="Cable UTP Cat6", activo=True),
                CatalogoItem(nombre="Conector RJ45", activo=True),
            ]
        )
        seed_db.commit()

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def login(client: TestClient, username: str, password: str) -> None:
    response = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert response.status_code == 303


def test_home_muestra_metricas_por_estado_para_usuario(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-2001",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Pendiente usuario",
            ),
            Requisicion(
                folio="REQ-2002",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Aprobada usuario",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-2003",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="rechazada",
                justificacion="Rechazada usuario",
                rejected_by=aprobador.id,
                rejected_at=datetime.now(),
                rejection_reason="No procede",
            ),
            Requisicion(
                folio="REQ-2004",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Entregada usuario",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
                delivered_to="Usuario Ops",
            ),
        ]
    )
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.get("/")
    assert response.status_code == 200

    html = response.text
    assert "Mis requisiciones" in html
    assert "Mis pendientes" in html
    assert "Aprobadas historicas" in html
    assert "Rechazadas" in html
    assert "Mis entregadas" in html
    assert "Creadas este mes" in html
    assert "Pendientes de aprobar" in html
    assert "Pendientes de entregar" in html
    assert "Rechazadas" in html
    assert "Entregadas (30 dias)" in html
    assert "Pendientes por aprobar" not in html
    assert "Pendientes por entregar" not in html


def test_crear_requisicion(client: TestClient, db_session: Session):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-1001",
            "cliente_nombre": "Cliente Uno",
            "cliente_ruta_principal": "RA02",
            "justificacion": "Material para mantenimiento correctivo",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "25",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    req = db_session.query(Requisicion).filter(Requisicion.folio == "REQ-0001").first()
    assert req is not None
    assert req.estado == "pendiente"
    assert req.departamento == "Operaciones"
    assert req.cliente_codigo == "C-1001"
    assert req.cliente_nombre == "Cliente Uno"
    assert req.cliente_ruta_principal == "RA02"
    assert len(req.items) == 1
    assert req.items[0].descripcion == "Cable UTP Cat6"


def test_crear_requisicion_ignora_departamento_enviado(client: TestClient, db_session: Session):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "departamento": "Ventas",
            "cliente_codigo": "C-2001",
            "cliente_nombre": "Cliente Dos",
            "cliente_ruta_principal": "rb03",
            "justificacion": "Prueba de spoof de departamento",
            "items[0][descripcion]": "Conector RJ45",
            "items[0][cantidad]": "2",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    req = db_session.query(Requisicion).order_by(Requisicion.id.desc()).first()
    assert req is not None
    assert req.departamento == "Operaciones"
    assert req.cliente_ruta_principal == "RB03"


def test_aprobar_requisicion(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req = Requisicion(
        folio="REQ-0001",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Requisicion para prueba de aprobacion",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "aprob.ops", "pass123")
    response = client.post(
        f"/aprobar/{req.id}",
        data={"comentario": "Aprobado para continuidad operativa"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "aprobada"
    assert req.approved_by == aprobador.id
    assert req.approved_at is not None
    assert req.approval_comment == "Aprobado para continuidad operativa"


def test_aprobador_puede_aprobar_otra_area(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req = Requisicion(
        folio="REQ-0098",
        solicitante_id=user.id,
        departamento="Ventas",
        estado="pendiente",
        justificacion="Requisicion de otra area para validar alcance aprobador",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "aprob.ops", "pass123")
    response = client.post(
        f"/aprobar/{req.id}",
        data={"comentario": "Aprobada sin restriccion por area"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "aprobada"
    assert req.approved_by == aprobador.id


def test_aprobador_puede_abrir_vista_gestion_aprobacion(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = Requisicion(
        folio="REQ-0201",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Vista dedicada de aprobacion",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "aprob.ops", "pass123")
    response = client.get(f"/aprobar/{req.id}/gestionar")
    assert response.status_code == 200
    assert "Gestionar Aprobacion" in response.text
    assert req.folio in response.text


def test_rechazar_requisicion_guarda_actor(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req = Requisicion(
        folio="REQ-0009",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Requisicion para prueba de rechazo",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "aprob.ops", "pass123")
    response = client.post(
        f"/rechazar/{req.id}",
        data={"razon": "Sin presupuesto", "comentario": "Revisar en proximo ciclo"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "rechazada"
    assert req.rejected_by == aprobador.id
    assert req.rejected_at is not None
    assert req.rejection_reason == "Sin presupuesto"
    assert req.rejection_comment == "Revisar en proximo ciclo"


def test_crear_requisicion_rechaza_item_fuera_catalogo(client: TestClient):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-3001",
            "cliente_nombre": "Cliente Tres",
            "cliente_ruta_principal": "RA02",
            "justificacion": "Intento con item invalido",
            "items[0][descripcion]": "ITEM NO VALIDO",
            "items[0][cantidad]": "1",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Item no permitido en catalogo"


def test_crear_requisicion_rechaza_items_duplicados(client: TestClient):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-4001",
            "cliente_nombre": "Cliente Cuatro",
            "cliente_ruta_principal": "RA02",
            "justificacion": "Intento con item duplicado",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1",
            "items[1][descripcion]": "Cable UTP Cat6",
            "items[1][cantidad]": "2",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No se permiten items duplicados en una misma requisicion"


def test_crear_requisicion_normaliza_item_con_espacios_y_mayusculas(client: TestClient, db_session: Session):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-4002",
            "cliente_nombre": "Cliente Cinco",
            "cliente_ruta_principal": "RA02",
            "justificacion": "Normalizacion de item",
            "items[0][descripcion]": "  cable   utp   CAT6  ",
            "items[0][cantidad]": "1",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    req = db_session.query(Requisicion).filter(Requisicion.cliente_codigo == "C-4002").first()
    assert req is not None
    assert req.items[0].descripcion == "Cable UTP Cat6"


def test_crear_requisicion_requiere_datos_cliente(client: TestClient):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "",
            "cliente_nombre": "",
            "cliente_ruta_principal": "",
            "justificacion": "Sin datos cliente",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Codigo de cliente invalido"


def test_crear_requisicion_requiere_formato_ruta_principal(client: TestClient):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-5001",
            "cliente_nombre": "Cliente Ruta Invalida",
            "cliente_ruta_principal": "RUTA1",
            "justificacion": "Prueba de validacion de ruta principal",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Ruta principal invalida (formato: AA00)"


def test_usuario_puede_eliminar_su_requisicion_pendiente(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = Requisicion(
        folio="REQ-0501",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Eliminar pendiente propia",
    )
    db_session.add(req)
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.post(f"/mis-requisiciones/{req.id}/eliminar", follow_redirects=False)
    assert response.status_code == 303
    assert db_session.query(Requisicion).filter(Requisicion.id == req.id).first() is None


def test_usuario_no_puede_eliminar_su_requisicion_no_pendiente(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    req = Requisicion(
        folio="REQ-0502",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="No debe eliminarse si ya aprobada",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.post(f"/mis-requisiciones/{req.id}/eliminar", follow_redirects=False)
    assert response.status_code == 303
    assert db_session.query(Requisicion).filter(Requisicion.id == req.id).first() is not None


def test_usuario_no_puede_eliminar_requisicion_ajena(client: TestClient, db_session: Session):
    otro = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    req = Requisicion(
        folio="REQ-0503",
        solicitante_id=otro.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="No debe eliminarse por otro usuario",
    )
    db_session.add(req)
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.post(f"/mis-requisiciones/{req.id}/eliminar", follow_redirects=False)
    assert response.status_code == 303
    assert db_session.query(Requisicion).filter(Requisicion.id == req.id).first() is not None


def test_entregar_requisicion(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0001",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Requisicion para prueba de entrega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={
            "resultado": "completa",
            "delivered_to": "Juan Perez",
            "comentario": "Entregado completo y verificado",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.delivered_by == bodega.id
    assert req.delivery_result == "completa"
    assert req.delivered_to == "Juan Perez"
    assert req.delivered_at is not None
    assert req.delivery_comment == "Entregado completo y verificado"

    vista_bodega = client.get("/bodega")
    assert vista_bodega.status_code == 200
    html = vista_bodega.text
    assert "Historial de bodega" in html
    assert "REQ-0001" in html
    assert "Bodega Uno" in html
    assert "modal-detalle" in html
    assert "Ver" in html


def test_bodega_puede_marcar_entrega_parcial(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0011",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Entrega parcial por faltante",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)
    db_session.add(
        Item(
            requisicion_id=req.id,
            descripcion="Cable UTP Cat6",
            cantidad=1.0,
            unidad="unidad",
        )
    )
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response_inicio = client.post(
        f"/entregar/{req.id}",
        data={"resultado": "parcial"},
        follow_redirects=False,
    )
    assert response_inicio.status_code == 303
    assert response_inicio.headers["location"] == f"/entregar/{req.id}/parcial"

    form_parcial = client.get(f"/entregar/{req.id}/parcial")
    assert form_parcial.status_code == 200
    assert "Entrega Parcial" in form_parcial.text

    item = req.items[0]
    response = client.post(
        f"/entregar/{req.id}/parcial",
        data={
            f"entregado_{item.id}": "0.5",
            "delivered_to": "Juan Perez",
            "comentario": "Falto 1 item por quiebre de stock",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.delivered_by == bodega.id
    assert req.delivery_result == "parcial"
    assert req.delivery_comment == "Falto 1 item por quiebre de stock"
    assert req.items[0].cantidad_entregada == 0.5


def test_bodega_puede_abrir_vista_gestion_entrega(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req = Requisicion(
        folio="REQ-0202",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Vista dedicada de bodega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.get(f"/bodega/{req.id}/gestionar")
    assert response.status_code == 200
    assert "Gestionar Entrega" in response.text
    assert req.folio in response.text


def test_bodega_puede_marcar_no_entregada(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0012",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Sin inventario",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={
            "resultado": "no_entregada",
            "delivered_to": "",
            "comentario": "No hay stock ni sustituto",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.delivered_by == bodega.id
    assert req.delivery_result == "no_entregada"
    assert req.delivered_to is None
    assert req.delivery_comment == "No hay stock ni sustituto"


def test_bodega_entrega_completa_requiere_recibe(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req = Requisicion(
        folio="REQ-0013",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Validacion de quien recibe",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={"resultado": "completa", "delivered_to": "", "comentario": ""},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert "/bodega?msg=Debes+indicar+quien+recibe+%28minimo+3+caracteres%29&type=error" in response.headers[
        "location"
    ]
    db_session.refresh(req)
    assert req.estado == "aprobada"


def test_aprobador_ve_historial_completo_en_aprobar(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req_pendiente = Requisicion(
        folio="REQ-0101",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Pendiente ops",
    )
    req_aprobada = Requisicion(
        folio="REQ-0102",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Aprobada ops",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    req_rechazada = Requisicion(
        folio="REQ-0103",
        solicitante_id=user.id,
        departamento="Ventas",
        estado="rechazada",
        justificacion="Rechazada ventas",
        rejected_by=aprobador.id,
        rejected_at=datetime.now(),
        rejection_reason="No procede",
    )
    req_entregada = Requisicion(
        folio="REQ-0104",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="entregada",
        justificacion="Entregada ops",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        delivered_to="Usuario Ops",
    )
    db_session.add_all([req_pendiente, req_aprobada, req_rechazada, req_entregada])
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/aprobar")

    assert response.status_code == 200
    html = response.text
    assert "REQ-0101" in html
    assert "REQ-0102" in html
    assert "REQ-0103" in html
    assert "REQ-0104" in html
    assert "pendiente de aprobar" in html
    assert "pendiente de entregar" in html
    assert "rechazada" in html
    assert "entregada" in html
    assert "Usuario Ops" in html
    assert "Aprobador Ops" in html
    assert "Bodega Uno" in html
    assert "modal-detalle" in html
    assert "Ver" in html


def test_aprobar_permita_filtrar_por_estado(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req_pendiente = Requisicion(
        folio="REQ-0201",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Filtro estado pendiente",
    )
    req_rechazada = Requisicion(
        folio="REQ-0202",
        solicitante_id=user.id,
        departamento="Ventas",
        estado="rechazada",
        justificacion="Filtro estado rechazada",
        rejected_by=aprobador.id,
        rejected_at=datetime.now(),
        rejection_reason="No aplica",
    )
    db_session.add_all([req_pendiente, req_rechazada])
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/aprobar?estado=rechazada")
    assert response.status_code == 200
    assert "REQ-0202" in response.text
    assert "REQ-0201" not in response.text


def test_bodega_permita_filtrar_historial_por_resultado(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req_completa = Requisicion(
        folio="REQ-0301",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="entregada",
        justificacion="Historial completa",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        delivery_result="completa",
        delivered_to="Juan Perez",
    )
    req_no_entregada = Requisicion(
        folio="REQ-0302",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="entregada",
        justificacion="Historial no entregada",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        delivery_result="no_entregada",
        delivery_comment="Sin stock",
    )
    db_session.add_all([req_completa, req_no_entregada])
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/bodega?vista=historial&resultado=no_entregada")
    assert response.status_code == 200
    assert "REQ-0302" in response.text
    assert "REQ-0301" not in response.text
