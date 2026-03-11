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

## ADR-005 | 2026-03-03 | Separar tipo fisico del item y contexto operativo
- Contexto:
  - `CatalogoItem.tipo_item` ya clasifica el item como `RETORNABLE` o `CONSUMIBLE`.
  - Esa clasificacion no alcanza para decidir si un retorno debe esperarse en todos los casos.
  - En instalacion inicial de un item retornable, `regresa = 0` es un caso valido y generaba falsos positivos en `ALERTA_RETORNO_INCOMPLETO`.
- Decision:
  - Agregar `Item.contexto_operacion` por linea de requisicion con valores `instalacion_inicial` o `reposicion`.
  - Mantener `tipo_item`/`liquidation_mode` como definicion fisica del item.
  - Usar `contexto_operacion` para modular solo la alerta de retorno incompleto, sin alterar el resto de validaciones y flujo.
- Motivo:
  - Separar el contexto operativo del comportamiento fisico evita sobrecargar `RETORNABLE` con semantica de negocio que no siempre aplica.
  - Reduce falsos positivos sin degradar trazabilidad.
- Alternativas descartadas:
  - Reinterpretar `RETORNABLE` para que no implique expectativa de retorno.
  - Resolver el caso manualmente via comentarios o excepciones operativas.
- Impacto:
  - Nueva columna en `items`.
  - El formulario de creacion captura el contexto por linea.
  - El detalle de liquidacion puede mostrar `RETORNABLE / Instalacion inicial` para auditoria.

## ADR-006 | 2026-03-10 | Respaldo/restauracion admin con alcance a datos, no a infraestructura
- Contexto:
  - La app necesita una recuperacion rapida ante fallos operativos sin introducir complejidad de infraestructura desde la propia UI.
  - La persistencia actual es SQLite y la configuracion critica llega por variables de entorno, no por un archivo administrado por la app.
- Decision:
  - Implementar una pantalla exclusiva de `admin` para generar respaldos ZIP y restaurarlos.
  - El respaldo incluye solo:
    - copia consistente de la base SQLite
    - `manifest.json` con fecha, checksum y metadatos de compatibilidad
  - La restauracion opera sobre la DB activa, crea un backup automatico previo y bloquea temporalmente nuevas requests mientras copia la base.
- Motivo:
  - Recuperar la data de negocio en minutos sin asumir control sobre Docker, codigo o `.env`.
  - Evitar copias crudas inseguras de SQLite mientras la app esta escribiendo.
- Alternativas descartadas:
  - Copiar el archivo `.db` directamente desde la UI sin bloqueo ni backup API de SQLite.
  - Intentar respaldar/restaurar tambien codigo, contenedor o `.env` desde la aplicacion.
- Impacto:
  - Nueva ruta admin para `Respaldos`.
  - Nuevo directorio runtime `backups/` fuera de control de versiones.
  - La restauracion obliga a volver a iniciar sesion y puede invalidar sesiones activas.

## ADR-007 | 2026-03-11 | Cambio formal de fase a beta operativa en produccion y continuidad agnostica al LLM
- Contexto:
  - La app ya no es un MVP teorico ni un prototipo local.
  - Entro en produccion beta el `2026-03-10` dentro de la LAN, con usuarios y operacion real.
  - El proyecto continuara evolucionando via `vibe coding`, potencialmente con distintas IAs y herramientas a lo largo del tiempo.
- Decision:
  - Declarar la fase actual como `beta operativa en produccion controlada`.
  - Mantener como principio rector la solucion mas simple posible, privilegiando mantenibilidad y continuidad operativa.
  - Tratar la gobernanza documental del repo como fuente de verdad transversal y agnostica al proveedor/modelo de IA.
- Motivo:
  - El lenguaje de `MVP` ya no describe correctamente el estado del producto ni el riesgo operativo actual.
  - Con usuarios reales, cada cambio requiere mayor disciplina de trazabilidad, handoff y registro de decisiones/bugs.
  - La continuidad del proyecto no debe depender del contexto de un chat ni de una herramienta especifica.
- Alternativas descartadas:
  - Mantener el lenguaje de MVP por inercia documental.
  - Mover el conocimiento operativo a conversaciones aisladas o a una sola herramienta de IA.
- Impacto:
  - `CONTRACT.md` y `README.md` deben reflejar la fase beta operativa.
  - Todo cambio relevante debe seguir registrandose en `WORKLOG`, `TASKS`, `HANDOFF` y `DECISIONS` cuando corresponda.
  - El foco de trabajo se desplaza de construir base funcional a endurecer operacion, corregir, mantener y ampliar de forma incremental.
