# Decisions Log

## ADR-001 | 2026-02-10 | Auth por sesion en lugar de HTTP Basic
- Contexto:
  - El MVP usa server-side rendering con menu, login y logout.
- Decision:
  - Usar login por formulario + cookie de sesion firmada.
- Motivo:
  - Mejor UX para usuarios internos no tecnicos.
  - Coherencia con templates y flujo de navegacion.
- Alternativas descartadas:
  - HTTP Basic: simple, pero fricciona con logout real y experiencia web.
- Impacto:
  - Requiere middleware de sesion y control explicito de permisos por ruta.

## ADR-002 | 2026-02-10 | Gobernanza multi-IA en repo
- Contexto:
  - Se trabajara con Codex/Claude/Gemini desde CLI.
- Decision:
  - Adoptar `CONTRACT`, `HANDOFF`, `TASKS`, `WORKLOG`, `DECISIONS`.
- Motivo:
  - Evitar perdida de contexto y reducir onboarding entre sesiones.
- Impacto:
  - Overhead minimo de documentacion, alto retorno en continuidad.

## ADR-003 | 2026-02-13 | Reinicio de liquidacion desde baseline pre-feature
- Contexto:
  - La primera implementacion de liquidacion resulto insatisfactoria a nivel funcional/UX.
  - Se necesita rehacerla con menor complejidad, partiendo de un estado estable previo.
- Decision:
  - Reanclar el trabajo en commit `3d7702b` (estado pre-liquidacion) en rama dedicada `feat/liquidacion-rework-v2`.
  - Reabrir `REQ-060+` como nueva linea de ejecucion para liquidacion.
- Motivo:
  - Reducir deuda de decisiones iterativas y evitar arrastrar logica confusa.
  - Mantener simplicidad operativa y trazabilidad clara para multi-IA.
- Impacto:
  - No cambia la base funcional previa (`REQ-001` a `REQ-059`).
  - A partir de este punto, liquidacion se rediseña incrementalmente y cada paso debe quedar registrado en `TASKS` + `WORKLOG` + `HANDOFF`.
