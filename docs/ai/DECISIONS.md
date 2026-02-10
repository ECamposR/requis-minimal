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
