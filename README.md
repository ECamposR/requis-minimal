# Sistema de Requisiciones ProHygiene (v1.x)

Aplicación interna LAN para gestionar requisiciones desde solicitud hasta liquidación y soporte de registro en ProKey.

## Estado actual
- Versión operativa `v1.x` (ya no MVP base).
- Flujo implementado:
  - `pendiente` -> `aprobada` / `rechazada` -> `entregada` -> `liquidada`
- Funciones clave activas:
  - catálogo administrable (CRUD + importación CSV/XLSX + búsqueda)
  - entrega con firma de recibido por usuario + PIN
  - liquidación por ítem con alertas y trazabilidad
  - detalle tipo dashboard con timeline
  - generación de PDF para requisiciones liquidadas

## Stack
- Backend: `FastAPI`
- Persistencia: `SQLite` + `SQLAlchemy`
- Frontend: `Jinja2` + `Vanilla JS` + `PicoCSS` + `theme.css`
- PDF: `reportlab`

## Roles
- `admin`
- `aprobador`
- `bodega`
- `jefe_bodega` (aprobador + bodega)
- `user`
- `tecnico` (sin login; usado para firma con PIN)

## Arranque local rápido
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Variables de entorno
Archivo base: `.env.example`

Variables principales:
- `SECRET_KEY`
- `DATABASE_URL` (por defecto SQLite local)
- `APP_NAME`

## Usuarios semilla (init_db.py)
- `admin / admin123`
- `juan.perez / password`
- `carlos.lopez / password`
- `jose.bodega / password`

## Pruebas
```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q tests/test_basic_flow.py
pytest -q tests/test_liquidacion.py
```

## PDF de liquidación
- Endpoint: `GET /requisiciones/{id}/pdf`
- Solo disponible cuando la requisición está en estado `liquidada`
- Respuesta inline (`application/pdf`) con:
  - resumen de estado
  - timeline
  - items liquidados
  - alertas y diferencia por ítem

## Despliegue
### Opción 1: local/systemd (simple)
- recomendado para entorno interno pequeño con SQLite local.

### Opción 2: Docker + Caddy (configurado en repo)
- `Dockerfile`
- `docker-compose.yml`
- `deploy/caddy/`

Revisar decisiones y pasos en:
- `docs/ai/DECISIONS.md` (ADR-004)
- `docs/LAN_DEPLOY.md`

## Gobernanza multi-IA
Fuente de continuidad operativa:
- `docs/ai/CONTRACT.md`
- `docs/ai/HANDOFF.md`
- `docs/ai/TASKS.md`
- `docs/ai/WORKLOG.md`
- `docs/ai/DECISIONS.md`
