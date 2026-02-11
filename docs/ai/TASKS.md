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
- `REQ-015` | `done` | CRUD de usuarios para admin (crear, editar, eliminar) desde web.
- `REQ-016` | `done` | Cambiar captura de items a catalogo predefinido + selector (sin unidad en UI).
- `REQ-017` | `done` | Migrar catalogo de items de fijo en codigo a administrable por admin en DB.
- `REQ-018` | `done` | Permitir a admin/aprobador ver historial completo en `/aprobar` (pendiente/aprobada/rechazada).
- `REQ-019` | `done` | Trazabilidad en aprobacion: mostrar solicitante y actor (aprobador/rechazador) + persistir `rejected_by/rejected_at`.
- `REQ-020` | `done` | Trazabilidad de bodega: mostrar actor de entrega (`delivered_by`) en historial y detalle.
- `REQ-021` | `done` | En vista bodega mostrar quien solicito y quien aprobo cada requisicion.
- `REQ-022` | `done` | Corregir eliminacion de usuarios con historial (evitar 500) y limpiar warnings ORM de relaciones.
- `REQ-023` | `done` | Implementar baja logica de usuarios (`activo`) con desactivar/reactivar y bloqueo de login para inactivos.
- `REQ-024` | `done` | Vista bodega con historial de requisiciones entregadas (ya no desaparecen tras procesar).
- `REQ-025` | `done` | Boton `Ver` (detalle con items) habilitado en historiales de aprobar y bodega.
- `REQ-026` | `done` | Comentarios de proceso en aprobar/rechazar/entregar para trazabilidad operativa.
- `REQ-027` | `done` | Compactar UI de tablas/formularios y ampliar entrega de bodega con resultado (`completa`, `parcial`, `no_entregada`).
- `REQ-028` | `done` | Flujo de entrega parcial en 2 pasos: redirigir a edicion de cantidades entregadas por item y cerrar con trazabilidad.
- `REQ-029` | `done` | Evitar items duplicados dentro de una misma requisicion (UI + validacion backend).
- `REQ-030` | `done` | Restringir departamento de usuarios admin a lista predefinida (`Cuentas`, `Ventas`, `Bodega`, `Admon`, `Logistica`).

## Prioridad Baja
- `REQ-013` | `done` | Guia breve de despliegue LAN y backup operativo.
- `REQ-014` | `done` | Pulido UI minimo (mensajes flash, badges de estado, errores claros).
