# Sistema de Requisiciones ProHygiene (v1.x)

Aplicación interna LAN para gestionar requisiciones desde solicitud hasta liquidación y soporte de registro en ProKey.

## Manual de usuario final
- Ver `MANUAL_USUARIO.md`

## Estado actual
- Versión operativa `v1.x` (ya no MVP base).
- Flujo implementado:
  - `pendiente` -> `aprobada` / `rechazada` -> `entregada` -> `liquidada` -> `liquidada_en_prokey`
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

## Importación masiva de usuarios (admin)
- Pantalla: `Administración de Usuarios`
- Endpoint: `POST /admin/usuarios/importar`
- Formato de archivo soportado: `XLSX` y `CSV`
- Columnas requeridas: `NOMBRE`, `PUESTO`
- Flujo:
  - `Previsualizar` (`dry-run`): valida y muestra qué filas se crearán/actualizarán.
  - `Importar`: aplica cambios de forma idempotente.
- Reglas de mapeo por puesto:
  - `AUXILIAR DE BODEGA` -> `rol=bodega`, `departamento=Bodega`
  - `TECNICO DE SERVICIO` -> `rol=tecnico`, `departamento=Logistica`
  - `EJECUTIVO/A DE CUENTAS` -> `rol=user`, `departamento=Cuentas`
  - `EJECUTIVO DE VENTAS` -> `rol=user`, `departamento=Ventas`
  - `ASISTENTE ADMINISTRATIVO` -> `rol=user`, `departamento=Admon`
  - `GERENTE GENERAL` y `JEFES` -> `rol=aprobador`, `departamento=Admon`
- Regla de username:
  - `inicial del primer nombre + primer apellido`
  - Ejemplo: `Carlos Humberto Ramirez Segura` -> `cramirez`
  - Si hay colisión se agrega sufijo numérico (`cramirez2`, `cramirez3`, ...).
- Credenciales iniciales por importación:
  - Roles no técnicos: contraseña temporal `Temp@2026`
  - Técnicos: PIN temporal `1234` y `puede_iniciar_sesion=False`

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
- Disponible cuando la requisición está en estado `liquidada` o `liquidada_en_prokey`
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
