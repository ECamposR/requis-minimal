# MVP Task Board

Estados: `todo` | `in_progress` | `done` | `blocked`

## Reinicio Liquidacion (desde `3d7702b`)
- `REQ-060` | `done` | Base de liquidacion implementada: estado `liquidada`, campos base en `requisiciones/items`, migracion robusta e idempotente + baseline de entrega (`cantidad_entregada`) normalizado.
- `REQ-061` | `done` | Endpoint y UI de captura de liquidacion (`GET/POST /liquidar/{id}`), alertas no bloqueantes persistidas por item e inmutabilidad post-liquidacion.
- `REQ-062` | `done` | Modal detalle de requisiciones liquidadas en solo lectura: tabla estilo papel, resumen de liquidacion en cabecera, alertas por item y evento de timeline.
- `REQ-063` | `done` | Suite de integracion de flujo completo con liquidacion y escenarios canónicos (sin alertas, faltante, retorno extra, salida sin soporte) + precondiciones/inmutabilidad/timeline.
- `REQ-064` | `done` | Liquidacion permite `prokey_ref` vacio: guarda `NULL`, no bloquea cierre, y detalle muestra "Pendiente" con badge "Prokey pendiente".
- `REQ-065` | `done` | Edicion posterior de `prokey_ref` para requisiciones liquidadas (admin o solicitante), sin reabrir ni modificar cantidades/alertas.
- `REQ-066` | `done` | Liquidacion por item con modo `RETORNABLE/CONSUMIBLE`, campo UI `No usado` y alertas/diferencia recalculadas por modo (no bloqueantes).
- `REQ-067` | `done` | Modal detalle de requisiciones liquidadas actualizado al modelo por modo: `Tipo/Usado/No usado/Regresa/Diferencia/Ingreso PK` y payload enriquecido.
- `REQ-068` | `done` | Bloqueo de liquidacion para items sin definir (`entregado>0` y `usado+no_usado+regresa=0`), con validacion backend obligatoria + validacion frontend de apoyo y preservacion de datos digitados.
- `REQ-069` | `done` | Alertas de liquidacion en modal con etiquetas humanas (`Faltante/Sobrante/Retorno extra/Inconsistencia`), tooltip con detalle numerico y codigo interno, mas robustez de payload `liquidation_alerts=[]`.
- `REQ-070` | `done` | Modal detalle liquidada muestra comentario general de liquidacion (con `—` si vacio) y nota por item bajo descripcion; payload JSON normalizado para `liquidation_comment` e `item_liquidation_note`.
- `REQ-071` | `done` | Rediseño del modal detalle a vista dashboard: cards superiores + timeline lateral + tabla central, “Alertas de conciliación”, DIF por signo, notas de ítem destacadas y comentarios secundarios colapsables.
- `REQ-072` | `done` | Refinamiento visual de la vista dashboard del modal: badges/severidades más legibles, DIF con mayor contraste, densidad de tabla ajustada y estilos scoped para no afectar otras vistas.
- `REQ-073` | `done` | UI polish del dashboard en modal: cards más compactas con patrón label/valor, timeline vertical con nodos, DIF como chip con signo, modal casi fullscreen y notas por ítem con mayor énfasis contextual.
- `REQ-074` | `done` | Ajustes finos UX en dashboard del detalle: “Alta severidad”, acción sugerida por alertas, `Ingreso PK` como `—` en consumibles, centrado numérico y botón PDF habilitado solo en `liquidada`.
- `REQ-075` | `done` | Corrección de hora de creación en detalle: `created_at` ya no depende de `func.now()` (UTC SQLite) y se persiste en hora local al crear requisición.
- `REQ-076` | `done` | Buscador server-side en Catálogo Admin con query param `q` (case-insensitive), barra de búsqueda en UI con limpiar/conteo y test de filtro por nombre.
- `REQ-077` | `done` | Nueva Requisición usa `input + datalist` para autocompletar ítems del catálogo activo, con validación UX de item válido/duplicado y respaldo de validación backend existente.
- `REQ-079` | `done` | Aplicación global de paleta “Arctic Glass (Gradient Boost)” en toda la app mediante overrides de color en `theme.css`, sin cambios de layout/estructura ni lógica.
- `REQ-079B` | `done` | Reparación de consistencia del tema Arctic Glass: neutralización de colores legacy dark y unificación por tokens/overrides scopiados (tablas, paneles, inputs, botones, badges y modal).
- `REQ-080` | `done` | Rediseño visual de Inicio a dashboard limpio (header + botón, 6 KPI con “Ver detalle”, panel de indicadores y panel de acciones rápidas), sin cambios de lógica ni queries backend.
- `REQ-080A` | `done` | Ajuste puntual Home: corrección de fondo/estilo del bloque `Indicadores Rápidos` (`home-panel-header`) para eliminar franja/tono oscuro residual.
- `REQ-080B` | `done` | Ajuste puntual Nueva Requisición: campos `cliente_codigo`, `cliente_nombre`, `cliente_ruta_principal` mantienen fondo blanco y texto negro en negrita durante edición/focus/autofill.
- `REQ-080C` | `done` | Ajuste puntual modal Detalle: unificación de fondo y superficies internas al tema Arctic Glass (blanco con degradado azulado, sin gris legacy).
- `REQ-081` | `done` | Alerta adicional de inventario para ítems `RETORNABLE`: `ALERTA_RETORNO_INCOMPLETO` cuando `regresa < entregado`, con label/tooltip humano en modal y conteo automático en conciliación.
- `REQ-082` | `done` | Fix robusto de `ALERTA_RETORNO_INCOMPLETO`: normalización de modo/cantidades en backend, persistencia de alertas siempre como array JSON, normalización API y validación con tests DB/API.
- `REQ-083` | `done` | Validación fuerte de liquidación por cobertura: `Usado + No usado == Entregado` obligatorio y consistencia de `Regresa` por modo (`CONSUMIBLE` exacto, `RETORNABLE` no superior a cobertura), con bloqueo en backend/frontend y errores por fila.
- `REQ-084` | `done` | Unificación de fechas/horas: tablas SSR renderizan `YYYY-MM-DD HH:MM:SS` sin microsegundos y liquidación deja de guardar `liquidated_at` en UTC, evitando desfase de +6h en detalle futuro.
- `REQ-085` | `done` | Firma de recibido con PIN por receptor: usuarios con `pin_hash`/`puede_iniciar_sesion`, rol `tecnico`, entrega completa/parcial con receptor + validación PIN, trazabilidad `recibido_por_id/recibido_at` en detalle y timeline.
- `REQ-085A` | `done` | Ajuste de usuarios técnicos: ya no requieren contraseña al crear/editar; usan PIN obligatorio para firma y mantienen login deshabilitado.

