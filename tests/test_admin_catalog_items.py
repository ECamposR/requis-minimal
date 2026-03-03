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


def test_admin_import_catalog_csv_crea_y_reactiva_items():
    client, db, engine = _build_client()
    try:
        # Item existente inactivo para validar reactivacion por import
        existente = db.query(CatalogoItem).filter(CatalogoItem.nombre == "Cable UTP Cat6").first()
        existente.activo = False
        db.commit()

        _login(client, "admin", "admin123")
        csv_data = "nombre\nCable UTP Cat6\nConector RJ45\nConector RJ45\n"
        response = client.post(
            "/admin/catalogo-items/importar",
            files={"archivo": ("catalogo.csv", csv_data.encode("utf-8"), "text/csv")},
            data={"activar_importados": "on"},
            follow_redirects=False,
        )
        assert response.status_code == 303

        cable = db.query(CatalogoItem).filter(CatalogoItem.nombre == "Cable UTP Cat6").first()
        conector = db.query(CatalogoItem).filter(CatalogoItem.nombre == "Conector RJ45").first()
        assert cable is not None
        assert cable.activo is True
        assert conector is not None
        assert conector.activo is True
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


def test_admin_catalog_busqueda_por_q_case_insensitive():
    client, db, engine = _build_client()
    try:
        db.add_all(
            [
                CatalogoItem(nombre="MOPA MOD 24", activo=True),
                CatalogoItem(nombre="ALFOMBRA 2X3", activo=True),
                CatalogoItem(nombre="SPRAY CITRUS", activo=True),
            ]
        )
        db.commit()

        _login(client, "admin", "admin123")

        all_resp = client.get("/admin/catalogo-items")
        assert all_resp.status_code == 200
        html = all_resp.text
        assert "MOPA MOD 24" in html
        assert "ALFOMBRA 2X3" in html
        assert "SPRAY CITRUS" in html

        mopa_resp = client.get("/admin/catalogo-items?q=mopa")
        assert mopa_resp.status_code == 200
        assert 'value="mopa"' in mopa_resp.text
        assert "MOPA MOD 24" in mopa_resp.text
        assert "ALFOMBRA 2X3" not in mopa_resp.text
        assert "SPRAY CITRUS" not in mopa_resp.text

        spray_resp = client.get("/admin/catalogo-items?q=sPrAy")
        assert spray_resp.status_code == 200
        assert "SPRAY CITRUS" in spray_resp.text
        assert "MOPA MOD 24" not in spray_resp.text
        assert "ALFOMBRA 2X3" not in spray_resp.text
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


def test_admin_puede_borrar_todo_el_catalogo_con_doble_confirmacion():
    client, db, engine = _build_client()
    try:
        db.add_all(
            [
                CatalogoItem(nombre="MOPA MOD 24", activo=True),
                CatalogoItem(nombre="SPRAY CITRUS", activo=True),
            ]
        )
        db.commit()

        _login(client, "admin", "admin123")
        response = client.post(
            "/admin/catalogo-items/eliminar-todos",
            data={"confirmacion_texto": "BORRAR CATALOGO", "confirmacion_check": "on"},
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert db.query(CatalogoItem).count() == 0
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


def test_admin_no_puede_borrar_todo_el_catalogo_sin_doble_confirmacion():
    client, db, engine = _build_client()
    try:
        db.add(CatalogoItem(nombre="ALFOMBRA 2X3", activo=True))
        db.commit()

        _login(client, "admin", "admin123")
        response = client.post(
            "/admin/catalogo-items/eliminar-todos",
            data={"confirmacion_texto": "BORRAR", "confirmacion_check": "on"},
            follow_redirects=False,
        )

        assert response.status_code == 303
        assert db.query(CatalogoItem).count() > 0
    finally:
        client.close()
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()
