from datetime import datetime, timezone, timedelta
import json
from typing import Any

# El Salvador es UTC-6 y no observa DST. Offset fijo para independizar
# la app de la configuración de zona horaria del servidor/contenedor.
_TZ_SV = timezone(timedelta(hours=-6))


def now_sv() -> datetime:
    """Retorna la hora actual de El Salvador (UTC-6) como datetime naive."""
    return datetime.now(_TZ_SV).replace(tzinfo=None)

from sqlalchemy.orm import Session

from .models import Item, Requisicion, Usuario

UNIDAD_POR_DEFECTO = "unidad"


def calcular_retorno_esperado(
    mode: str | None,
    used: float,
    not_used: float,
    contexto_operacion: str | None = None,
) -> float:
    normalized_mode = str(mode or "RETORNABLE").upper().strip()
    if normalized_mode not in ("RETORNABLE", "CONSUMIBLE"):
        normalized_mode = "RETORNABLE"
    normalized_contexto = str(contexto_operacion or "").strip().lower() or "reposicion"

    # En instalacion inicial, aunque el item sea retornable, solo se espera
    # retorno de lo no usado. Lo instalado por primera vez no debe generar
    # faltante operativo.
    if normalized_mode == "CONSUMIBLE" or normalized_contexto == "instalacion_inicial":
        return not_used
    return used + not_used


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
    cliente_ruta_principal: str,
    motivo_requisicion: str,
    justificacion: str,
    receptor_designado_id: int | None = None,
) -> Requisicion:
    req = Requisicion(
        folio=generar_folio(db),
        solicitante_id=solicitante_id,
        departamento=departamento,
        cliente_codigo=cliente_codigo,
        cliente_nombre=cliente_nombre,
        cliente_ruta_principal=cliente_ruta_principal,
        motivo_requisicion=motivo_requisicion,
        estado="pendiente",
        justificacion=justificacion,
        receptor_designado_id=receptor_designado_id,
        # Evita depender del server_default SQLite (UTC) para mantener hora local consistente.
        created_at=now_sv(),
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
    contexto_operacion: str | None = None,
    es_demo: bool = False,
) -> Item:
    item = Item(
        requisicion_id=requisicion_id,
        descripcion=descripcion,
        cantidad=float(cantidad),
        unidad=unidad,
        contexto_operacion=contexto_operacion,
        es_demo=es_demo,
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
        descripcion = str(row.get("descripcion", "")).strip()
        cantidad_raw = str(row.get("cantidad", "")).strip()

        # Ignore fully empty rows, but fail on partial rows to avoid ambiguous saves.
        if not descripcion and not cantidad_raw:
            continue
        if not descripcion or not cantidad_raw:
            raise ValueError("Cada item debe tener descripcion y cantidad")

        try:
            cantidad = float(cantidad_raw)
        except ValueError as exc:
            raise ValueError("Cantidad de item invalida") from exc
        if cantidad <= 0:
            raise ValueError("Cantidad de item debe ser mayor que cero")

        unidad = str(row.get("unidad", UNIDAD_POR_DEFECTO)).strip() or UNIDAD_POR_DEFECTO
        contexto_operacion_raw = str(row.get("contexto_operacion", "")).strip().lower()
        if contexto_operacion_raw not in ("", "reposicion", "instalacion_inicial"):
            raise ValueError("Contexto de operacion invalido")
        contexto_operacion = contexto_operacion_raw or None
        es_demo_raw = str(form_data.get(f"es_demo_{idx}", "")).strip().lower()
        es_demo = es_demo_raw in ("on", "1", "true", "yes")
        items.append(
            {
                "descripcion": descripcion,
                "cantidad": cantidad,
                "unidad": unidad,
                "contexto_operacion": contexto_operacion,
                "es_demo": es_demo,
            }
        )
    return items


def puede_aprobar(requisicion: Requisicion, rol: str) -> bool:
    if requisicion.estado != "pendiente":
        return False
    return rol in ["admin", "aprobador", "jefe_bodega"]


def puede_entregar(requisicion: Requisicion, rol: str) -> bool:
    if rol not in ["bodega", "admin", "jefe_bodega"]:
        return False
    return requisicion.estado == "preparado"


def puede_preparar(requisicion: Requisicion, rol: str) -> bool:
    if rol not in ["bodega", "admin", "jefe_bodega"]:
        return False
    return requisicion.estado == "aprobada"


def puede_liquidar(requisicion: Requisicion, usuario: Usuario) -> bool:
    """Retorna True solo si la requisición es elegible para liquidación por este usuario."""
    if requisicion.estado != "entregada":
        return False
    if requisicion.delivery_result not in ("completa", "parcial"):
        return False
    if usuario.rol not in ("admin", "bodega", "jefe_bodega"):
        return False
    return True


def calcular_alertas_item(item: Item) -> list[dict[str, Any]]:
    """Calcula alertas para un ítem liquidado. No bloquea por diferencia != 0."""
    alertas: list[dict[str, Any]] = []
    delivered = round(float(item.cantidad_entregada or 0), 4)
    returned = round(float(item.qty_returned_to_warehouse or 0), 4)
    used = round(float(item.qty_used or 0), 4)
    not_used = round(float(item.qty_left_at_client or 0), 4)
    raw_mode = getattr(item, "liquidation_mode", None) or getattr(item, "tipo", None) or "RETORNABLE"
    mode = str(raw_mode).upper().strip()
    if mode not in ("RETORNABLE", "CONSUMIBLE"):
        mode = "RETORNABLE"
    contexto_operacion = str(getattr(item, "contexto_operacion", None) or "").strip().lower() or "reposicion"
    expected_return = calcular_retorno_esperado(mode, used, not_used, contexto_operacion)
    diferencia = expected_return - returned

    if diferencia > 0:
        alertas.append(
            {
                "type": "ALERTA_FALTANTE",
                "severity": "warn",
                "data": {
                    "mode": mode,
                    "expected_return": expected_return,
                    "returned": returned,
                    "diferencia": diferencia,
                },
            }
        )
    if diferencia < 0:
        alertas.append(
            {
                "type": "ALERTA_SOBRANTE",
                "severity": "warn",
                "data": {
                    "mode": mode,
                    "expected_return": expected_return,
                    "returned": returned,
                    "diferencia": diferencia,
                },
            }
        )
    if returned > delivered:
        alertas.append(
            {
                "type": "ALERTA_RETORNO_EXTRA",
                "severity": "high",
                "data": {"returned": returned, "delivered": delivered},
            }
        )
    if (
        mode == "RETORNABLE"
        and contexto_operacion != "instalacion_inicial"
        and delivered > 0
        and returned < delivered
    ):
        alertas.append(
            {
                "type": "ALERTA_RETORNO_INCOMPLETO",
                "severity": "warn",
                "data": {
                    "delivered": delivered,
                    "returned": returned,
                    "missing": delivered - returned,
                    "delta": delivered - returned,
                    "contexto_operacion": contexto_operacion,
                },
            }
        )
    total_out = used + not_used
    if total_out > delivered:
        alertas.append(
            {
                "type": "ALERTA_SALIDA_SIN_SOPORTE",
                "severity": "high",
                "data": {
                    "delivered": delivered,
                    "used": used,
                    "not_used": not_used,
                    "total_out": total_out,
                },
            }
        )

    return alertas


def validar_liquidacion_item(
    delivered: float,
    used: float,
    not_used: float,
    returned: float,
    mode: str,
) -> str | None:
    coverage_total = used + not_used
    if coverage_total != delivered:
        return (
            "Debes distribuir la cantidad entregada entre Usado y No usado. "
            f"Entregado={delivered}, Usado+No usado={coverage_total}"
        )

    if mode == "CONSUMIBLE" and returned != not_used:
        return (
            "En consumible, Regresa debe ser igual a No usado. "
            f"Regresa={returned}, No usado={not_used}"
        )

    return None


def ejecutar_liquidacion(
    db: Session,
    requisicion: Requisicion,
    usuario: Usuario,
    prokey_ref: str | None,
    liquidation_comment: str | None,
    items_data: dict[int, dict[str, Any]],
) -> None:
    """
    Ejecuta la liquidación de una requisición.
    items_data: {item_id: {qty_returned_to_warehouse, qty_used, qty_left_at_client, item_liquidation_note}}
    Requisición debe estar en estado 'entregada'. NO se bloquea por delta != 0.
    """
    if requisicion.estado == "liquidada":
        raise ValueError("Esta requisición ya fue liquidada")

    for item in requisicion.items:
        data = items_data.get(item.id, {})
        qty_returned = round(float(data.get("qty_returned_to_warehouse", 0)), 4)
        qty_used = round(float(data.get("qty_used", 0)), 4)
        qty_not_used = round(float(data.get("qty_left_at_client", 0)), 4)
        delivered = item.cantidad_entregada or 0
        mode = str(data.get("liquidation_mode", "RETORNABLE")).upper()
        if mode not in ("RETORNABLE", "CONSUMIBLE"):
            mode = "RETORNABLE"
        validation_error = validar_liquidacion_item(delivered, qty_used, qty_not_used, qty_returned, mode)
        if validation_error:
            raise ValueError(validation_error)

        item.qty_returned_to_warehouse = qty_returned
        item.qty_used = qty_used
        item.qty_left_at_client = qty_not_used
        item.liquidation_mode = mode
        item.item_liquidation_note = data.get("item_liquidation_note") or None

        alertas = calcular_alertas_item(item)
        item.liquidation_alerts = json.dumps(alertas)

    requisicion.estado = "liquidada"
    requisicion.prokey_ref = prokey_ref or None
    requisicion.liquidation_comment = liquidation_comment or None
    requisicion.liquidated_by = usuario.id
    requisicion.liquidated_at = now_sv()

    db.commit()


def marcar_liquidada_en_prokey(db: Session, req_id: int, usuario_id: int) -> Requisicion:
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    if not req:
        raise ValueError("Requisicion no encontrada")
    if req.estado != "liquidada":
        raise ValueError("Solo se puede confirmar en Prokey una requisicion en estado liquidada")

    req.estado = "liquidada_en_prokey"
    req.prokey_liquidada_at = now_sv()
    req.prokey_liquidada_por = usuario_id
    db.commit()
    db.refresh(req)
    return req


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
    recibido_por_id: int | None = None,
    recibido_at: datetime | None = None,
) -> Requisicion:
    if requisicion.estado == "liquidada_en_prokey":
        raise ValueError("La requisicion ya fue cerrada en Prokey y no admite cambios")

    if nuevo_estado == "aprobada":
        requisicion.estado = "aprobada"
        requisicion.approved_at = now_sv()
        requisicion.approved_by = actor_id
        requisicion.approval_comment = approval_comment
    elif nuevo_estado == "preparado":
        requisicion.estado = "preparado"
        requisicion.prepared_at = now_sv()
        requisicion.prepared_by = actor_id
    elif nuevo_estado == "rechazada":
        requisicion.estado = "rechazada"
        requisicion.rejected_at = now_sv()
        requisicion.rejected_by = actor_id
        requisicion.rejection_reason = rejection_reason
        requisicion.rejection_comment = rejection_comment
    elif nuevo_estado == "entregada":
        requisicion.estado = "entregada"
        requisicion.delivered_at = now_sv()
        requisicion.delivered_by = actor_id
        requisicion.delivered_to = delivered_to
        requisicion.recibido_por_id = recibido_por_id
        requisicion.recibido_at = recibido_at
        requisicion.delivery_result = delivery_result or "completa"
        requisicion.delivery_comment = delivery_comment
    elif nuevo_estado == "liquidada":
        requisicion.estado = "liquidada"
    else:
        raise ValueError("Estado no soportado")

    db.commit()
    db.refresh(requisicion)
    return requisicion
