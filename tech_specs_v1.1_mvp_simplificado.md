# Especificacion Tecnica v1.1 (MVP Simplificado)

Documento derivado para implementacion rapida por IA, sin tocar el original.

## 1. Objetivo
- Sistema interno LAN para requisiciones fuera de picking ERP.
- Prioridad: simplicidad operativa, mantenimiento facil, entrega rapida.
- Escala objetivo: ~20 usuarios totales, concurrencia habitual <10.

## 2. Alcance MVP (cerrado)
- Flujo unico: `pendiente -> aprobada|rechazada -> entregada`.
- Sin borradores.
- Sin edicion luego de enviar.
- Sin notificaciones automaticas.
- Sin reportes avanzados.
- Sin integracion ERP.

## 3. Stack (cerrado)
- Python 3.11+
- FastAPI
- SQLAlchemy 2.x
- SQLite local (`requisiciones.db`)
- Jinja2 + HTML forms + PicoCSS + JS vanilla
- Uvicorn (sin Docker en MVP)

## 4. Autenticacion (decision cerrada)
- **Modelo unico**: login por formulario + cookie de sesion firmada.
- Endpoints:
  - `GET /login`
  - `POST /login`
  - `POST /logout`
- No usar HTTP Basic en este MVP.
- Passwords hasheadas con bcrypt.

## 5. Roles y permisos
- `user`: crear y ver propias requisiciones.
- `aprobador`: crear/ver propias + aprobar/rechazar de su departamento.
- `bodega`: ver aprobadas y marcar entregadas.
- `admin`: acceso total sin filtro por departamento.

## 6. Modelo de datos minimo

### usuarios
- `id` PK
- `username` unico
- `password` hash bcrypt
- `nombre`
- `rol` (`user|aprobador|bodega|admin`)
- `departamento`

### requisiciones
- `id` PK
- `folio` unico (`REQ-0001`, `REQ-0002`, ...)
- `solicitante_id` FK usuarios
- `departamento`
- `estado` (`pendiente|aprobada|rechazada|entregada`)
- `justificacion`
- `created_at`
- `approved_at`
- `approved_by` FK usuarios
- `delivered_at`
- `delivered_by` FK usuarios
- `delivered_to` (nombre de quien recibe)
- `rejection_reason`

### items
- `id` PK
- `requisicion_id` FK requisiciones
- `descripcion` (seleccionada desde catalogo activo administrado por `admin`)
- `cantidad > 0`
- `unidad` (interna, no capturada en UI MVP)

### catalogo_items
- `id` PK
- `nombre` unico
- `activo` (bool)

### indices minimos
- `requisiciones(estado)`
- `requisiciones(solicitante_id)`
- `requisiciones(departamento)`

## 7. Endpoints MVP

### HTML
- `GET /` dashboard
- `GET /crear`
- `POST /crear`
- `GET /mis-requisiciones`
- `GET /aprobar`
- `POST /aprobar/{id}`
- `POST /rechazar/{id}`
- `GET /bodega`
- `POST /entregar/{id}`

### JSON
- `GET /api/requisiciones/{id}` detalle para modales
- `GET /health`

## 8. Reglas de negocio clave
- Solo se puede aprobar/rechazar si estado actual es `pendiente`.
- Solo se puede entregar si estado actual es `aprobada`.
- `aprobador` solo opera requisiciones de su departamento.
- `admin` puede ver y operar todo.
- Debe existir al menos 1 item al crear requisicion.
- Los items enviados deben pertenecer al catalogo activo en DB.

## 9. Estructura de proyecto
```text
requisiciones-system/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── auth.py
│   └── crud.py
├── templates/
├── static/
├── init_db.py
├── requirements.txt
└── README.md
```

## 10. Lineamientos para vibecoding multi-IA
- Toda sesion debe actualizar:
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
  - `docs/ai/DECISIONS.md` (si hubo decisiones nuevas)
- No introducir nuevas librerias sin registrarlo en decisiones.
- No cambiar alcance MVP sin marcarlo explicitamente.

## 11. Definition of Done por tarea
- Funciona en UI y backend para el caso principal.
- Respeta permisos por rol y transicion de estado.
- Tiene validacion minima de entradas.
- Queda registrado en bitacora y handoff.

## 12. Deployment minimo (LAN)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 13. Limites de escalabilidad MVP
- SQLite es suficiente para carga esperada (<10 concurrentes reales).
- Senales para migrar a Postgres:
  - Bloqueos frecuentes en escritura.
  - Tiempo de respuesta degradado de forma sostenida.
  - Aumento fuerte de volumen (ej. >500 req/mes).

---

**Version:** 1.1-simplificada  
**Fecha:** 2026-02-10  
**Base:** Resumen operativo del `tech_specs.md` original para ejecucion por IA.
