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

## ADR-004 | 2026-03-02 | Despliegue con Docker + Caddy como reverse proxy
- Contexto:
  - La app entra a producción dentro de la LAN de la empresa.
  - El servidor Proxmox ya corre ~5 contenedores Docker; este es el primero de cara al usuario.
  - No existía reverse proxy en el servidor.
- Decisión:
  - Desplegar la app como contenedor Docker (`Dockerfile` + `docker-compose.yml` en raíz del repo).
  - Usar Caddy 2 como reverse proxy en contenedor separado (`deploy/caddy/`).
  - Compartir red Docker externa llamada `proxy` entre Caddy y la app.
  - Persistir SQLite en volumen local `./data/requisiciones.db` (fuera del container).
- Motivo:
  - Uniformidad con infraestructura Docker existente.
  - Caddy es la opción más simple para "configurar y olvidar" en LAN (sin base de datos, config mínima).
  - Red externa desacopla Caddy de cada servicio: agregar futuro servicio = nuevo compose + bloque en Caddyfile.
- Alternativas descartadas:
  - LXC en Proxmox: válido en aislamiento, pero rompe uniformidad con el resto de la infra Docker.
  - Nginx Proxy Manager: GUI útil, pero requiere base de datos MariaDB y mayor complejidad operacional.
  - Systemd en el host Docker: sin aislamiento, riesgo de conflictos con otros servicios del VM.
- Impacto:
  - `DATABASE_URL` cambia de `sqlite:///./requisiciones.db` a `sqlite:////app/data/requisiciones.db`.
  - La app no expone puertos directamente; todo el tráfico entra por Caddy en puerto 80.
  - Contenedores existentes en el servidor no requieren ningún cambio.

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
