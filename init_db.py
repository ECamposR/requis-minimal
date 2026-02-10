from sqlalchemy.orm import Session

from app.auth import hash_password
from app.database import Base, engine
from app.models import Usuario

Base.metadata.create_all(bind=engine)


def seed_users() -> None:
    with Session(engine) as db:
        existing = db.query(Usuario).count()
        if existing > 0:
            print("Base de datos ya inicializada, no se insertan usuarios de ejemplo.")
            return

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
        db.add_all(users)
        db.commit()
        print("Base de datos inicializada con usuarios de prueba.")


if __name__ == "__main__":
    seed_users()
