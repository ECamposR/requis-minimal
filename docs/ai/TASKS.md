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
- `REQ-031` | `done` | En nueva requisicion, departamento autocompletado desde usuario autenticado (sin edicion manual).
- `REQ-032` | `done` | En creacion de requisicion, exigir `codigo cliente` y `nombre cliente` obligatorios.
- `REQ-033` | `done` | Iniciar V2 visual corporativa (header/nav/paleta/tipografia) alineada a referencias de marca.
- `REQ-034` | `done` | Primera iteracion dark theme corporativa (nav/superficies/tablas/modales) manteniendo identidad ProHygiene.
- `REQ-035` | `done` | Segunda iteracion dark: home con metricas, login mejorado y formularios/tablas con mayor jerarquia visual.
- `REQ-036` | `done` | Tercera iteracion dark: estado activo en nav + pulido de legibilidad en tablas operativas y acciones.
- `REQ-037` | `done` | Consolidar `style.css` (eliminar duplicidad/capas conflictivas) manteniendo look dark corporativo.
- `REQ-038` | `done` | Dashboard de inicio con metricas por estado para todos los roles + colores diferenciados por tarjeta.
- `REQ-039` | `done` | Reemplazar acciones compactas de `Aprobar` y `Bodega` por vistas dedicadas de gestion por requisicion.
- `REQ-040` | `done` | Agregar metricas simples en inicio (`creadas este mes`, `pendientes +48h`, `entregadas 30 dias`) manteniendo enfoque MVP.
- `REQ-041` | `done` | Agregar campo obligatorio `Ruta Principal del Cliente` con formato `AA00` en creacion de requisicion.
- `REQ-042` | `done` | Permitir que aprobadores vean/aprueben todas las requisiciones sin restriccion por departamento.
- `REQ-043` | `done` | Agregar busqueda/filtros en `Aprobar` y `Bodega` para escalar consultas de requisiciones.
- `REQ-044` | `done` | Separar estados operativos en UI/filtros: `Pendiente de aprobar` y `Pendiente de entregar`.
- `REQ-045` | `done` | Robustecer `run_migrations()` para que arranque en DB limpia sin error `no such table`.
- `REQ-046` | `done` | Evitar agregar nueva fila de item si la fila anterior no tiene item/cantidad valida.
- `REQ-047` | `done` | Endurecer parseo backend de items para evitar falsos `Item no permitido en catalogo`.
- `REQ-048` | `done` | Permitir eliminar requisiciones propias solo si estan en `pendiente de aprobar`.
- `REQ-049` | `done` | Corregir validacion intermitente de catalogo al crear requisicion (escape de opciones JS + normalizacion backend de nombre de item).
- `REQ-050` | `done` | Unificar metrica de `Pendientes de aprobar` entre tarjetas y grafico en inicio (segun rol).
- `REQ-051` | `done` | En vistas `Gestionar` (aprobar/bodega), mostrar datos de cliente y ruta; ocultar departamento.
- `REQ-052` | `done` | Importar catalogo de items desde CSV/XLSX en admin (alta masiva simple con deduplicacion).
- `REQ-053` | `done` | Redisenar modal de detalle de requisicion para layout tipo panel (items arriba + info/estado/comentarios en dos columnas).
- `REQ-054` | `done` | Ampliar ancho del modal detalle y paneles internos para evitar contenido apinado.
- `REQ-055` | `done` | Ajustar modal detalle a layout plano de referencia (sin tarjetas internas por campo, mas ancho util).
- `REQ-056` | `done` | Alinear aspecto visual del modal detalle con captura de referencia (labels coloreados, cantidades centradas, chip de resultado).
- `REQ-057` | `done` | Iteracion UI dashboard: header/nav estilo prototipo + metric cards estilo prototipo (sin tocar seccion de barras).
- `REQ-058` | `done` | Unificar tema visual en vistas operativas/admin (navbar reusable, paneles, formularios, tablas, badges) sin cambios de logica.
- `REQ-059` | `done` | Registrar en detalle de requisicion la linea de tiempo de cambios de estado (creacion, aprobacion/rechazo, preparacion/entrega y recibido) con hora `HH:MM:SS`.
- `REQ-060` | `done` | Extender modelo para liquidacion (campos por item: usado/devuelto nuevo/devuelto danado) y habilitar estado `liquidada` con migracion SQLite.

## Prioridad Baja
- `REQ-013` | `done` | Guia breve de despliegue LAN y backup operativo.
- `REQ-014` | `done` | Pulido UI minimo (mensajes flash, badges de estado, errores claros).
