# MVP Task Board

Estados: `todo` | `in_progress` | `done` | `blocked`

## Prioridad Alta
- `REQ-001` | `done` | Crear contrato de colaboracion AI y alcance MVP congelado.
- `REQ-002` | `done` | Corregir inconsistencias criticas en `tech_specs.md`.
- `REQ-003` | `done` | Crear bitacora y handoff estandar multi-IA.
- `REQ-004` | `done` | Bootstrap de estructura FastAPI + templates + static.
- `REQ-005` | `done` | Implementar modelos SQLAlchemy (`Usuario`, `Requisicion`, `Item`).
- `REQ-006` | `done` | Implementar `database.py` + `get_db` + sesion SQLite.
- `REQ-007` | `done` | Implementar autenticacion por sesion (`/login`, `/logout`, dependencias de usuario actual).

## Prioridad Media
- `REQ-008` | `done` | Implementar `/crear` con parse de items dinamicos y persistencia.
- `REQ-009` | `done` | Implementar aprobacion/rechazo con validacion de estado y rol.
- `REQ-010` | `done` | Implementar vista bodega y transicion a `entregada`.
- `REQ-011` | `done` | Implementar endpoint `GET /api/requisiciones/{id}` con control de acceso.
- `REQ-012` | `done` | Crear tests basicos de flujo feliz (crear, aprobar, entregar).

## Prioridad Baja
- `REQ-013` | `done` | Guia breve de despliegue LAN y backup operativo.
- `REQ-014` | `done` | Pulido UI minimo (mensajes flash, badges de estado, errores claros).
