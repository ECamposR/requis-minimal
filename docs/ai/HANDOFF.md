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

## En progreso
- Definir siguiente incremento funcional post-liquidacion (reporteria minima y/o export operativo).
- Ejecutar smoke manual de liquidacion en UI para validar experiencia completa de bloqueo/edicion.
- Validar UX final de alertas en modal (copys, tooltips y consistencia de colores en distintos navegadores).
- Validar UX del comentario y notas en modal (saltos de linea y legibilidad en resoluciones medias).

## Proximo paso exacto
1. Ejecutar smoke manual en navegador para REQ-070 (con y sin comentario, con y sin notas por item).
2. Correr `pytest -q tests/test_liquidacion.py -v` como validacion cruzada tras REQ-070.
3. Definir siguiente REQ funcional (reporteria/export) en `TASKS`.

## Riesgos abiertos
- Drift entre lo ya experimentado y lo que se va a rehacer en esta rama.
- Repetir complejidad innecesaria en liquidacion (evitar sobre-UX antes de validar flujo minimo).
- Mantener governance docs sincronizados en cada commit.

## Archivo / Historico (NO usar para ejecucion)
- El handoff largo anterior se considera historico.  
- Para ejecucion, usar solo este bloque activo.
