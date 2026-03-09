# AI Collaboration Contract (MVP)

## 1) Objetivo
Construir un MVP interno de requisiciones en LAN, rapido y simple, evitando sobreingenieria.

## 2) Decisiones Congeladas de Alcance
- Framework backend: `FastAPI`.
- Persistencia: `SQLite` local (`requisiciones.db`).
- Frontend: `Jinja2 + HTML forms + Vanilla JS + PicoCSS`.
- Sin Docker en MVP.
- Sin integraciones externas (ERP, email, bots, webhooks).
- Sin notificaciones automáticas en MVP.
- Sin borradores y sin edicion post-envio.
- Flujo de estados: `pendiente -> aprobada|rechazada -> preparado -> entregada -> liquidada -> liquidada_en_prokey`.

## 3) Autenticacion (decision cerrada)
- Se usara `login por formulario` + `cookie de sesion firmada`.
- No se usara `HTTP Basic` en el MVP porque el sistema es SSR con navegacion de menu y `logout`.
- Passwords siempre hasheados con `bcrypt`.
- Roles permitidos: `user`, `aprobador`, `bodega`, `admin`.

## 4) Reglas de Implementacion
- Mantener funciones y archivos pequenos, con nombres descriptivos.
- Cualquier cambio de alcance debe registrarse en `docs/ai/DECISIONS.md`.
- No agregar librerias sin justificar en `DECISIONS.md`.
- No introducir background jobs ni colas en MVP.

## 5) Definition of Done (DoD) por tarea
- Criterio funcional cumplido.
- Permisos por rol respetados.
- Validaciones minimas de backend implementadas.
- Test minimo agregado/actualizado (cuando aplique).
- Registro en `docs/ai/WORKLOG.md` y estado en `docs/ai/TASKS.md`.

## 6) Entrega entre IAs
Antes de cerrar una sesion:
- Actualizar `HANDOFF.md` con estado real y siguiente paso exacto.
- Registrar cambios y comandos en `WORKLOG.md`.
- Marcar tareas en `TASKS.md`.
- Documentar decisiones no triviales en `DECISIONS.md`.
