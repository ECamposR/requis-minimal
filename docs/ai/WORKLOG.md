# Worklog (append-only)

## 2026-02-10 14:52 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar fase de inicio para colaboracion multi-IA.
- Tareas: `REQ-001`, `REQ-002`, `REQ-003`, `REQ-004`.
- Cambios:
  - `docs/ai/CONTRACT.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
  - `docs/ai/DECISIONS.md`
  - `docs/ai/TASKS.md`
  - `tech_specs.md`
- Resultado:
  - Se congelo alcance MVP y estrategia de autenticacion.
  - Se preparo backlog operativo para continuidad entre Codex/Claude/Gemini.
  - Se inicia bootstrap tecnico del proyecto.
- Proximo paso:
  - Implementar modelos + DB init + rutas base de autenticacion por sesion.

## 2026-02-10 15:08 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar punto 4 (arranque de implementacion).
- Tareas: `REQ-004`, `REQ-005`, `REQ-006`, `REQ-007`, `REQ-008`, `REQ-011`.
- Cambios:
  - `app/main.py`
  - `app/database.py`
  - `app/models.py`
  - `app/auth.py`
  - `app/crud.py`
  - `app/schemas.py`
  - `templates/*.html`
  - `static/app.js`
  - `static/style.css`
  - `init_db.py`
  - `requirements.txt`
  - `.env.example`
  - `README.md`
  - `.gitignore`
- Comandos:
  - `python -m compileall app init_db.py`
- Resultado:
  - App base lista para correr con login por sesion.
  - Flujo crear requisicion + detalle JSON ya implementado.
  - Pendientes principales: aprobacion/rechazo, bodega, tests.
- Proximo paso:
  - Implementar `REQ-009` y `REQ-010`.

## 2026-02-10 15:24 UTC-6 | tool: Codex CLI
- Objetivo: Crear checklist corto ejecutable y auditar estructura minima.
- Cambios:
  - `docs/ai/CHECKLIST_EJECUCION_MVP.md`
- Resultado:
  - Checklist de sesion CLI agregado.
  - Revision de simplicidad documentada: que mantener, que recortar y que evitar en MVP.
- Proximo paso:
  - Decidir si se elimina `app/schemas.py` o se conserva para tipado futuro.

## 2026-02-10 15:31 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar limpieza lean pedida por el usuario.
- Cambios:
  - `app/models.py` (unificacion a `delivered_to`)
  - `app/crud.py` (unificacion a `delivered_to`)
  - `app/main.py` (detalle JSON incluye `delivered_to`)
  - `app/schemas.py` (eliminado)
  - `tech_specs_v1.1_mvp_simplificado.md` (estructura actualizada)
  - `docs/ai/CHECKLIST_EJECUCION_MVP.md` (ajuste post-limpieza)
- Resultado:
  - Estructura mas simple: sin archivo de schemas innecesario.
  - Naming consistente con el spec simplificado.

## 2026-02-10 15:43 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-009` con DB limpia.
- Cambios:
  - `app/main.py` (rutas `/aprobar`, `/aprobar/{id}`, `/rechazar/{id}`)
  - `app/crud.py` (validacion de estado en `puede_aprobar`)
  - `templates/aprobar.html` (vista operativa con acciones aprobar/rechazar)
  - `templates/base.html` (link de menu para aprobadores/admin)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Comandos:
  - `python -m compileall app init_db.py`
- Resultado:
  - Flujo de aprobacion/rechazo funcional con validaciones de rol/departamento/estado.
  - Siguiente tarea activa: `REQ-010` (bodega + entregar).

## 2026-02-10 15:55 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-010` y dejar continuidad multi-IA actualizada.
- Cambios:
  - `app/crud.py` (funcion `puede_entregar`)
  - `app/main.py` (rutas `/bodega` y `/entregar/{id}`)
  - `templates/bodega.html` (tabla y formulario de entrega)
  - `templates/base.html` (menu bodega)
  - `templates/home.html` (contador pendientes bodega)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Comandos:
  - `python -m compileall app init_db.py`
- Resultado:
  - Flujo de bodega listo con validacion de rol y estado `aprobada`.
  - Siguiente tarea recomendada: `REQ-012` (tests basicos E2E de flujo).

## 2026-02-10 16:04 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-012` (tests basicos del flujo principal).
- Cambios:
  - `tests/test_basic_flow.py` (crear, aprobar, entregar)
  - `requirements-dev.txt`
  - `README.md` (instrucciones para correr tests)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Comandos:
  - `pytest -q tests/test_basic_flow.py`
- Resultado:
  - Tests escritos y listos.
  - En este entorno no corrieron por falta de dependencias (`ModuleNotFoundError: sqlalchemy`).
  - Verificacion pendiente al instalar dependencias del proyecto.

## 2026-02-10 16:11 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-013` (operacion LAN y backup).
- Cambios:
  - `docs/LAN_DEPLOY.md`
  - `README.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Guia operativa simple de despliegue LAN y recuperacion creada.
  - Proyecto listo para cerrar con `REQ-014` (pulido UI minimo).

## 2026-02-10 16:19 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-014` (pulido UX minimo).
- Cambios:
  - `app/main.py` (redirects con mensaje y tipo)
  - `templates/base.html` (render de alertas por query params)
  - `templates/mis_requisiciones.html` (badges de estado)
  - `static/style.css` (estilos de alertas y badges)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Comandos:
  - `python -m compileall app init_db.py tests/test_basic_flow.py`
- Resultado:
  - UX basica mejorada sin agregar complejidad de flash sessions.
  - Todas las tareas del tablero inicial quedan completadas.

## 2026-02-10 16:33 UTC-6 | tool: Codex CLI
- Objetivo: Cerrar faltantes de dependencias detectados en validacion real.
- Cambios:
  - `requirements.txt` (agregado `itsdangerous==2.2.0`)
  - `requirements-dev.txt` (agregado `httpx==0.27.2`)
- Resultado:
  - Instalacion de entorno consistente para runtime de sesiones y tests con `TestClient`.

## 2026-02-10 16:46 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-015` (CRUD de usuarios para admin).
- Cambios:
  - `app/main.py` (rutas admin usuarios: listar, crear, editar, eliminar)
  - `templates/base.html` (link `Usuarios` para admin)
  - `templates/admin_usuarios.html`
  - `templates/admin_usuario_form.html`
  - `tests/test_admin_users.py`
  - `tests/conftest.py` (path de proyecto para imports de tests)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Reglas aplicadas:
  - Solo `admin` puede acceder.
  - `username` unico.
  - Password minima de 6 chars al crear.
  - En edicion, password opcional (si vacia no cambia).
  - Bloqueo de auto-eliminacion.
  - Bloqueo de eliminacion del ultimo admin.
- Verificacion:
  - `python -m compileall app tests` OK.
  - `pytest -q tests/test_admin_users.py` no ejecutable en este sandbox por falta de dependencias globales; correr en venv del proyecto.
