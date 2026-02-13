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

## ADR-003 | 2026-02-13 | Transicion de MVP a v1.x operativa (alineacion de gobernanza)
- Contexto:
  - El contrato original de MVP quedo desfasado respecto a lo implementado.
  - El sistema ya incluye trazabilidad, entrega parcial, liquidacion y flujos operativos adicionales.
- Decision:
  - Actualizar `CONTRACT.md` a un contrato de gobernanza v1.x.
  - Mantener stack y principios de simpleza.
  - Exigir ADR para cambios core (estados, permisos globales, reglas operativas centrales, integraciones).
- Motivo:
  - Evitar contradicciones entre documentacion y estado real del producto.
  - Controlar deriva tecnica manteniendo velocidad de trabajo multi-IA.
- Impacto:
  - No hay cambios de codigo de app ni de base de datos.
  - A partir de esta decision, el proceso documental queda alineado con la realidad operativa.

## ADR-004 | 2026-02-13 | Nomenclatura operativa vs estado persistido
- Contexto:
  - En uso diario se emplean etiquetas como "pendiente de aprobar" y "pendiente de entregar".
  - Estas etiquetas pueden confundirse con estados de base de datos.
- Decision:
  - Estandarizar que esas etiquetas son solo operativas (filtros/vistas).
  - Los estados persistidos oficiales siguen siendo:
    - `pendiente`, `aprobada`, `rechazada`, `entregada`, `liquidada`.
- Motivo:
  - Evitar errores funcionales y de comunicacion entre equipos e IAs.
- Impacto:
  - Sin cambios tecnicos.
  - Mejora de claridad en tickets, handoffs y validaciones manuales.
