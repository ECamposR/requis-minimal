import os
import re
from io import BytesIO
import csv
from datetime import datetime, timedelta

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload
from starlette.middleware.sessions import SessionMiddleware
from urllib.parse import quote_plus

from .auth import authenticate_user, get_current_user, login_user, logout_user
from .crud import (
    agregar_item_db,
    crear_requisicion_db,
    parse_items_from_form,
    puede_aprobar,
    puede_entregar,
    transicionar_requisicion,
)
from .database import get_db, run_migrations
from .models import CatalogoItem, Requisicion, Usuario

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

app = FastAPI(title=os.getenv("APP_NAME", "Sistema de Requisiciones MVP"))
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DEPARTAMENTOS_VALIDOS = ["Cuentas", "Ventas", "Bodega", "Admon", "Logistica"]
CATALOGO_HEADERS = {"nombre", "item", "producto", "descripcion"}


@app.on_event("startup")
def startup_migrations() -> None:
    run_migrations()


def normalize_catalog_name(value: str) -> str:
    return " ".join(value.split()).strip().casefold()


def _extract_names_from_rows(rows: list[list[str]]) -> list[str]:
    if not rows:
        return []
    header_idx = -1
    first = [c.strip().casefold() for c in rows[0]]
    for idx, value in enumerate(first):
        if value in CATALOGO_HEADERS:
            header_idx = idx
            break

    start = 1 if header_idx >= 0 else 0
    name_idx = header_idx if header_idx >= 0 else 0

    names: list[str] = []
    seen: set[str] = set()
    for row in rows[start:]:
        if name_idx >= len(row):
            continue
        name = " ".join(str(row[name_idx]).split()).strip()
        if len(name) < 2:
            continue
        key = normalize_catalog_name(name)
        if key in seen:
            continue
        seen.add(key)
        names.append(name)
    return names


def _parse_catalog_csv(raw: bytes) -> list[str]:
    text = ""
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if not text:
        raise ValueError("No se pudo leer el CSV")
    reader = csv.reader(text.splitlines())
    rows = [[str(cell).strip() for cell in row] for row in reader if any(str(cell).strip() for cell in row)]
    return _extract_names_from_rows(rows)


def _parse_catalog_xlsx(raw: bytes) -> list[str]:
    try:
        from openpyxl import load_workbook
    except ModuleNotFoundError as exc:
        raise ValueError("Falta dependencia openpyxl para importar XLSX") from exc

    wb = load_workbook(filename=BytesIO(raw), read_only=True, data_only=True)
    try:
        ws = wb.active
        rows: list[list[str]] = []
        for row in ws.iter_rows(values_only=True):
            values = ["" if value is None else str(value).strip() for value in row]
            if any(values):
                rows.append(values)
        return _extract_names_from_rows(rows)
    finally:
        wb.close()


def template_context(request: Request, current_user: Usuario | None = None, **kwargs: object) -> dict[str, object]:
    return {"request": request, "current_user": current_user, **kwargs}


def redirect_with_message(url: str, message: str, level: str = "success") -> RedirectResponse:
    safe_msg = quote_plus(message)
    safe_level = quote_plus(level)
    sep = "&" if "?" in url else "?"
    return RedirectResponse(url=f"{url}{sep}msg={safe_msg}&type={safe_level}", status_code=303)


def ensure_admin(current_user: Usuario) -> None:
    if current_user.rol != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/login")
