import re
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.database import get_db
from app.main import app
from app.models import Base, CatalogoItem, Item, Requisicion, Usuario
from app.pdf_generator import generate_requisicion_pdf

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
                    pin_hash=hash_password("1234"),
                    nombre="Usuario Ops",
                    rol="user",
                    departamento="Operaciones",
                ),
                Usuario(
                    username="aprob.ops",
                    password=hash_password("pass123"),
                    pin_hash=hash_password("1234"),
                    nombre="Aprobador Ops",
                    rol="aprobador",
                    departamento="Operaciones",
                ),
                Usuario(
                    username="logistica.1",
                    password=hash_password("pass123"),
                    pin_hash=hash_password("1234"),
                    nombre="Logistica Uno",
                    rol="logistica",
                    departamento="Admon",
                ),
                Usuario(
                    username="bodega.1",
                    password=hash_password("pass123"),
                    pin_hash=hash_password("1234"),
                    nombre="Bodega Uno",
                    rol="bodega",
                    departamento="Bodega",
                ),
                Usuario(
                    username="admin.1",
                    password=hash_password("pass123"),
                    pin_hash=hash_password("1234"),
                    nombre="Admin Uno",
                    rol="admin",
                    departamento="Admon",
                ),
                Usuario(
                    username="tecnico.1",
                    password=hash_password("pass123"),
                    pin_hash=hash_password("4321"),
                    nombre="Tecnico Uno",
                    rol="tecnico",
                    departamento="Logistica",
                    puede_iniciar_sesion=False,
                ),
                Usuario(
                    username="tecnico.2",
                    password=hash_password("pass123"),
                    pin_hash=hash_password("8765"),
                    nombre="Tecnico Dos",
                    rol="tecnico",
                    departamento="Logistica",
                    puede_iniciar_sesion=False,
                ),
            ]
        )
        seed_db.add_all(
            [
                CatalogoItem(nombre="Cable UTP Cat6", activo=True),
                CatalogoItem(nombre="Conector RJ45", activo=True),
                CatalogoItem(nombre="CONCENTRADO SHF", activo=True, permite_decimal=True),
                CatalogoItem(nombre="LIQUIDO CONCENTRADO DESODORIZADOR", activo=True, permite_decimal=True),
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
            Requisicion(
                folio="REQ-2005",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada_en_prokey",
                justificacion="Cerrada usuario",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
        ]
    )
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.get("/")
    assert response.status_code == 200

    html = response.text
    assert "Todas Mis Requisiciones" in html
    assert "Requisiciones Pendientes" in html
    assert "Requisiciones Finalizadas" in html
    assert "Creadas Este Mes" in html
    assert "Requisiciones Rechazadas" not in html
    assert "Requieren Seguimiento" not in html
    assert "Acciones Rápidas" not in html
    assert "home-kpi-grid--single-row" in html
    assert "Estado de Mis Requisiciones" in html
    assert "Pendiente de aprobación" in html
    assert "En proceso" in html
    assert "Pendiente de cierre" in html
    assert "Finalizada" in html
    assert "Mis Requisiciones por Mes" in html
    assert "Tiempo de Cierre" in html
    assert "0-1 días" in html
    assert "2-3 días" in html
    assert "4-7 días" in html
    assert "8+ días" in html
    assert "Indicadores Rápidos" not in html
    assert "Aprobadas Históricas" not in html
    assert "Mis Entregadas" not in html
    assert "Pendientes por aprobar" not in html
    assert "Pendientes de entregar" not in html


def test_home_bodega_muestra_cards_operativas_compactas(client: TestClient):
    login(client, "bodega.1", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Pendientes de Procesar" in html
    assert "Pendientes de Liquidar" in html
    assert "Finalizadas sin Prokey" in html
    assert "Finalizadas en Prokey" in html
    assert "Preparadas" not in html
    assert "No Entregadas" not in html
    assert "home-kpi-grid--single-row" in html
    assert "Acciones Rápidas" not in html
    assert "/bodega" in html
    assert "/bodega?vista=historial" in html


def test_home_bodega_muestra_panel_estado_operativo(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-BOD-01",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Pendiente procesar",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-BOD-02",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Pendiente liquidar",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-BOD-03",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada",
                justificacion="Liquidada",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
                liquidated_by=bodega.id,
                liquidated_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-BOD-04",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada_en_prokey",
                justificacion="Cerrada Prokey",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-BOD-05",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="No entregada",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
                delivery_result="no_entregada",
            ),
        ]
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Estado de Operación de Bodega" in html
    assert "Resume el estado actual de las requisiciones gestionadas por bodega." in html
    assert "Pendientes de Procesar" in html
    assert "Pendientes de Liquidar" in html
    assert "Finalizadas en Prokey" in html
    assert "No Entregadas" in html


def test_home_bodega_muestra_movimiento_mensual(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    ahora = datetime.now()
    db_session.add_all(
        [
            Requisicion(
                folio="REQ-BOD-M1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Entrega mes actual",
                approved_by=aprobador.id,
                approved_at=ahora,
                delivered_by=bodega.id,
                delivered_at=ahora,
            ),
            Requisicion(
                folio="REQ-BOD-M2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada",
                justificacion="Entrega mes anterior",
                approved_by=aprobador.id,
                approved_at=ahora,
                delivered_by=bodega.id,
                delivered_at=ahora.replace(month=max(1, ahora.month - 1)),
            ),
        ]
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Movimiento de Requisiciones por Mes" in html
    assert "Muestra el volumen de requisiciones entregadas por mes." in html
    assert "user-monthly-chart" in html


def test_home_bodega_muestra_resultados_de_entrega(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    ahora = datetime.now()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-BOD-R1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Entrega completa",
                approved_by=aprobador.id,
                approved_at=ahora,
                delivered_by=bodega.id,
                delivered_at=ahora,
                delivery_result="completa",
            ),
            Requisicion(
                folio="REQ-BOD-R2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Entrega parcial",
                approved_by=aprobador.id,
                approved_at=ahora,
                delivered_by=bodega.id,
                delivered_at=ahora,
                delivery_result="parcial",
            ),
            Requisicion(
                folio="REQ-BOD-R3",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="No entregada",
                approved_by=aprobador.id,
                approved_at=ahora,
                delivered_by=bodega.id,
                delivered_at=ahora,
                delivery_result="no_entregada",
            ),
        ]
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Resultados de Entrega" in html
    assert "Expone cómo terminan las entregas gestionadas por bodega." in html
    assert "Completa" in html
    assert "Parcial" in html
    assert "No Entregada" in html
    assert "home-bottom-grid--bodega-insights" in html


def test_mis_requisiciones_filtra_abiertas_para_alinear_cards_home(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-2010",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Pendiente visible",
            ),
            Requisicion(
                folio="REQ-2011",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Seguimiento visible",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-2012",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="rechazada",
                justificacion="Rechazada oculta",
            ),
            Requisicion(
                folio="REQ-2013",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada_en_prokey",
                justificacion="Cerrada oculta",
            ),
        ]
    )
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.get("/mis-requisiciones?estado=abiertas")
    assert response.status_code == 200
    html = response.text
    assert "REQ-2010" in html
    assert "REQ-2011" in html
    assert "REQ-2012" not in html
    assert "REQ-2013" not in html
    assert 'name="estado"' in html
    assert 'value="abiertas"' in html


def test_dashboard_backend_restringe_acceso_por_rol(client: TestClient):
    login(client, "user.ops", "pass123")
    response_page = client.get("/monitor")
    response_api = client.get("/api/dashboard/basicos")
    response_auditoria = client.get("/api/dashboard/auditoria")
    assert response_page.status_code == 403
    assert response_api.status_code == 403
    assert response_auditoria.status_code == 403


