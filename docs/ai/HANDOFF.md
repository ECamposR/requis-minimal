# Handoff Activo

## Estado actual
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
- `REQ-094` completada: el generador `app/pdf_generator.py` quedó integrado al backend real; `GET /requisiciones/{id}/pdf` produce PDF solo para requisiciones `liquidada`, el detalle API expone `pdf_url` y el botón `Ver PDF` del modal apunta al endpoint inline.
- `REQ-094A` completada: el PDF ya no toma `Ingreso PK` desde una referencia textual; ahora usa la cantidad operativa por ítem y la columna `DIF` muestra `Falta/Extra` con número, igual que el detalle web.
- `REQ-094B` completada: el PDF reemplaza el texto `ProHygiene` del header por el logo real usado en la app (`static/branding/logo-prohygiene-es.png`), manteniendo fallback textual si el recurso no carga.
- `REQ-091B` completada: se corrigió el faltante de CSS (`form-grid-2`) que impedía ver el nuevo layout del catálogo; ahora el orden visual sí se aplica.

## Despliegue en producción (nuevo frente)
- Stack Docker + Caddy configurado y listo en el repo (`Dockerfile`, `docker-compose.yml`, `deploy/caddy/`).
- Pendiente ejecutar en servidor real: `REQ-087` (smoke test) y `REQ-088` (migrar DB existente).
- Ver `docs/ai/DECISIONS.md` ADR-004 para la justificación completa.

## En progreso
- Definir siguiente incremento funcional post-liquidacion (reporteria minima y/o export operativo).
- Ejecutar smoke manual de entrega con firma y de liquidacion para validar experiencia completa de bloqueo/edicion.
- Validar UX final de alertas en modal (copys, tooltips y consistencia de colores en distintos navegadores).
- Validar UX del comentario y notas en modal (saltos de linea y legibilidad en resoluciones medias).
- Validar UX del layout dashboard (desktop/laptop) para evitar overflow y scroll excesivo.
- Confirmar que el scope CSS del modal no afecta vistas externas (aprobar/bodega/listados).
- Revisar balance final de densidad visual para evitar sobrecarga en pantallas pequeñas.

## Proximo paso exacto
### Frente despliegue (REQ-087 / REQ-088):
1. En el servidor Docker: `docker network create proxy`
2. `cd deploy/caddy && docker compose up -d`
3. Copiar DB existente: `mkdir -p data && cp /ruta/actual/requisiciones.db data/requisiciones.db`
4. Crear `.env` desde `.env.example` con `SECRET_KEY` real y `DATABASE_URL=sqlite:////app/data/requisiciones.db`
5. `docker compose up -d` (desde raíz del repo)
6. Validar acceso LAN: `http://<IP-servidor>/`

### Frente funcional (pendiente anterior):
1. Crear una requisición con un item retornable marcado como `Instalación inicial`, entregarla y liquidarla con `Regresa = 0` para confirmar que no aparece `Retorno incompleto`.
2. Abrir el detalle de esa requisición y verificar que la columna `Tipo` muestre el contexto operativo junto al modo (`RETORNABLE / Instalación inicial`).
3. Abrir una requisición `liquidada`, pulsar `Ver PDF` y validar que el documento carga inline con datos reales, alertas y timeline sin errores de Unicode.
4. Validar un caso con `Regresa` menor al esperado para confirmar que el PDF muestra `Falta X` y que `Ingreso PK (Bodega)` coincide con el detalle web.
5. Validar visualmente el encabezado del PDF para confirmar que el logo se ve bien escalado y no invade el bloque del folio.

## Riesgos abiertos
- Drift entre lo ya experimentado y lo que se va a rehacer en esta rama.
- Repetir complejidad innecesaria en liquidacion (evitar sobre-UX antes de validar flujo minimo).
- Mantener governance docs sincronizados en cada commit.
- El entorno actual deja `TestClient` colgado incluso contra `/health`; para validar REQ-085 se usó compilación y smoke directo de modelo/auth/CRUD con DB temporal, pero falta smoke HTTP/manual real.

## Archivo / Historico (NO usar para ejecucion)
- El handoff largo anterior se considera historico.  
- Para ejecucion, usar solo este bloque activo.
