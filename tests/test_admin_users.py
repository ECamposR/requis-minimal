from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.database import get_db
from app.main import app
from app.models import Base, CatalogoItem, Requisicion, Usuario

TEST_DB_URL = "sqlite:///./test_admin_users.db"


def _login(client: TestClient, username: str, password: str) -> None:
    response = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )
    assert response.status_code in [303, 401]


def _build_client():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with Session(engine) as seed_db:
        seed_db.add_all(
            [
                Usuario(
                    username="admin",
                    password=hash_password("admin123"),
                    nombre="Administrador",
                    rol="admin",
                    departamento="TI",
                ),
                Usuario(
                    username="user.ops",
                    password=hash_password("pass123"),
                    nombre="Usuario Ops",
                    rol="user",
                    departamento="Operaciones",
                ),
            ]
        )
        seed_db.add(CatalogoItem(nombre="Cable UTP Cat6", activo=True))
        seed_db.commit()

    db = TestingSessionLocal()

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    return client, db, engine


def test_admin_user_crud_flow():
    client, db, engine = _build_client()
    try:
        _login(client, "admin", "admin123")

        create_resp = client.post(
            "/admin/usuarios",
            data={
                "username": "nuevo.user",
                "nombre": "Nuevo Usuario",
                "rol": "aprobador",
                "departamento": "Operaciones",
                "password": "nuevo123",
            },
            follow_redirects=False,
        )
        assert create_resp.status_code == 303

        nuevo = db.query(Usuario).filter(Usuario.username == "nuevo.user").first()
        assert nuevo is not None
        assert nuevo.rol == "aprobador"

        edit_resp = client.post(
            f"/admin/usuarios/{nuevo.id}/editar",
            data={
                "username": "nuevo.user",
                "nombre": "Nuevo Editado",
                "rol": "bodega",
                "departamento": "Bodega",
                "password": "",
            },
            follow_redirects=False,
        )
        assert edit_resp.status_code == 303
        db.refresh(nuevo)
        assert nuevo.nombre == "Nuevo Editado"
        assert nuevo.rol == "bodega"

        delete_resp = client.post(
            f"/admin/usuarios/{nuevo.id}/eliminar",
            follow_redirects=False,
        )
        assert delete_resp.status_code == 303
        assert db.query(Usuario).filter(Usuario.id == nuevo.id).first() is None
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


def test_non_admin_cannot_access_user_admin_routes():
    client, db, engine = _build_client()
    try:
        _login(client, "user.ops", "pass123")
        response = client.get("/admin/usuarios")
        assert response.status_code == 403
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


def test_admin_no_puede_eliminar_usuario_con_historial():
    client, db, engine = _build_client()
    try:
        _login(client, "admin", "admin123")

        admin = db.query(Usuario).filter(Usuario.username == "admin").first()
        user_ops = db.query(Usuario).filter(Usuario.username == "user.ops").first()

        req = Requisicion(
            folio="REQ-9999",
            solicitante_id=user_ops.id,
            departamento="Operaciones",
            estado="aprobada",
            justificacion="Historial de prueba",
            approved_by=admin.id,
            approved_at=datetime.now(),
        )
        db.add(req)
        db.commit()

        delete_resp = client.post(
            f"/admin/usuarios/{user_ops.id}/eliminar",
            follow_redirects=False,
        )
        assert delete_resp.status_code == 303

        sigue = db.query(Usuario).filter(Usuario.id == user_ops.id).first()
        assert sigue is not None
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


def test_admin_puede_desactivar_y_reactivar_usuario():
    client, db, engine = _build_client()
    try:
        _login(client, "admin", "admin123")
        user_ops = db.query(Usuario).filter(Usuario.username == "user.ops").first()

        desactivar = client.post(
            f"/admin/usuarios/{user_ops.id}/desactivar",
            follow_redirects=False,
        )
        assert desactivar.status_code == 303
        db.refresh(user_ops)
        assert user_ops.activo is False

        reactivar = client.post(
            f"/admin/usuarios/{user_ops.id}/reactivar",
            follow_redirects=False,
        )
        assert reactivar.status_code == 303
        db.refresh(user_ops)
        assert user_ops.activo is True
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


def test_usuario_inactivo_no_puede_login():
    client, db, engine = _build_client()
    try:
        user_ops = db.query(Usuario).filter(Usuario.username == "user.ops").first()
        user_ops.activo = False
        db.commit()

        response = client.post(
            "/login",
            data={"username": "user.ops", "password": "pass123"},
            follow_redirects=False,
        )
        assert response.status_code == 401
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()