def test_dashboard_backend_habilita_acceso_para_aprobador(client: TestClient):
    login(client, "aprob.ops", "pass123")
    response_page = client.get("/monitor")
    response_api = client.get("/api/dashboard/basicos")
    assert response_page.status_code == 200
    assert "Monitor de Actividad" in response_page.text
    assert "cdn.jsdelivr.net/npm/chart.js" in response_page.text
    assert "async function cargarDatosBasicos()" in response_page.text
    assert "async function cargarDatosAuditoria()" in response_page.text
    assert "chart-motivos" in response_page.text
    assert "chart-solicitantes" in response_page.text
    assert "chart-items" in response_page.text
    assert "chart-horario" in response_page.text
    assert "chart-diferencia-producto" in response_page.text
    assert "chart-diferencia-tecnico" in response_page.text
    assert "kpi-tiempo-promedio-prokey" in response_page.text
    assert "kpi-promedio-requisiciones-dia" in response_page.text
    assert "kpi-indice-discrepancia" in response_page.text
    assert "kpi-inversion-demos" in response_page.text
    assert 'data-drilldown-kind="discrepancias"' in response_page.text
    assert 'data-drilldown-kind="demos"' in response_page.text
    assert "/api/dashboard/auditoria/discrepancias" in response_page.text
    assert "/api/dashboard/auditoria/demos" in response_page.text
    assert response_api.status_code == 200
    payload = response_api.json()
    assert "kpis" in payload
    assert "motivos" in payload
    assert "top_solicitantes" in payload
    assert "top_items" in payload
    assert "horario" in payload
    assert payload["horario"]["alert_from_hour"] == 14

    response_auditoria = client.get("/api/dashboard/auditoria")
    assert response_auditoria.status_code == 200
    payload_auditoria = response_auditoria.json()
    assert "kpis" in payload_auditoria
    assert "diferencia_por_producto" in payload_auditoria
    assert "diferencias_por_tecnico" in payload_auditoria


def test_dashboard_basicos_agrega_metricas_base(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req_1 = Requisicion(
        folio="REQ-DASH-01",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        motivo_requisicion="Demostración",
        justificacion="Contingencia uno",
        approved_by=aprobador.id,
        approved_at=datetime(2026, 3, 11, 9, 5, 0),
        created_at=datetime(2026, 3, 11, 13, 30, 0),
    )
    req_2 = Requisicion(
        folio="REQ-DASH-02",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        motivo_requisicion="Servicio No Programado",
        justificacion="Contingencia dos",
        approved_by=aprobador.id,
        approved_at=datetime(2026, 3, 11, 15, 5, 0),
        created_at=datetime(2026, 3, 11, 15, 45, 0),
    )
    req_3 = Requisicion(
        folio="REQ-DASH-03",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        motivo_requisicion="Demostración",
        justificacion="Contingencia tres",
        created_at=datetime(2026, 3, 11, 15, 10, 0),
    )
    req_4 = Requisicion(
        folio="REQ-DASH-04",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="liquidada_en_prokey",
        motivo_requisicion="Demostración",
        justificacion="Contingencia cuatro",
        created_at=datetime(2026, 3, 12, 10, 0, 0),
        liquidated_at=datetime(2026, 3, 13, 12, 0, 0),
        prokey_liquidada_at=datetime(2026, 3, 13, 16, 0, 0),
    )
    req_5 = Requisicion(
        folio="REQ-DASH-05",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="liquidada_en_prokey",
        motivo_requisicion="Reposición",
        justificacion="Contingencia cinco",
        created_at=datetime(2026, 3, 13, 8, 0, 0),
        liquidated_at=datetime(2026, 3, 13, 18, 0, 0),
        prokey_liquidada_at=datetime(2026, 3, 14, 2, 0, 0),
    )
    db_session.add_all([req_1, req_2, req_3, req_4, req_5])
    db_session.commit()
    db_session.refresh(req_1)
    db_session.refresh(req_2)
    db_session.refresh(req_3)
    db_session.refresh(req_4)
    db_session.refresh(req_5)

    db_session.add_all(
        [
            Item(requisicion_id=req_1.id, descripcion="Cable UTP Cat6", cantidad=3, unidad="unidad"),
            Item(requisicion_id=req_2.id, descripcion="Cable UTP Cat6", cantidad=2, unidad="unidad"),
            Item(requisicion_id=req_3.id, descripcion="Conector RJ45", cantidad=5, unidad="unidad"),
            Item(requisicion_id=req_4.id, descripcion="Cable UTP Cat6", cantidad=1, unidad="unidad"),
            Item(requisicion_id=req_5.id, descripcion="Bomba Dosificadora", cantidad=4, unidad="unidad"),
        ]
    )
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/api/dashboard/basicos")
    assert response.status_code == 200
    payload = response.json()

    assert payload["kpis"]["promedio_horas_hasta_prokey"] == 24.0
    assert payload["kpis"]["requisiciones_liquidadas_en_prokey"] == 2
    assert payload["kpis"]["requisiciones_promedio_por_dia"] == 1.67
    assert payload["kpis"]["dias_observados"] == 3
    assert payload["kpis"]["total_requisiciones"] == 5

    motivos = dict(zip(payload["motivos"]["labels"], payload["motivos"]["values"]))
    assert motivos["Demostración"] == 3
    assert motivos["Servicio No Programado"] == 1
    assert motivos["Reposición"] == 1

    solicitantes = dict(zip(payload["top_solicitantes"]["labels"], payload["top_solicitantes"]["values"]))
    assert solicitantes[user.nombre] == 5

    items = dict(zip(payload["top_items"]["labels"], payload["top_items"]["values"]))
    assert items["Cable UTP Cat6"] == 6.0
    assert items["Conector RJ45"] == 5.0
    assert items["Bomba Dosificadora"] == 4.0
    assert payload["horario"]["labels"][13] == "13:00"
    assert payload["horario"]["values"][13] == 1
    assert payload["horario"]["values"][15] == 2
    assert payload["horario"]["alert_from_hour"] == 14


def test_dashboard_basicos_excluye_fines_de_semana_del_promedio_diario(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-DASH-WD-01",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                motivo_requisicion="Demostración",
                justificacion="Viernes",
                created_at=datetime(2026, 3, 13, 10, 0, 0),
            ),
            Requisicion(
                folio="REQ-DASH-WD-02",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                motivo_requisicion="Demostración",
                justificacion="Lunes",
                created_at=datetime(2026, 3, 16, 10, 0, 0),
            ),
        ]
    )
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/api/dashboard/basicos")
    assert response.status_code == 200
    payload = response.json()

    assert payload["kpis"]["dias_observados"] == 2
    assert payload["kpis"]["requisiciones_promedio_por_dia"] == 1.0


