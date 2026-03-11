# AI Collaboration Contract (Beta Operativa)

## 1) Objetivo
Operar y evolucionar una aplicacion interna de requisiciones ya desplegada en LAN, manteniendola simple, estable y facil de sostener, evitando sobreingenieria.

## 1.1) Fase actual del producto
- El proyecto ya no esta en fase MVP.
- La fase actual es `beta operativa en produccion controlada`.
- La app entro en produccion beta el `2026-03-10`, con usuarios y operacion real.
- A partir de esta fase, el foco principal es:
  - estabilidad operativa
  - correcciones rapidas y seguras
  - endurecimiento de validaciones y permisos
  - observabilidad y recuperacion ante fallos
  - mejoras funcionales incrementales solo cuando agreguen valor real sin disparar complejidad

## 2) Decisiones Congeladas de Alcance
- Framework backend: `FastAPI`.
- Persistencia: `SQLite` local (`requisiciones.db`).
- Frontend: `Jinja2 + HTML forms + Vanilla JS + PicoCSS`.
- Sin integraciones externas (ERP, email, bots, webhooks).
- Sin notificaciones automáticas en esta etapa.
- Sin borradores y sin edicion post-envio.
- Flujo de estados: `pendiente -> aprobada|rechazada -> preparado -> entregada -> liquidada -> liquidada_en_prokey`.

Notas:
- El despliegue productivo actual si usa `Docker + Caddy`, segun `ADR-004`.
- La simplicidad sigue siendo regla rectora: cualquier incremento debe justificar su costo operativo.

## 3) Autenticacion (decision cerrada)
- Se usara `login por formulario` + `cookie de sesion firmada`.
- No se usara `HTTP Basic` porque el sistema es SSR con navegacion de menu y `logout`.
- Passwords siempre hasheados con `bcrypt`.
- Roles permitidos: `user`, `aprobador`, `bodega`, `jefe_bodega`, `admin`, `tecnico`.

## 4) Reglas de Implementacion
- Mantener funciones y archivos pequenos, con nombres descriptivos.
- Cualquier cambio de alcance debe registrarse en `docs/ai/DECISIONS.md`.
- No agregar librerias sin justificar en `DECISIONS.md`.
- No introducir background jobs ni colas sin necesidad operacional comprobada.
- Priorizar siempre la solucion mas simple que resuelva el problema real.
- Antes de ampliar arquitectura, agotar primero ajustes de flujo, validacion, UX y documentacion.
- Mantener compatibilidad con trabajo por `vibe coding`: cambios pequenos, iterativos y faciles de revisar.
- La gobernanza debe ser agnostica al modelo LLM y a la herramienta usada (`Codex`, `Claude`, `Gemini`, u otras). El metodo de trabajo pertenece al repo, no al proveedor.
- Cada cambio relevante debe dejar rastro documental minimo: que se hizo, por que, impacto, comandos de validacion y siguiente paso si queda algo abierto.

## 5) Definition of Done (DoD) por tarea
- Criterio funcional cumplido.
- Permisos por rol respetados.
- Validaciones minimas de backend implementadas.
- Test minimo agregado/actualizado (cuando aplique).
- Registro en `docs/ai/WORKLOG.md` y estado en `docs/ai/TASKS.md`.
- Si cambia una regla, criterio operativo o fase del producto, registrar tambien en `docs/ai/DECISIONS.md` y reflejarlo en `README.md` o `HANDOFF.md` cuando corresponda.

## 6) Entrega entre IAs
Antes de cerrar una sesion:
- Actualizar `HANDOFF.md` con estado real y siguiente paso exacto.
- Registrar cambios y comandos en `WORKLOG.md`.
- Marcar tareas en `TASKS.md`.
- Documentar decisiones no triviales en `DECISIONS.md`.

## 7) Regla de continuidad operativa
- Nunca asumir que el conocimiento esta "en el chat"; el estado verdadero debe quedar en los archivos de gobernanza.
- Todo bug, ajuste, decision, regresion detectada o hallazgo operativo relevante debe documentarse.
- Si algo se corrige sin quedar documentado, para efectos del proyecto esa correccion queda incompleta.
