# CONTRATO DE GOBERNANZA v1.x

## 1) Objetivo del sistema
- Operar un sistema interno de requisiciones para LAN.
- Prioridad: simpleza, mantenibilidad y continuidad entre IAs (vibecoding controlado).
- Criterio de valor: resolver necesidad operativa real con el menor costo de complejidad.

## 2) Decisiones congeladas (se mantienen)
- Backend: `FastAPI`.
- Persistencia: `SQLite` local.
- UI: `SSR Jinja2 + HTML forms + Vanilla JS + PicoCSS`.
- Sin Docker.
- Sin integraciones externas directas (ERP/CRM/email/webhooks/bots).
- Sin jobs en background, colas ni workers.
- Autenticacion por formulario + sesion firmada.
- Roles base: `user`, `aprobador`, `bodega`, `admin`.

## 3) Decisiones evolucionadas (ya parte del producto)
- El sistema ya opera como v1.x con trazabilidad por flujo.
- Hay gestion operativa por rol para crear, aprobar/rechazar, entregar y liquidar requisiciones.
- Existen vistas de historial y detalle con linea de tiempo.
- El catalogo de items es administrable desde la app.
- Se mantiene enfoque monolitico simple: todo dentro del mismo servicio.

## 4) Flujo de estados vigente
- Estados persistidos en requisicion:
  - `pendiente`
  - `aprobada`
  - `rechazada`
  - `entregada`
  - `liquidada`
- Aclaracion operativa:
  - "Pendiente de aprobar" y "Pendiente de entregar" son etiquetas de vista/filtro.
  - No implican estados tecnicos nuevos en base de datos.

## 4.1) Glosario corto
- Estado persistido:
  - Valor guardado en base de datos que gobierna reglas del flujo.
- Etiqueta operativa:
  - Nombre de vista/filtro para el usuario; no cambia el estado en base.

## 5) Reglas anti-deriva
- No microservicios.
- No colas ni eventos asincronos.
- No nuevas capas arquitectonicas sin necesidad operativa clara.
- No nuevas dependencias si el problema se resuelve con stack actual.
- Cada feature nueva debe justificar: valor operativo + costo de complejidad.
- Cambios de permisos globales requieren ADR.
- Cambios de estado o reglas core requieren ADR.
- Documentacion de sesion obligatoria en `TASKS`, `WORKLOG` y `HANDOFF`.

## 6) Definicion de cambio de alcance
- Se considera cambio de alcance:
  - Agregar/eliminar estados del flujo.
  - Cambiar semantica de roles o permisos globales.
  - Cambiar reglas core de aprobacion/entrega/liquidacion.
  - Introducir integraciones externas.
  - Cambiar estrategia de persistencia o migraciones complejas.
- No se considera cambio de alcance:
  - Pulido UI/UX y estilos.
  - Ajustes de textos/copy.
  - Refactors documentales o de legibilidad sin cambiar comportamiento.

## 7) Fuentes de verdad de gobernanza
- `CONTRACT.md`: reglas del juego vigentes.
- `DECISIONS.md`: ADRs de cambios core.
- `TASKS.md`: estado de trabajo.
- `WORKLOG.md`: registro cronologico append-only.
- `HANDOFF.md`: estado activo para continuidad entre IAs.