def test_dashboard_auditoria_agrega_kpis_y_diferencias(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    tecnico_1 = db_session.query(Usuario).filter(Usuario.username == "tecnico.1").first()
    tecnico_2 = db_session.query(Usuario).filter(Usuario.username == "tecnico.2").first()

    req_1 = Requisicion(
        folio="REQ-AUD-01",
        solicitante_id=user.id,
        receptor_designado_id=tecnico_1.id,
        departamento="Operaciones",
        estado="liquidada",
        motivo_requisicion="Demostración",
        justificacion="Auditoria uno",
        approved_by=aprobador.id,
        approved_at=datetime(2026, 3, 11, 10, 0, 0),
        liquidated_at=datetime(2026, 3, 11, 16, 0, 0),
    )
    req_2 = Requisicion(
        folio="REQ-AUD-02",
        solicitante_id=user.id,
        receptor_designado_id=tecnico_2.id,
        departamento="Operaciones",
        estado="liquidada_en_prokey",
        motivo_requisicion="Servicio No Programado",
        justificacion="Auditoria dos",
        approved_by=aprobador.id,
        approved_at=datetime(2026, 3, 11, 11, 0, 0),
        liquidated_at=datetime(2026, 3, 11, 17, 0, 0),
    )
    req_3 = Requisicion(
        folio="REQ-AUD-03",
        solicitante_id=user.id,
        receptor_designado_id=tecnico_1.id,
        departamento="Operaciones",
        estado="liquidada",
        motivo_requisicion="Otros",
        justificacion="Auditoria tres",
        approved_by=aprobador.id,
        approved_at=datetime(2026, 3, 11, 12, 0, 0),
        liquidated_at=datetime(2026, 3, 11, 18, 0, 0),
    )
    db_session.add_all([req_1, req_2, req_3])
    db_session.commit()
    db_session.refresh(req_1)
    db_session.refresh(req_2)
    db_session.refresh(req_3)

    db_session.add_all(
        [
            Item(
                requisicion_id=req_1.id,
                descripcion="Cable UTP Cat6",
                cantidad=5,
                cantidad_entregada=5,
                qty_used=3,
                qty_left_at_client=1,
                qty_returned_to_warehouse=2,
                liquidation_mode="RETORNABLE",
                contexto_operacion="reposicion",
                unidad="unidad",
                es_demo=False,
            ),
            Item(
                requisicion_id=req_1.id,
                descripcion="Conector RJ45",
                cantidad=4,
                cantidad_entregada=4,
                qty_used=1,
                qty_left_at_client=1,
                qty_returned_to_warehouse=2,
                liquidation_mode="CONSUMIBLE",
                contexto_operacion="reposicion",
                unidad="unidad",
                es_demo=True,
            ),
            Item(
                requisicion_id=req_2.id,
                descripcion="Cable UTP Cat6",
                cantidad=2,
                cantidad_entregada=2,
                qty_used=1,
                qty_left_at_client=0,
                qty_returned_to_warehouse=0,
                liquidation_mode="RETORNABLE",
                contexto_operacion="reposicion",
                unidad="unidad",
                es_demo=True,
            ),
            Item(
                requisicion_id=req_3.id,
                descripcion="Conector RJ45",
                cantidad=3,
                cantidad_entregada=3,
                qty_used=1,
                qty_left_at_client=2,
                qty_returned_to_warehouse=2,
                liquidation_mode="RETORNABLE",
                contexto_operacion="instalacion_inicial",
                unidad="unidad",
                es_demo=False,
            ),
        ]
    )
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/api/dashboard/auditoria")
    assert response.status_code == 200
    payload = response.json()

    assert payload["kpis"]["requisiciones_cerradas"] == 3
    assert payload["kpis"]["requisiciones_con_diferencia"] == 2
    assert payload["kpis"]["indice_discrepancia_pct"] == 66.67
    assert payload["kpis"]["inversion_demos"] == 6.0

    diferencia_productos = dict(zip(payload["diferencia_por_producto"]["labels"], payload["diferencia_por_producto"]["values"]))
    assert diferencia_productos["Cable UTP Cat6"] == 2.0
    assert diferencia_productos["Conector RJ45"] == 1.0

    diferencia_tecnicos = dict(zip(payload["diferencias_por_tecnico"]["labels"], payload["diferencias_por_tecnico"]["values"]))
    assert diferencia_tecnicos["Tecnico Uno"] == 1.0
    assert diferencia_tecnicos["Tecnico Dos"] == 2.0

    response_drilldown_diferencias = client.get("/api/dashboard/auditoria/discrepancias")
    assert response_drilldown_diferencias.status_code == 200
    payload_drilldown_diferencias = response_drilldown_diferencias.json()
    assert payload_drilldown_diferencias["kind"] == "discrepancias"
    assert payload_drilldown_diferencias["total"] == 2
    assert {item["folio"] for item in payload_drilldown_diferencias["items"]} == {"REQ-AUD-01", "REQ-AUD-02"}

    response_drilldown_demos = client.get("/api/dashboard/auditoria/demos")
    assert response_drilldown_demos.status_code == 200
    payload_drilldown_demos = response_drilldown_demos.json()
    assert payload_drilldown_demos["kind"] == "demos"
    assert payload_drilldown_demos["total"] == 2
    assert {item["folio"] for item in payload_drilldown_demos["items"]} == {"REQ-AUD-01", "REQ-AUD-02"}


def test_navbar_muestra_contingencias_solo_para_roles_autorizados(client: TestClient):
    login(client, "aprob.ops", "pass123")
    response_aprobador = client.get("/")
    assert response_aprobador.status_code == 200
    assert "Monitor de Actividad" in response_aprobador.text

    client.post("/logout")
    login(client, "user.ops", "pass123")
    response_user = client.get("/")
    assert response_user.status_code == 200
    assert "Monitor de Actividad" not in response_user.text


def test_navbar_admin_agrupa_administracion_y_menu_usuario(client: TestClient):
    login(client, "admin.1", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Administración" in html
    assert "/admin/usuarios" in html
    assert "/admin/catalogo-items" in html
    assert "/admin/respaldos" in html
    assert 'class="user-trigger' in html
    assert "Cambiar contrasena" in html


def test_monitor_renderiza_fase_2_de_auditoria(client: TestClient):
    login(client, "aprob.ops", "pass123")
    response = client.get("/monitor")
    assert response.status_code == 200
    html = response.text
    assert "Auditoría y Diferencias" in html
    assert "/api/dashboard/auditoria" in html
    assert "dashboard-bi-drilldown" in html
    assert "Ranking de Diferencia por Producto" in html
    assert "Diferencias por Tecnico" in html


def test_home_aprobador_muestra_cards_operativas_globales(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    db_session.add_all(
        [
            Requisicion(
                folio="REQ-2301",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Pendiente para aprobador",
            ),
            Requisicion(
                folio="REQ-2302",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Entregada pendiente de liquidar",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-2303",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="rechazada",
                justificacion="Rechazada para aprobador",
                rejected_by=aprobador.id,
                rejected_at=datetime.now(),
                rejection_reason="No procede",
            ),
        ]
    )
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "Pendientes por Aprobar" in html
    assert "Pendientes de Entregar" in html
    assert "Pendientes de Liquidar" in html
    assert "Requisiciones Rechazadas" in html
    assert "Todas Mis Requisiciones" not in html
    assert "Requisiciones Pendientes" not in html
    assert "Requisiciones Finalizadas" not in html
    assert "home-kpi-grid--single-row" in html
    assert "Acciones Rápidas" not in html
    assert "Aprobadas Históricas" not in html
    assert "/aprobar" in html
    assert "/todas-requisiciones?estado=pendiente_entregar" in html
    assert "/todas-requisiciones?estado=entregada" in html
    assert "/todas-requisiciones?estado=rechazada" in html


def test_home_aprobador_muestra_panel_estado_global(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-APR-01",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Pendiente global",
            ),
            Requisicion(
                folio="REQ-APR-02",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Pendiente entrega global",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-APR-03",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Pendiente liquidacion global",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-APR-04",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="rechazada",
                justificacion="Rechazada global",
                rejected_by=aprobador.id,
                rejected_at=datetime.now(),
                rejection_reason="No procede",
            ),
            Requisicion(
                folio="REQ-APR-05",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada_en_prokey",
                justificacion="Finalizada global",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
        ]
    )
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Estado Global de Requisiciones" in html
    assert "Resume el estado actual del flujo completo de requisiciones." in html
    assert "Pendiente de aprobación" in html
    assert "Pendiente de entrega" in html
    assert "Pendiente de liquidación" in html
    assert "Finalizada" in html
    assert "Rechazada" in html


def test_home_aprobador_muestra_requisiciones_por_mes(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    ahora = datetime.now()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-APR-M1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Mes actual aprobador",
                created_at=ahora,
            ),
            Requisicion(
                folio="REQ-APR-M2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Mes anterior aprobador",
                created_at=ahora.replace(month=max(1, ahora.month - 1)),
            ),
        ]
    )
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Requisiciones por Mes" in html
    assert "Muestra el volumen global de requisiciones creadas por mes." in html
    assert "user-monthly-chart" in html


def test_home_aprobador_muestra_motivos_de_requisicion(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-APR-P1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Pendiente reciente",
                motivo_requisicion="Demostración",
            ),
            Requisicion(
                folio="REQ-APR-P2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Pendiente antiguo",
                motivo_requisicion="R1E",
            ),
            Requisicion(
                folio="REQ-APR-P3",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Motivo repetido",
                motivo_requisicion="Demostración",
            ),
        ]
    )
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Motivos de Requisición" in html
    assert "Muestra los principales motivos de uso de la aplicación." in html
    assert "Demostración" in html
    assert "R1E" in html
    assert "home-bottom-grid--aprobador-insights" in html


