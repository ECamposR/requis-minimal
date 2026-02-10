from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import hash_password
from app.database import get_db
from app.main import app
from app.models import Base, CatalogoItem, Usuario

TEST_DB_URL = "sqlite:///./test_admin_catalog_items.db"


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
                CatalogoItem(nombre="Cable UTP Cat6", activo=True),
            ]
        )
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


def test_admin_catalog_item_crud_flow():
    client, db, engine = _build_client()
    try:
        _login(client, "admin", "admin123")

        create_resp = client.post(
            "/admin/catalogo-items",
            data={"nombre": "Canaleta PVC", "activo": "on"},
            follow_redirects=False,
        )
        assert create_resp.status_code == 303

        item = db.query(CatalogoItem).filter(CatalogoItem.nombre == "Canaleta PVC").first()
        assert item is not None
        assert item.activo is True

        edit_resp = client.post(
            f"/admin/catalogo-items/{item.id}/editar",
            data={"nombre": "Canaleta PVC 20x12"},
            follow_redirects=False,
        )
        assert edit_resp.status_code == 303
        db.refresh(item)
        assert item.nombre == "Canaleta PVC 20x12"
        assert item.activo is False

        delete_resp = client.post(
            f"/admin/catalogo-items/{item.id}/eliminar",
            follow_redirects=False,
        )
        assert delete_resp.status_code == 303
        assert db.query(CatalogoItem).filter(CatalogoItem.id == item.id).first() is None
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


def test_non_admin_cannot_access_catalog_admin_routes():
    client, db, engine = _build_client()
    try:
        _login(client, "user.ops", "pass123")
        response = client.get("/admin/catalogo-items")
        assert response.status_code == 403
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()