## Post-MVP
- `REQ-089` | `done` | Admin puede eliminar cualquier requisición sin restricción de estado desde `/aprobar`, con confirmación JS y cascade delete de ítems.
- `REQ-090` | `done` | Nuevo rol `jefe_bodega` que combina `aprobador` + `bodega`: acceso completo a aprobar, bodega y liquidación; ve historial completo de entregas; ambos ítems de nav visibles.
- `REQ-090A` | `done` | Corrección de permisos/visibilidad de `jefe_bodega`: aprobación operativa habilitada también en backend (`puede_aprobar`) y enlaces del Home alineados con su rol mixto.
- `REQ-091` | `done` | Admin puede borrar todo el catálogo de items con doble verificación (checkbox + texto exacto), manteniendo la acción exclusiva al rol admin.
- `REQ-091A` | `done` | Ajuste de layout en catálogo admin: importar y borrar todo comparten fila superior; búsqueda baja a una fila independiente para mejorar jerarquía visual.
- `REQ-092` | `done` | El catálogo pasa a ser fuente de verdad para default de liquidación: `CatalogoItem.tipo_item` persistido y calculado automáticamente; liquidación usa ese valor por nombre normalizado y deja opción explícita cuando el tipo es `null`.
- `REQ-092A` | `done` | Fix de adopción de `tipo_item`: backfill automático para catálogo existente y fallback visual en liquidación cuando aún hay registros sin clasificar persistidos.
- `REQ-092B` | `done` | Fix técnico de `REQ-092`: extracción de la clasificación de catálogo a módulo independiente para eliminar import circular entre `database.py` y `crud.py`.
- `REQ-093` | `done` | Se agrega `Item.contexto_operacion` (`reposicion` / `instalacion_inicial`) por línea de requisición; `ALERTA_RETORNO_INCOMPLETO` deja de dispararse en instalaciones iniciales y el detalle muestra el contexto junto al tipo para trazabilidad.
- `REQ-093A` | `done` | En liquidación, `Tipo` deja de ser editable cuando el catálogo ya lo clasifica; solo se mantiene como selector en ítems sin `tipo_item`, y backend fuerza el valor de catálogo para evitar overrides manuales.
- `REQ-093B` | `done` | Ajuste de UX en detalle liquidado: la columna `DIF` ya no muestra signos ambiguos (`+/-`) y ahora comunica `Falta`, `Extra` u `OK` según el sentido operativo del retorno.
- `REQ-093C` | `done` | Ajuste de copy en detalle liquidado: el encabezado `Ingreso PK` ahora explicita `Ingreso PK (Bodega)` para dejar claro el responsable operativo del registro.
- `REQ-094` | `done` | Integración de exportación PDF para requisiciones liquidadas: endpoint `GET /requisiciones/{id}/pdf`, mapeo al modelo real, `pdf_url` en detalle y dependencia `reportlab`.
- `REQ-094A` | `done` | Ajuste de consistencia PDF vs detalle liquidado: `Ingreso PK (Bodega)` por ítem usa la cantidad operativa real y `DIF` muestra `Falta/Extra` con magnitud numérica, alineado con la app.
- `REQ-094B` | `done` | Ajuste de branding en PDF: el header superior izquierdo ahora usa el logo real de ProHygiene tomado de `static/branding/logo-prohygiene-es.png` en lugar del texto plano.
- `REQ-094C` | `done` | Fix de actor en PDF: la card de estado y la línea de tiempo ahora muestran el liquidador real (`liquidado_por_nombre`) en el evento `Liquidada`, evitando atribuir esa acción al aprobador.
- `REQ-093D` | `done` | El detalle de requisición ahora muestra `contexto_operacion` también antes de la liquidación, debajo de la descripción del ítem, para dar visibilidad completa del caso (`Reposición` / `Instalación inicial`) en todo el ciclo.
- `REQ-093E` | `done` | Ajuste de lógica de retorno esperado: en `RETORNABLE + instalacion_inicial`, la diferencia y alertas de faltante ya no tratan lo instalado por primera vez como equipo que debía regresar; el retorno esperado pasa a ser solo `No usado`.
- `REQ-093F` | `done` | Corrección de paridad PDF vs app para `instalacion_inicial`: la columna `DIF` del PDF ahora respeta `contexto_operacion` y deja de mostrar falsos faltantes en ítems retornables de primera instalación.
- `REQ-095` | `done` | Ajuste operativo de vista `Bodega`: usuarios `bodega` ahora ven todas las requisiciones pendientes de preparar o liquidar (`aprobada` + `entregada` elegible), mientras que su historial queda restringido a las que ellos prepararon o liquidaron.
- `REQ-096` | `done` | Actualización integral de `README.md` al estado real v1.x (roles, flujo completo, firma con PIN, liquidación, PDF y opciones de despliegue).
- `REQ-097` | `done` | Manejo de autenticación web: cuando no hay sesión, rutas SSR ahora redirigen a `/login` (en vez de mostrar `401`), manteniendo `401` JSON en rutas `/api/*`.
- `REQ-098` | `done` | Etiqueta "Para Demo" por ítem: campo `es_demo` booleano, visible en bodega, detalle y PDF; sin efecto en lógica de liquidación.
- `REQ-098A` | `done` | Fix visual checkbox Para Demo: corregido tipo de input de radio a checkbox en template y JS dinámico.
- `REQ-098B` | `done` | Fix visual checkbox Para Demo: border-radius cuadrado y checkmark ✓ visible en estado checked.
- `REQ-098C` | `done` | Fix definitivo checkbox Para Demo: `!important` para neutralizar `pico.css` y user agent stylesheet.
- `REQ-099` | `done` | Receptor designado al crear requisición: campo `receptor_designado_id`, selección obligatoria en `/crear`, visibilidad en firma de bodega con confirmación si cambia y exposición en API detalle.
- `REQ-099A` | `done` | Mejora UX de cambio de receptor en firma bodega (`gestionar` y `entrega parcial`): selector bloqueado por defecto, botón `Cambiar receptor`, advertencia visual integrada y retiro de `confirm()` del navegador.
- `REQ-099B` | `done` | UX antifallo en cambio de receptor: tras habilitar edición aparecen `Guardar cambio` y `Cancelar`; al guardar/cancelar el selector vuelve a bloquearse para evitar cambios accidentales.
- `REQ-099C` | `done` | Estado terminal `liquidada_en_prokey`: transición exclusiva de `jefe_bodega`, trazabilidad (`prokey_liquidada_at`/`prokey_liquidada_por`), botón `Confirmar en Prokey`, badge diferenciado y detalle/timeline actualizados.
- `REQ-099D` | `done` | Fix de migración SQLite para REQ-099C: reconstrucción automática de `requisiciones` cuando el CHECK de `estado` no incluye `liquidada_en_prokey`, evitando error 500 al confirmar en Prokey en DB históricas.
- `REQ-099E` | `done` | Permiso extendido de confirmación en Prokey para rol `admin` (backend + botón en bodega + test de acceso actualizado).
- `REQ-099F` | `done` | Fix de robustez en validación JS de `Liquidar`: normalización defensiva de campos numéricos (`''/NaN/coma decimal`) y recálculo stateless por evento para evitar botón deshabilitado residual.
- `REQ-099G` | `done` | Liquidación RETORNABLE: `Regresa > cobertura/entregado` deja de bloquear guardado y pasa a advertencia no bloqueante con alerta persistida (`ALERTA_RETORNO_EXTRA`).
- `REQ-099H` | `done` | PDF habilitado también para estado terminal `liquidada_en_prokey` (endpoint + `pdf_url` API + botón en detalle).
- `REQ-099I` | `done` | Incidente de despliegue Docker remoto: desalineación de versión entre `main.py` y `models.py` (atributos Prokey faltantes); se corrigió con guards defensivos + commit de modelo/migración y verificación en contenedor (`True True`).
- `REQ-091B` | `done` | Fix de layout en catálogo admin: se agregó la grilla CSS faltante (`form-grid-2`) para que el reordenamiento visual de tarjetas realmente se aplique.
- `REQ-100` | `done` | Importación masiva de usuarios desde XLSX/CSV (`NOMBRE`, `PUESTO`) con mapeo de puesto->rol/departamento, previsualización (`dry-run`) y ejecución idempotente (crear/actualizar).
- `REQ-100A` | `done` | Ajuste de naming en importación de usuarios: username generado como `inicial del primer nombre + primer apellido` (con sufijo por colisión) y documentación operativa actualizada.
- `REQ-101` | `done` | Cambio de contraseña por usuario autenticado (`GET/POST /mi-cuenta/password`) con validación de contraseña actual, longitud mínima, confirmación y bloqueo de reutilización.
- `REQ-102` | `done` | Logging estructurado JSON con `request_id`, middleware de trazabilidad de requests/errores y eventos de autenticación (login/login fallido/logout), con soporte opcional de archivo rotativo.

## Despliegue Producción
- `REQ-086` | `done` | Agregar Dockerfile, docker-compose.yml de la app y configuración de Caddy (`deploy/caddy/`) para despliegue LAN con reverse proxy. Red Docker externa `proxy` desacopla Caddy de cada servicio.
- `REQ-087` | `todo` | Smoke test de despliegue en servidor Proxmox: crear red `proxy`, levantar Caddy, levantar app, validar acceso desde LAN.
- `REQ-088` | `todo` | Migrar DB existente al volumen Docker (`./data/requisiciones.db`) antes del primer arranque en producción.

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

## Prioridad Baja
- `REQ-013` | `done` | Guia breve de despliegue LAN y backup operativo.
- `REQ-014` | `done` | Pulido UI minimo (mensajes flash, badges de estado, errores claros).