def test_bodega_no_ve_accesos_de_creacion_ni_mis_requisiciones(client: TestClient):
    login(client, "bodega.1", "pass123")
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "/crear" not in html
    assert "/mis-requisiciones" not in html
    assert "/bodega" in html


def test_bodega_es_redirigido_si_intenta_abrir_crear_o_mis_requisiciones(client: TestClient):
    login(client, "bodega.1", "pass123")
    response_crear = client.get("/crear", follow_redirects=False)
    response_mis = client.get("/mis-requisiciones", follow_redirects=False)
    assert response_crear.status_code == 303
    assert response_crear.headers["location"].startswith("/bodega?")
    assert response_mis.status_code == 303
    assert response_mis.headers["location"].startswith("/bodega?")


def test_bodega_no_puede_crear_requisicion_por_post_directo(client: TestClient, db_session: Session):
    login(client, "bodega.1", "pass123")
    tecnico = db_session.query(Usuario).filter(Usuario.username == "tecnico.1").first()
    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-1099",
            "cliente_nombre": "Cliente bloqueado",
            "cliente_ruta_principal": "RA02",
            "receptor_designado_id": str(tecnico.id),
            "motivo_requisicion": "Servicio pendiente",
            "justificacion": "No debe permitir crear a bodega",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith("/bodega?")
    assert db_session.query(Requisicion).filter(Requisicion.cliente_nombre == "Cliente bloqueado").first() is None


def test_crear_requisicion(client: TestClient, db_session: Session):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-1001",
            "cliente_nombre": "Cliente Uno",
            "cliente_ruta_principal": "RA02",
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
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
    assert req.motivo_requisicion == "Servicio pendiente"
    assert len(req.items) == 1
    assert req.items[0].descripcion == "Cable UTP Cat6"


def test_crear_requisicion_redirige_si_falta_receptor_designado(client: TestClient):
    login(client, "user.ops", "pass123")
    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-1001",
            "cliente_nombre": "Cliente Uno",
            "cliente_ruta_principal": "RA02",
            "motivo_requisicion": "Servicio pendiente",
            "justificacion": "Formulario desactualizado",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "25",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/crear?")
    assert "msg=" in location
    assert "type=warning" in location


def test_crear_requisicion_requiere_motivo(client: TestClient):
    login(client, "user.ops", "pass123")
    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-1002",
            "cliente_nombre": "Cliente sin motivo",
            "cliente_ruta_principal": "RA02",
            "receptor_designado_id": "1",
            "motivo_requisicion": "",
            "justificacion": "Debe fallar por motivo vacio",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Debes seleccionar un motivo"


def test_crear_requisicion_rechaza_motivo_invalido(client: TestClient):
    login(client, "user.ops", "pass123")
    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-1003",
            "cliente_nombre": "Cliente motivo invalido",
            "cliente_ruta_principal": "RA02",
            "receptor_designado_id": "1",
            "motivo_requisicion": "MOTIVO_INVALIDO",
            "justificacion": "Debe fallar por motivo invalido",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Motivo de requisicion invalido"


def test_crear_requisicion_rechaza_decimal_en_item_no_habilitado(client: TestClient):
    login(client, "user.ops", "pass123")
    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-1010",
            "cliente_nombre": "Cliente Entero",
            "cliente_ruta_principal": "RA02",
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
            "justificacion": "Debe fallar por decimal no permitido",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1.5",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "El item Cable UTP Cat6 solo permite cantidades enteras"


