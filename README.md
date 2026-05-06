# Sistema de Requisiciones ProHygiene (beta operativa v1.x)

Aplicación interna LAN para gestionar requisiciones desde solicitud hasta liquidación y soporte de registro en ProKey.

## Manual de usuario final
- Ver `MANUAL_USUARIO.md`

## Estado actual
- Fase actual: `beta operativa en produccion controlada`.
- Inicio de beta productiva: `2026-03-10`.
- Version operativa: `v1.x` (ya no MVP base).
- Flujo implementado:
  - `pendiente` -> `aprobada` / `rechazada` -> `preparado` -> `entregada` -> `liquidada` -> `liquidada_en_prokey`
- Funciones clave activas:
  - catálogo administrable (CRUD + importación CSV/XLSX + búsqueda)
  - entrega con firma de recibido por usuario + PIN
  - cambio de contraseña autoservicio para usuarios con login habilitado
  - liquidación por ítem con confirmación por contraseña, alertas y trazabilidad
  - detalle tipo dashboard con timeline
  - exportación CSV/XLSX en `Todas las Requisiciones` respetando filtros activos
  - generación de PDF desde requisiciones aprobadas en adelante

## Criterio de evolucion
- El sistema se desarrolla y mantiene bajo un enfoque de simplicidad operativa: resolver el problema real con la menor complejidad posible.
- El proyecto sigue creciendo mediante `vibe coding`, pero con disciplina documental estricta.
- La gobernanza es agnostica al modelo LLM y a la herramienta usada; cualquier sesion debe dejar contexto util para la siguiente.
- Todo cambio relevante debe quedar registrado en:
  - `docs/ai/WORKLOG.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/DECISIONS.md` cuando aplique

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
- `LOG_LEVEL` (default `INFO`)
- `LOG_TO_FILE` (`1` para habilitar archivo rotativo)
- `LOG_DIR` (default `logs/`)
- `LOG_FILE` (default `app.log`)
- `LOG_MAX_BYTES` (default `5242880`)
- `LOG_BACKUP_COUNT` (default `5`)
- `BACKUPS_DIR` (default `backups/`)

### Reconstruir `.env` en emergencia
Si se pierde el archivo `.env`, en este proyecto Docker debes recrearlo con estos valores minimos:

```env
DATABASE_URL=sqlite:////app/data/requisiciones.db
SECRET_KEY=<SECRET_KEY_GENERADA>
APP_NAME=Sistema de Requisiciones ProHygiene
```

Notas:
- `DATABASE_URL=sqlite:////app/data/requisiciones.db` es la ruta correcta actual para Docker.
- Esa ruta funciona junto al volumen de `docker-compose.yml`:
  - `./data:/app/data`
- Si cambias `SECRET_KEY`, todas las sesiones activas se invalidan y los usuarios tendran que iniciar sesion de nuevo.

### Generar un `SECRET_KEY` nuevo
Usa cualquiera de estos comandos:

```bash
python - <<'PY'
import secrets
print(secrets.token_urlsafe(48))
PY
```

o en una sola linea:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Pasos rapidos para reconstruir `.env`
1. Crear el archivo:
```bash
cp .env.example .env
```
2. Editar `.env` y dejar:
```env
DATABASE_URL=sqlite:////app/data/requisiciones.db
SECRET_KEY=<pega_aqui_la_clave_generada>
APP_NAME=Sistema de Requisiciones ProHygiene
```
3. Reiniciar la app:
```bash
docker compose up -d --build
```

### Verificacion rapida
Confirma que el contenedor lea la ruta correcta de DB:

```bash
docker compose exec requisiciones python -c "from app.database import DATABASE_URL; print(DATABASE_URL)"
```

Debe imprimir:

```text
sqlite:////app/data/requisiciones.db
```

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
- Disponible cuando la requisición está en estado `aprobada`, `preparado`, `entregada`, `liquidada` o `liquidada_en_prokey`
- Respuesta inline (`application/pdf`) con:
  - resumen de estado
  - timeline
  - items liquidados
  - alertas y diferencia por ítem

## Logging y observabilidad básica
- Logs estructurados JSON en salida estándar (útil para Docker).
- `request_id` por solicitud (`X-Request-ID` en respuesta).
- Registro de:
  - requests (`method`, `path`, `status_code`, `duration_ms`, `user_id`, `client_ip`)
  - excepciones HTTP
  - login exitoso/fallido y logout
- Opcional: archivo rotativo vía `LOG_TO_FILE=1`.

## Respaldos y restauracion (solo admin)
- Pantalla: `Respaldos`
- Disponible solo cuando la app usa `SQLite`
- Genera un archivo `.zip` con:
  - copia consistente de la base de datos operativa
  - `manifest.json` con fecha, formato y checksum
- La restauracion:
  - reemplaza la base actual por el respaldo seleccionado
  - crea automaticamente un backup previo de seguridad
  - obliga a volver a iniciar sesion
- Alcance:
  - recupera la data operativa de la app
  - no restaura codigo, imagen Docker ni el archivo `.env`

## Backup completo desde servidor Docker
Si necesitas un respaldo operativo completo desde el servidor, existe el script:

```bash
./scripts/backup_docker_prod.sh
```

Genera un `.tar.gz` en `backups/full/` con:
- snapshot consistente de `data/requisiciones.db`
- `.env`
- `docker-compose.yml`
- `Dockerfile`
- `README.md`
- `deploy/caddy/Caddyfile`
- `deploy/caddy/docker-compose.yml`
- estado de Caddy (`/data` y `/config`) si el contenedor `caddy` está corriendo
- `manifest.txt` con host, commit y contenedores activos

Variables opcionales:
- `APP_CONTAINER` (default `requisiciones`)
- `CADDY_CONTAINER` (default `caddy`)
- `APP_DB_PATH` (default `/app/data/requisiciones.db`)
- `OUTPUT_DIR` (default `./backups/full`)

Ejemplo:

```bash
OUTPUT_DIR=/srv/backups/requisiciones ./scripts/backup_docker_prod.sh
```

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

Regla base:
- el conocimiento del proyecto debe vivir en el repo, no depender de un chat, un modelo o una herramienta concreta
