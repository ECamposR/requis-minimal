import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
from .database import get_db
from .models import Requisicion, Usuario

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me")

app = FastAPI(title=os.getenv("APP_NAME", "Sistema de Requisiciones MVP"))
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def template_context(request: Request, current_user: Usuario | None = None, **kwargs: object) -> dict[str, object]:
    return {"request": request, "current_user": current_user, **kwargs}


def redirect_with_message(url: str, message: str, level: str = "success") -> RedirectResponse:
    safe_msg = quote_plus(message)
    safe_level = quote_plus(level)
    sep = "&" if "?" in url else "?"
    return RedirectResponse(url=f"{url}{sep}msg={safe_msg}&type={safe_level}", status_code=303)


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
    mis_requisiciones = (
        db.query(Requisicion).filter(Requisicion.solicitante_id == current_user.id).count()
    )
    pendientes_aprobar = 0
    if current_user.rol in ["aprobador", "admin"]:
        filtros = [Requisicion.estado == "pendiente"]
        if current_user.rol == "aprobador":
            filtros.append(Requisicion.departamento == current_user.departamento)
        pendientes_aprobar = db.query(Requisicion).filter(*filtros).count()
    pendientes_bodega = 0
    if current_user.rol in ["bodega", "admin"]:
        pendientes_bodega = db.query(Requisicion).filter(Requisicion.estado == "aprobada").count()

    return templates.TemplateResponse(
        "home.html",
        template_context(
            request,
            current_user,
            mis_requisiciones=mis_requisiciones,
            pendientes_aprobar=pendientes_aprobar,
            pendientes_bodega=pendientes_bodega,
        ),
    )


@app.get("/crear")
def crear_form(request: Request, current_user: Usuario = Depends(get_current_user)):
    return templates.TemplateResponse("crear_requisicion.html", template_context(request, current_user))


@app.post("/crear")
async def crear(
    request: Request,
    departamento: str = Form(...),
    justificacion: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = crear_requisicion_db(
        db=db,
        solicitante_id=current_user.id,
        departamento=departamento,
        justificacion=justificacion,
    )

    form_data = await request.form()
    items_data = parse_items_from_form(form_data)
    if not items_data:
        raise HTTPException(status_code=400, detail="Debe agregar al menos un item")

    for item_data in items_data:
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


@app.get("/aprobar")
def aprobar_view(request: Request, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.rol not in ["aprobador", "admin"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    query = db.query(Requisicion).filter(Requisicion.estado == "pendiente")
    if current_user.rol == "aprobador":
        query = query.filter(Requisicion.departamento == current_user.departamento)

    pendientes = query.order_by(Requisicion.created_at.asc()).all()
    return templates.TemplateResponse(
        "aprobar.html",
        template_context(request, current_user, pendientes=pendientes),
    )


@app.post("/aprobar/{req_id}")
def aprobar(req_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if not puede_aprobar(req, current_user.rol, current_user.departamento):
        raise HTTPException(status_code=403, detail="No autorizado")

    transicionar_requisicion(db, req, nuevo_estado="aprobada", actor_id=current_user.id)
    return redirect_with_message("/aprobar", "Requisicion aprobada", "success")


@app.post("/rechazar/{req_id}")
def rechazar(
    req_id: int,
    razon: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if not puede_aprobar(req, current_user.rol, current_user.departamento):
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
    )
    return redirect_with_message("/aprobar", "Requisicion rechazada", "warning")


@app.get("/bodega")
def bodega_view(request: Request, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.rol not in ["bodega", "admin"]:
        raise HTTPException(status_code=403, detail="No autorizado")

    aprobadas = (
        db.query(Requisicion)
        .filter(Requisicion.estado == "aprobada")
        .order_by(Requisicion.approved_at.asc(), Requisicion.created_at.asc())
        .all()
    )
    return templates.TemplateResponse(
        "bodega.html",
        template_context(request, current_user, aprobadas=aprobadas),
    )


@app.post("/entregar/{req_id}")
def entregar(
    req_id: int,
    delivered_to: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Requisicion no encontrada")
    if not puede_entregar(req, current_user.rol):
        raise HTTPException(status_code=403, detail="No autorizado")

    delivered_to_limpio = delivered_to.strip()
    if len(delivered_to_limpio) < 3:
        raise HTTPException(status_code=400, detail="El nombre de quien recibe debe tener al menos 3 caracteres")

    transicionar_requisicion(
        db,
        req,
        nuevo_estado="entregada",
        actor_id=current_user.id,
        delivered_to=delivered_to_limpio,
    )
    return redirect_with_message("/bodega", "Requisicion marcada como entregada", "success")


@app.get("/api/requisiciones/{req_id}")
def detalle_requisicion(req_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    req = (
        db.query(Requisicion)
        .options(joinedload(Requisicion.items))
        .filter(Requisicion.id == req_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="No existe")

    can_view = (
        current_user.rol == "admin"
        or current_user.id == req.solicitante_id
        or (current_user.rol == "aprobador" and current_user.departamento == req.departamento)
        or (current_user.rol == "bodega" and req.estado in ["aprobada", "entregada"])
    )
    if not can_view:
        raise HTTPException(status_code=403, detail="No autorizado")

    return {
        "id": req.id,
        "folio": req.folio,
        "departamento": req.departamento,
        "estado": req.estado,
        "justificacion": req.justificacion,
        "created_at": req.created_at,
        "delivered_to": req.delivered_to,
        "rejection_reason": req.rejection_reason,
        "items": [
            {"descripcion": item.descripcion, "cantidad": item.cantidad, "unidad": item.unidad}
            for item in req.items
        ],
    }
