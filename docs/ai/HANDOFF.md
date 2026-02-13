# Handoff Activo

## Estado actual
- Rama de reinicio creada desde commit base pre-liquidacion: `feat/liquidacion-rework-v2` en `3d7702b`.
- Alcance funcional vigente: hasta `REQ-059` (sin estado `liquidada`, sin campos de liquidacion).
- Objetivo de esta rama: rehacer la liquidacion desde cero con enfoque mas simple y trazable.

## En progreso
- `REQ-060` reabierta en modo `in_progress` para nueva implementacion de liquidacion.

## Proximo paso exacto
1. Definir y congelar en `TASKS` la nueva regla operativa de liquidacion (modelo papel).
2. Implementar `REQ-060` minimo:
   - estado `liquidada`,
   - campos base por item para liquidacion,
   - migracion SQLite incremental segura.
3. Ejecutar smoke test manual de flujo completo: `pendiente -> aprobada/rechazada -> entregada`.
4. Solo despues abrir `REQ-061` (UI/validaciones de liquidacion).

## Riesgos abiertos
- Drift entre lo ya experimentado y lo que se va a rehacer en esta rama.
- Repetir complejidad innecesaria en liquidacion (evitar overrides/ramas de UX hasta validar base).
- Mantener governance docs sincronizados en cada commit.

## Archivo / Historico (NO usar para ejecucion)
- El handoff largo anterior se considera historico.  
- Para ejecucion, usar solo este bloque activo.
