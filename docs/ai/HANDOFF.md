# Handoff Activo

## Estado actual
- Producto en fase `v1.x operativa` (ya no solo MVP teorico).
- Gobernanza multi-IA activa con fuentes de verdad:
  - `docs/ai/CONTRACT.md`
  - `docs/ai/DECISIONS.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/WORKLOG.md`
  - `docs/ai/HANDOFF.md`
- Flujo operativo vigente en produccion interna:
  - `pendiente`, `aprobada`, `rechazada`, `entregada`, `liquidada`.
- Punto de retorno recomendado (tag base conocido):
  - `v1.3.0-base-estable`

## En progreso
- No hay tareas funcionales en ejecucion al cierre de esta sesion.
- Gobernanza actualizada para reflejar estado real v1.x.

## Proximo paso exacto
- Ejecutar smoke test manual corto en entorno local/LAN:
  - Login por rol (`user`, `aprobador`, `bodega`, `admin`).
  - Crear requisicion y validar paso por estados operativos.
  - Validar vista detalle (timeline + bloque de liquidacion).
  - Confirmar que filtros operativos no contradicen estados persistidos.
- Registrar resultados del smoke test en `WORKLOG.md` y, si aplica, abrir tareas en `TASKS.md`.

## Riesgos abiertos
- Desalineacion futura entre lenguaje operativo de negocio y estados persistidos.
- Crecimiento de reglas por rol sin ADR cuando afecte permisos globales.
- Deriva de complejidad si se intentan introducir integraciones externas sin control.

## Regla de sesion
- Tomar una sola tarea activa por sesion, cerrar ciclo corto y actualizar siempre `WORKLOG`, `TASKS` y `HANDOFF`.
- Si el cambio afecta reglas core (estados/permisos/integraciones), crear ADR antes de continuar.

## Archivo / Historico (NO usar para ejecucion)
- Si aparece un handoff largo o contradictorio, archivarlo en `docs/ai/archive/HANDOFF_YYYY-MM-DD.md`.
- Este archivo debe mantenerse corto y ejecutable como unica referencia activa.
