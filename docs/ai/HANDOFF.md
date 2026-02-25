# Handoff Activo

## Estado actual
- Rama de reinicio creada desde commit base pre-liquidacion: `feat/liquidacion-rework-v2` en `3d7702b`.
- `REQ-060` completada en esta rama: ya existe estado `liquidada`, campos de liquidacion base y migracion SQLite robusta.
- Baseline de entrega normalizado: en entrega completa, `cantidad_entregada` queda persistida por item (sin depender de fallbacks).

## En progreso
- `REQ-061` pendiente de implementacion (UI y flujo de captura de liquidacion sobre la base ya creada en `REQ-060`).

## Proximo paso exacto
1. Diseñar y acordar el formulario de liquidacion minimo (`REQ-061`) reutilizando la data model agregada.
2. Implementar captura por item sin romper flujo actual (`pendiente -> aprobada/rechazada -> entregada`).
3. Exponer datos de liquidacion en detalle/API cuando corresponda.

## Riesgos abiertos
- Drift entre lo ya experimentado y lo que se va a rehacer en esta rama.
- Repetir complejidad innecesaria en liquidacion (evitar sobre-UX antes de validar flujo minimo).
- Mantener governance docs sincronizados en cada commit.

## Archivo / Historico (NO usar para ejecucion)
- El handoff largo anterior se considera historico.  
- Para ejecucion, usar solo este bloque activo.