def test_crear_requisicion_permite_decimal_en_item_habilitado(client: TestClient, db_session: Session):
    login(client, "user.ops", "pass123")
    response = client.post(
        "/crear",
        data={
            "cliente_codigo": "C-1011",
            "cliente_nombre": "Cliente Decimal",
            "cliente_ruta_principal": "RA02",
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
            "justificacion": "Debe aceptar decimal en concentrado",
            "items[0][descripcion]": "LIQUIDO CONCENTRADO DESODORIZADOR",
            "items[0][cantidad]": "1.5",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    req = db_session.query(Requisicion).order_by(Requisicion.id.desc()).first()
    assert req is not None
    assert req.items[0].descripcion == "LIQUIDO CONCENTRADO DESODORIZADOR"
    assert req.items[0].cantidad == 1.5


def test_crear_requisicion_ignora_departamento_enviado(client: TestClient, db_session: Session):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "departamento": "Ventas",
            "cliente_codigo": "C-2001",
            "cliente_nombre": "Cliente Dos",
            "cliente_ruta_principal": "rb03",
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
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


def test_pdf_disponible_desde_aprobada(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req = Requisicion(
        folio="REQ-0099",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="PDF debe estar disponible desde aprobada",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        cliente_codigo="C-9090",
        cliente_nombre="Cliente PDF",
        cliente_ruta_principal="RA02",
    )
    db_session.add(req)
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get(f"/requisiciones/{req.id}/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_pdf_sigue_bloqueado_en_pendiente(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = Requisicion(
        folio="REQ-0100",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="PDF no debe abrirse en pendiente",
        cliente_codigo="C-9091",
        cliente_nombre="Cliente PDF Pendiente",
        cliente_ruta_principal="RA02",
    )
    db_session.add(req)
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.get(f"/requisiciones/{req.id}/pdf")
    assert response.status_code == 403
    assert response.json()["detail"] == "PDF disponible solo desde requisiciones aprobadas"


def test_pdf_aprobada_usa_cantidad_solicitada(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    req = Requisicion(
        folio="REQ-0101",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="PDF debe mostrar cantidad solicitada antes de entrega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        cliente_codigo="C-9092",
        cliente_nombre="Cliente PDF Solicitado",
        cliente_ruta_principal="RA02",
    )
    db_session.add(req)
    db_session.commit()
    db_session.add(
        Item(
            requisicion_id=req.id,
            descripcion="Cable UTP Cat6",
            cantidad=7,
            cantidad_entregada=0,
            unidad="unidad",
        )
    )
    db_session.commit()

    login(client, "aprob.ops", "pass123")
    response = client.get(f"/requisiciones/{req.id}/pdf")
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")


def test_pdf_incluye_receptor_designado_en_payload(client: TestClient, db_session: Session, monkeypatch):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    tecnico = db_session.query(Usuario).filter(Usuario.username == "tecnico.1").first()

    req = Requisicion(
        folio="REQ-0101A",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="PDF debe incluir receptor designado",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        cliente_codigo="C-9093",
        cliente_nombre="Cliente PDF Receptor",
        cliente_ruta_principal="RA03",
        receptor_designado_id=tecnico.id,
    )
    db_session.add(req)
    db_session.commit()

    captured = {}

    def fake_generate(req_data):
        captured.update(req_data)
        return b"%PDF-TEST"

    monkeypatch.setattr("app.pdf_generator.generate_requisicion_pdf", fake_generate)

    login(client, "aprob.ops", "pass123")
    response = client.get(f"/requisiciones/{req.id}/pdf")
    assert response.status_code == 200
    assert response.content == b"%PDF-TEST"
    assert captured["solicitante_nombre"] == user.nombre
    assert captured["receptor_designado_nombre"] == tecnico.nombre
    assert captured["receptor_designado_rol"] == tecnico.rol


def test_pdf_multipagina_muestra_todos_los_items():
    req_data = {
        "id": 999,
        "folio": "REQ-0999",
        "estado": "liquidada",
        "created_at": "2026-03-11 11:00:00",
        "approved_at": "2026-03-11 11:05:00",
        "prepared_at": "2026-03-11 11:10:00",
        "delivered_at": "2026-03-11 11:15:00",
        "recibido_at": "2026-03-11 11:15:00",
        "liquidated_at": "2026-03-11 11:30:00",
        "cliente": "Cliente Multipagina",
        "codigo_cliente": "C-9999",
        "ruta": "RA09",
        "solicitante_nombre": "Usuario Ops",
        "receptor_designado_nombre": "Tecnico Uno",
        "receptor_designado_rol": "tecnico",
        "aprobador_nombre": "Aprobador Ops",
        "preparador_nombre": "Bodega Uno",
        "jefe_bodega_nombre": "Bodega Uno",
        "liquidado_por_nombre": "Bodega Uno",
        "recibido_por_nombre": "Tecnico Uno",
        "prokey_ref": "PK-999",
        "justificacion": "Prueba de paginacion de PDF",
        "comentario_liquidacion": "Todos los items deben aparecer en el PDF aunque ocupen varias paginas.",
        "items": [
            {
                "descripcion": f"Item de prueba numero {index} con descripcion larga para forzar paginacion",
                "cantidad_solicitada": 1,
                "cantidad_entregada": 1,
                "cantidad_usada": 1,
                "cantidad_no_usada": 0,
                "cantidad_retorna": 1,
                "liquidation_mode": "RETORNABLE",
                "contexto_operacion": "reposicion",
                "es_demo": False,
                "pk_ingreso_qty": 1,
                "liquidation_alerts": [],
                "nota_liquidacion": "Nota breve" if index % 3 == 0 else None,
            }
            for index in range(1, 45)
        ],
    }

    pdf_bytes = generate_requisicion_pdf(req_data)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(re.findall(rb"/Type /Page(?!s)", pdf_bytes)) >= 2


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


def test_jefe_bodega_puede_aprobar_requisicion(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    jefe_bodega = db_session.query(Usuario).filter(Usuario.username == "jefe.bodega").first()

    req = Requisicion(
        folio="REQ-0099",
        solicitante_id=user.id,
        departamento="Ventas",
        estado="pendiente",
        justificacion="Requisicion para validar rol mixto jefe_bodega",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "jefe.bodega", "pass123")
    response = client.post(
        f"/aprobar/{req.id}",
        data={"comentario": "Aprobada desde rol combinado"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "aprobada"
    assert req.approved_by == jefe_bodega.id


def test_aprobar_view_muestra_gestion_para_jefe_bodega(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    req = Requisicion(
        folio="REQ-0100",
        solicitante_id=user.id,
        departamento="Ventas",
        estado="pendiente",
        justificacion="Pendiente visible para jefe_bodega",
    )
    db_session.add(req)
    db_session.commit()

    login(client, "jefe.bodega", "pass123")
    response = client.get("/aprobar")

    assert response.status_code == 200
    assert f"/aprobar/{req.id}/gestionar" in response.text


def test_listados_con_filtros_exponen_autosubmit_en_selectores(client: TestClient):
    login(client, "jefe.bodega", "pass123")

    aprobar = client.get("/aprobar")
    assert aprobar.status_code == 200
    assert "js-autosubmit-filters" in aprobar.text
    assert "data-autosubmit-select" in aprobar.text

    todas = client.get("/todas-requisiciones")
    assert todas.status_code == 200
    assert "js-autosubmit-filters" in todas.text
    assert "data-autosubmit-select" in todas.text
    assert "data-date-picker" in todas.text
    assert "showPicker" in todas.text

    bodega = client.get("/bodega")
    assert bodega.status_code == 200
    assert "js-autosubmit-filters" in bodega.text
    assert "data-autosubmit-select" in bodega.text
    assert "data-date-picker" in bodega.text
    assert "showPicker" in bodega.text


def test_home_jefe_bodega_muestra_links_de_aprobar_y_bodega(client: TestClient):
    login(client, "jefe.bodega", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Todas Mis Requisiciones" not in html
    assert 'Pendientes de Procesar' in html
    assert 'Pendientes de Liquidar' in html
    assert 'Liquidadas' not in html
    assert 'Finalizadas en Prokey' in html
    assert '/aprobar' in html
    assert '/bodega' in html
    assert '/bodega?vista=historial' in html


def test_home_jefe_bodega_muestra_panel_estado_global(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    db_session.add_all(
        [
            Requisicion(
                folio="REQ-JB-EST-1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Pendiente jefe bodega",
            ),
            Requisicion(
                folio="REQ-JB-EST-2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Proceso jefe bodega",
            ),
            Requisicion(
                folio="REQ-JB-EST-3",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Liquidacion jefe bodega",
            ),
            Requisicion(
                folio="REQ-JB-EST-4",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada_en_prokey",
                justificacion="Finalizada jefe bodega",
            ),
            Requisicion(
                folio="REQ-JB-EST-5",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="rechazada",
                justificacion="Rechazada jefe bodega",
            ),
        ]
    )
    db_session.commit()

    login(client, "jefe.bodega", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Estado Global del Flujo" in html
    assert "Resume el estado actual del flujo de requisiciones bajo supervisión." in html
    assert "Pendiente de aprobación" in html
    assert "Pendiente de proceso" in html
    assert "Pendiente de liquidación" in html
    assert "Finalizada" in html
    assert "Rechazada" in html


def test_home_jefe_bodega_muestra_requisiciones_por_mes(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    ahora = datetime.now()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-JB-M1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Mes actual jefe bodega",
                created_at=ahora,
            ),
            Requisicion(
                folio="REQ-JB-M2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Mes anterior jefe bodega",
                created_at=ahora - timedelta(days=35),
            ),
        ]
    )
    db_session.commit()

    login(client, "jefe.bodega", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Requisiciones por Mes" in html
    assert "Muestra el volumen global de requisiciones creadas por mes." in html
    assert "user-monthly-chart" in html


def test_home_jefe_bodega_muestra_resultados_de_entrega(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    ahora = datetime.now()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-JB-R1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Entrega completa jefe bodega",
                approved_by=aprobador.id,
                approved_at=ahora,
                delivered_by=bodega.id,
                delivered_at=ahora,
                delivery_result="completa",
            ),
            Requisicion(
                folio="REQ-JB-R2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Entrega parcial jefe bodega",
                approved_by=aprobador.id,
                approved_at=ahora,
                delivered_by=bodega.id,
                delivered_at=ahora,
                delivery_result="parcial",
            ),
            Requisicion(
                folio="REQ-JB-R3",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="entregada",
                justificacion="Entrega fallida jefe bodega",
                approved_by=aprobador.id,
                approved_at=ahora,
                delivered_by=bodega.id,
                delivered_at=ahora,
                delivery_result="no_entregada",
            ),
        ]
    )
    db_session.commit()

    login(client, "jefe.bodega", "pass123")
    response = client.get("/")

    assert response.status_code == 200
    html = response.text
    assert "Resultados de Entrega" in html
    assert "Expone cómo terminan las entregas gestionadas en operación." in html
    assert "Completa" in html
    assert "Parcial" in html
    assert "No Entregada" in html
    assert "home-bottom-grid--jefe-bodega-insights" in html
    assert "Acciones Rápidas" not in html


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
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
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
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
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
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
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
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
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
            "receptor_designado_id": "1",
            "motivo_requisicion": "Servicio pendiente",
            "justificacion": "Prueba de validacion de ruta principal",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Ruta principal invalida (formato: AA00)"


def test_usuario_puede_editar_requisicion_pendiente_propia(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    receptor = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    req = Requisicion(
        folio="REQ-0500",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        cliente_codigo="C-EDIT-1",
        cliente_nombre="Cliente Original",
        cliente_ruta_principal="RA02",
        motivo_requisicion="Servicio pendiente",
        justificacion="Texto original",
        receptor_designado_id=receptor.id,
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)
    db_session.add(
        Item(
            requisicion_id=req.id,
            descripcion="Cable UTP Cat6",
            cantidad=1,
            unidad="unidad",
            contexto_operacion="reposicion",
            es_demo=False,
        )
    )
    db_session.commit()

    login(client, "user.ops", "pass123")
    form_resp = client.get(f"/mis-requisiciones/{req.id}/editar")
    assert form_resp.status_code == 200
    assert "Editar Requisicion" in form_resp.text

    edit_resp = client.post(
        f"/mis-requisiciones/{req.id}/editar",
        data={
            "cliente_codigo": "C-EDIT-2",
            "cliente_nombre": "Cliente Editado",
            "cliente_ruta_principal": "RB03",
            "receptor_designado_id": str(receptor.id),
            "motivo_requisicion": "Queja Fragancia",
            "justificacion": "Texto actualizado",
            "items[0][descripcion]": "Conector RJ45",
            "items[0][cantidad]": "3",
            "items[0][contexto_operacion]": "instalacion_inicial",
            "es_demo_0": "on",
        },
        follow_redirects=False,
    )
    assert edit_resp.status_code == 303
    db_session.refresh(req)
    assert req.cliente_codigo == "C-EDIT-2"
    assert req.cliente_nombre == "Cliente Editado"
    assert req.cliente_ruta_principal == "RB03"
    assert req.motivo_requisicion == "Queja Fragancia"
    assert req.justificacion == "Texto actualizado"
    assert len(req.items) == 1
    assert req.items[0].descripcion == "Conector RJ45"
    assert req.items[0].cantidad == 3
    assert req.items[0].contexto_operacion == "instalacion_inicial"
    assert req.items[0].es_demo is True


def test_usuario_no_puede_editar_requisicion_aprobada(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    req = Requisicion(
        folio="REQ-0500A",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        cliente_codigo="C-APR-1",
        cliente_nombre="Cliente Aprobado",
        cliente_ruta_principal="RA02",
        motivo_requisicion="Servicio pendiente",
        justificacion="No editable",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.post(
        f"/mis-requisiciones/{req.id}/editar",
        data={
            "cliente_codigo": "C-APR-2",
            "cliente_nombre": "No debe cambiar",
            "cliente_ruta_principal": "RA02",
            "receptor_designado_id": str(aprobador.id),
            "motivo_requisicion": "Otros",
            "justificacion": "Intento",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "1",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    db_session.refresh(req)
    assert req.cliente_codigo == "C-APR-1"


def test_usuario_no_puede_editar_requisicion_de_otro(client: TestClient, db_session: Session):
    otro = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    req = Requisicion(
        folio="REQ-0500B",
        solicitante_id=otro.id,
        departamento="Operaciones",
        estado="pendiente",
        cliente_codigo="C-OTRO-1",
        cliente_nombre="Cliente Otro",
        cliente_ruta_principal="RA02",
        motivo_requisicion="Otros",
        justificacion="No editable por user.ops",
        receptor_designado_id=otro.id,
    )
    db_session.add(req)
    db_session.commit()

    login(client, "user.ops", "pass123")
    response = client.get(f"/mis-requisiciones/{req.id}/editar", follow_redirects=False)
    assert response.status_code == 303


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
        estado="preparado",
        justificacion="Requisicion para prueba de entrega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={
            "resultado": "completa",
            "recibido_por_id": str(user.id),
            "pin_receptor": "1234",
            "comentario": "Entregado completo y verificado",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.delivered_by == bodega.id
    assert req.delivery_result == "completa"
    assert req.delivered_to == user.nombre
    assert req.recibido_por_id == user.id
    assert req.recibido_at is not None
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


def test_detalle_conserva_receptor_designado_y_receptor_real(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    otro = db_session.query(Usuario).filter(Usuario.username == "user.otro").first()

    req = Requisicion(
        folio="REQ-0001B",
        solicitante_id=user.id,
        receptor_designado_id=otro.id,
        departamento="Operaciones",
        estado="preparado",
        justificacion="Cambio de receptor en entrega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={
            "resultado": "completa",
            "recibido_por_id": str(user.id),
            "pin_receptor": "1234",
            "comentario": "Recibio otra persona autorizada",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    detail = client.get(f"/api/requisiciones/{req.id}")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["receptor_designado"]["nombre"] == otro.nombre
    assert payload["receptor_designado"]["rol"] == otro.rol
    assert payload["recibido_por"] == user.nombre
    assert payload["recibido_por_detalle"]["nombre"] == user.nombre
    assert payload["recibido_por_detalle"]["rol"] == user.rol


def test_bodega_puede_marcar_entrega_parcial(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0011",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="preparado",
        justificacion="Entrega parcial por faltante",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
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
    response_inicio = client.post(f"/entregar/{req.id}", data={"resultado": "parcial"}, follow_redirects=False)
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
            "recibido_por_id": str(user.id),
            "pin_receptor": "1234",
            "comentario": "Falto 1 item por quiebre de stock",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.delivered_by == bodega.id
    assert req.delivery_result == "parcial"
    assert req.recibido_por_id == user.id
    assert req.delivery_comment == "Falto 1 item por quiebre de stock"
    assert req.items[0].cantidad_entregada == 0.5


def test_bodega_puede_abrir_vista_gestion_entrega(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0202",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="preparado",
        justificacion="Vista dedicada de bodega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.get(f"/bodega/{req.id}/gestionar")
    assert response.status_code == 200
    assert "Gestionar Entrega" in response.text
    assert req.folio in response.text


def test_bodega_debe_preparar_antes_de_entregar(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0203",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="aprobada",
        justificacion="Debe pasar por preparado",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    preparar_form = client.get(f"/bodega/{req.id}/preparar")
    assert preparar_form.status_code == 200
    assert "Preparar Requisición" in preparar_form.text
    assert "Debe pasar por preparado" in preparar_form.text

    preparar = client.post(f"/bodega/{req.id}/preparar", follow_redirects=False)
    assert preparar.status_code == 303
    db_session.refresh(req)
    assert req.estado == "preparado"
    assert req.prepared_by == bodega.id
    assert req.prepared_at is not None

    gestionar = client.get(f"/bodega/{req.id}/gestionar")
    assert gestionar.status_code == 200
    assert "Gestionar Entrega" in gestionar.text


def test_bodega_puede_marcar_no_entregada(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0012",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="preparado",
        justificacion="Sin inventario",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
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
    assert req.estado == "no_entregada"
    assert req.delivered_by == bodega.id
    assert req.delivery_result == "no_entregada"
    assert req.delivered_to is None
    assert req.delivery_comment == "No hay stock ni sustituto"


def test_bodega_no_entregada_no_requiere_pin_aun_con_receptor_designado(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0012A",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="preparado",
        justificacion="No entregada con receptor designado",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
        receptor_designado_id=user.id,
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={
            "resultado": "no_entregada",
            "recibido_por_id": str(user.id),
            "pin_receptor": "",
            "comentario": "Cliente no estaba disponible para recibir",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "no_entregada"
    assert req.delivery_result == "no_entregada"
    assert req.recibido_por_id is None
    assert req.recibido_at is None
    assert req.delivered_to is None


def test_bodega_entrega_completa_requiere_recibe(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0013",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="preparado",
        justificacion="Validacion de quien recibe",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={"resultado": "completa", "recibido_por_id": "", "pin_receptor": "", "comentario": ""},
        follow_redirects=False,
    )

    assert response.status_code == 400
    db_session.refresh(req)
    assert req.estado == "preparado"


def test_entrega_con_pin_incorrecto_no_procesa(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0015",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="preparado",
        justificacion="PIN incorrecto",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={
            "resultado": "completa",
            "recibido_por_id": str(user.id),
            "pin_receptor": "9999",
            "comentario": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 400
    db_session.refresh(req)
    assert req.estado == "preparado"
    assert req.recibido_por_id is None


def test_entrega_con_receptor_inexistente_no_procesa(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0016",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="preparado",
        justificacion="Receptor inexistente",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        prepared_by=bodega.id,
        prepared_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "bodega.1", "pass123")
    response = client.post(
        f"/entregar/{req.id}",
        data={
            "resultado": "completa",
            "recibido_por_id": "999999",
            "pin_receptor": "1234",
            "comentario": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 400
    db_session.refresh(req)
    assert req.estado == "preparado"
    assert req.recibido_por_id is None


def test_detalle_requisicion_devuelve_timeline_con_hitos(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req = Requisicion(
        folio="REQ-0014",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="entregada",
        justificacion="Timeline completo",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        delivered_to="Jaime Campos",
        delivery_result="completa",
    )
    db_session.add(req)
    db_session.commit()
    db_session.refresh(req)

    login(client, "user.ops", "pass123")
    response = client.get(f"/api/requisiciones/{req.id}")
    assert response.status_code == 200
    data = response.json()
    timeline = data.get("timeline", [])

    eventos = [item.get("evento") for item in timeline]
    assert "Requisicion creada" in eventos
    assert "Requisicion aprobada" in eventos
    assert "Preparacion/entrega de bodega" in eventos
    assert "Recibido" in eventos


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
    assert "REQ-0102" not in html
    assert "REQ-0103" not in html
    assert "REQ-0104" not in html
    assert "pendiente de aprobar" in html


def test_logistica_ve_todas_las_requisiciones_pero_no_aprueba(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    logistica = db_session.query(Usuario).filter(Usuario.username == "logistica.1").first()

    req_1 = Requisicion(
        folio="REQ-AUDIT-01",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="pendiente",
        justificacion="Pendiente visible a logistica",
    )
    req_2 = Requisicion(
        folio="REQ-AUDIT-02",
        solicitante_id=aprobador.id,
        departamento="Operaciones",
        estado="liquidada",
        justificacion="Liquidada visible a logistica",
    )
    req_3 = Requisicion(
        folio="REQ-AUDIT-03",
        solicitante_id=logistica.id,
        departamento="Admon",
        estado="pendiente",
        justificacion="Propia de logistica",
    )
    db_session.add_all([req_1, req_2, req_3])
    db_session.commit()

    login(client, "logistica.1", "pass123")
    response = client.get("/mis-requisiciones")
    assert response.status_code == 200
    html = response.text
    assert "Mis Requisiciones" in html
    assert "REQ-AUDIT-03" in html
    assert "REQ-AUDIT-01" not in html
    assert "REQ-AUDIT-02" not in html

    response_todas = client.get("/todas-requisiciones")
    assert response_todas.status_code == 200
    html_todas = response_todas.text
    assert "Todas las Requisiciones" in html_todas
    assert "REQ-AUDIT-01" in html_todas
    assert "REQ-AUDIT-02" in html_todas
    assert "REQ-AUDIT-03" in html_todas
    assert "Usuario Ops" in html_todas
    assert "Aprobador Ops" in html_todas

    aprobar = client.get("/aprobar")
    assert aprobar.status_code == 403


def test_todas_requisiciones_permita_filtrar_por_estado(client: TestClient, db_session: Session):
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
    response = client.get("/todas-requisiciones?estado=rechazada")
    assert response.status_code == 200
    assert "REQ-0202" in response.text
    assert "REQ-0201" not in response.text


def test_todas_requisiciones_permita_buscar_por_motivo_receptor_actor_y_prokey(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    jefe_bodega = db_session.query(Usuario).filter(Usuario.username == "jefe.bodega").first()

    req = Requisicion(
        folio="REQ-0203",
        solicitante_id=user.id,
        receptor_designado_id=jefe_bodega.id,
        departamento="Operaciones",
        estado="liquidada_en_prokey",
        motivo_requisicion="Queja de ultima hora",
        justificacion="Busqueda ampliada",
        prokey_ref="PK-7788",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        liquidated_by=jefe_bodega.id,
        liquidated_at=datetime.now(),
        prokey_liquidada_por=aprobador.id,
        prokey_liquidada_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()

    login(client, "aprob.ops", "pass123")

    response_motivo = client.get("/todas-requisiciones?q=Queja")
    assert response_motivo.status_code == 200
    assert "REQ-0203" in response_motivo.text

    response_receptor = client.get("/todas-requisiciones?q=Jefe")
    assert response_receptor.status_code == 200
    assert "REQ-0203" in response_receptor.text

    response_actor = client.get("/todas-requisiciones?q=Aprobador")
    assert response_actor.status_code == 200
    assert "REQ-0203" in response_actor.text

    response_prokey = client.get("/todas-requisiciones?q=PK-7788")
    assert response_prokey.status_code == 200
    assert "REQ-0203" in response_prokey.text


def test_bodega_puede_ver_todas_las_requisiciones(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-BOD-TODAS-1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="pendiente",
                justificacion="Pendiente visible para bodega",
            ),
            Requisicion(
                folio="REQ-BOD-TODAS-2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada_en_prokey",
                justificacion="Liquidada visible para bodega",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
        ]
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/todas-requisiciones")

    assert response.status_code == 200
    html = response.text
    assert "Todas las Requisiciones" in html
    assert "REQ-BOD-TODAS-1" in html
    assert "REQ-BOD-TODAS-2" in html


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
        estado="no_entregada",
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


def test_bodega_default_usa_vista_pendientes_y_selector_de_etapa(client: TestClient):
    login(client, "bodega.1", "pass123")
    response = client.get("/bodega")

    assert response.status_code == 200
    html = response.text
    assert "Pendientes + Historial" not in html
    assert 'option value="pendientes" selected' in html
    assert 'name="etapa"' in html
    assert "Aprobadas" in html
    assert "Preparadas" in html
    assert "Entregadas pendientes de liquidar" in html


def test_bodega_puede_filtrar_pendientes_por_etapa(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-BOD-ETAPA-1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Solo aprobada",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-BOD-ETAPA-2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="preparado",
                justificacion="Solo preparada",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                prepared_at=datetime.now(),
            ),
        ]
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/bodega?vista=pendientes&etapa=preparado")

    assert response.status_code == 200
    html = response.text
    assert "REQ-BOD-ETAPA-2" in html
    assert "REQ-BOD-ETAPA-1" not in html


def test_bodega_puede_filtrar_historial_por_etapa_no_entregada(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-BOD-HET-1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="no_entregada",
                justificacion="No entregada historial",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
                delivery_result="no_entregada",
            ),
            Requisicion(
                folio="REQ-BOD-HET-2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="liquidada",
                justificacion="Liquidada historial",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
                delivered_by=bodega.id,
                delivered_at=datetime.now(),
                liquidated_by=bodega.id,
                liquidated_at=datetime.now(),
            ),
        ]
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/bodega?vista=historial&etapa=no_entregada")

    assert response.status_code == 200
    html = response.text
    assert "REQ-BOD-HET-1" in html
    assert "REQ-BOD-HET-2" not in html
    assert "No entregadas" in html
    assert 'option value="pendiente_prokey"' not in html
    assert 'option value="finalizada_sin_prokey"' in html


def test_bodega_trata_liquidada_como_pendiente_hasta_prokey(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req_liquidada = Requisicion(
        folio="REQ-BOD-LIQ-1",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="liquidada",
        justificacion="Aun pendiente de Prokey",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        liquidated_by=bodega.id,
        liquidated_at=datetime.now(),
    )
    db_session.add(req_liquidada)
    db_session.commit()

    login(client, "jefe.bodega", "pass123")

    response_pendientes = client.get("/bodega?vista=pendientes")
    assert response_pendientes.status_code == 200
    assert "REQ-BOD-LIQ-1" in response_pendientes.text
    assert "Confirmar en Prokey" in response_pendientes.text

    response_historial = client.get("/bodega?vista=historial")
    assert response_historial.status_code == 200
    assert "REQ-BOD-LIQ-1" not in response_historial.text


def test_bodega_no_muestra_confirmar_en_prokey_si_no_aplica(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req_liquidada = Requisicion(
        folio="REQ-BOD-LIQ-NA-1",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="liquidada",
        justificacion="Todo regreso sin uso",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        liquidated_by=bodega.id,
        liquidated_at=datetime.now(),
        prokey_no_aplica=True,
    )
    db_session.add(req_liquidada)
    db_session.commit()

    login(client, "jefe.bodega", "pass123")

    response = client.get("/bodega?vista=pendientes")
    assert response.status_code == 200
    assert "REQ-BOD-LIQ-NA-1" in response.text
    assert "No Aplica Confirmar en Prokey" in response.text


def test_bodega_expone_departamento_y_fechas_en_filtros(client: TestClient):
    login(client, "bodega.1", "pass123")
    response = client.get("/bodega")

    assert response.status_code == 200
    html = response.text
    assert 'name="departamento"' in html
    assert 'name="fecha_desde"' in html
    assert 'name="fecha_hasta"' in html


def test_bodega_puede_filtrar_por_departamento(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-BOD-DEP-1",
                solicitante_id=user.id,
                departamento="Ventas",
                estado="aprobada",
                justificacion="Filtro ventas",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
            Requisicion(
                folio="REQ-BOD-DEP-2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Filtro operaciones",
                approved_by=aprobador.id,
                approved_at=datetime.now(),
            ),
        ]
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/bodega?departamento=Ventas")

    assert response.status_code == 200
    html = response.text
    assert "REQ-BOD-DEP-1" in html
    assert "REQ-BOD-DEP-2" not in html


def test_bodega_puede_filtrar_por_rango_de_fechas(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    ahora = datetime.now()

    db_session.add_all(
        [
            Requisicion(
                folio="REQ-BOD-FEC-1",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Dentro de rango",
                approved_by=aprobador.id,
                approved_at=ahora,
                created_at=ahora,
            ),
            Requisicion(
                folio="REQ-BOD-FEC-2",
                solicitante_id=user.id,
                departamento="Operaciones",
                estado="aprobada",
                justificacion="Fuera de rango",
                approved_by=aprobador.id,
                approved_at=ahora - timedelta(days=20),
                created_at=ahora - timedelta(days=20),
            ),
        ]
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    fecha_desde = (ahora - timedelta(days=3)).strftime("%Y-%m-%d")
    fecha_hasta = (ahora + timedelta(days=1)).strftime("%Y-%m-%d")
    response = client.get(f"/bodega?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}")

    assert response.status_code == 200
    html = response.text
    assert "REQ-BOD-FEC-1" in html
    assert "REQ-BOD-FEC-2" not in html


def test_bodega_busca_por_receptor_y_actores_operativos(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    jefe_bodega = db_session.query(Usuario).filter(Usuario.username == "jefe.bodega").first()

    req = Requisicion(
        folio="REQ-BOD-BUS-1",
        solicitante_id=user.id,
        receptor_designado_id=jefe_bodega.id,
        departamento="Operaciones",
        estado="liquidada",
        justificacion="Busqueda actor bodega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        delivered_to="Tecnico Uno",
        liquidated_by=bodega.id,
        liquidated_at=datetime.now(),
    )
    db_session.add(req)
    db_session.commit()

    login(client, "bodega.1", "pass123")

    response_receptor = client.get("/bodega?vista=pendientes&q=Bodega Uno")
    assert response_receptor.status_code == 200
    assert "REQ-BOD-BUS-1" in response_receptor.text

    response_actor = client.get("/bodega?vista=pendientes&q=Bodega Auxiliar")
    assert response_actor.status_code == 200
    assert "REQ-BOD-BUS-1" in response_actor.text

    response_aprobador = client.get("/bodega?vista=pendientes&q=Aprobador Uno")
    assert response_aprobador.status_code == 200
    assert "REQ-BOD-BUS-1" in response_aprobador.text


def test_bodega_no_duplica_entregadas_activas_en_historial(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()

    req_entregada = Requisicion(
        folio="REQ-0303",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="entregada",
        justificacion="Pendiente de liquidar",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        delivery_result="completa",
        delivered_to="Juan Perez",
    )
    req_liquidada = Requisicion(
        folio="REQ-0304",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="liquidada",
        justificacion="Ya liquidada",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=bodega.id,
        delivered_at=datetime.now(),
        delivery_result="completa",
        delivered_to="Juan Perez",
        liquidated_by=bodega.id,
        liquidated_at=datetime.now(),
    )
    db_session.add_all([req_entregada, req_liquidada])
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/bodega")
    assert response.status_code == 200
    html = response.text

    assert "Pendientes de Procesar" in html
    assert "Historial" in html
    assert "REQ-0303" in html
    assert "REQ-0304" in html

    response_historial = client.get("/bodega?vista=historial")
    assert response_historial.status_code == 200
    html_historial = response_historial.text
    assert "REQ-0304" not in html_historial
    assert "REQ-0303" not in html_historial


def test_bodega_ve_historial_completo_de_liquidaciones_ajenas(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    admin = db_session.query(Usuario).filter(Usuario.username == "admin.1").first()

    req_finalizada = Requisicion(
        folio="REQ-BOD-HIST-ALL-1",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="finalizada_sin_prokey",
        justificacion="Cierre visible a toda bodega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=admin.id,
        delivered_at=datetime.now(),
        liquidated_by=admin.id,
        liquidated_at=datetime.now(),
        delivery_result="completa",
    )
    req_prokey = Requisicion(
        folio="REQ-BOD-HIST-ALL-2",
        solicitante_id=user.id,
        departamento="Operaciones",
        estado="liquidada_en_prokey",
        justificacion="Prokey visible a toda bodega",
        approved_by=aprobador.id,
        approved_at=datetime.now(),
        delivered_by=admin.id,
        delivered_at=datetime.now(),
        liquidated_by=admin.id,
        liquidated_at=datetime.now(),
        prokey_liquidada_por=admin.id,
        prokey_liquidada_at=datetime.now(),
        delivery_result="completa",
    )
    db_session.add_all([req_finalizada, req_prokey])
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/bodega?vista=historial")

    assert response.status_code == 200
    html = response.text
    assert "REQ-BOD-HIST-ALL-1" in html
    assert "REQ-BOD-HIST-ALL-2" in html


def test_todas_requisiciones_muestra_alerta_sla_en_estado_y_fecha_de_auditoria(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    ahora = datetime.now()

    db_session.add(
        Requisicion(
            folio="REQ-SLA-001",
            solicitante_id=user.id,
            departamento="Operaciones",
            estado="aprobada",
            justificacion="Brecha SLA",
            approved_by=aprobador.id,
            approved_at=ahora - timedelta(hours=49),
            created_at=ahora - timedelta(hours=60),
        )
    )
    db_session.commit()

    login(client, "admin.1", "pass123")
    response = client.get("/todas-requisiciones")

    assert response.status_code == 200
    html = response.text
    assert "Fecha de Creación" in html
    assert "REQ-SLA-001" in html
    assert "row-alert-bg" in html
    assert "badge-danger" in html
    assert "⚠️ SLA &gt; 48h" in html

    row_match = re.search(r'<tr[^>]*class="row-alert-bg"[^>]*>.*?REQ-SLA-001.*?</tr>', html, re.S)
    assert row_match is not None
    row_html = row_match.group(0)
    cells = re.findall(r'<td(?: class="[^"]+")?>(.*?)</td>', row_html, re.S)
    assert len(cells) >= 10
    assert "badge-danger" in cells[1]
    assert "badge-danger" not in cells[6]
    assert "badge-danger" not in cells[7]


def test_bodega_muestra_alerta_sla_en_fecha_clave(client: TestClient, db_session: Session):
    user = db_session.query(Usuario).filter(Usuario.username == "user.ops").first()
    aprobador = db_session.query(Usuario).filter(Usuario.username == "aprob.ops").first()
    bodega = db_session.query(Usuario).filter(Usuario.username == "bodega.1").first()
    ahora = datetime.now()

    db_session.add(
        Requisicion(
            folio="REQ-SLA-002",
            solicitante_id=user.id,
            departamento="Operaciones",
            estado="aprobada",
            justificacion="Brecha SLA bodega",
            approved_by=aprobador.id,
            approved_at=ahora - timedelta(hours=50),
            created_at=ahora - timedelta(hours=60),
        )
    )
    db_session.commit()

    login(client, "bodega.1", "pass123")
    response = client.get("/bodega?vista=pendientes")

    assert response.status_code == 200
    html = response.text
    assert "Pendientes de Procesar" in html
    assert "REQ-SLA-002" in html
    assert "row-alert-bg" in html
    assert "badge-danger" in html
    assert "⚠️ SLA &gt; 48h" in html

    row_match = re.search(r'<tr[^>]*class="row-alert-bg"[^>]*>.*?REQ-SLA-002.*?</tr>', html, re.S)
    assert row_match is not None
    row_html = row_match.group(0)
    cells = re.findall(r'<td(?: class="[^"]+")?>(.*?)</td>', row_html, re.S)
    assert len(cells) >= 9
    assert "badge-danger" in cells[6]
    assert "badge-danger" not in cells[1]
