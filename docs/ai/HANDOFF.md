# Handoff Activo

## Estado actual
- Proyecto inicializado con especificacion MVP y protocolo de colaboracion multi-IA.
- Alcance y autenticacion definidos en `docs/ai/CONTRACT.md`.
- Especificacion tecnica normalizada en `tech_specs.md`.
- Bootstrap tecnico funcional listo (`app/`, `templates/`, `static/`, `init_db.py`).
- Flujo de aprobacion/rechazo implementado (`REQ-009`).
- Flujo de bodega/entrega implementado (`REQ-010`).
- Tests basicos de flujo agregados (`REQ-012`).
- Guia LAN/backup agregada (`REQ-013`).
- Pulido UI minimo agregado (`REQ-014`).
- Administracion de usuarios por admin agregada (`REQ-015`).
- Formulario de requisicion migrado a selector de catalogo de items (`REQ-016`).
- Catalogo de items migrado a entidad administrable por admin (`REQ-017`).
- Vista de aprobacion con historial completo para admin/aprobador (`REQ-018`).
- Trazabilidad de aprobacion/rechazo visible y persistida (`REQ-019`).
- Trazabilidad de entrega por bodega visible en historial y API (`REQ-020`).
- Vista de bodega con trazabilidad de solicitante y aprobador (`REQ-021`).
- Eliminacion de usuarios con historial protegida y mapeos ORM ajustados (`REQ-022`).
- Baja logica de usuarios con estado activo/inactivo (`REQ-023`).
- Vista bodega con historial de entregadas (`REQ-024`).
- Boton `Ver` en historiales de aprobar y bodega (`REQ-025`).
- Comentarios de proceso en aprobar/rechazar/entregar (`REQ-026`).
- UI compacta para tablas/acciones y flujo de bodega con resultado de entrega (`REQ-027`).
- Entrega parcial en 2 pasos con edicion de cantidades por item (`REQ-028`).
- Bloqueo de items duplicados por requisicion en formulario y backend (`REQ-029`).
- Departamento de usuarios administrado por lista cerrada en alta/edicion (`REQ-030`).
- Departamento en alta de requisicion fijado por sesion del usuario (`REQ-031`).
- Requisicion ahora exige datos de cliente (`codigo` + `nombre`) en alta (`REQ-032`).
- V2 visual iniciada con identidad corporativa (header/nav/paleta/tipografia) (`REQ-033`).
- Primera iteracion dark theme corporativa aplicada sobre base V2 (`REQ-034`).
- Segunda iteracion dark aplicada (home/login/forms/tables con mayor jerarquia visual) (`REQ-035`).
- Tercera iteracion dark aplicada (nav activo + tablas/acciones operativas refinadas) (`REQ-036`).
- CSS consolidado para V2 dark, eliminando reglas duplicadas/conflictivas (`REQ-037`).
- Dashboard de inicio extendido con metricas por estado para todos los usuarios (`REQ-038`).
- Flujo de gestion en `Aprobar` y `Bodega` movido a vistas dedicadas por requisicion (`REQ-039`).
- Home extendido con metricas operativas simples adicionales por usuario (`REQ-040`).
- Alta de requisicion ahora exige `Ruta Principal del Cliente` con formato validado `AA00` (`REQ-041`).
- Rol `aprobador` ahora puede gestionar y ver todas las requisiciones (sin filtro por departamento) (`REQ-042`).
- Baseline UI consolidada en `main` tras merge de `feat/ui-v2-prohygiene` (merge commit `0817f61`).
- Tag operativo publicado: `v1.2.0-ui-base` (punto de retorno para UI base aprobada).

## En progreso
- Smoke test funcional final post-merge/tag sobre `main`.

## Proximo paso exacto
- Ejecutar smoke test de aprobacion/historial:
  - Login como `aprobador` y abrir `/aprobar`.
  - Verificar visualizacion de requisiciones en estados `pendiente`, `aprobada` y `rechazada`, incluyendo solicitante.
  - Verificar columna "Gestionado por" para aprobadas/rechazadas/entregadas.
  - Confirmar que solo puede gestionar pendientes de su departamento.
  - Login como `admin` y confirmar que puede gestionar cualquier pendiente.
  - Rechazar una requisicion y confirmar persistencia de actor en historial.
  - Entregar una requisicion desde bodega y confirmar actor `delivered_by` en historial y modal detalle.
  - En `/bodega`, verificar columnas `Solicitante` y `Aprobado por`.
  - Intentar eliminar usuario con requisiciones asociadas y verificar mensaje controlado (sin 500).
  - Desactivar usuario y validar que no puede iniciar sesion.
  - Reactivar usuario y validar que recupera acceso.
  - En `/bodega`, verificar seccion "Historial de entregadas" con actor de entrega.
  - Verificar en `/aprobar` y `/bodega` que el boton `Ver` abre detalle con items.
- Verificar en `/aprobar` y `/bodega` que comentarios se guardan y se ven en modal detalle.
- Verificar en `/bodega` registro de resultado: `completa`, `parcial` y `no_entregada`.
- Verificar que `parcial` y `no_entregada` exigen comentario y que `no_entregada` permite dejar vacio "Recibe".
- Verificar que al elegir `parcial` redirige a `/entregar/{id}/parcial`, permite editar cantidades entregadas por item y guarda `cantidad_entregada`.
- Verificar en `/crear` que un item ya seleccionado queda bloqueado en las demas filas y que backend rechaza duplicados si se fuerza request manual.
- Verificar en `/admin/usuarios` que `Departamento` se selecciona desde lista fija y backend rechaza valores fuera de catalogo.
- Verificar en `/crear` que el departamento se muestra solo lectura y backend usa siempre `current_user.departamento` (aunque se envie otro valor en el form).
- Verificar en `/crear` que no permite enviar requisicion sin `codigo cliente` y `nombre cliente`, y que ambos se reflejan en detalle de requisicion.
- Revisar consistencia visual de todas las vistas restantes sobre la nueva base corporativa y ajustar componentes puntuales (tablas/formularios/modales) si hace falta.
- Iterar contraste fino y micro-espaciados del dark theme con feedback visual de usuario (esta iteracion es base).
- Ajustar siguientes detalles de V2 dark segun feedback visual: ritmo tipografico del menu y densidad de tablas largas.
- Desde `REQ-037`, tomar `static/style.css` como base limpia para siguientes iteraciones visuales.
- Validar con feedback visual si el contraste de tarjetas metricas necesita un ajuste adicional (actualmente diferenciadas por color de estado).
- Validar UX final de pantallas `GET /aprobar/{id}/gestionar` y `GET /bodega/{id}/gestionar` (copy, espaciado y ayudas contextuales).

## Riesgos abiertos
- Mantener consistencia entre permisos por rol y consultas por departamento.
- Evitar drift entre especificacion y codigo durante iteraciones rapidas con IA.
- Pendiente de verificacion real de tests en entorno con dependencias instaladas.
- Validar end-to-end UI admin en navegador en entorno real.
- Verificar que no existan requisiciones abiertas con items eliminados del catalogo (aceptable en MVP).
- Confirmar migracion de DB existente: columnas `rejected_by` y `rejected_at`.

## Como retomar en 5 minutos
1. Leer `docs/ai/CONTRACT.md`.
2. Revisar ultimas entradas de `docs/ai/WORKLOG.md`.
3. Tomar una tarea `todo` de mayor prioridad en `docs/ai/TASKS.md`.
4. Levantar app con DB limpia (`python init_db.py` + `uvicorn app.main:app --reload`) y continuar.
5. Si se requiere rollback UI, usar `git checkout v1.2.0-ui-base`.
