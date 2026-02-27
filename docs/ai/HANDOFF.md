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

## En progreso
- Definir siguiente incremento funcional post-liquidacion (reporteria minima y/o export operativo).
- Ejecutar smoke manual de liquidacion en UI para validar experiencia completa de bloqueo/edicion.
- Validar UX final de alertas en modal (copys, tooltips y consistencia de colores en distintos navegadores).
- Validar UX del comentario y notas en modal (saltos de linea y legibilidad en resoluciones medias).
- Validar UX del layout dashboard (desktop/laptop) para evitar overflow y scroll excesivo.
- Confirmar que el scope CSS del modal no afecta vistas externas (aprobar/bodega/listados).
- Revisar balance final de densidad visual para evitar sobrecarga en pantallas pequeñas.

## Proximo paso exacto
1. Ejecutar smoke manual de REQ-073 en `/aprobar` y `/bodega` (liquidada/no liquidada) verificando fullscreen, chips DIF y timeline vertical.
2. Confirmar en 1366x768 y móvil que el modal no genera scroll horizontal y mantiene legibilidad.
3. Definir siguiente REQ funcional (reporteria/export) en `TASKS`.

## Riesgos abiertos
- Drift entre lo ya experimentado y lo que se va a rehacer en esta rama.
- Repetir complejidad innecesaria en liquidacion (evitar sobre-UX antes de validar flujo minimo).
- Mantener governance docs sincronizados en cada commit.

## Archivo / Historico (NO usar para ejecucion)
- El handoff largo anterior se considera historico.  
- Para ejecucion, usar solo este bloque activo.
