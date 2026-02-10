from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.database import get_db
from app.main import app
from app.models import Base, Requisicion, Usuario

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


def test_crear_requisicion(client: TestClient, db_session: Session):
    login(client, "user.ops", "pass123")

    response = client.post(
        "/crear",
        data={
            "departamento": "Operaciones",
            "justificacion": "Material para mantenimiento correctivo",
            "items[0][descripcion]": "Cable UTP Cat6",
            "items[0][cantidad]": "25",
            "items[0][unidad]": "m",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    req = db_session.query(Requisicion).filter(Requisicion.folio == "REQ-0001").first()
    assert req is not None
    assert req.estado == "pendiente"
    assert len(req.items) == 1


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
    response = client.post(f"/aprobar/{req.id}", follow_redirects=False)

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "aprobada"
    assert req.approved_by == aprobador.id
    assert req.approved_at is not None


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
        data={"delivered_to": "Juan Perez"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    db_session.refresh(req)
    assert req.estado == "entregada"
    assert req.delivered_by == bodega.id
    assert req.delivered_to == "Juan Perez"
    assert req.delivered_at is not None
