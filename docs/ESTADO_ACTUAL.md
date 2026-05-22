# Estado actual del sistema

## Resumen
La aplicación de requisiciones es un sistema interno en producción controlada para gestionar el ciclo operativo de requisiciones desde la solicitud hasta la liquidación y el cierre en ProKey.

Se usa de forma estable dentro de la organización y prioriza continuidad operativa, trazabilidad y simplicidad técnica. La interfaz sigue siendo web, con enfoque SSR y soporte de vistas operativas para el flujo diario.

## Alcance actual
El sistema cubre la creación, revisión, aprobación, preparación, entrega, liquidación y cierre operativo de requisiciones. También incluye consulta de detalle, PDF, exportaciones, respaldos y soporte de monitoreo operativo donde ya está documentado.

No cubre un rediseño completo del producto, ni cambios de plataforma, ni integraciones externas. La prioridad actual no es ampliar alcance funcional sino mantener estabilidad y ordenar la documentación existente.

## Entorno de ejecución
La aplicación corre como servicio interno en Docker, con uso controlado dentro de la red de la organización.

La persistencia principal es local sobre SQLite, con operación administrada por SQLAlchemy. El despliegue está pensado para uso interno, con foco en continuidad y recuperación simple ante fallos operativos.

## Stack técnico
- Backend: FastAPI
- Frontend: Jinja2, Vanilla JS, PicoCSS, `theme.css`
- Persistencia: SQLite + SQLAlchemy
- PDF: `reportlab`
- Despliegue: Docker
- Pruebas: suite automatizada en `tests/`

## Roles del sistema
- `admin`: administración general del sistema, usuarios, catálogo y funciones de control.
- `aprobador`: revisa requisiciones pendientes y decide aprobación o rechazo.
- `bodega`: atiende preparación, entrega, liquidación y revisión operativa.
- `jefe_bodega`: combina capacidades de aprobación y bodega, además de cierre final en ProKey.
- `user`: solicitante estándar que crea requisiciones y consulta su propio historial.
- `tecnico`: rol operativo para firma con PIN, sin inicio de sesión web.

## Flujo operativo principal
El flujo principal es:

`pendiente -> aprobada/rechazada -> preparado -> entregada/no_entregada -> pendiente_prokey/finalizada_sin_prokey -> liquidada_en_prokey`

Algunos estados intermedios o variantes pueden existir por compatibilidad histórica del sistema. La semántica operativa vigente debe entenderse desde el flujo actual, no desde representaciones antiguas ya superadas.

## Funcionalidades activas
- Creación de requisiciones con datos de cliente, receptor y detalle de ítems.
- Aprobación o rechazo con trazabilidad de actor y tiempo.
- Preparación por bodega antes de la entrega.
- Entrega con firma y PIN.
- Entrega parcial y resultado `no_entregada`.
- Liquidación por ítem con alertas operativas y validaciones de cobertura.
- Gestión de referencia ProKey.
- Generación de PDF de requisición.
- Exportaciones desde vistas operativas documentadas.
- Respaldos desde la aplicación y script de backup completo cuando aplica.
- Monitor o dashboard operativo donde ya esté documentado en la gobernanza.

## Persistencia y respaldos
La base operativa es SQLite. El sistema mantiene respaldos desde la aplicación para recuperación de datos y, cuando está documentado para el entorno Docker, existe además un script de respaldo completo del entorno operativo.

La estrategia de respaldo busca preservar la data útil del sistema sin introducir complejidad innecesaria en la operación diaria.

## Observabilidad básica
La aplicación incluye logging estructurado y trazabilidad por request mediante `request_id`. También registra eventos operativos relevantes, como autenticación y errores de ejecución, cuando corresponda.

## Limitaciones conocidas
- Arquitectura monolítica simple.
- `app/main.py` concentra bastante lógica de orquestación.
- El CSS ha crecido por evolución incremental.
- Las migraciones SQLite requieren atención manual y validación cuidadosa.
- Las vistas de bodega todavía no están optimizadas para móvil.

## Prioridad actual
1. Ordenar la documentación.
2. Adaptar las vistas de bodega para móviles.
3. Mantener la estabilidad del flujo actual.

## Fuera de alcance actual
- Refactor grande.
- Cambio de base de datos.
- Framework frontend nuevo.
- Cambios de infraestructura.
- Rediseño completo de la app.
