from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from .models import Item, Requisicion

UNIDAD_POR_DEFECTO = "unidad"


def generar_folio(db: Session) -> str:
    ultimo = db.query(Requisicion).order_by(Requisicion.id.desc()).first()
    numero = (ultimo.id + 1) if ultimo else 1
    return f"REQ-{numero:04d}"


def crear_requisicion_db(
    db: Session,
    solicitante_id: int,
    departamento: str,
    cliente_codigo: str,
    cliente_nombre: str,
    justificacion: str,
) -> Requisicion:
    req = Requisicion(
        folio=generar_folio(db),
        solicitante_id=solicitante_id,
        departamento=departamento,
        cliente_codigo=cliente_codigo,
        cliente_nombre=cliente_nombre,
        estado="pendiente",
        justificacion=justificacion,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


def agregar_item_db(
    db: Session,
    requisicion_id: int,
    descripcion: str,
    cantidad: float,
    unidad: str = UNIDAD_POR_DEFECTO,
) -> Item:
    item = Item(
        requisicion_id=requisicion_id,
        descripcion=descripcion,
        cantidad=float(cantidad),
        unidad=unidad,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def parse_items_from_form(form_data: Any) -> list[dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for key, value in form_data.items():
        if not key.startswith("items["):
            continue
        # Formato esperado: items[0][descripcion]
        first = key.split("[", 1)[1]
        idx = first.split("]", 1)[0]
        field = key.rsplit("[", 1)[1].rstrip("]")
        rows.setdefault(idx, {})[field] = value

    items: list[dict[str, Any]] = []
    for idx in sorted(rows.keys(), key=lambda x: int(x)):
        row = rows[idx]
        if {"descripcion", "cantidad"}.issubset(row.keys()):
            unidad = str(row.get("unidad", UNIDAD_POR_DEFECTO)).strip() or UNIDAD_POR_DEFECTO
            items.append(
                {
                    "descripcion": str(row["descripcion"]).strip(),
                    "cantidad": float(row["cantidad"]),
                    "unidad": unidad,
                }
            )
    return items


def puede_aprobar(requisicion: Requisicion, rol: str, departamento: str) -> bool:
    if requisicion.estado != "pendiente":
        return False
    if rol == "admin":
        return True
    return rol == "aprobador" and requisicion.departamento == departamento


def puede_entregar(requisicion: Requisicion, rol: str) -> bool:
    if rol not in ["bodega", "admin"]:
        return False
    return requisicion.estado == "aprobada"


def transicionar_requisicion(
    db: Session,
    requisicion: Requisicion,
    nuevo_estado: str,
    actor_id: int,
    approval_comment: str | None = None,
    rejection_reason: str | None = None,
    rejection_comment: str | None = None,
    delivered_to: str | None = None,
    delivery_result: str | None = None,
    delivery_comment: str | None = None,
) -> Requisicion:
    if nuevo_estado == "aprobada":
        requisicion.estado = "aprobada"
        requisicion.approved_at = datetime.now()
        requisicion.approved_by = actor_id
        requisicion.approval_comment = approval_comment
    elif nuevo_estado == "rechazada":
        requisicion.estado = "rechazada"
        requisicion.rejected_at = datetime.now()
        requisicion.rejected_by = actor_id
        requisicion.rejection_reason = rejection_reason
        requisicion.rejection_comment = rejection_comment
    elif nuevo_estado == "entregada":
        requisicion.estado = "entregada"
        requisicion.delivered_at = datetime.now()
        requisicion.delivered_by = actor_id
        requisicion.delivered_to = delivered_to
        requisicion.delivery_result = delivery_result or "completa"
        requisicion.delivery_comment = delivery_comment
    else:
        raise ValueError("Estado no soportado")

    db.commit()
    db.refresh(requisicion)
    return requisicion