def login_form(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse("login.html", template_context(request))


@app.post("/login")
def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, username=username, password=password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            template_context(request, error="Credenciales incorrectas"),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    login_user(request, user)
    return RedirectResponse(url="/", status_code=303)


@app.post("/logout")
def logout(request: Request):
    logout_user(request)
    return RedirectResponse(url="/login", status_code=303)


@app.get("/")
def home(request: Request, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    mis_requisiciones_query = db.query(Requisicion).filter(Requisicion.solicitante_id == current_user.id)
    ahora = datetime.now()
    inicio_mes = datetime(ahora.year, ahora.month, 1)
    hace_30_dias = ahora - timedelta(days=30)

    mis_requisiciones = mis_requisiciones_query.count()
    mis_pendientes = mis_requisiciones_query.filter(Requisicion.estado == "pendiente").count()
    mis_aprobadas = mis_requisiciones_query.filter(Requisicion.estado == "aprobada").count()
    mis_rechazadas = mis_requisiciones_query.filter(Requisicion.estado == "rechazada").count()
    mis_entregadas = mis_requisiciones_query.filter(Requisicion.estado == "entregada").count()
    mis_creadas_mes = mis_requisiciones_query.filter(Requisicion.created_at >= inicio_mes).count()
    mis_entregadas_30d = mis_requisiciones_query.filter(
        Requisicion.estado == "entregada", Requisicion.delivered_at >= hace_30_dias
    ).count()
    pendientes_aprobar = 0
    if current_user.rol in ["aprobador", "admin"]:
        pendientes_aprobar = db.query(Requisicion).filter(Requisicion.estado == "pendiente").count()
    pendientes_aprobar_panel = pendientes_aprobar if current_user.rol in ["aprobador", "admin"] else mis_pendientes
    mis_aprobadas_historicas = mis_requisiciones_query.filter(Requisicion.approved_by.isnot(None)).count()
    aprobadas_panel = (
        db.query(Requisicion).filter(Requisicion.approved_by.isnot(None)).count()
        if current_user.rol in ["admin", "aprobador", "bodega"]
        else mis_aprobadas_historicas
    )
    pendientes_bodega = 0
    if current_user.rol in ["bodega", "admin"]:
        pendientes_bodega = db.query(Requisicion).filter(Requisicion.estado == "aprobada").count()
    pendientes_entregar_panel = pendientes_bodega if current_user.rol in ["bodega", "admin"] else aprobadas_panel
    rechazadas_panel = (
        db.query(Requisicion).filter(Requisicion.estado == "rechazada").count()
        if current_user.rol in ["admin", "aprobador", "bodega"]
        else mis_rechazadas
    )
    escala_metricas_home = max(
        1,
        mis_creadas_mes,
        pendientes_aprobar_panel,
        pendientes_entregar_panel,
        rechazadas_panel,
        mis_entregadas_30d,
    )

    return templates.TemplateResponse(
        "home.html",
        template_context(
            request,
            current_user,
            mis_requisiciones=mis_requisiciones,
            mis_pendientes=mis_pendientes,
            mis_aprobadas=mis_aprobadas,
            aprobadas_panel=aprobadas_panel,
            mis_rechazadas=mis_rechazadas,
            mis_entregadas=mis_entregadas,
            mis_creadas_mes=mis_creadas_mes,
            mis_entregadas_30d=mis_entregadas_30d,
            pendientes_aprobar_panel=pendientes_aprobar_panel,
            pendientes_entregar_panel=pendientes_entregar_panel,
            rechazadas_panel=rechazadas_panel,
            escala_metricas_home=escala_metricas_home,
            pendientes_aprobar=pendientes_aprobar,
            pendientes_bodega=pendientes_bodega,
        ),
    )


@app.get("/crear")
def crear_form(request: Request, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    catalogo_items = (
        db.query(CatalogoItem)
        .filter(CatalogoItem.activo.is_(True))
        .order_by(CatalogoItem.nombre.asc())
        .all()
    )
    return templates.TemplateResponse(
        "crear_requisicion.html",
        template_context(request, current_user, catalogo_items=[i.nombre for i in catalogo_items]),
    )


@app.post("/crear")
async def crear(
    request: Request,
    cliente_codigo: str = Form(...),
    cliente_nombre: str = Form(...),
    cliente_ruta_principal: str = Form(...),
    justificacion: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cliente_codigo_limpio = cliente_codigo.strip()
    cliente_nombre_limpio = cliente_nombre.strip()
    cliente_ruta_principal_limpia = cliente_ruta_principal.strip().upper()
    if len(cliente_codigo_limpio) < 2:
        raise HTTPException(status_code=400, detail="Codigo de cliente invalido")
    if len(cliente_nombre_limpio) < 3:
        raise HTTPException(status_code=400, detail="Nombre de cliente invalido")
    if not re.fullmatch(r"[A-Z]{2}\d{2}", cliente_ruta_principal_limpia):
        raise HTTPException(status_code=400, detail="Ruta principal invalida (formato: AA00)")

    req = crear_requisicion_db(
        db=db,
        solicitante_id=current_user.id,
        departamento=current_user.departamento,
        cliente_codigo=cliente_codigo_limpio,
        cliente_nombre=cliente_nombre_limpio,
        cliente_ruta_principal=cliente_ruta_principal_limpia,
        justificacion=justificacion,
    )

    form_data = await request.form()
    try:
        items_data = parse_items_from_form(form_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not items_data:
        raise HTTPException(status_code=400, detail="Debe agregar al menos un item")
    descripciones = [normalize_catalog_name(item["descripcion"]) for item in items_data]
    if len(set(descripciones)) != len(descripciones):
        raise HTTPException(
            status_code=400,
            detail="No se permiten items duplicados en una misma requisicion",
        )

    catalogo_habilitado = {
        normalize_catalog_name(row.nombre): row.nombre
        for row in db.query(CatalogoItem.nombre).filter(CatalogoItem.activo.is_(True)).all()
    }
    if not catalogo_habilitado:
        raise HTTPException(status_code=400, detail="No hay items activos en catalogo")

    for item_data in items_data:
        descripcion_normalizada = normalize_catalog_name(item_data["descripcion"])
        if descripcion_normalizada not in catalogo_habilitado:
            raise HTTPException(status_code=400, detail="Item no permitido en catalogo")
        item_data["descripcion"] = catalogo_habilitado[descripcion_normalizada]
        agregar_item_db(db, req.id, **item_data)

    return redirect_with_message("/mis-requisiciones", "Requisicion creada", "success")


@app.get("/mis-requisiciones")
def mis_requisiciones(
    request: Request, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)
):
    requisiciones = (
        db.query(Requisicion)
        .filter(Requisicion.solicitante_id == current_user.id)
        .order_by(Requisicion.created_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        "mis_requisiciones.html", template_context(request, current_user, requisiciones=requisiciones)
    )


@app.post("/mis-requisiciones/{req_id}/eliminar")
def eliminar_mi_requisicion(
    req_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = (
        db.query(Requisicion)
        .filter(Requisicion.id == req_id, Requisicion.solicitante_id == current_user.id)
        .first()
    )
    if not req:
        return redirect_with_message("/mis-requisiciones", "Requisicion no encontrada", "error")
    if req.estado != "pendiente":
        return redirect_with_message(
            "/mis-requisiciones",
            "Solo puedes eliminar requisiciones en pendiente de aprobar",
            "error",
        )

    db.delete(req)
    db.commit()
    return redirect_with_message("/mis-requisiciones", "Requisicion eliminada", "warning")


@app.get("/aprobar")
def aprobar_view(request: Request, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.rol not in ["aprobador", "admin"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    q = request.query_params.get("q", "").strip()
    estado = request.query_params.get("estado", "todos").strip().lower()
    departamento = request.query_params.get("departamento", "todos").strip()

    alias_estado = {
        "pendiente_aprobar": "pendiente",
        "pendiente_entregar": "aprobada",
    }
    estado_real = alias_estado.get(estado, estado)
    estados_validos = {"pendiente", "aprobada", "rechazada", "entregada", "liquidada"}
    query = (
        db.query(Requisicion)
        .options(
            joinedload(Requisicion.solicitante),
            joinedload(Requisicion.aprobador),
            joinedload(Requisicion.rechazador),
            joinedload(Requisicion.entregador),
        )
        .filter(Requisicion.estado.in_(["pendiente", "aprobada", "rechazada", "entregada", "liquidada"]))
    )
    if estado_real in estados_validos:
        query = query.filter(Requisicion.estado == estado_real)
    if departamento and departamento != "todos":
        query = query.filter(Requisicion.departamento == departamento)
    if q:
        patron = f"%{q}%"
        query = query.filter(
            or_(
                Requisicion.folio.ilike(patron),
                Requisicion.departamento.ilike(patron),
                Requisicion.justificacion.ilike(patron),
                Requisicion.cliente_codigo.ilike(patron),
                Requisicion.cliente_nombre.ilike(patron),
                Requisicion.solicitante.has(Usuario.nombre.ilike(patron)),
            )
        )

    requisiciones = query.order_by(Requisicion.created_at.desc()).all()
    departamentos = [
        row[0]
        for row in db.query(Requisicion.departamento).distinct().order_by(Requisicion.departamento.asc()).all()
        if row[0]
    ]
    return templates.TemplateResponse(
        "aprobar.html",
        template_context(
            request,
            current_user,
            requisiciones=requisiciones,
            filtro_q=q,
            filtro_estado=estado,
            filtro_departamento=departamento,
            departamentos=departamentos,
        ),
    )


@app.get("/aprobar/{req_id}/gestionar")
def aprobar_gestionar(
    req_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.rol not in ["aprobador", "admin"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    req = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.solicitante), joinedload(Requisicion.items))
        .filter(Requisicion.id == req_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if req.estado != "pendiente":
        return redirect_with_message("/aprobar", "Solo puedes gestionar requisiciones pendientes", "warning")
    if not puede_aprobar(req, current_user.rol):
        raise HTTPException(status_code=403, detail="No autorizado")

    return templates.TemplateResponse(
        "aprobar_gestionar.html",
        template_context(request, current_user, req=req),
    )


@app.post("/aprobar/{req_id}")
def aprobar(
    req_id: int,
    comentario: str = Form(""),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if not puede_aprobar(req, current_user.rol):
        raise HTTPException(status_code=403, detail="No autorizado")

    transicionar_requisicion(
        db,
        req,
        nuevo_estado="aprobada",
        actor_id=current_user.id,
        approval_comment=comentario.strip() or None,
    )
    return redirect_with_message("/aprobar", "Requisicion aprobada", "success")


@app.post("/rechazar/{req_id}")
def rechazar(
    req_id: int,
    razon: str = Form(...),
    comentario: str = Form(""),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if not puede_aprobar(req, current_user.rol):
        raise HTTPException(status_code=403, detail="No autorizado")

    razon_limpia = razon.strip()
    if len(razon_limpia) < 3:
        raise HTTPException(status_code=400, detail="La razon debe tener al menos 3 caracteres")

    transicionar_requisicion(
        db,
        req,
        nuevo_estado="rechazada",
        actor_id=current_user.id,
        rejection_reason=razon_limpia,
        rejection_comment=comentario.strip() or None,
    )
    return redirect_with_message("/aprobar", "Requisicion rechazada", "warning")


@app.get("/bodega")
def bodega_view(request: Request, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.rol not in ["bodega", "admin"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    q = request.query_params.get("q", "").strip()
    vista = request.query_params.get("vista", "todos").strip().lower()
    resultado = request.query_params.get("resultado", "todos").strip().lower()

    pendientes_query = (
        db.query(Requisicion)
        .options(
            joinedload(Requisicion.solicitante),
            joinedload(Requisicion.aprobador),
        )
        .filter(Requisicion.estado == "aprobada")
    )
    if q:
        patron = f"%{q}%"
        pendientes_query = pendientes_query.filter(
            or_(
                Requisicion.folio.ilike(patron),
                Requisicion.departamento.ilike(patron),
                Requisicion.justificacion.ilike(patron),
                Requisicion.cliente_codigo.ilike(patron),
                Requisicion.cliente_nombre.ilike(patron),
                Requisicion.solicitante.has(Usuario.nombre.ilike(patron)),
            )
        )

    pendientes_entrega = pendientes_query.order_by(Requisicion.approved_at.asc(), Requisicion.created_at.asc()).all()

    historial_query = (
        db.query(Requisicion)
        .options(
            joinedload(Requisicion.solicitante),
            joinedload(Requisicion.aprobador),
            joinedload(Requisicion.entregador),
        )
        .filter(Requisicion.estado == "entregada")
    )
    if current_user.rol == "bodega":
        historial_query = historial_query.filter(Requisicion.delivered_by == current_user.id)
    if resultado in {"completa", "parcial", "no_entregada"}:
        historial_query = historial_query.filter(Requisicion.delivery_result == resultado)
    if q:
        patron = f"%{q}%"
        historial_query = historial_query.filter(
            or_(
                Requisicion.folio.ilike(patron),
                Requisicion.departamento.ilike(patron),
                Requisicion.justificacion.ilike(patron),
                Requisicion.cliente_codigo.ilike(patron),
                Requisicion.cliente_nombre.ilike(patron),
                Requisicion.solicitante.has(Usuario.nombre.ilike(patron)),
                Requisicion.delivered_to.ilike(patron),
            )
        )

    historial_entregadas = historial_query.order_by(Requisicion.delivered_at.desc()).all()

    return templates.TemplateResponse(
        "bodega.html",
        template_context(
            request,
            current_user,
            pendientes_entrega=pendientes_entrega,
            historial_entregadas=historial_entregadas,
            filtro_q=q,
            filtro_vista=vista,
            filtro_resultado=resultado,
        ),
    )


@app.get("/bodega/{req_id}/gestionar")
def bodega_gestionar(
    req_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.rol not in ["bodega", "admin"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    req = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.solicitante), joinedload(Requisicion.aprobador), joinedload(Requisicion.items))
        .filter(Requisicion.id == req_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if req.estado != "aprobada":
        return redirect_with_message("/bodega", "Solo puedes gestionar requisiciones aprobadas", "warning")
    if not puede_entregar(req, current_user.rol):
        raise HTTPException(status_code=403, detail="No autorizado")

    return templates.TemplateResponse(
        "bodega_gestionar.html",
        template_context(request, current_user, req=req),
    )


@app.post("/entregar/{req_id}")
def entregar(
    req_id: int,
    delivered_to: str = Form(""),
    resultado: str = Form("completa"),
    comentario: str = Form(""),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if not puede_entregar(req, current_user.rol):
        raise HTTPException(status_code=403, detail="No autorizado")

    resultados_validos = {"completa", "parcial", "no_entregada"}
    if resultado not in resultados_validos:
        return redirect_with_message("/bodega", "Resultado de entrega invalido", "error")

    if resultado == "parcial":
        return RedirectResponse(url=f"/entregar/{req_id}/parcial", status_code=303)

    delivered_to_limpio = delivered_to.strip()
    comentario_limpio = comentario.strip()
    if resultado in {"completa", "parcial"} and len(delivered_to_limpio) < 3:
        return redirect_with_message(
            "/bodega",
            "Debes indicar quien recibe (minimo 3 caracteres)",
            "error",
        )
    if resultado in {"parcial", "no_entregada"} and len(comentario_limpio) < 5:
        return redirect_with_message(
            "/bodega",
            "Para entrega parcial o no entregada, agrega comentario (minimo 5 caracteres)",
            "error",
        )

    transicionar_requisicion(
        db,
        req,
        nuevo_estado="entregada",
        actor_id=current_user.id,
        delivered_to=delivered_to_limpio or None,
        delivery_result=resultado,
        delivery_comment=comentario_limpio or None,
    )
    if resultado == "completa":
        for item in req.items:
            item.cantidad_entregada = item.cantidad
        db.commit()
    if resultado == "no_entregada":
        for item in req.items:
            item.cantidad_entregada = 0
        db.commit()
    mensajes = {
        "completa": ("Requisicion marcada como entrega completa", "success"),
        "parcial": ("Requisicion marcada como entrega parcial", "warning"),
        "no_entregada": ("Requisicion registrada como no entregada", "warning"),
    }
    msg, tipo = mensajes[resultado]
    return redirect_with_message("/bodega", msg, tipo)


@app.get("/entregar/{req_id}/parcial")
def entrega_parcial_form(
    req_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.items), joinedload(Requisicion.solicitante), joinedload(Requisicion.aprobador))
        .filter(Requisicion.id == req_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if not puede_entregar(req, current_user.rol):
        raise HTTPException(status_code=403, detail="No autorizado")

    return templates.TemplateResponse(
        "bodega_entrega_parcial.html",
        template_context(request, current_user, req=req),
    )


@app.post("/entregar/{req_id}/parcial")
async def entrega_parcial_guardar(
    req_id: int,
    request: Request,
    delivered_to: str = Form(...),
    comentario: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.items))
        .filter(Requisicion.id == req_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if not puede_entregar(req, current_user.rol):
        raise HTTPException(status_code=403, detail="No autorizado")

    delivered_to_limpio = delivered_to.strip()
    comentario_limpio = comentario.strip()
    if len(delivered_to_limpio) < 3:
        raise HTTPException(status_code=400, detail="El nombre de quien recibe debe tener al menos 3 caracteres")
    if len(comentario_limpio) < 5:
        raise HTTPException(status_code=400, detail="Comentario minimo de 5 caracteres para entrega parcial")

    form_data = await request.form()
    total_entregado = 0.0
    parcial_detectada = False
    for item in req.items:
        raw = str(form_data.get(f"entregado_{item.id}", "0")).strip() or "0"
        try:
            entregado = float(raw)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Cantidad entregada invalida") from exc
        if entregado < 0:
            raise HTTPException(status_code=400, detail="Cantidad entregada no puede ser negativa")
        if entregado > item.cantidad:
            raise HTTPException(status_code=400, detail="Cantidad entregada no puede exceder la solicitada")
        item.cantidad_entregada = entregado
        total_entregado += entregado
        if entregado < item.cantidad:
            parcial_detectada = True

    if total_entregado <= 0:
        raise HTTPException(status_code=400, detail="Debe entregar al menos una cantidad para marcar parcial")
    if not parcial_detectada:
        raise HTTPException(status_code=400, detail="Si entregaste todo, usa resultado completa")

    transicionar_requisicion(
        db,
        req,
        nuevo_estado="entregada",
        actor_id=current_user.id,
        delivered_to=delivered_to_limpio,
        delivery_result="parcial",
        delivery_comment=comentario_limpio,
    )
    return redirect_with_message("/bodega", "Requisicion marcada como entrega parcial", "warning")


@app.get("/admin/usuarios")
def admin_usuarios(request: Request, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    ensure_admin(current_user)
    estado = request.query_params.get("estado", "activos")
    query = db.query(Usuario)
    if estado == "activos":
        query = query.filter(Usuario.activo.is_(True))
    elif estado == "inactivos":
        query = query.filter(Usuario.activo.is_(False))
    usuarios = query.order_by(Usuario.activo.desc(), Usuario.id.asc()).all()
    return templates.TemplateResponse(
        "admin_usuarios.html",
        template_context(request, current_user, usuarios=usuarios, estado=estado),
    )


@app.get("/admin/usuarios/nuevo")
def admin_usuario_nuevo(request: Request, current_user: Usuario = Depends(get_current_user)):
    ensure_admin(current_user)
    return templates.TemplateResponse(
        "admin_usuario_form.html",
        template_context(
            request,
            current_user,
            modo="crear",
            usuario=None,
            roles=["user", "aprobador", "bodega", "admin"],
            departamentos=DEPARTAMENTOS_VALIDOS,
        ),
    )


@app.post("/admin/usuarios")
def admin_usuario_crear(
    request: Request,
    username: str = Form(...),
    nombre: str = Form(...),
    rol: str = Form(...),
    departamento: str = Form(...),
    password: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    roles_validos = ["user", "aprobador", "bodega", "admin"]
    username_limpio = username.strip()
    nombre_limpio = nombre.strip()
    depto_limpio = departamento.strip()

    if rol not in roles_validos:
        raise HTTPException(status_code=400, detail="Rol invalido")
    if depto_limpio not in DEPARTAMENTOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Departamento invalido")
    if len(username_limpio) < 3 or len(nombre_limpio) < 3 or len(depto_limpio) < 2:
        raise HTTPException(status_code=400, detail="Datos incompletos o invalidos")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="La contrasena debe tener al menos 6 caracteres")

    existe = db.query(Usuario).filter(Usuario.username == username_limpio).first()
    if existe:
        return redirect_with_message("/admin/usuarios", "Username ya existe", "error")

    from .auth import hash_password

    nuevo = Usuario(
        username=username_limpio,
        nombre=nombre_limpio,
        rol=rol,
        departamento=depto_limpio,
        activo=True,
        password=hash_password(password),
    )
    db.add(nuevo)
    db.commit()
    return redirect_with_message("/admin/usuarios", "Usuario creado", "success")


@app.get("/admin/usuarios/{user_id}/editar")
def admin_usuario_editar_form(
    user_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return templates.TemplateResponse(
        "admin_usuario_form.html",
        template_context(
            request,
            current_user,
            modo="editar",
            usuario=usuario,
            roles=["user", "aprobador", "bodega", "admin"],
            departamentos=DEPARTAMENTOS_VALIDOS,
        ),
    )


@app.post("/admin/usuarios/{user_id}/editar")
def admin_usuario_editar(
    user_id: int,
    username: str = Form(...),
    nombre: str = Form(...),
    rol: str = Form(...),
    departamento: str = Form(...),
    password: str = Form(""),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    roles_validos = ["user", "aprobador", "bodega", "admin"]
    username_limpio = username.strip()
    nombre_limpio = nombre.strip()
    depto_limpio = departamento.strip()
    if rol not in roles_validos:
        raise HTTPException(status_code=400, detail="Rol invalido")
    if depto_limpio not in DEPARTAMENTOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Departamento invalido")
    if len(username_limpio) < 3 or len(nombre_limpio) < 3 or len(depto_limpio) < 2:
        raise HTTPException(status_code=400, detail="Datos incompletos o invalidos")

    duplicado = db.query(Usuario).filter(Usuario.username == username_limpio, Usuario.id != user_id).first()
    if duplicado:
        return redirect_with_message("/admin/usuarios", "Username ya existe", "error")

    usuario.username = username_limpio
    usuario.nombre = nombre_limpio
    usuario.rol = rol
    usuario.departamento = depto_limpio

    if password.strip():
        if len(password.strip()) < 6:
            raise HTTPException(status_code=400, detail="La contrasena debe tener al menos 6 caracteres")
        from .auth import hash_password

        usuario.password = hash_password(password.strip())

    db.commit()
    return redirect_with_message("/admin/usuarios", "Usuario actualizado", "success")


@app.post("/admin/usuarios/{user_id}/eliminar")
def admin_usuario_eliminar(
    user_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.id == current_user.id:
        return redirect_with_message("/admin/usuarios", "No puedes eliminar tu propio usuario", "error")

    if usuario.rol == "admin":
        total_admins = db.query(Usuario).filter(Usuario.rol == "admin").count()
        if total_admins <= 1:
            return redirect_with_message("/admin/usuarios", "No puedes eliminar el ultimo admin", "error")

    referencias = (
        db.query(Requisicion.id)
        .filter(
            or_(
                Requisicion.solicitante_id == usuario.id,
                Requisicion.approved_by == usuario.id,
                Requisicion.rejected_by == usuario.id,
                Requisicion.delivered_by == usuario.id,
            )
        )
        .first()
    )
    if referencias:
        return redirect_with_message(
            "/admin/usuarios",
            "No puedes eliminar un usuario con historial en requisiciones",
            "error",
        )

    db.delete(usuario)
    db.commit()
    return redirect_with_message("/admin/usuarios", "Usuario eliminado", "warning")


@app.post("/admin/usuarios/{user_id}/desactivar")
def admin_usuario_desactivar(
    user_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.id == current_user.id:
        return redirect_with_message("/admin/usuarios", "No puedes desactivar tu propio usuario", "error")
    if not usuario.activo:
        return redirect_with_message("/admin/usuarios", "Usuario ya inactivo", "warning")

    usuario.activo = False
    db.commit()
    return redirect_with_message("/admin/usuarios", "Usuario desactivado", "warning")


@app.post("/admin/usuarios/{user_id}/reactivar")
def admin_usuario_reactivar(
    user_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    usuario = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if usuario.activo:
        return redirect_with_message("/admin/usuarios", "Usuario ya activo", "warning")

    usuario.activo = True
    db.commit()
    return redirect_with_message("/admin/usuarios", "Usuario reactivado", "success")


@app.get("/admin/catalogo-items")
def admin_catalogo_items(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    items = db.query(CatalogoItem).order_by(CatalogoItem.nombre.asc()).all()
    return templates.TemplateResponse(
        "admin_catalogo_items.html",
        template_context(request, current_user, items=items),
    )


@app.post("/admin/catalogo-items/importar")
async def admin_catalogo_item_importar(
    archivo: UploadFile = File(...),
    activar_importados: str | None = Form(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    filename = (archivo.filename or "").strip()
    if not filename:
        return redirect_with_message("/admin/catalogo-items", "Debes seleccionar un archivo", "error")

    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in {"csv", "xlsx"}:
        return redirect_with_message("/admin/catalogo-items", "Formato no soportado. Usa CSV o XLSX", "error")

    raw = await archivo.read()
    if not raw:
        return redirect_with_message("/admin/catalogo-items", "El archivo esta vacio", "error")

    try:
        if ext == "csv":
            nombres = _parse_catalog_csv(raw)
        else:
            nombres = _parse_catalog_xlsx(raw)
    except ValueError as exc:
        return redirect_with_message("/admin/catalogo-items", str(exc), "error")

    if not nombres:
        return redirect_with_message("/admin/catalogo-items", "No se encontraron nombres de items validos", "error")

    activar = activar_importados == "on"
    existentes = {normalize_catalog_name(i.nombre): i for i in db.query(CatalogoItem).all()}
    creados = 0
    actualizados = 0
    sin_cambios = 0

    for nombre in nombres:
        key = normalize_catalog_name(nombre)
        existente = existentes.get(key)
        if existente:
            if existente.activo != activar:
                existente.activo = activar
                actualizados += 1
            else:
                sin_cambios += 1
            continue
        db.add(CatalogoItem(nombre=nombre, activo=activar))
        creados += 1

    db.commit()
    msg = f"Importacion completada. Creados: {creados}, actualizados: {actualizados}, sin cambios: {sin_cambios}"
    return redirect_with_message("/admin/catalogo-items", msg, "success")


@app.get("/admin/catalogo-items/nuevo")
def admin_catalogo_item_nuevo(request: Request, current_user: Usuario = Depends(get_current_user)):
    ensure_admin(current_user)
    return templates.TemplateResponse(
        "admin_catalogo_item_form.html",
        template_context(request, current_user, modo="crear", item=None),
    )


@app.post("/admin/catalogo-items")
def admin_catalogo_item_crear(
    nombre: str = Form(...),
    activo: str = Form("on"),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    nombre_limpio = nombre.strip()
    if len(nombre_limpio) < 2:
        raise HTTPException(status_code=400, detail="Nombre de item invalido")

    existe = db.query(CatalogoItem).filter(CatalogoItem.nombre == nombre_limpio).first()
    if existe:
        return redirect_with_message("/admin/catalogo-items", "El item ya existe", "error")

    nuevo = CatalogoItem(nombre=nombre_limpio, activo=(activo == "on"))
    db.add(nuevo)
    db.commit()
    return redirect_with_message("/admin/catalogo-items", "Item creado", "success")


@app.get("/admin/catalogo-items/{item_id}/editar")
def admin_catalogo_item_editar_form(
    item_id: int,
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    item = db.query(CatalogoItem).filter(CatalogoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return templates.TemplateResponse(
        "admin_catalogo_item_form.html",
        template_context(request, current_user, modo="editar", item=item),
    )


@app.post("/admin/catalogo-items/{item_id}/editar")
def admin_catalogo_item_editar(
    item_id: int,
    nombre: str = Form(...),
    activo: str | None = Form(None),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    item = db.query(CatalogoItem).filter(CatalogoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    nombre_limpio = nombre.strip()
    if len(nombre_limpio) < 2:
        raise HTTPException(status_code=400, detail="Nombre de item invalido")

    duplicado = (
        db.query(CatalogoItem)
        .filter(CatalogoItem.nombre == nombre_limpio, CatalogoItem.id != item_id)
        .first()
    )
    if duplicado:
        return redirect_with_message("/admin/catalogo-items", "El item ya existe", "error")

    item.nombre = nombre_limpio
    item.activo = activo == "on"
    db.commit()
    return redirect_with_message("/admin/catalogo-items", "Item actualizado", "success")


@app.post("/admin/catalogo-items/{item_id}/eliminar")
def admin_catalogo_item_eliminar(
    item_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_admin(current_user)
    item = db.query(CatalogoItem).filter(CatalogoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    db.delete(item)
    db.commit()
    return redirect_with_message("/admin/catalogo-items", "Item eliminado", "warning")


@app.get("/api/requisiciones/{req_id}")
def detalle_requisicion(req_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    req = (
        db.query(Requisicion)
        .options(
            joinedload(Requisicion.items),
            joinedload(Requisicion.solicitante),
            joinedload(Requisicion.aprobador),
            joinedload(Requisicion.rechazador),
            joinedload(Requisicion.entregador),
        )
        .filter(Requisicion.id == req_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="No existe")

    can_view = (
        current_user.rol == "admin"
        or current_user.id == req.solicitante_id
        or current_user.rol == "aprobador"
        or (current_user.rol == "bodega" and req.estado in ["aprobada", "entregada", "liquidada"])
    )
    if not can_view:
        raise HTTPException(status_code=403, detail="No autorizado")

    timeline: list[dict[str, object]] = []
    if req.created_at:
        timeline.append(
            {
                "evento": "Requisicion creada",
                "actor": req.solicitante.nombre if req.solicitante else None,
                "fecha_hora": req.created_at,
            }
        )
    if req.approved_at:
        timeline.append(
            {
                "evento": "Requisicion aprobada",
                "actor": req.aprobador.nombre if req.aprobador else None,
                "fecha_hora": req.approved_at,
            }
        )
    if req.rejected_at:
        timeline.append(
            {
                "evento": "Requisicion rechazada",
                "actor": req.rechazador.nombre if req.rechazador else None,
                "fecha_hora": req.rejected_at,
            }
        )
    if req.delivered_at:
        timeline.append(
            {
                "evento": "Preparacion/entrega de bodega",
                "actor": req.entregador.nombre if req.entregador else None,
                "fecha_hora": req.delivered_at,
            }
        )
        if req.delivered_to:
            timeline.append(
                {
                    "evento": "Recibido",
                    "actor": req.delivered_to,
                    "fecha_hora": req.delivered_at,
                }
            )

    return {
        "id": req.id,
        "folio": req.folio,
        "solicitante": req.solicitante.nombre if req.solicitante else None,
        "departamento": req.departamento,
        "cliente_codigo": req.cliente_codigo,
        "cliente_nombre": req.cliente_nombre,
        "cliente_ruta_principal": req.cliente_ruta_principal,
        "estado": req.estado,
        "justificacion": req.justificacion,
        "created_at": req.created_at,
        "approved_by": req.aprobador.nombre if req.aprobador else None,
        "approval_comment": req.approval_comment,
        "rejected_by": req.rechazador.nombre if req.rechazador else None,
        "rejection_comment": req.rejection_comment,
        "delivered_by": req.entregador.nombre if req.entregador else None,
        "delivered_to": req.delivered_to,
        "delivery_result": req.delivery_result,
        "delivery_comment": req.delivery_comment,
        "rejection_reason": req.rejection_reason,
        "approved_at": req.approved_at,
        "rejected_at": req.rejected_at,
        "delivered_at": req.delivered_at,
        "timeline": timeline,
        "items": [
            {
                "descripcion": item.descripcion,
                "cantidad": item.cantidad,
                "cantidad_entregada": item.cantidad_entregada,
                "unidad": item.unidad,
            }
            for item in req.items
        ],
    }
