# Worklog (append-only)

## 2026-02-10 14:52 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar fase de inicio para colaboracion multi-IA.
- Tareas: `REQ-001`, `REQ-002`, `REQ-003`, `REQ-004`.
- Cambios:
  - `docs/ai/CONTRACT.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
  - `docs/ai/DECISIONS.md`
  - `docs/ai/TASKS.md`
  - `tech_specs.md`
- Resultado:
  - Se congelo alcance MVP y estrategia de autenticacion.
  - Se preparo backlog operativo para continuidad entre Codex/Claude/Gemini.
  - Se inicia bootstrap tecnico del proyecto.
- Proximo paso:
  - Implementar modelos + DB init + rutas base de autenticacion por sesion.

## 2026-02-10 15:08 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar punto 4 (arranque de implementacion).
- Tareas: `REQ-004`, `REQ-005`, `REQ-006`, `REQ-007`, `REQ-008`, `REQ-011`.
- Cambios:
  - `app/main.py`
  - `app/database.py`
  - `app/models.py`
  - `app/auth.py`
  - `app/crud.py`
  - `app/schemas.py`
  - `templates/*.html`
  - `static/app.js`
  - `static/style.css`
  - `init_db.py`
  - `requirements.txt`
  - `.env.example`
  - `README.md`
  - `.gitignore`
- Comandos:
  - `python -m compileall app init_db.py`
- Resultado:
  - App base lista para correr con login por sesion.
  - Flujo crear requisicion + detalle JSON ya implementado.
  - Pendientes principales: aprobacion/rechazo, bodega, tests.
- Proximo paso:
  - Implementar `REQ-009` y `REQ-010`.

## 2026-02-10 15:24 UTC-6 | tool: Codex CLI
- Objetivo: Crear checklist corto ejecutable y auditar estructura minima.
- Cambios:
  - `docs/ai/CHECKLIST_EJECUCION_MVP.md`
- Resultado:
  - Checklist de sesion CLI agregado.
  - Revision de simplicidad documentada: que mantener, que recortar y que evitar en MVP.
- Proximo paso:
  - Decidir si se elimina `app/schemas.py` o se conserva para tipado futuro.

## 2026-02-10 15:31 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar limpieza lean pedida por el usuario.
- Cambios:
  - `app/models.py` (unificacion a `delivered_to`)
  - `app/crud.py` (unificacion a `delivered_to`)
  - `app/main.py` (detalle JSON incluye `delivered_to`)
  - `app/schemas.py` (eliminado)
  - `tech_specs_v1.1_mvp_simplificado.md` (estructura actualizada)
  - `docs/ai/CHECKLIST_EJECUCION_MVP.md` (ajuste post-limpieza)
- Resultado:
  - Estructura mas simple: sin archivo de schemas innecesario.
  - Naming consistente con el spec simplificado.

## 2026-02-10 15:43 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-009` con DB limpia.
- Cambios:
  - `app/main.py` (rutas `/aprobar`, `/aprobar/{id}`, `/rechazar/{id}`)
  - `app/crud.py` (validacion de estado en `puede_aprobar`)
  - `templates/aprobar.html` (vista operativa con acciones aprobar/rechazar)
  - `templates/base.html` (link de menu para aprobadores/admin)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Comandos:
  - `python -m compileall app init_db.py`
- Resultado:
  - Flujo de aprobacion/rechazo funcional con validaciones de rol/departamento/estado.
  - Siguiente tarea activa: `REQ-010` (bodega + entregar).

## 2026-02-10 15:55 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-010` y dejar continuidad multi-IA actualizada.
- Cambios:
  - `app/crud.py` (funcion `puede_entregar`)
  - `app/main.py` (rutas `/bodega` y `/entregar/{id}`)
  - `templates/bodega.html` (tabla y formulario de entrega)
  - `templates/base.html` (menu bodega)
  - `templates/home.html` (contador pendientes bodega)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Comandos:
  - `python -m compileall app init_db.py`
- Resultado:
  - Flujo de bodega listo con validacion de rol y estado `aprobada`.
  - Siguiente tarea recomendada: `REQ-012` (tests basicos E2E de flujo).

## 2026-02-10 16:04 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-012` (tests basicos del flujo principal).
- Cambios:
  - `tests/test_basic_flow.py` (crear, aprobar, entregar)
  - `requirements-dev.txt`
  - `README.md` (instrucciones para correr tests)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Comandos:
  - `pytest -q tests/test_basic_flow.py`
- Resultado:
  - Tests escritos y listos.
  - En este entorno no corrieron por falta de dependencias (`ModuleNotFoundError: sqlalchemy`).
  - Verificacion pendiente al instalar dependencias del proyecto.

## 2026-02-10 16:11 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-013` (operacion LAN y backup).
- Cambios:
  - `docs/LAN_DEPLOY.md`
  - `README.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Guia operativa simple de despliegue LAN y recuperacion creada.
  - Proyecto listo para cerrar con `REQ-014` (pulido UI minimo).

## 2026-02-10 16:19 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar `REQ-014` (pulido UX minimo).
- Cambios:
  - `app/main.py` (redirects con mensaje y tipo)
  - `templates/base.html` (render de alertas por query params)
  - `templates/mis_requisiciones.html` (badges de estado)
  - `static/style.css` (estilos de alertas y badges)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Comandos:
  - `python -m compileall app init_db.py tests/test_basic_flow.py`
- Resultado:
  - UX basica mejorada sin agregar complejidad de flash sessions.
  - Todas las tareas del tablero inicial quedan completadas.

## 2026-02-10 16:33 UTC-6 | tool: Codex CLI
- Objetivo: Cerrar faltantes de dependencias detectados en validacion real.
- Cambios:
  - `requirements.txt` (agregado `itsdangerous==2.2.0`)
  - `requirements-dev.txt` (agregado `httpx==0.27.2`)
- Resultado:
  - Instalacion de entorno consistente para runtime de sesiones y tests con `TestClient`.

## 2026-02-10 16:46 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-015` (CRUD de usuarios para admin).
- Cambios:
  - `app/main.py` (rutas admin usuarios: listar, crear, editar, eliminar)
  - `templates/base.html` (link `Usuarios` para admin)
  - `templates/admin_usuarios.html`
  - `templates/admin_usuario_form.html`
  - `tests/test_admin_users.py`
  - `tests/conftest.py` (path de proyecto para imports de tests)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Reglas aplicadas:
  - Solo `admin` puede acceder.
  - `username` unico.
  - Password minima de 6 chars al crear.
  - En edicion, password opcional (si vacia no cambia).
  - Bloqueo de auto-eliminacion.
  - Bloqueo de eliminacion del ultimo admin.
- Verificacion:
  - `python -m compileall app tests` OK.
  - `pytest -q tests/test_admin_users.py` no ejecutable en este sandbox por falta de dependencias globales; correr en venv del proyecto.

## 2026-02-10 17:18 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-016` (catalogo de items con selector y sin unidad en UI).
- Cambios:
  - `app/crud.py` (catalogo base, unidad por defecto, parse sin campo unidad en formulario)
  - `app/main.py` (envio de catalogo a template y validacion server-side de item permitido)
  - `templates/crear_requisicion.html` (selector de item en lugar de texto libre)
  - `static/app.js` (agregado dinamico de filas con `select` y detalle sin unidad visible)
  - `tests/test_basic_flow.py` (payload actualizado sin unidad)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `tech_specs_v1.1_mvp_simplificado.md`
- Resultado:
  - UX de creacion mas simple y consistente: item elegido desde lista predefinida.
  - Menor riesgo de typos y duplicados de item.
  - Compatibilidad mantenida sin migracion de DB (unidad interna por defecto).

## 2026-02-10 17:46 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-017` (catalogo administrable por admin en DB).
- Cambios:
  - `app/models.py` (nuevo modelo `CatalogoItem`)
  - `app/main.py` (lectura de catalogo desde DB, validacion server-side y CRUD admin de catalogo)
  - `init_db.py` (seed idempotente de usuarios y catalogo)
  - `templates/base.html` (menu admin a catalogo)
  - `templates/admin_catalogo_items.html`
  - `templates/admin_catalogo_item_form.html`
  - `tests/test_basic_flow.py` (seed de catalogo en fixture)
  - `tests/test_admin_users.py` (seed de catalogo en fixture)
  - `tests/test_admin_catalog_items.py` (pruebas CRUD y permisos)
  - `.gitignore`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Se elimina dependencia de catalogo fijo en codigo.
  - El administrador puede crear/editar/desactivar/eliminar items desde la web.
  - `/crear` ahora depende del catalogo activo de DB.

## 2026-02-10 18:05 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-018` (historial completo en `/aprobar` para admin/aprobador).
- Cambios:
  - `app/main.py` (consulta de `pendiente|aprobada|rechazada` en vista `/aprobar`)
  - `templates/aprobar.html` (columna estado + acciones condicionadas por permiso/estado)
  - `tests/test_basic_flow.py` (nuevo test de visualizacion de historial completo)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Admin y aprobador ya visualizan historial completo de aprobacion.
  - Las acciones de aprobar/rechazar siguen restringidas por reglas existentes.

## 2026-02-10 18:22 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-019` (trazabilidad completa en historial de aprobacion).
- Cambios:
  - `app/models.py` (nuevos campos `rejected_by`, `rejected_at` y relaciones de usuario actor)
  - `app/crud.py` (rechazo ahora registra actor y fecha)
  - `app/database.py` (migracion SQLite automatica de columnas faltantes)
  - `app/main.py` (startup migration + carga de relaciones para historial/API)
  - `templates/aprobar.html` (columnas `Solicitante` y `Gestionado por`)
  - `init_db.py` (ejecuta migracion al inicializar)
  - `tests/test_basic_flow.py` (test de rechazo con actor y test de historial con nombres)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Historial de aprobacion ahora es trazable por persona que solicita y persona que gestiona.
  - La informacion de rechazo ya no se pierde: queda actor + timestamp persistidos.

## 2026-02-10 18:34 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-020` (trazabilidad de entrega por bodega).
- Cambios:
  - `app/models.py` (relacion `entregador` via `delivered_by`)
  - `app/main.py` (historial `/aprobar` incluye `entregada` + actor de entrega; API expone `delivered_by`)
  - `templates/aprobar.html` (columna `Gestionado por` contempla estado `entregada`)
  - `static/app.js` (modal muestra solicitante y actores: aprobado/rechazado/entregado)
  - `tests/test_basic_flow.py` (historial cubre estado `entregada` y actor de bodega)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Trazabilidad unificada para todo el ciclo: quien solicito, aprobo/rechazo y entrego.

## 2026-02-10 18:42 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-021` (trazabilidad en vista de bodega).
- Cambios:
  - `app/main.py` (carga de relaciones `solicitante` y `aprobador` en `/bodega`)
  - `templates/bodega.html` (columnas `Solicitante` y `Aprobado por`)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Operacion de bodega ahora ve contexto completo de origen y aprobacion antes de entregar.

## 2026-02-10 19:05 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-022` (fix de eliminacion de usuarios con historial + warnings ORM).
- Cambios:
  - `app/models.py` (relaciones `back_populates` entre `Usuario` y `Requisicion` para aprobacion/rechazo/entrega)
  - `app/main.py` (bloqueo de eliminacion si el usuario participa en historial de requisiciones)
  - `tests/test_admin_users.py` (nuevo test para impedir eliminacion de usuario con historial)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Se elimina el `500` por `NOT NULL constraint failed` al borrar usuarios con historial.
  - Se corrige configuracion ORM para evitar warnings por relaciones en conflicto.

## 2026-02-10 19:22 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-023` (baja logica de usuarios).
- Cambios:
  - `app/models.py` (campo `usuarios.activo`)
  - `app/database.py` (migracion SQLite agrega columna `activo` con default activo)
  - `app/auth.py` (login y sesion solo para usuarios activos)
  - `app/main.py` (filtros admin por estado + endpoints desactivar/reactivar)
  - `templates/admin_usuarios.html` (estado y acciones desactivar/reactivar)
  - `tests/test_admin_users.py` (tests de desactivar/reactivar y login bloqueado para inactivos)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Usuarios fuera de la empresa pueden quedar inactivos sin perder historial.
  - Operacion diaria puede enfocarse en usuarios activos sin romper trazabilidad.

## 2026-02-10 19:36 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-024` (historial visible en vista de bodega).
- Cambios:
  - `app/main.py` (separa `pendientes_entrega` e `historial_entregadas`; para bodega filtra historial por `delivered_by`)
  - `templates/bodega.html` (dos bloques: pendientes y historial entregado)
  - `tests/test_basic_flow.py` (verifica que al entregar ya aparece en historial de bodega)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Bodega mantiene trazabilidad operativa sin que las requisiciones entregadas desaparezcan de su vista.

## 2026-02-10 19:48 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-025` (detalle de items en historiales aprobar/bodega).
- Cambios:
  - `templates/aprobar.html` (agrega columna detalle, boton `Ver`, modal y carga de `app.js`)
  - `templates/bodega.html` (agrega boton `Ver` en pendientes e historial, modal y `app.js`)
  - `tests/test_basic_flow.py` (verifica presencia de boton `Ver` y modal en ambas vistas)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - El detalle de requisicion (incluyendo items) ya es accesible desde historiales operativos.

## 2026-02-10 20:04 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-026` (comentarios operativos en aprobacion/rechazo/entrega).
- Cambios:
  - `app/models.py` (campos `approval_comment`, `rejection_comment`, `delivery_comment`)
  - `app/database.py` (migracion SQLite incremental para nuevas columnas)
  - `app/crud.py` (transicion de estado persiste comentarios por etapa)
  - `app/main.py` (rutas `/aprobar`, `/rechazar`, `/entregar` reciben comentario; API expone comentarios)
  - `templates/aprobar.html` (inputs de comentario en aprobar/rechazar)
  - `templates/bodega.html` (input de comentario en entrega)
  - `static/app.js` (modal muestra comentarios de aprobacion/rechazo/entrega)
  - `tests/test_basic_flow.py` (assert de persistencia de comentarios)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Proceso queda mejor documentado por cada actor sin romper flujo actual.

## 2026-02-11 16:05 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-027` (UI compacta + resultados de entrega en bodega).
- Cambios:
  - `static/style.css` (compactacion de tablas, inputs, botones y formularios inline)
  - `app/models.py` (nuevo campo `delivery_result` en `Requisicion`)
  - `app/database.py` (migracion incremental para `delivery_result`)
  - `app/crud.py` (persistencia de `delivery_result` en transicion a entrega)
  - `app/main.py` (validacion y guardado de `resultado` en `/entregar/{id}`)
  - `templates/bodega.html` (selector de resultado y columna de resultado en historial)
  - `templates/aprobar.html` (formularios compactos)
  - `static/app.js` (detalle muestra `Resultado entrega`)
  - `tests/test_basic_flow.py` (cobertura para entrega completa/parcial/no_entregada)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Bodega ahora registra si la entrega fue completa, parcial o no entregada.
  - Cuando el resultado es parcial o no entregada, el comentario es obligatorio para trazabilidad.
  - La UI en tablas operativas queda mas compacta para soportar campos/acciones adicionales.

## 2026-02-11 16:26 UTC-6 | tool: Codex CLI
- Objetivo: Implementar `REQ-028` (entrega parcial editable por item para trazabilidad real).
- Cambios:
  - `app/models.py` (campo `Item.cantidad_entregada`)
  - `app/database.py` (migracion incremental de `cantidad_entregada` en `items`)
  - `app/main.py` (flujo de bodega: parcial en 2 pasos, rutas `/entregar/{id}/parcial` GET+POST)
  - `templates/bodega.html` (aviso de redireccion para parcial)
  - `templates/bodega_entrega_parcial.html` (pantalla de edicion de cantidades)
  - `static/app.js` (detalle muestra solicitado vs entregado)
  - `tests/test_basic_flow.py` (test de flujo parcial en 2 pasos y persistencia de cantidades)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Bodega ya puede registrar entrega parcial con cantidades reales por item.
  - La requisicion se marca `entregada` solo al confirmar esa edicion parcial.
  - Se mantiene trazabilidad de resultado, actor, receptor, comentario y cantidades efectivamente entregadas.

## 2026-02-11 16:41 UTC-6 | tool: Codex CLI
- Objetivo: Compactacion UI mas agresiva en vistas operativas (aprobacion y bodega).
- Cambios:
  - `static/style.css` (override de variables Pico para modo denso, tabla compacta, truncado, acciones colapsables)
  - `templates/aprobar.html` (acciones en `details/summary`, columnas compactas)
  - `templates/bodega.html` (procesamiento en `details/summary`, columnas compactas)
- Resultado:
  - Menor uso horizontal por fila y mayor legibilidad en pantallas medianas.
  - Formulario de acciones solo se expande cuando se necesita, reduciendo aspecto apiñado.

## 2026-02-11 16:49 UTC-6 | tool: Codex CLI
- Objetivo: Iterar densidad UI a nivel intermedio (menos agresiva que version compacta extrema).
- Cambios:
  - `static/style.css` (tipografia, espaciados y altura de controles en punto medio).
- Resultado:
  - Se conserva ganancia de espacio respecto al estado original, pero con mejor legibilidad y menos compresion visual.

## 2026-02-11 16:55 UTC-6 | tool: Codex CLI
- Objetivo: Probar incremento de escala visual +10% sobre el ajuste intermedio.
- Cambios:
  - `static/style.css` (aumento de `--pico-font-size`, tamaño de tablas y controles).
- Resultado:
  - Interfaz más grande sin perder el layout compacto en acciones/tablas.

## 2026-02-11 17:06 UTC-6 | tool: Codex CLI
- Objetivo: Mejorar visualizacion de detalle de requisicion en modal.
- Cambios:
  - `static/app.js` (items renderizados en tabla: item, cantidad solicitada y cantidad despachada cuando aplica).
  - `static/style.css` (estilos de tabla de detalle, alineacion numerica y wrapper con scroll).
- Resultado:
  - Mayor legibilidad y trazabilidad de cantidades en el detalle, especialmente para entregas parciales.

## 2026-02-11 17:15 UTC-6 | tool: Codex CLI
- Objetivo: Evitar duplicado de item en una misma requisicion.
- Cambios:
  - `static/app.js` (bloqueo de opciones repetidas entre filas y re-sincronizacion al eliminar fila)
  - `app/main.py` (validacion backend de duplicados antes de persistir)
  - `tests/test_basic_flow.py` (nuevo test de rechazo de items duplicados)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - El usuario no puede seleccionar dos veces el mismo item en UI.
  - Si se manipula el request, backend bloquea la requisicion con error 400.

## 2026-02-11 17:27 UTC-6 | tool: Codex CLI
- Objetivo: Restringir departamento de usuarios a lista predefinida en modulo admin.
- Cambios:
  - `app/main.py` (constante `DEPARTAMENTOS_VALIDOS`, envio a template y validacion backend en crear/editar usuario)
  - `templates/admin_usuario_form.html` (campo departamento cambia de input libre a selector)
  - `tests/test_admin_users.py` (fixtures y payloads adaptados + test de departamento invalido)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Admin ya no escribe departamentos libres; selecciona uno de la lista oficial.
  - Se bloquean intentos de envio con departamentos no permitidos.

## 2026-02-11 17:39 UTC-6 | tool: Codex CLI
- Objetivo: Quitar seleccion manual de departamento en creacion de requisicion.
- Cambios:
  - `templates/crear_requisicion.html` (departamento visible en solo lectura)
  - `app/main.py` (`/crear` toma `departamento` desde `current_user.departamento`)
  - `tests/test_basic_flow.py` (ajustes de payload y test para ignorar departamento enviado en request)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - El usuario no puede alterar el departamento al crear requisicion.
  - Se evita spoofing por formulario del cliente.

## 2026-02-11 17:52 UTC-6 | tool: Codex CLI
- Objetivo: Exigir datos de cliente al crear requisicion.
- Cambios:
  - `app/models.py` (campos `cliente_codigo`, `cliente_nombre` en `Requisicion`)
  - `app/database.py` (migracion incremental para nuevos campos)
  - `app/crud.py` (`crear_requisicion_db` recibe y persiste datos de cliente)
  - `app/main.py` (`/crear` valida y requiere codigo/nombre cliente; detalle API los expone)
  - `templates/crear_requisicion.html` (campos obligatorios en formulario)
  - `static/app.js` (modal detalle muestra datos de cliente)
  - `tests/test_basic_flow.py` (payloads actualizados + test de validacion)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Toda nueva requisicion queda asociada a codigo y nombre de cliente.
  - Se mantiene trazabilidad de cliente en el detalle operativo.

## 2026-02-11 18:04 UTC-6 | tool: Codex CLI
- Objetivo: Mejorar usabilidad del modal de detalle en pantallas sub-FHD.
- Cambios:
  - `static/app.js` (reorganizacion del detalle en grilla horizontal + bloques de notas + tabla de items)
  - `static/style.css` (layout responsive para modal, ancho ampliado y estilos de bloques en claro/oscuro)
- Resultado:
  - Menor scroll vertical en detalle de requisicion.
  - Mejor aprovechamiento horizontal con adaptacion responsive.

## 2026-02-11 18:11 UTC-6 | tool: Codex CLI
- Objetivo: Mejorar legibilidad visual de casillas en modal de detalle.
- Cambios:
  - `static/style.css` (fondos con gradiente suave y contraste de texto en claro/oscuro).
- Resultado:
  - Se elimina el look de bloques blancos planos y mejora lectura del contenido.

## 2026-02-11 18:18 UTC-6 | tool: Codex CLI
- Objetivo: Corregir estilos del modal que estaban siendo sobreescritos (campos blancos / texto bajo contraste).
- Cambios:
  - `static/style.css` (selectores especificos `#modal-detalle`, contraste alto y soporte dark via `data-theme` + `prefers-color-scheme`).
- Resultado:
  - Las casillas del modal ya no quedan blancas y el texto gana legibilidad.

## 2026-02-11 18:31 UTC-6 | tool: Codex CLI
- Objetivo: Corregir UX de validacion en entrega de bodega para evitar JSON 400 en formulario web.
- Cambios:
  - `app/main.py` (`/entregar/{id}` devuelve redirect con mensaje de error en validaciones de formulario)
  - `tests/test_basic_flow.py` (nuevo test para caso "quien recibe" obligatorio en entrega completa)
- Resultado:
  - En UI, el usuario vuelve a `/bodega` con mensaje claro en lugar de `Bad Request` JSON.

## 2026-02-11 18:47 UTC-6 | tool: Codex CLI
- Objetivo: Iniciar V2 visual alineada a referencia corporativa ProHygiene.
- Cambios:
  - `templates/base.html` (header en dos franjas, marca estilo corporativo, menu horizontal y shell principal)
  - `static/style.css` (paleta azul corporativa, tipografia Montserrat, tarjetas/tablas y ajustes responsive)
- Resultado:
  - La app ahora adopta una identidad visual consistente con el sitio de referencia.
  - Mejor jerarquia visual y usabilidad en anchos medios/bajos.

## 2026-02-11 19:05 UTC-6 | tool: Codex CLI
- Objetivo: Entregar primera iteracion de UI dark theme inspirada en marca corporativa.
- Cambios:
  - `templates/base.html` (activar `data-theme=dark`)
  - `static/style.css` (overrides dark para header/nav/superficies/formularios/tablas/modales y legibilidad de logo)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - La app adopta un look dark corporativo con acentos azules y mejor uso visual para iterar detalles finos en siguientes pasos.

## 2026-02-11 19:18 UTC-6 | tool: Codex CLI
- Objetivo: Continuar iteracion de UI dark con mayor jerarquia y usabilidad.
- Cambios:
  - `templates/home.html` (hero operativo + tarjetas metricas)
  - `templates/login.html` (login shell centrado + card mas clara)
  - `templates/crear_requisicion.html` (grilla de campos de contexto en 3 columnas)
  - `templates/mis_requisiciones.html` (tabla compacta unificada)
  - `static/style.css` (estilos de page hero, metric cards, login shell y refinamientos de menu/tablas)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Interfaz dark mas consistente con mejor distribucion visual y menor sensacion de bloque plano.

## 2026-02-11 19:31 UTC-6 | tool: Codex CLI
- Objetivo: Continuar pulido de V2 dark en pantallas operativas.
- Cambios:
  - `templates/base.html` (estado activo en links del menu segun ruta)
  - `templates/aprobar.html` y `templates/bodega.html` (subtitulos operativos)
  - `static/style.css` (overrides finales para nav activo, columnas/table density y acciones)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Mejor orientacion de navegacion y legibilidad de tablas en aprobacion/bodega sin perder compactacion.

## 2026-02-11 19:48 UTC-6 | tool: Codex CLI
- Objetivo: Ejecutar la iteracion propuesta de limpieza tecnica de UI.
- Cambios:
  - `static/style.css` reescrito y consolidado (se removieron capas duplicadas y bloques conflictivos)
  - Se mantuvo la estetica dark corporativa con nav activo, tablas operativas, modal y responsive.
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Hoja de estilos mas mantenible y predecible para iteraciones visuales siguientes.
  - Se corrigio deriva de cascada que estaba introduciendo resultados inconsistentes.

## 2026-02-11 20:04 UTC-6 | tool: Codex CLI
- Objetivo: Mejorar visibilidad del panel de inicio y extender informacion para roles no admin.
- Cambios:
  - `app/main.py` (conteos de requisiciones propias por estado: pendiente/aprobada/rechazada/entregada)
  - `templates/home.html` (nuevas tarjetas por estado para todos los roles)
  - `static/style.css` (colores diferenciados por tarjeta dentro de la paleta dark actual)
  - `tests/test_basic_flow.py` (test de metricas por estado para usuario rol `user`)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Dashboard inicial mas informativo y consistente entre roles.
  - El usuario agente ya ve sus requisiciones separadas por estado, no solo el total.

## 2026-02-11 20:22 UTC-6 | tool: Codex CLI
- Objetivo: Reemplazar paneles compactos de accion en `Aprobar` y `Bodega` por vistas dedicadas de gestion.
- Cambios:
  - `app/main.py` (nuevas rutas `GET /aprobar/{id}/gestionar` y `GET /bodega/{id}/gestionar` con validaciones de rol/estado)
  - `templates/aprobar.html` y `templates/bodega.html` (accion cambia a enlace `Gestionar`)
  - `templates/aprobar_gestionar.html` (pantalla completa para aprobar/rechazar)
  - `templates/bodega_gestionar.html` (pantalla completa para registrar entrega)
  - `static/style.css` (nuevos estilos `gestion-*` para layout y formularios)
  - `tests/test_basic_flow.py` (tests para acceso a nuevas vistas de gestion)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Flujo operativo mas claro y legible, sin menu colapsado ni campos cortados.
  - Queda pendiente confirmar ejecucion de tests en entorno local: en este sandbox `pytest` quedo colgado sin salida y finalizo por timeout.

## 2026-02-11 20:36 UTC-6 | tool: Codex CLI
- Objetivo: Agregar metricas simples en inicio sin aumentar complejidad del MVP.
- Cambios:
  - `app/main.py` (calculo de `mis_creadas_mes`, `mis_pendientes_antiguas`, `mis_entregadas_30d`)
  - `templates/home.html` (3 tarjetas nuevas de metricas)
  - `static/style.css` (variantes visuales `metric-month`, `metric-aging`, `metric-30d`)
  - `tests/test_basic_flow.py` (asserts de labels nuevas en home)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Inicio mas informativo con calculos ligeros y sin introducir complejidad tecnica adicional.

## 2026-02-11 20:44 UTC-6 | tool: Codex CLI
- Objetivo: Ajustar indicadores del inicio para mayor claridad operativa.
- Cambios:
  - `app/main.py` (reemplazo de pendiente +48h por pendientes generales y nueva metrica de pendientes de entregar)
  - `templates/home.html` (grafico con filas: pendientes, pendientes de entregar y rechazadas)
  - `static/style.css` (nuevas barras `bar-pending`, `bar-delivery`, `bar-rejected`)
  - `tests/test_basic_flow.py` (asserts de labels actualizados)
- Resultado:
  - Indicadores mas intuitivos para operacion diaria sin aumentar complejidad tecnica.

## 2026-02-11 20:52 UTC-6 | tool: Codex CLI
- Objetivo: Corregir conteo de rechazadas en dashboard para roles operativos.
- Cambios:
  - `app/main.py` (nuevo `rechazadas_panel`: global para admin/aprobador/bodega, propio para user)
  - `templates/home.html` (tarjeta y grafico usan `rechazadas_panel`; etiqueta de tarjeta ajustada a `Rechazadas`)
  - `tests/test_basic_flow.py` (assert de label actualizado)
- Resultado:
  - Las rechazadas ya se reflejan correctamente en tarjeta y grafico segun el alcance del rol.

## 2026-02-11 20:58 UTC-6 | tool: Codex CLI
- Objetivo: Corregir conteo de aprobadas en dashboard para roles operativos.
- Cambios:
  - `app/main.py` (nuevo `aprobadas_panel`: global para admin/aprobador/bodega, propio para user)
  - `app/main.py` (`pendientes_entregar_panel` ahora usa `aprobadas_panel` fuera de bodega/admin)
  - `templates/home.html` (tarjeta usa `Aprobadas` + `aprobadas_panel`)
  - `tests/test_basic_flow.py` (assert de label actualizado)
- Resultado:
  - Conteo de aprobadas consistente con el alcance de rol, igual que rechazadas.

## 2026-02-11 21:09 UTC-6 | tool: Codex CLI
- Objetivo: Redisenar pantalla de login segun referencia visual corporativa, sin opciones extras.
- Cambios:
  - `templates/login.html` (estructura nueva con logo centrado, copy, formulario limpio y footer de sistema)
  - `static/style.css` (estilos dedicados para card/login-form/footer en dark theme)
- Resultado:
  - Login mas cercano a la referencia entregada, sin recuperar clave ni recordar sesion.

## 2026-02-11 21:18 UTC-6 | tool: Codex CLI
- Objetivo: Registrar hito de integracion Git/GitHub para continuidad multi-IA.
- Git/GitHub:
  - Commit en rama feature: `5864cc6` (`feat: finalize login page and hide global header on login`)
  - Merge a principal: `feat/ui-v2-prohygiene` -> `main` (merge commit `0817f61`)
  - Push remoto: `origin/main` actualizado a `0817f61`
  - Tag anotado publicado: `v1.2.0-ui-base`
- Resultado:
  - UI base aprobada queda congelada y referenciable por cualquier IA/operador sin ambiguedad.

## 2026-02-11 21:34 UTC-6 | tool: Codex CLI
- Objetivo: Agregar nuevo campo obligatorio en alta de requisicion: `Ruta Principal del Cliente`.
- Cambios:
  - `app/models.py` (nuevo campo `cliente_ruta_principal` en `Requisicion`)
  - `app/database.py` (migracion incremental SQLite para columna `cliente_ruta_principal`)
  - `app/crud.py` (persistencia del nuevo campo)
  - `app/main.py` (validacion obligatoria con regex `^[A-Z]{2}[0-9]{2}$`, normalizacion a mayusculas)
  - `templates/crear_requisicion.html` (input requerido con `pattern` y ejemplo `RA02`)
  - `static/app.js` y `app/main.py` (`/api/requisiciones/{id}` incluye ruta principal en detalle)
  - `tests/test_basic_flow.py` (payloads de creacion actualizados + test de formato invalido)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Nuevas requisiciones solo se crean con ruta principal valida en formato de 2 letras + 2 numeros.

## 2026-02-11 21:44 UTC-6 | tool: Codex CLI
- Objetivo: Cambiar alcance del rol `aprobador` para que gestione requisiciones de toda la empresa.
- Cambios:
  - `app/crud.py` (`puede_aprobar` deja de filtrar por departamento)
  - `app/main.py` (pendientes por aprobar global para aprobador/admin; permisos de aprobar/rechazar/gestionar y detalle API sin filtro por departamento para aprobador)
  - `templates/aprobar.html` (boton `Gestionar` habilitado para cualquier pendiente cuando rol es aprobador/admin)
  - `tests/test_basic_flow.py` (nuevo test: aprobador puede aprobar requisicion de otra area)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Solo usuarios `user` quedan restringidos a ver/operar lo propio; aprobadores tienen alcance global.

## 2026-02-11 22:02 UTC-6 | tool: Codex CLI
- Objetivo: Agregar capacidad de busqueda y filtros en vistas de alto volumen (`/aprobar`, `/bodega`).
- Cambios:
  - `app/main.py` (`/aprobar`: filtros `q`, `estado`, `departamento`; `/bodega`: filtros `q`, `vista`, `resultado`)
  - `templates/aprobar.html` (barra de filtros + limpiar)
  - `templates/bodega.html` (barra de filtros + secciones condicionales por vista)
  - `static/style.css` (estilos `filters-bar` responsive)
  - `tests/test_basic_flow.py` (tests de filtrado en aprobar y bodega)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Busqueda/filtro simple y suficiente para crecimiento de historial sin introducir complejidad extra.

## 2026-02-11 22:16 UTC-6 | tool: Codex CLI
- Objetivo: Diferenciar los dos pendientes operativos en la UI de estados/filtros.
- Cambios:
  - `app/main.py` (`/aprobar` soporta alias de filtro: `pendiente_aprobar` -> `pendiente`, `pendiente_entregar` -> `aprobada`)
  - `templates/aprobar.html` (filtro con ambos pendientes y badges con etiquetas operativas)
  - `templates/mis_requisiciones.html` (etiquetas de estado alineadas: pendiente aprobar/pendiente entregar)
  - `tests/test_basic_flow.py` (asserts de etiquetas actualizados)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - El usuario puede distinguir y filtrar claramente entre pendiente de aprobacion y pendiente de entrega, sin migrar estados de DB.

## 2026-02-11 22:28 UTC-6 | tool: Codex CLI
- Objetivo: Corregir fallo de arranque en DB limpia (`no such table: usuarios`).
- Cambios:
  - `app/database.py` (`run_migrations()` ahora ejecuta `Base.metadata.create_all` antes de ALTERs y verifica existencia de tablas)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Uvicorn puede iniciar correctamente tras borrar `requisiciones.db`; migraciones incrementales ya no fallan en bases nuevas.

## 2026-02-11 22:46 UTC-6 | tool: Codex CLI
- Objetivo: Endurecer flujo de alta de items en creacion de requisicion (UI + backend).
- Cambios:
  - `static/app.js` (bloqueo de `+ Agregar item` si la fila previa no tiene item/cantidad valida)
  - `app/crud.py` (`parse_items_from_form` ahora ignora filas vacias completas y rechaza filas parciales o cantidades invalidas)
  - `app/main.py` (captura `ValueError` del parser y devuelve `400` con mensaje explicito)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Se evita crear filas encadenadas incompletas y desaparece el falso positivo `Item no permitido en catalogo` cuando el problema real es fila invalida.

## 2026-02-11 23:02 UTC-6 | tool: Codex CLI
- Objetivo: Permitir eliminacion de requisiciones propias solo antes de aprobacion.
- Cambios:
  - `app/main.py` (nueva ruta `POST /mis-requisiciones/{id}/eliminar` con validacion de propiedad + estado `pendiente`)
  - `templates/mis_requisiciones.html` (boton `Eliminar` visible solo cuando estado es pendiente)
  - `tests/test_basic_flow.py` (3 tests: elimina propia pendiente, bloquea no-pendiente, bloquea requisicion ajena)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Resultado:
  - Se mantiene trazabilidad historica en estados ya gestionados y se habilita correccion temprana para requisiciones pendientes.

## 2026-02-11 23:24 UTC-6 | tool: Codex CLI
- Objetivo: Corregir error intermitente al crear requisiciones: `Item no permitido en catalogo`.
- Causa identificada:
  - En filas de items agregadas por JS, las opciones se construian sin escape HTML; items con comillas (ej. `Mopa 12"`) rompian el `value`.
  - La validacion backend comparaba nombres exactos sin normalizar, sensible a espacios/mayusculas.
- Cambios:
  - `static/app.js` (`renderItemOptions` ahora escapa `value` y texto con `escapeHtml`)
  - `app/main.py` (normalizacion de nombre de item en backend con `normalize_catalog_name`; validacion/duplicados por clave normalizada y persistencia del nombre canonico del catalogo)
  - `tests/test_basic_flow.py` (nuevo caso de normalizacion de item con mayusculas/espacios)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Validacion:
  - `python -m compileall app static templates tests` OK.
  - Nota: ejecucion de `pytest` con `TestClient` puede quedar bloqueada si hay instancia activa de `uvicorn --reload` usando la misma SQLite durante startup/migraciones.
- Resultado:
  - Creacion de requisiciones robusta para items con caracteres especiales y variaciones de formato de entrada.

## 2026-02-11 15:31 CST | tool: Codex CLI
- Objetivo: Corregir inconsistencia en inicio para rol aprobador (tarjeta y grafico de pendientes de aprobar).
- Causa identificada:
  - La tarjeta usaba `pendientes_aprobar` (global) y el grafico usaba `mis_pendientes` (propias), mostrando valores distintos.
- Cambios:
  - `app/main.py` (nueva variable `pendientes_aprobar_panel`; escala del grafico usa esta variable)
  - `templates/home.html` (fila `Pendientes de aprobar` del mini-grafico ahora usa `pendientes_aprobar_panel`)
  - `tests/test_basic_flow.py` (nuevo test de regresion para aprobador)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Validacion:
  - `python -m compileall app templates tests` OK.
  - `pytest` del caso puntual en este entorno corta por timeout (probable bloqueo de SQLite si hay proceso concurrente con la DB).
- Resultado:
  - Los valores de pendientes de aprobar quedan consistentes entre tarjeta y grafico segun rol.

## 2026-02-11 15:44 CST | tool: Codex CLI
- Objetivo: Mejorar contexto operativo en vistas de gestion de aprobacion y bodega.
- Cambios:
  - `templates/aprobar_gestionar.html` (agrega `Codigo cliente`, `Cliente` y `Ruta principal`; elimina `Departamento` del encabezado)
  - `templates/bodega_gestionar.html` (agrega `Codigo cliente`, `Cliente` y `Ruta principal`; elimina `Departamento` del encabezado)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Validacion:
  - `python -m compileall templates` OK.
- Resultado:
  - Las pantallas de gestion muestran datos clave del cliente sin ruido de departamento, mejorando decision operativa.

## 2026-02-11 15:50 CST | tool: Codex CLI
- Objetivo: Habilitar importacion masiva de catalogo desde archivo para evitar alta item por item.
- Cambios:
  - `app/main.py` (nuevo endpoint `POST /admin/catalogo-items/importar` + parseo CSV/XLSX + deduplicacion por nombre normalizado)
  - `templates/admin_catalogo_items.html` (formulario de carga con archivo y opcion de activar items importados)
  - `tests/test_admin_catalog_items.py` (caso de importacion CSV con creacion y reactivacion de items)
  - `requirements.txt` (agrega `openpyxl` para soporte XLSX)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Validacion:
  - `python -m compileall app templates tests` OK.
  - `pytest` de `tests/test_admin_catalog_items.py` en este entorno no devolvio salida dentro de timeout; probable conflicto por SQLite concurrente.
- Resultado:
  - Se puede cargar catalogo desde CSV o XLSX de forma simple y controlada desde UI de admin.

## 2026-02-11 16:07 CST | tool: Codex CLI
- Objetivo: Congelar baseline funcional previo a iniciar reporteria.
- Git/GitHub:
  - Tag anotado creado: `v1.3.0-base-estable`
  - Commit referenciado: `18c21f7`
  - Push de tag a remoto completado: `origin/v1.3.0-base-estable`
- Cambios:
  - `docs/ai/HANDOFF.md` (registro del nuevo tag de corte)
- Resultado:
  - Punto de retorno claro y estable para comenzar siguiente fase (reporteria minima).

## 2026-02-11 16:17 CST | tool: Codex CLI
- Objetivo: Ajustar la vista de detalle de requisiciones al nuevo diseño de referencia.
- Cambios:
  - `static/app.js` (nuevo markup del modal detalle: items arriba + panel principal + sidebar de estado/comentarios; titulo dinamico con folio)
  - `static/style.css` (estilos del nuevo layout: tablas, paneles, chips de resultado y jerarquia visual)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Validacion:
  - `python -m compileall static templates` OK.
- Resultado:
  - El detalle deja de ser una lista plana y pasa a una composicion mas legible y operativa, priorizando visibilidad de items.

## 2026-02-11 16:19 CST | tool: Codex CLI
- Objetivo: Corregir densidad visual del modal detalle (contenido apiñado por ancho insuficiente).
- Cambios:
  - `static/style.css` (ancho del modal incrementado a `min(98vw, 1260px)` y ajuste de proporciones en `detalle-layout`)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Validacion:
  - `python -m compileall static` OK.
- Resultado:
  - Mayor espacio horizontal para tabla/items/paneles; mejora de legibilidad en desktop.

## 2026-02-11 16:22 CST | tool: Codex CLI
- Objetivo: Re-alinear modal detalle con referencia visual (menos tarjetas, mas limpieza).
- Cambios:
  - `static/app.js` (nuevo markup plano en detalle: tabla superior + bloque general + listas de estado/comentarios)
  - `static/style.css` (elimina tarjetas por campo, aumenta ancho util del modal, tipografia/espaciado mas abiertos)
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
- Validacion:
  - `python -m compileall static` OK.
- Resultado:
  - Detalle visualmente mas cercano a referencia compartida, sin sobreposiciones ni micro-cajas por dato.

## 2026-02-11 17:35 CST | tool: Claude Code
- Objetivo: Alinear aspecto visual del modal detalle con captura de referencia corporativa.
- Cambios:
  - `static/app.js` (labels con iconos coloreados por tipo de dato: naranja/verde/azul; chip para resultado entrega; clase qty-zero para despachado=0)
  - `static/style.css` (variantes de color para meta-labels, cantidades centradas en tabla items, estilos para chips de resultado y flujo-item)
  - `docs/ai/TASKS.md` (registro de `REQ-056`)
  - `docs/ai/HANDOFF.md` (actualizado estado actual)
  - `docs/ai/WORKLOG.md` (entrada de sesion)
- Validacion:
  - Cambios exclusivamente de UI/CSS, sin tocar logica backend ni rutas.
- Resultado:
  - Modal detalle visualmente identico a referencia: labels con color semantico, cantidades centradas, resultado de entrega como badge, todos los campos siempre visibles.

## 2026-02-12 09:24 CST | tool: Codex CLI
- Objetivo: Iteracion UI de dashboard para replicar prototipo en header/nav y metric cards.
- Cambios:
  - `templates/base.html` (nuevo layout de topbar: marca textual + nav capsule con iconos SVG inline + avatar chip + boton salir sobrio)
  - `templates/home.html` (cards de metricas con wrappers/clases minimas para titulo, valor e icono, sin cambiar cantidad/orden)
  - `static/style.css` (bloque `V2 prototipo header + metric cards` con estilos dark compactos y acentos por tipo)
  - `docs/ai/TASKS.md` (registro de `REQ-057`)
  - `docs/ai/HANDOFF.md` (estado visual actualizado)
  - `docs/ai/WORKLOG.md` (entrada de sesion)
- Validacion:
  - `python -m compileall templates static` OK.
  - Startup smoke-test: `uvicorn` levanta y cierra correctamente bajo `timeout`.
- Restricciones respetadas:
  - No se cambio logica/rutas/contadores.
  - No se modifico HTML/CSS del bloque `Indicadores rapidos` con barras.
- Resultado:
  - Header/nav y tarjetas adoptan lenguaje visual del prototipo sin afectar la estructura funcional existente.

## 2026-02-12 09:53 CST | tool: Codex CLI
- Objetivo: Unificar diseno UI en todas las vistas operativas y administrativas sin tocar logica de negocio.
- Cambios:
  - `templates/base.html` (carga `theme.css` y navbar via include reutilizable)
  - `templates/partials/navbar.html` (componente de navegacion centralizado)
  - `templates/macros/ui.html` (macros reutilizables: `page_header`, `status_badge`)
  - Vistas actualizadas con layout consistente de paneles/tablas/forms:
    - `templates/home.html`
    - `templates/crear_requisicion.html`
    - `templates/mis_requisiciones.html`
    - `templates/aprobar.html`
    - `templates/aprobar_gestionar.html`
    - `templates/bodega.html`
    - `templates/bodega_gestionar.html`
    - `templates/bodega_entrega_parcial.html`
    - `templates/admin_usuarios.html`
    - `templates/admin_usuario_form.html`
    - `templates/admin_catalogo_items.html`
    - `templates/admin_catalogo_item_form.html`
  - `static/theme.css` (tokens dark + overrides de navbar, cards, paneles, tablas, badges, botones y forms)
  - `docs/ai/TASKS.md` (`REQ-058`)
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Validacion:
  - `python -m compileall templates static` OK.
  - Smoke startup: `uvicorn` inicia y apaga correctamente bajo `timeout`.
- Restricciones respetadas:
  - Sin cambios en rutas/endpoints, nombres de campos, payloads, validaciones o flujo.
  - Sin dependencias nuevas.
  - Seccion de barras `Indicadores rapidos` mantenida sin cambios funcionales.
- Resultado:
  - Sistema visualmente coherente en todas las vistas clave con componentes reutilizables y tema centralizado.

## 2026-02-12 10:35 CST | tool: Codex CLI
- Objetivo: Agregar trazabilidad temporal en vista detalle de requisiciones para cada hito del flujo.
- Cambios:
  - `app/main.py`:
    - `GET /api/requisiciones/{id}` ahora incluye `timeline` con eventos:
      - `Requisicion creada`
      - `Requisicion aprobada` o `Requisicion rechazada`
      - `Preparacion/entrega de bodega`
      - `Recibido` (cuando aplica)
    - Se exponen timestamps (`approved_at`, `rejected_at`, `delivered_at`) en el payload de detalle.
  - `static/app.js`:
    - Se agrega `fmtDateTime()` para mostrar `dd/mm/yyyy HH:MM:SS`.
    - Se renderiza nuevo bloque `Historial` en el modal de detalle con evento, actor y fecha-hora.
  - `static/style.css`:
    - Estilos para timeline (`timeline-list`, `timeline-item`, `timeline-time`, etc.).
  - `tests/test_basic_flow.py`:
    - Nuevo test `test_detalle_requisicion_devuelve_timeline_con_hitos`.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`, `docs/ai/WORKLOG.md`.
- Validacion:
  - `python -m compileall app static tests` OK.
  - Nota: `pytest` en este entorno CLI quedo bloqueado sin salida; validar en entorno local activo.
- Resultado:
  - El detalle ahora muestra historial de cambios con fecha y hora incluyendo segundos (`HH:MM:SS`), mejorando trazabilidad operativa.

## 2026-02-13 13:05 CST | tool: Codex CLI
- Objetivo: Registrar reinicio de la linea de liquidacion desde baseline pre-liquidacion.
- Cambios:
  - Rama nueva creada desde `3d7702b`: `feat/liquidacion-rework-v2`.
  - `docs/ai/HANDOFF.md`: reducido a handoff activo corto y ejecutable para reinicio.
  - `docs/ai/TASKS.md`: reabiertos `REQ-060`, `REQ-061`, `REQ-062` en bloque de reinicio.
  - `docs/ai/DECISIONS.md`: nuevo `ADR-003` formalizando el reinicio desde baseline.
  - `docs/ai/WORKLOG.md`: registro de esta sesion.
- Codigo de app:
  - No se realizaron cambios en backend/frontend/logica; solo documentacion de gobernanza.
- Resultado:
  - Queda oficializado en gobernanza IA que la liquidacion se rehara desde este punto, evitando arrastrar implementaciones previas no satisfactorias.
- Proximo paso:
  - Implementar `REQ-060` minimo en esta rama y validar flujo base sin agregar complejidad adicional.

## 2026-02-25 13:02 CST | tool: Codex CLI
- Objetivo: Implementar `REQ-060` (modelo de datos + migracion + baseline de entrega) sin cambios de UI.
- Cambios de codigo:
  - `app/models.py`
    - Estado `liquidada` agregado al `CheckConstraint` de `requisiciones`.
    - Nuevos campos en `Requisicion`: `prokey_ref`, `liquidation_comment`, `liquidated_by`, `liquidated_at`.
    - Nueva relacion: `liquidator`.
    - Nuevos campos en `Item`: `qty_returned_to_warehouse`, `qty_used`, `qty_left_at_client`, `item_liquidation_note`, `liquidation_alerts` (todos nullable, sin default).
  - `app/database.py`
    - Migraciones incrementales para 9 columnas nuevas de liquidacion.
    - Manejo de error especifico en ALTER TABLE:
      - tolera solo "duplicate column/already exists",
      - loguea y relanza cualquier error real.
    - Backfill de `cantidad_entregada` para historicos con `estado='entregada'` y `delivery_result='completa'`.
  - `app/main.py`
    - Normalizacion baseline en entrega completa: antes de transicionar, si `cantidad_entregada` es `NULL` se setea a `cantidad`.
    - Estados validos de filtros ampliados con `liquidada`.
    - Acceso de rol bodega al detalle incluye estado `liquidada`.
  - `app/crud.py`
    - `transicionar_requisicion` ahora acepta `nuevo_estado='liquidada'`.
  - `tests/test_liquidacion_model.py` (nuevo)
    - 7 pruebas: estado `liquidada`, nullables de liquidacion, baseline completa, no sobreescritura parcial, migracion en DB nueva e idempotencia.
- Cambios de gobernanza:
  - `docs/ai/TASKS.md` (`REQ-060` -> `done`).
  - `docs/ai/HANDOFF.md` actualizado con estado post-REQ-060 y siguiente paso `REQ-061`.
  - `docs/ai/WORKLOG.md` (esta entrada).
- Comandos ejecutados:
  - `python -m compileall app init_db.py`
  - `python -m compileall app init_db.py tests/test_liquidacion_model.py`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion_model.py -v` -> **7 passed**
  - `.venv/bin/python init_db.py` -> OK
  - `timeout 8s .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8015` -> startup/shutdown OK (timeout esperado).
- Resultado:
  - REQ-060 queda base lista para construir UI/flujo de liquidacion sin romper el flujo operativo vigente.
- Proximo paso:
  - Iniciar `REQ-061` (captura de liquidacion en interfaz, validaciones y persistencia usando campos nuevos).

## 2026-02-25 14:05 CST | tool: Codex CLI
- Objetivo: Implementar `REQ-061` (endpoint + UI de liquidacion) con alertas no bloqueantes e inmutabilidad.
- Cambios de codigo:
  - `app/crud.py`
    - Nuevas funciones:
      - `puede_liquidar(requisicion, usuario)` (roles `admin`/`bodega`, estado `entregada`, resultado `completa|parcial`).
      - `calcular_alertas_item(item)` con reglas:
        - `ALERTA_FALTANTE` (`warn`) para `delta > 0`.
        - `ALERTA_SOBRANTE` (`warn`) para `delta < 0`.
        - `ALERTA_RETORNO_EXTRA` (`high`) para `returned > delivered`.
        - `ALERTA_SALIDA_SIN_SOPORTE` (`high`) para `used+left > delivered`.
      - `ejecutar_liquidacion(...)`:
        - persiste cantidades/nota por item,
        - persiste `liquidation_alerts` como JSON,
        - transiciona a `liquidada`,
        - guarda `prokey_ref`, `liquidation_comment`, `liquidated_by`, `liquidated_at`,
        - impide reliquidar (`ValueError`).
  - `app/main.py`
    - Nuevas rutas:
      - `GET /liquidar/{req_id}`: validacion de elegibilidad + inmutabilidad.
      - `POST /liquidar/{req_id}`: parseo de formulario, validacion de enteros >=0, `prokey_ref` obligatorio, ejecucion de liquidacion.
    - `bodega_view` ahora incluye historial de estados `entregada` y `liquidada`.
  - `templates/liquidar.html` (nuevo)
    - Tabla de captura: `Entregado`, `Regresa`, `Usado`, `Dejado en cliente`, `Ocupo`, `Delta`, `Nota`.
    - JS en vivo: recalculo `ocupo` y `delta`, resaltado visual no bloqueante (`delta-warn`/`delta-danger`).
    - Campos finales: `prokey_ref` obligatorio y `liquidation_comment` opcional.
  - `templates/bodega.html`
    - En historial se agrega columna `Liquidacion` con boton `Liquidar` solo para casos elegibles (`estado=entregada` y `delivery_result` en `completa|parcial`).
    - Requisiciones ya `liquidada` muestran badge.
  - `static/theme.css`
    - Estilos de celdas de calculo y resaltado de delta.
  - `tests/test_liquidacion.py` (nuevo)
    - 12 pruebas cubriendo elegibilidad, guardado, alertas por tipo/severity, no bloqueo por delta, `prokey_ref` requerido, inmutabilidad, y restriccion por rol.
- Gobernanza actualizada:
  - `docs/ai/TASKS.md`: `REQ-061` marcado `done`.
  - `docs/ai/HANDOFF.md`: siguiente objetivo movido a `REQ-062`.
  - `docs/ai/WORKLOG.md`: entrada de sesion.
- Comandos ejecutados:
  - `python -m compileall app init_db.py templates` -> OK
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v` -> **12 passed**
  - Intento smoke `tests/test_basic_flow.py` selectivo: en este entorno CLI quedo colgado (no concluyente).
- Resultado:
  - REQ-061 queda implementada end-to-end sin bloquear liquidacion por inconsistencias y manteniendo reglas de acceso/inmutabilidad.
- Proximo paso:
  - Iniciar `REQ-062` para trazabilidad y exposicion de datos de liquidacion en detalle/API.
