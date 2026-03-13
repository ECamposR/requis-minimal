# Handoff Activo

## Estado actual
- La app ya no debe tratarse como MVP: desde el `2026-03-10` esta en `beta operativa en produccion controlada` dentro de la LAN, con usuarios y uso real.
- La gobernanza vigente mantiene el espiritu original de simplicidad, pero endurece la exigencia documental: cualquier bug, cambio, hallazgo o decision relevante debe quedar registrado en `WORKLOG/TASKS/HANDOFF/DECISIONS` segun aplique.
- Rama activa: `chore/ui-usabilidad-ajustes`, destinada a ajustes incrementales de UI/usabilidad sin alterar la logica de negocio.
- `REQ-127` completada en esta rama: `Aprobar` queda como bandeja de pendientes y la consulta global se mueve a `Todas las Requisiciones` (`/todas-requisiciones`) con filtros por estado, departamento y rango de fechas para roles de supervision.
- `REQ-128` completada en esta rama: los filtros basados en selectores (`estado`/`departamento`) ahora se autoaplican en `Aprobar` y `Todas las Requisiciones`; el boton `Buscar` se conserva para texto libre y fechas.
- Frente activo en rama `feat/bi-dashboard`: `Monitor de Actividad` para `admin`, `aprobador` y `jefe_bodega`.
- `REQ-119` completada: el navbar ya agrupa los accesos `admin` bajo un dropdown `Administracion` y el bloque de usuario ahora despliega `Cambiar contrasena` + `Salir`, reduciendo ancho horizontal sin introducir JS adicional.
- `REQ-123` completada en `main`: `Gestionar Entrega` y `Entrega Parcial` ahora fuerzan en JS el estado inicial bloqueado del receptor; el selector solo se habilita tras pulsar `Cambiar receptor`.
- Contexto de negocio clave del Monitor de Actividad: esta app funciona como registro de contingencias cuando Prokey ya cerro rutas a las `14:00`. El monitor debe explicar `por que`, `quien`, `que` y `cuando` ocurre ese uso para ayudar a reducirlo, no para medir productividad.
- Rama de reinicio creada desde commit base pre-liquidacion: `feat/liquidacion-rework-v2` en `3d7702b`.
- `REQ-060` completada en esta rama: ya existe estado `liquidada`, campos de liquidacion base y migracion SQLite robusta.
- Baseline de entrega normalizado: en entrega completa, `cantidad_entregada` queda persistida por item (sin depender de fallbacks).
- `REQ-061` completada: captura de liquidacion en UI/endpoint con alertas no bloqueantes e inmutabilidad post-liquidacion.
- `REQ-062` completada: detalle de requisiciones liquidadas en modo solo lectura con tabla papel, resumen de liquidacion y timeline.
- `REQ-063` completada: tests de integracion de flujo completo de liquidacion y escenarios canónicos.
- `REQ-064` completada: `prokey_ref` ya no es obligatorio al liquidar; si falta, queda `NULL` y el detalle lo marca como "Pendiente" con badge operativo.
- `REQ-065` completada: ya existe pantalla dedicada para completar `prokey_ref` en estado `liquidada`, con permisos para admin o solicitante y sin tocar cantidades de liquidacion.
- `REQ-066` completada: captura de liquidacion por item ahora usa modo `RETORNABLE/CONSUMIBLE`, renombra `No usado` y calcula alertas por diferencia segun modo.
- `REQ-067` completada: detalle (API + modal) de requisiciones liquidadas ya refleja columnas y calculos por modo, incluyendo `Ingreso PK` solo para retornables.
- `REQ-068` completada: bloqueo de liquidacion si un item entregado queda "sin definir" (todo en cero), con re-render conservando datos, resaltado de filas incompletas y defensa doble en backend.
- `REQ-069` completada: modal de detalle traduce codigos `ALERTA_*` a etiquetas humanas y muestra detalle numerico en tooltip, manteniendo severidad visual y trazabilidad interna.
- `REQ-070` completada: modal liquidada ahora muestra comentario general (con placeholder `—` cuando falta) y nota por item bajo la descripcion; endpoint normaliza ambos campos.
- `REQ-071` completada: modal detalle rediseñado a formato dashboard con cards de contexto/estado/alertas de conciliación, timeline lateral, DIF consistente por signo y secciones secundarias colapsables.
- `REQ-072` completada: refinamiento visual del dashboard del modal (badges/severidades, contraste DIF, densidad de tabla, notas y colapsables), todo scoped a `#modal-detalle`.
- `REQ-073` completada: ajuste fino visual acercando la propuesta (cards compactas con kv, timeline vertical con nodos, DIF como chip con signo y modal casi fullscreen scoped).
- `REQ-074` completada: pulido UX del dashboard del detalle (label "Alta severidad", acción sugerida por prioridad de alertas, `Ingreso PK` en consumibles como `—`, columnas numéricas centradas y botón PDF activo solo cuando estado=`liquidada`).
- `REQ-075` completada: fix de desfase +6h en `created_at` para nuevas requisiciones (se guarda explícitamente hora local en creación, evitando UTC de `func.now()` en SQLite).
- `REQ-076` completada: catálogo admin con buscador `q` por nombre (filtro case-insensitive server-side), input persistente, botón limpiar y conteo contextual en pantalla.
- `REQ-077` completada: creación de requisiciones con autocompletado nativo (`datalist`) para ítems de catálogo activo y validación UX para impedir ítems no válidos o duplicados antes de agregar/enviar.
- `REQ-079` completada: actualización visual global a tema Arctic Glass (Gradient Boost) aplicada solo con CSS (colores/tokens), sin cambios de estructura ni flujo funcional.
- `REQ-079B` completada: hardening visual del tema Arctic Glass sobre estilos legacy (dark) con overrides de alta prioridad y tokens unificados para tablas, paneles, formularios, botones, badges y detalle.
- `REQ-080` completada: home `/` renovado a dashboard limpio con seis KPIs, panel de indicadores y acciones rápidas, con estilos scopiados (`route-home`) para evitar impacto en otras vistas.
- `REQ-080A` completada: corrección de fondo en bloque `Indicadores Rápidos` (header del panel) para eliminar tono oscuro heredado.
- `REQ-080B` completada: mejora de legibilidad en campos de cliente de `Nueva Requisición` (fondo blanco + texto negro en negrita en edición/focus/autofill).
- `REQ-080C` completada: modal de detalle alineado al tema Arctic Glass, eliminando superficie gris residual en contenedor principal y tarjetas internas.
- `REQ-081` completada: nueva alerta de inventario `ALERTA_RETORNO_INCOMPLETO` para ítems `RETORNABLE` cuando `regresa < entregado`, visible en detalle con label/tooltip humano e incluida en conteos de conciliación.
- `REQ-082` completada: corrección del bug donde `ALERTA_RETORNO_INCOMPLETO` no aparecía de forma consistente; backend ahora normaliza `delivered/returned/mode`, persiste `liquidation_alerts` siempre como array JSON y API entrega lista robusta para UI.
- `REQ-083` completada: liquidación ahora exige cobertura real (`Usado + No usado == Entregado`) y consistencia de `Regresa` por modo antes de guardar; frontend resalta filas inválidas, muestra mensaje por fila y deshabilita `Liquidar` hasta corregir.
- `REQ-084` completada: fechas de tablas SSR unificadas sin microsegundos y `liquidated_at` ahora se guarda en hora local; `fmtDateTime` del modal evita conversiones de zona horaria al formatear strings del API.
- `REQ-085` completada: firma de recibido con PIN por receptor en flujo de bodega, soporte de usuarios `tecnico` sin login, y nueva trazabilidad `recibido_por_id/recibido_at` visible en API y timeline.
- `REQ-085A` completada: alta/edicion de usuarios `tecnico` ya no exige contraseña; el PIN pasa a ser el dato obligatorio operativo para firma, manteniendo `puede_iniciar_sesion=False`.
- Fix posterior aplicado sobre `REQ-085A`: `POST /admin/usuarios` ya no declara `password` como `Form(...)`; ahora acepta valor vacio y la validacion real queda gobernada por rol (tecnico sin contraseña, otros roles con contraseña).
- `REQ-090A` completada: `jefe_bodega` ya aprueba requisiciones de forma efectiva en backend (no solo por UI/nav), el Home ahora le muestra también los accesos/acciones de aprobar y bodega, y `/aprobar` vuelve a exponer el botón `Gestionar` para ese rol.
- `REQ-091` completada: admin ya puede borrar todo el catálogo desde una acción dedicada con doble verificación real (checkbox + texto `BORRAR CATALOGO`), sin abrir permisos a otros roles.
- `REQ-091A` completada: el layout del catálogo admin se reordenó para mostrar `Importar` y `Borrar todo` lado a lado, dejando `Buscar` debajo.
- `REQ-092` completada: `CatalogoItem.tipo_item` ya persiste el default `RETORNABLE/CONSUMIBLE/null`, calculado automáticamente por primera palabra; la pantalla de liquidación toma ese valor desde catálogo (por nombre normalizado) y deja selección explícita cuando no hay match.
- `REQ-092A` completada: se corrigió el caso de catálogo histórico sin `tipo_item`; `run_migrations()` ahora hace backfill y liquidación tiene fallback para no mostrar `Seleccionar...` cuando el nombre sí clasifica.
- `REQ-092B` completada: se eliminó la import circular creada por el backfill de catálogo; la clasificación ahora vive en `app/catalog_types.py`, reutilizable tanto por migraciones como por runtime.
- `REQ-093` completada: cada `Item` ahora persiste `contexto_operacion` (`reposicion` / `instalacion_inicial`) desde la creación de la requisición; el detalle de liquidación lo muestra junto al tipo y `ALERTA_RETORNO_INCOMPLETO` ya no se genera para instalaciones iniciales.
- `REQ-093A` completada: en liquidación el `Tipo` ya no se puede cambiar si el catálogo lo definió; UI lo muestra como chip de solo lectura y backend ignora overrides manuales, manteniendo selector solo para ítems sin clasificación.
- `REQ-093B` completada: la columna `DIF` en el detalle liquidado ya no usa `+/-` ambiguos; ahora renderiza `Falta`, `Extra` u `OK` con tooltip explicativo según el retorno esperado vs regresado.
- `REQ-093C` completada: el detalle liquidado ahora muestra `Ingreso PK (Bodega)` en el encabezado de la columna para reforzar que ese valor corresponde al registro operativo de bodega.
- `REQ-093D` completada: el detalle de requisición ya muestra `Reposición` / `Instalación inicial` también fuera de la etapa de liquidación, debajo de la descripción de cada ítem solicitado, manteniendo trazabilidad del contexto operativo durante todo el flujo.
- `REQ-093E` completada: la diferencia y las alertas de faltante ahora respetan `contexto_operacion`; para `RETORNABLE + instalacion_inicial` el retorno esperado ya no es `Usado + No usado`, sino solo `No usado`, evitando falsos faltantes en instalaciones iniciales.
- `REQ-093F` completada: el PDF de liquidación quedó alineado con la lógica anterior; su `DIF` ya no calcula faltante en `RETORNABLE + instalacion_inicial` cuando `Regresa=0` y `No usado=0`.
- `REQ-095` completada: la vista `Bodega` para rol `bodega` ahora expone todas las requisiciones operativas pendientes (`aprobada` y `entregada` lista para liquidar`) en una sola sección, pero el historial personal queda filtrado a las requisiciones que ese usuario preparó o liquidó.
- `REQ-096` completada: `README.md` actualizado al estado real v1.x (flujo vigente, roles actuales, firma con PIN, liquidación, PDF y opciones de despliegue local/Docker+Caddy).
- `REQ-097` completada: autenticación web ajustada para UX de entrada por IP/puerto; usuarios sin sesión ya no ven `401` en SSR y son redirigidos a `/login`, mientras `/api/*` conserva respuesta `401` JSON.
- `REQ-098` completada: cada línea de ítem ya puede marcarse como `Para Demo` al crear requisición (`Item.es_demo`), quedando visible en bodega, detalle y PDF sin alterar ninguna fórmula/alerta de liquidación.
- `REQ-098A/REQ-098B/REQ-098C` completadas: cierre de ajuste visual del control `Para Demo`; quedó como checkbox cuadrado con `✓` visible y estilos reforzados (`!important`) para neutralizar overrides de `pico.css` y del user agent (`appearance/border-radius`).
- `REQ-099` completada: creación de requisición ahora exige `receptor_designado` (usuario activo), se persiste en `requisiciones.receptor_designado_id`, bodega visualiza el designado en la captura de firma y, si selecciona receptor distinto, el sistema pide confirmación explícita antes de guardar.
- `REQ-099A` completada: en firma de bodega (`Gestionar Entrega` y `Entrega Parcial`) se reemplazó el `confirm()` por UX deliberada en página (selector de receptor bloqueado inicialmente + botón `Cambiar receptor` + advertencia visual integrada al habilitar cambio).
- `REQ-099B` completada: refuerzo UX para evitar cambios accidentales de receptor; al activar edición aparecen botones explícitos `Guardar cambio` / `Cancelar` y el selector vuelve a bloquearse tras confirmar o revertir.
- `REQ-099C` completada: se agregó cierre terminal `liquidada_en_prokey` (inmutable), con endpoint `POST /requisiciones/{id}/liquidar-prokey` exclusivo para `jefe_bodega`, persistencia de actor/fecha de cierre en Prokey y visualización en badge + detalle + timeline.
- `REQ-099D` completada: fix para DB históricas SQLite; `run_migrations()` ahora reconstruye `requisiciones` cuando detecta CHECK de `estado` sin `liquidada_en_prokey`, corrigiendo el 500 en `Confirmar en Prokey`.
- `REQ-099E` completada: el permiso de `Confirmar en Prokey` se extendió también a `admin` (UI en bodega + guard backend + test de permisos actualizado).
- `REQ-099F` completada: corrección de validación intermitente en `templates/liquidar.html`; la lectura numérica ahora normaliza `vacío/NaN/coma decimal` a `0` y el estado del botón `Liquidar` se recalcula completo en cada evento sin residuos.
- `REQ-099G` completada: en `RETORNABLE`, `Regresa` mayor que cobertura ya no bloquea `Liquidar`; frontend lo muestra como advertencia y backend lo acepta para registrar alerta operativa (`ALERTA_RETORNO_EXTRA`).
- `REQ-099H` completada: el PDF vuelve a estar disponible también tras el cierre final `liquidada_en_prokey` (URL API + endpoint + habilitación de botón en detalle).
- `REQ-099I` completada: incidente remoto Docker resuelto; se detectó build mixto (`main.py` nuevo + `models.py` viejo), se aplicaron guards de compatibilidad y se publicó el modelo/migración faltante. Verificación final en contenedor: `hasattr(Requisicion,'prokey_liquidator') == True` y `hasattr(Requisicion,'prokey_liquidada_at') == True`.
- `REQ-100` completada: importación masiva de usuarios desde XLSX/CSV (`NOMBRE`, `PUESTO`) en `/admin/usuarios`, con previsualización (`dry-run`), mapeo de puesto a `rol/departamento`, generación de `username` y ejecución idempotente de crear/actualizar.
- `REQ-100A` completada: la regla de `username` de la importación quedó fijada a `inicial del primer nombre + primer apellido` (ej. `Carlos Humberto Ramirez Segura` -> `cramirez`), manteniendo sufijo numérico por colisión.
- `REQ-101` completada: usuarios con sesión habilitada ya pueden cambiar su contraseña en `/mi-cuenta/password`; backend valida contraseña actual, mínimo de 8 caracteres, confirmación y evita reutilizar la misma contraseña.
- `REQ-102` completada: observabilidad base activada con logs JSON, `request_id` por request, trazabilidad de latencia/estado por ruta y eventos de autenticación (login exitoso/fallido/logout), más opción de archivo rotativo por variables de entorno.
- `REQ-103` completada: creación de requisición ahora exige seleccionar `motivo_requisicion` desde catálogo fijo de clasificaciones; el valor se persiste en DB sin impactar lógica operativa actual.
- `REQ-104` completada: solicitante puede editar su requisición solo mientras siga en `pendiente` y sin aprobación (`approved_by is None`), con actualización de cliente/ruta/receptor/motivo/justificación e ítems.
- `REQ-105` completada: selector de receptor ahora incluye buscador por texto para filtrar usuarios rápidamente en creación/edición de requisición y en firma de bodega (entrega completa y parcial).
- `REQ-105A` completada: `Gestionar Entrega` ahora muestra un error visible cuando la firma no se procesa (PIN faltante/incorrecto o receptor inválido), evitando la sensación de “no hizo nada”.
- `REQ-094` completada: el generador `app/pdf_generator.py` quedó integrado al backend real; `GET /requisiciones/{id}/pdf` produce PDF solo para requisiciones `liquidada`, el detalle API expone `pdf_url` y el botón `Ver PDF` del modal apunta al endpoint inline.
- `REQ-094A` completada: el PDF ya no toma `Ingreso PK` desde una referencia textual; ahora usa la cantidad operativa por ítem y la columna `DIF` muestra `Falta/Extra` con número, igual que el detalle web.
- `REQ-094B` completada: el PDF reemplaza el texto `ProHygiene` del header por el logo real usado en la app (`static/branding/logo-prohygiene-es.png`), manteniendo fallback textual si el recurso no carga.
- `REQ-094C` completada: se corrigió la atribución de actor en PDF; el evento `Liquidada` y la card de estado usan `liquidado_por_nombre` (liquidador real), no el aprobador.
- `REQ-091B` completada: se corrigió el faltante de CSS (`form-grid-2`) que impedía ver el nuevo layout del catálogo; ahora el orden visual sí se aplica.

## Despliegue en producción (nuevo frente)
- Stack Docker + Caddy configurado y listo en el repo (`Dockerfile`, `docker-compose.yml`, `deploy/caddy/`).
- Pendiente ejecutar en servidor real: `REQ-087` (smoke test) y `REQ-088` (migrar DB existente).
- Ver `docs/ai/DECISIONS.md` ADR-004 para la justificación completa.

## En progreso
- Fase 1 del `Monitor de Actividad` completada.
- `REQ-118A` completada: backend base ya existe con guard de roles y API `/api/dashboard/basicos` entregando payload para motivos, top solicitantes, top items y horario con `alert_from_hour=14`; la vista institucional ahora vive en `/monitor`.
- `REQ-118B` completada: `/monitor` ya renderiza `monitor_actividad.html` con grid SSR 2x2, cuatro `canvas` listos para Chart.js y enlace `Monitor de Actividad` visible solo para `admin`, `aprobador` y `jefe_bodega`.
- `REQ-118C` completada: el Monitor de Actividad ya carga datos por Fetch API, renderiza los 4 graficos con `Chart.js` y aplica color de alerta a las barras desde las `14:00` en adelante.
- Fase 2 del `Monitor de Actividad` definida y pendiente de ejecucion: auditoria de diferencias, discrepancias y merma usando `calcular_retorno_esperado` como fuente comun de verdad para el delta operativo.
- `REQ-118D` completada: backend `GET /api/dashboard/auditoria` ya procesa requisiciones cerradas (`liquidada` + `liquidada_en_prokey`), reutiliza `calcular_retorno_esperado`, entrega KPIs de discrepancia/inversion en demos y datasets para diferencia por producto y diferencias por tecnico.
- `REQ-118E` completada: `monitor_actividad.html` ya incluye una segunda seccion SSR para auditoria/diferencias con dos KPI cards y dos nuevos `canvas` para graficos de perdida.
- `REQ-118F` completada: el frontend ya consume `/api/dashboard/auditoria`, renderiza KPIs y graficos de diferencias en paleta de alerta sin romper los graficos de la Fase 1.
- `REQ-118G` completada: se agregan endpoints de drill-down para los KPI de auditoria, permitiendo listar requisiciones cerradas con diferencia y requisiciones cerradas con demo.
- `REQ-118H` completada: los KPI `Indice de Discrepancia` e `Inversion en Demos` ahora muestran boton `Ver detalle` y un panel inline con las requisiciones relacionadas dentro del mismo monitor.
- Definir siguiente incremento funcional post-liquidacion (reporteria minima y/o export operativo).
- Ejecutar smoke manual de entrega con firma y de liquidacion para validar experiencia completa de bloqueo/edicion.
- Validar UX final de alertas en modal (copys, tooltips y consistencia de colores en distintos navegadores).
- Validar UX del comentario y notas en modal (saltos de linea y legibilidad en resoluciones medias).
- Validar UX del layout dashboard (desktop/laptop) para evitar overflow y scroll excesivo.
- Confirmar que el scope CSS del modal no afecta vistas externas (aprobar/bodega/listados).
- Revisar balance final de densidad visual para evitar sobrecarga en pantallas pequeñas.

## Proximo paso exacto
### Frente BI / Monitor de Actividad (`REQ-118`):
1. Validar visualmente la Fase 2 del Monitor de Actividad con datos reales y ajustar densidad/etiquetas si algun grafico se satura.
2. Definir la siguiente iteracion BI: filtros de periodo/departamento o nuevas metricas de auditoria (`tiempos de liquidacion`, `diferencias por motivo`, `tendencia semanal`).

### Frente despliegue (REQ-087 / REQ-088):
1. En el servidor Docker: `docker network create proxy`
2. `cd deploy/caddy && docker compose up -d`
3. Copiar DB existente: `mkdir -p data && cp /ruta/actual/requisiciones.db data/requisiciones.db`
4. Crear `.env` desde `.env.example` con `SECRET_KEY` real y `DATABASE_URL=sqlite:////app/data/requisiciones.db`
5. `docker compose up -d` (desde raíz del repo)
6. Validar acceso LAN: `http://<IP-servidor>/`

### Frente funcional (pendiente anterior):
1. Validar manualmente en UI el caso mixto: una requisición con dos ítems retornables, uno en `Instalación inicial` y otro en `Reposición`, para confirmar que la tabla de liquidación refleja diferencias distintas por fila según contexto.
2. Abrir el detalle de esa requisición y verificar que la columna `Tipo` muestre el contexto operativo junto al modo (`RETORNABLE / Instalación inicial`) y que el ítem de instalación inicial no marque `Falta`.
3. Abrir una requisición `liquidada`, pulsar `Ver PDF` y validar que el documento carga inline con datos reales, alertas y timeline sin errores de Unicode.
4. Validar un caso con `Regresa` menor al esperado para confirmar que el PDF muestra `Falta X` y que `Ingreso PK (Bodega)` coincide con el detalle web.
5. Validar visualmente el encabezado del PDF para confirmar que el logo se ve bien escalado y no invade el bloque del folio.
6. Validar con un usuario `bodega` que `/bodega` muestra todas las `aprobada` y `entregada` pendientes de acción, pero que el historial solo conserva las que él preparó o liquidó.

## Riesgos abiertos
- Drift entre lo ya experimentado y lo que se va a rehacer en esta rama.
- Repetir complejidad innecesaria en liquidacion (evitar sobre-UX antes de validar flujo minimo).
- Mantener governance docs sincronizados en cada commit.
- El entorno actual deja `TestClient` colgado incluso contra `/health`; para validar REQ-085 se usó compilación y smoke directo de modelo/auth/CRUD con DB temporal, pero falta smoke HTTP/manual real.

## Ultimo cambio cerrado
- `REQ-118A` completada: backend base del Monitor de Actividad implementado. Ya existen `/monitor` y `/api/dashboard/basicos` con autorizacion para `admin`, `aprobador` y `jefe_bodega`; la API entrega las 4 agregaciones base listas para la UI actual.
- `REQ-118` completada: el workstream BI quedo formalmente abierto en rama dedicada y ya se descompuso en la epica `EPIC-BI-01` con tareas ejecutables `REQ-118A/B/C`, hoy institucionalizado como `Monitor de Actividad`.
- `REQ-117` completada: `Gestionar Entrega` ya no exige firma/PIN cuando el resultado es `no_entregada`, incluso si existe receptor designado o el frontend envia `recibido_por_id`; backend ignora la firma en ese caso, UI oculta los campos y solo exige comentario para cerrar la requisicion.
- `REQ-116` completada: documentacion de gobernanza y estado del producto actualizada para reflejar `beta operativa en produccion`, continuidad agnostica al LLM/herramienta y trazabilidad documental obligatoria como regla del repo.
- `REQ-106` completada: el catalogo ahora persiste `permite_decimal` como fuente de verdad. Solo `CONCENTRADO SHF` y `LIQUIDO CONCENTRADO DESODORIZADOR` quedan habilitados para cantidades decimales; crear/editar requisicion ajusta la UX del campo cantidad y el backend rechaza decimales para cualquier otro item activo del catalogo.
- `REQ-106A` completada: se corrigio la validacion JS del selector de items en crear/editar para aceptar tanto payload legado de strings como payload enriquecido de objetos, evitando falsos rechazos al enviar requisiciones.
- `REQ-106B` completada: la misma restriccion de enteros/decimales ahora aplica en liquidacion. Solo items con `permite_decimal` en catalogo aceptan fracciones en `Regresa`, `Usado` y `No usado`; el resto se bloquea con mensaje claro en frontend y backend.
- `REQ-106C` completada: se corrigio la validacion reactiva de `liquidar.html` para que el boton `Liquidar` se rehabilite al corregir un valor invalido, sin requerir recarga de pagina ni perder captura previa.
- `REQ-106D` completada: se reforzo la reevaluacion del formulario de liquidacion con listeners adicionales y sincronizacion diferida para evitar que el boton quede congelado despues de editar inputs numericos invalidos.
- `REQ-106E` completada: la liquidacion ahora muestra una alerta visual especifica cuando el bloqueo se debe a decimales no permitidos, con banner global y fila resaltada.
- `REQ-107` completada: crear/editar requisicion ahora incluye ayuda contextual en `Contexto operativo`, aclarando que `Instalacion inicial` se usa solo para `R1E` o `Demostracion`.
- `REQ-107A` completada: la vista de liquidacion ahora incluye ayuda contextual breve sobre la regla operativa de captura para orientar a bodega.
- `REQ-107B` completada: el campo `Referencia comprobante Prokey` se retiro de la vista de liquidacion; la referencia queda solo para consulta en detalle.
- `REQ-108` completada: el rol `bodega` plano ya no puede crear ni consultar sus propias requisiciones; navbar/home ocultan esos accesos y backend redirige `/crear`, `/mis-requisiciones`, editar y eliminar hacia `/bodega` sin afectar `jefe_bodega`.
- `REQ-109` completada: el PDF ya puede abrirse desde `aprobada` en adelante; el endpoint `/requisiciones/{id}/pdf` y el botón `Ver PDF` del detalle quedaron habilitados para `aprobada`, `entregada`, `liquidada` y `liquidada_en_prokey`.
- `REQ-109A` completada: el PDF distingue el caso `aprobada` pre-entrega; la tabla de ítems ya no titula `Entregado` ni usa `cantidad_entregada`, sino `Solicitado` con la cantidad original de la requisición.
- `REQ-110` completada: se agregó el estado previo `preparado` entre `aprobada` y `entregada`. Bodega ahora debe accionar `Preparar` primero y solo después puede abrir `Gestionar Entrega` para capturar firma/PIN y cerrar la entrega. El estado nuevo tiene trazabilidad (`prepared_at`/`prepared_by`), aparece en detalle/timeline/badges, entra en filtros y el PDF lo trata como etapa pre-entrega (muestra solicitado).
- `REQ-110A` completada: el paso `Preparar` ya no cambia estado desde el listado; ahora abre una vista dedicada con tabla de ítems y botones `Preparado` / `Cancelar` para confirmar deliberadamente la transición a `preparado`.
- `REQ-111` completada: `Ingreso PK (Bodega)` ya no equivale a `Regresa`. Para retornables ahora usa la formula compartida `min(used, returned) + max(returned - delivered, 0)`; consumibles siguen en `0`. El detalle web y el PDF salen del mismo payload/cuenta.
- `REQ-112` completada: la pantalla de liquidacion ahora muestra por item el `Contexto operativo` (`Reposicion` / `Instalacion inicial`) y la etiqueta `Para Demo`, reutilizando solo datos ya persistidos y sin tocar validaciones ni formulas.
- `REQ-112A` completada: la columna visual `Ocupo` se oculto de la captura de liquidacion; la suma `Usado + No usado` sigue usandose internamente para cobertura y mensajes, pero ya no se muestra como columna para reducir confusion.
- `REQ-113` completada: las vistas `Mis Requisiciones`, `Aprobar` y `Bodega` ya no renombran estados de forma distinta por pantalla. `status_badge` ahora normaliza etiquetas amigables (`Aprobada`, `Pendiente de aprobar`, `Liquidada en Prokey`, etc.) y las tablas consumen el estado real.
- `REQ-113A` completada: el chip de `Contexto operativo` en liquidacion subio contraste (fondo, borde y peso tipografico) para que `Reposicion` / `Instalacion inicial` no se pierdan sobre el fondo dark.
- `REQ-114` completada: admin ya puede generar respaldos ZIP y restaurarlos desde UI dedicada (`/admin/respaldos`). El alcance queda limitado a la DB SQLite + manifest; la restauracion crea backup previo, bloquea temporalmente requests y fuerza nuevo login.
- `REQ-114A` completada: se corrigio el primer bug operativo de `Respaldos`; el logger ya no intenta sobrescribir el atributo reservado `filename` de `LogRecord` y ahora registra `backup_filename/backup_source/safety_backup` sin romper la generacion del ZIP.
- `REQ-114B` completada: `README.md` ya incluye guia de contingencia para reconstruir `.env`, con `DATABASE_URL` exacta de Docker, generacion de `SECRET_KEY`, pasos de recreacion y comando de verificacion.
- `REQ-115` completada: el modal de detalle ya muestra el `receptor_designado` (nombre + rol) dentro de `Informacion general`; el dato ya venia en la API y faltaba solo renderizarlo en `static/app.js`.
- `REQ-115A` completada: el bloque `Resultado entrega` en la tarjeta `Estado liquidacion` ya no usa combinaciones lavadas sobre fondo gris; `resultado-chip` quedo reforzado con mejor fondo, borde y color de texto.

## Archivo / Historico (NO usar para ejecucion)
- El handoff largo anterior se considera historico.  
- Para ejecucion, usar solo este bloque activo.
