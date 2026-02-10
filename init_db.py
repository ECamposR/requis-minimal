from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import Base, engine
from app.models import CatalogoItem, Usuario

Base.metadata.create_all(bind=engine)


def seed_users() -> None:
    with Session(engine) as db:
        users = [
            Usuario(
                username="admin",
                password=hash_password("admin123"),
                nombre="Administrador",
                rol="admin",
                departamento="TI",
            ),
            Usuario(
                username="juan.perez",
                password=hash_password("password"),
                nombre="Juan Perez",
                rol="user",
                departamento="Operaciones",
            ),
            Usuario(
                username="carlos.lopez",
                password=hash_password("password"),
                nombre="Carlos Lopez",
                rol="aprobador",
                departamento="Operaciones",
            ),
            Usuario(
                username="jose.bodega",
                password=hash_password("password"),
                nombre="Jose Ramirez",
                rol="bodega",
                departamento="Bodega",
            ),
        ]
        nuevos_usuarios = 0
        for user in users:
            existe = db.query(Usuario).filter(Usuario.username == user.username).first()
            if existe:
                continue
            db.add(user)
            nuevos_usuarios += 1

        catalogo_base = [
            "Cable UTP Cat6",
            "Conector RJ45",
            "Patch cord 2m",
            "Canaleta PVC",
            "Switch 8 puertos",
            "Tornillo 1/4",
            "Guantes de seguridad",
            "Cinta aislante",
        ]
        nuevos_items = 0
        for nombre in catalogo_base:
            existe = db.query(CatalogoItem).filter(CatalogoItem.nombre == nombre).first()
            if existe:
                continue
            db.add(CatalogoItem(nombre=nombre, activo=True))
            nuevos_items += 1

        db.commit()
        print(
            f"Base de datos inicializada/actualizada. "
            f"Usuarios nuevos: {nuevos_usuarios}. "
            f"Items de catalogo nuevos: {nuevos_items}."
        )


if __name__ == "__main__":
    seed_users()
