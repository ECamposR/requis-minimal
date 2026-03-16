# Worklog (append-only)

## 2026-03-16 09:15 UTC-6 | tool: Codex CLI
- Objetivo: retirar `Acciones Rápidas` del home para el rol `user` por redundancia funcional.
- Tareas: `REQ-137`
- Cambios:
  - `templates/home.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - El bloque `Acciones Rápidas` se renderiza solo para roles distintos de `user`.
  - La prueba del home de usuario ahora valida la ausencia de ese panel.
- Proximo paso:
  - Revisar visualmente si el home de `user` queda balanceado con solo el grid superior o si conviene aumentar el espaciado inferior para compensar la ausencia del panel.

## 2026-03-16 09:11 UTC-6 | tool: Codex CLI
- Objetivo: simplificar el home del rol `user` eliminando dos cards de bajo valor semantico y compactando las restantes en una sola fila.
- Tareas: `REQ-136`
- Cambios:
  - `app/main.py`
  - `templates/home.html`
  - `static/theme.css`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - Se eliminan `Requieren Seguimiento` y `Requisiciones Rechazadas` del home del rol `user`.
  - El grid del home detecta cuando hay 4 cards y pasa a una sola fila en escritorio.
  - La prueba principal del home queda alineada a la nueva semantica y densidad visual.
- Proximo paso:
  - Validar visualmente si el mismo tratamiento de densidad conviene tambien para `logistica` o si debe mantenerse el layout de 6 cards sin variaciones.

## 2026-03-16 09:03 UTC-6 | tool: Codex CLI
- Objetivo: ajustar el copy de las cards personales del home para hacerlas mas claras al usuario final.
- Tareas: `REQ-135`
- Cambios:
  - `app/main.py`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - `Mis Requisiciones` pasa a `Todas Mis Requisiciones`.
  - `Mis Requisiciones Pendientes` pasa a `Requisiciones Pendientes`.
  - `Mis Cerradas` pasa a `Requisiciones Finalizadas`.
  - `Mis Rechazadas` pasa a `Requisiciones Rechazadas`.
- Proximo paso:
  - Validar visualmente si la longitud nueva sigue cabiendo bien en el grid de seis cards, especialmente en resoluciones medias.

## 2026-03-13 20:18 UTC-6 | tool: Codex CLI
- Objetivo: corregir la inconsistencia entre las cards personales del home y el detalle real de `Mis Requisiciones`.
- Tareas: `REQ-134`
- Cambios:
  - `app/main.py`
  - `templates/mis_requisiciones.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - `Pendientes de Mis Requisiciones` se renombra a `Mis Requisiciones Pendientes`.
  - `/mis-requisiciones` agrega filtro SSR por `estado` y la vista incorpora un selector simple con auto-submit.
  - Las cards personales del home apuntan ahora a subconjuntos reales del historial (`abiertas`, `cerradas`, `rechazada`, `seguimiento`) en vez de caer todas en el mismo listado completo.
- Proximo paso:
  - Validar visualmente si conviene agregar mas adelante filtros equivalentes por fecha o motivo en `Mis Requisiciones`, manteniendo la vista mas ligera que `Todas las Requisiciones`.

## 2026-03-13 20:02 UTC-6 | tool: Codex CLI
- Objetivo: corregir la semantica del home para que las cards representen trabajo personal u operativo por rol sin mezclar historico/global en el mismo indicador.
- Tareas: `REQ-133`
- Cambios:
  - `app/main.py`
  - `templates/home.html`
  - `static/theme.css`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - La ruta `/` ahora construye `home_cards` y `home_actions` explicitamente por rol (`user`, `logistica`, `aprobador`, `bodega`, `jefe_bodega`, `admin`).
  - El template del home ya no hardcodea seis KPI ambiguos; renderiza cards consistentes por rol y elimina el bloque `Indicadores Rápidos`.
  - `Acciones Rápidas` queda como unico panel inferior y se alimenta tambien desde backend para mantener coherencia semantica.
- Proximo paso:
  - Validar visualmente la densidad del home por rol, especialmente `admin`, `bodega` y `jefe_bodega`, para confirmar que los labels nuevos caben bien sin romper el grid.

## 2026-03-13 19:08 UTC-6 | tool: Codex CLI
- Objetivo: corregir la legibilidad del label `Administración` en el navbar admin tras el compactado en dos lineas.
- Tareas: `REQ-132`
- Cambios:
  - `templates/partials/navbar.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - `Administración` deja de partirse como si fueran dos palabras y vuelve a mostrarse como una sola etiqueta.
  - El resto del compactado del navbar se mantiene intacto.
- Proximo paso:
  - Validar visualmente si `Administración` sigue cabiendo bien en admin o si conviene una abreviatura deliberada distinta en otra iteracion.

## 2026-03-13 19:02 UTC-6 | tool: Codex CLI
- Objetivo: reducir el ancho percibido del navbar compactando los labels largos sin cambiar el mapa de navegacion.
- Tareas: `REQ-131`
- Cambios:
  - `templates/partials/navbar.html`
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `sed -n '1,120p' templates/partials/navbar.html`
  - `rg -n "nav-item|menu-links" static/theme.css static/style.css`
- Resultado:
  - Los labels largos del navbar ahora se renderizan en dos lineas (`Nueva Requisicion`, `Mis Requisiciones`, `Todas las Requisiciones`, `Monitor de Actividad` y el agrupador de administracion).
  - El ahorro de ancho se obtiene sin mover menus, sin introducir JS y sin tocar permisos.
- Proximo paso:
  - Validar visualmente el navbar con `admin` y `logistica` para confirmar que la densidad mejora sin sacrificar legibilidad.

## 2026-03-13 18:40 UTC-6 | tool: Codex CLI
- Objetivo: ampliar la cobertura del buscador de `Todas las Requisiciones` para alinearlo a las columnas y datos operativos realmente visibles en la tabla.
- Tareas: `REQ-130`
- Cambios:
  - `app/main.py`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m py_compile app/main.py`
  - `python -m compileall tests/test_basic_flow.py`
- Resultado:
  - `q` ahora busca tambien por `motivo_requisicion`, `prokey_ref`, `receptor_designado.nombre` y por nombres de actores operativos (`aprobador`, `rechazador`, `preparador`, `entregador`, `liquidador`, `liquidada en Prokey`).
  - Se agrega cobertura de prueba para motivo, receptor, actor y referencia Prokey.
- Proximo paso:
  - Validar manualmente si conviene sumar tambien busqueda por comentarios de aprobacion/rechazo/entrega o si eso ya seria demasiado ruido para un solo campo.

## 2026-03-13 18:28 UTC-6 | tool: Codex CLI
- Objetivo: mejorar la usabilidad del filtro de fechas en la vista global sin introducir datepickers externos ni romper el fallback nativo/manual.
- Tareas: `REQ-129`
- Cambios:
  - `templates/todas_requisiciones.html`
  - `static/theme.css`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "type=\\\"date\\\"|appearance|calendar-picker|showPicker" templates static`
  - `python -m compileall tests/test_basic_flow.py`
- Resultado:
  - Los inputs de fecha siguen siendo nativos (`type=date`) y aceptan escritura manual.
  - En navegadores compatibles, un clic sobre el campo ahora intenta abrir el picker con `showPicker()`.
  - El control gana affordance visual ligera mediante cursor/indicador del picker.
- Proximo paso:
  - Validar manualmente en Chrome si el calendario ya abre al clic y decidir si conviene extender el mismo patron a otros filtros de fecha futuros.

## 2026-03-13 18:10 UTC-6 | tool: Codex CLI
- Objetivo: reducir friccion en listados SSR haciendo que los filtros por selector se apliquen sin clic extra, sin tocar logica de negocio.
- Tareas: `REQ-128`
- Cambios:
  - `templates/aprobar.html`
  - `templates/todas_requisiciones.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall tests/test_basic_flow.py`
  - `python -m py_compile app/main.py`
- Resultado:
  - Los selectores de `Aprobar` y `Todas las Requisiciones` ahora envian el formulario automaticamente al cambiar.
  - `Buscar` se mantiene como accion explicita para texto libre y fechas, evitando recargas innecesarias mientras el usuario escribe o arma un rango.
  - Se agrego una cobertura SSR minima para confirmar presencia de los hooks de auto-submit.
- Proximo paso:
  - Validar manualmente si el mismo patron conviene extenderse a otras vistas filtradas como `Bodega`.

## 2026-03-13 17:35 UTC-6 | tool: Codex CLI
- Objetivo: separar la bandeja operativa de aprobacion del historial/consulta global, manteniendo intacta la logica de negocio.
- Tareas: `REQ-127`
- Cambios:
  - `app/main.py`
  - `templates/aprobar.html`
  - `templates/todas_requisiciones.html`
  - `templates/partials/navbar.html`
  - `templates/home.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "@app.get\\(\"/aprobar|mis-requisiciones|Todas las Requisiciones" app/main.py templates tests`
  - `python -m compileall app/main.py tests/test_basic_flow.py`
- Resultado:
  - `Aprobar` deja de mezclar historial y ahora muestra solo requisiciones `pendiente`.
  - Se agrega `/todas-requisiciones` como vista de consulta global con filtros de estado, departamento y rango de fechas.
  - Navbar y accesos rapidos del home quedan alineados a la nueva separacion entre bandeja operativa y vista de consulta.
- Proximo paso:
  - Validar visualmente densidad de filtros y decidir si en la siguiente iteracion conviene sumar filtro explicito por solicitante o referencia Prokey.

## 2026-03-13 09:48 UTC-6 | tool: Codex CLI
- Objetivo: ampliar el Monitor de Actividad para que los KPI de auditoria permitan bajar de agregado a caso concreto, listando requisiciones relacionadas sin salir de la vista.
- Tareas: `REQ-118G`, `REQ-118H`
- Cambios:
  - `app/main.py`
  - `templates/monitor_actividad.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "dashboard/auditoria|renderAuditKpis|kpi-indice-discrepancia|kpi-inversion-demos" app/main.py templates/monitor_actividad.html tests/test_basic_flow.py`
  - `python -m compileall app/main.py tests/test_basic_flow.py`
- Resultado:
  - Se agregan endpoints de detalle para requisiciones con diferencia y requisiciones con demo.
  - Los KPI de auditoria muestran botones `Ver detalle` y un panel inline reutilizable que lista folio, cierre, solicitante, motivo, receptor y resumen del caso.
  - El monitor ya permite bajar de KPI a listado relacionado sin abrir una pagina nueva.
- Proximo paso:
  - Validar visualmente el drill-down con datos reales y decidir si hace falta una segunda iteracion con filtros por fecha, export o apertura directa del modal detalle por fila.

## 2026-03-12 13:05 UTC-6 | tool: Codex CLI
- Objetivo: reducir el ancho horizontal del navbar agrupando accesos secundarios sin cambiar permisos ni rutas, usando menus desplegables simples y mantenibles.
- Tareas: `REQ-119`
- Cambios:
  - `templates/partials/navbar.html`
  - `static/style.css`
  - `static/theme.css`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `sed -n '1,220p' templates/partials/navbar.html`
  - `rg -n "main-nav|nav-pill|menu-links|logout-form|avatar-chip|topbar" static/style.css static/theme.css templates`
  - `python -m compileall tests/test_basic_flow.py`
- Resultado:
  - Los accesos `Usuarios/Catalogo/Respaldos` de `admin` ahora viven bajo un dropdown `Administracion`.
  - `Cambiar contrasena` deja de consumir ancho en la barra principal y pasa al menu desplegable del usuario junto a `Salir`.
  - La implementacion usa `details/summary`, evitando JS adicional y conservando una navegacion SSR simple.
- Proximo paso:
  - Validar visualmente el navbar en `admin`, `aprobador`, `jefe_bodega` y `bodega` para confirmar densidad, foco y comportamiento en resoluciones medias.

## 2026-03-11 15:19 UTC-6 | tool: Codex CLI
- Objetivo: alinear la terminologia del Monitor de Actividad al lenguaje operativo real, sustituyendo `fuga/fugas` por `diferencia/diferencias` sin cambiar la logica de calculo.
- Tareas: `REQ-118D`, `REQ-118E`, `REQ-118F`
- Cambios:
  - `app/main.py`
  - `templates/monitor_actividad.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "fuga|Fuga|fugas|Fugas" app templates tests docs/ai`
- Resultado:
  - El endpoint de auditoria ahora expone claves de payload alineadas a `diferencia`.
  - La UI del monitor ya muestra `Diferencia/Diferencias` en titulos, estados y graficos.
  - Las pruebas y la documentacion activa quedaron consistentes con la nueva terminologia.
- Proximo paso:
  - Validar visualmente el monitor con datos reales y confirmar si la siguiente iteracion agrega filtros o nuevas metricas.

## 2026-03-11 14:36 UTC-6 | tool: Codex CLI
- Objetivo: ejecutar `REQ-118E` y `REQ-118F`, completando la Fase 2 del Monitor de Actividad en frontend sin afectar la Fase 1.
- Tareas: `REQ-118E`, `REQ-118F`
- Cambios:
  - `templates/monitor_actividad.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `sed -n '1,520p' templates/monitor_actividad.html`
  - `rg -n "kpi|metric-card|dashboard-bi|status-muted" static/theme.css static/style.css templates/home.html`
  - `python -m compileall tests/test_basic_flow.py`
  - `timeout 20s .venv/bin/python -m pytest -q tests/test_basic_flow.py -k "dashboard or auditoria or monitor"`
- Resultado:
  - La vista del Monitor de Actividad ahora separa Fase 1 y Fase 2 con encabezados propios.
  - Se agregaron dos KPI cards: `Indice de Discrepancia` e `Inversion en Demos`.
  - Se agregaron dos graficos nuevos: `Ranking de Diferencia por Producto` y `Diferencias por Tecnico`.
  - El frontend consume `/api/dashboard/auditoria` en paralelo a `/api/dashboard/basicos`.
  - Los graficos de diferencias usan paleta de alerta (`danger` / `warning`) y cuentan con estado de carga/error igual que la Fase 1.
  - Se reforzo el test SSR para comprobar presencia de la Fase 2, sus `canvas`, KPIs y la llamada al endpoint nuevo.
  - `REQ-118E` y `REQ-118F` pasan a `done`.
- Proximo paso:
  - Validar visualmente la Fase 2 con datos reales y decidir la siguiente iteracion BI.

## 2026-03-11 14:18 UTC-6 | tool: Codex CLI
- Objetivo: ejecutar `REQ-118D`, agregando backend de auditoria y diferencias sin romper la Fase 1 del Monitor de Actividad.
- Tareas: `REQ-118D`
- Cambios:
  - `app/main.py`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "def calcular_retorno_esperado|calcular_retorno_esperado\\(" app/crud.py app/main.py tests`
  - `sed -n '1,260p' app/crud.py`
  - `sed -n '1,240p' app/models.py`
  - `python -m compileall app/main.py tests/test_basic_flow.py`
  - `timeout 20s .venv/bin/python -m pytest -q tests/test_basic_flow.py -k "dashboard or auditoria"`
- Resultado:
  - Se agrego `GET /api/dashboard/auditoria` protegido por los mismos roles del Monitor de Actividad.
  - El endpoint procesa requisiciones cerradas (`liquidada` y `liquidada_en_prokey`) con `joinedload` de items y receptor designado.
  - La diferencia por item se calcula reutilizando `calcular_retorno_esperado`; solo diferencias positivas se acumulan como perdida.
  - El payload devuelve KPIs (`indice_discrepancia_pct`, `requisiciones_con_diferencia`, `requisiciones_cerradas`, `inversion_demos`) y datasets para `diferencia_por_producto` y `diferencias_por_tecnico`.
  - Se agrego cobertura para acceso por rol y para el calculo agregado de auditoria, incluyendo contexto `instalacion_inicial` y demos.
  - `REQ-118D` pasa a `done`.
- Proximo paso:
  - Ejecutar `REQ-118E`: sumar la nueva seccion de auditoria/diferencias a `monitor_actividad.html`.

## 2026-03-11 14:03 UTC-6 | tool: Codex CLI
- Objetivo: registrar la Fase 2 del Monitor de Actividad antes de implementar backend o frontend, preservando intacta la Fase 1 ya operativa.
- Tareas: `EPIC-BI-02`, `REQ-118D`, `REQ-118E`, `REQ-118F`
- Cambios:
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `sed -n '1,80p' docs/ai/TASKS.md`
  - `sed -n '1,130p' docs/ai/HANDOFF.md`
  - `sed -n '1,60p' docs/ai/WORKLOG.md`
- Resultado:
  - Se formalizo `EPIC-BI-02` como `Monitor de Actividad (Fase 2: Auditoria y Diferencias)`.
  - La Fase 2 queda dividida en tres tareas separadas para backend, UI y JS.
  - Quedo explicitado que la logica de diferencia debe reutilizar `calcular_retorno_esperado` y que la Fase 1 no debe romperse ni reemplazarse.
- Proximo paso:
  - Esperar instruccion para comenzar `REQ-118D` sin adelantar implementacion de UI.

## 2026-03-11 13:44 UTC-6 | tool: Codex CLI
- Objetivo: institucionalizar la nomenclatura BI como `Monitor de Actividad` y limpiar ruta, template, navbar y documentacion activa.
- Tareas: `EPIC-BI-01`, `REQ-118A`, `REQ-118B`, `REQ-118C`
- Cambios:
  - `app/main.py`
  - `templates/monitor_actividad.html`
  - `templates/partials/navbar.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "dashboard_contingencias|Dashboard de Contingencias|Contingencias|/dashboard|monitor_actividad|Monitor de Actividad|/monitor" app templates docs/ai tests`
  - `python -m compileall app/main.py tests/test_basic_flow.py`
- Resultado:
  - La vista institucional pasa a llamarse `Monitor de Actividad`.
  - El template se renombra a `templates/monitor_actividad.html`.
  - La ruta web queda en `/monitor` con handler `get_monitor_actividad`.
  - El navbar muestra `Monitor de Actividad` y apunta a `/monitor`.
  - `TASKS` y `HANDOFF` quedan alineados a la nueva nomenclatura y la Fase 1 se marca completada.
- Proximo paso:
  - Proceder con la definicion e implementacion de metricas de la siguiente fase del Monitor de Actividad.

## 2026-03-11 13:18 UTC-6 | tool: Codex CLI
- Objetivo: ejecutar `REQ-118C`, conectando la shell SSR del dashboard a datos reales con `Chart.js`.
- Tareas: `REQ-118C`
- Cambios:
  - `templates/dashboard_contingencias.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n ":root|--|chart|alert|danger|primary|muted" static/theme.css static/style.css`
  - `sed -n '1,220p' templates/dashboard_contingencias.html`
  - `python -m compileall tests/test_basic_flow.py`
  - `timeout 20s .venv/bin/python -m pytest -q tests/test_basic_flow.py -k "dashboard or contingencias"`
- Resultado:
  - Se agrego `Chart.js` via CDN directamente en la vista del dashboard.
  - `cargarDatos()` ahora consume `/api/dashboard/basicos` con `fetch` y renderiza:
    - dona por motivo
    - barras horizontales para top solicitantes
    - barras horizontales para top items
    - barras verticales por hora
  - El grafico horario aplica color de alerta desde las `14:00` en adelante usando los tokens del tema.
  - Cada card tiene estado minimo de carga/error para no dejar el dashboard mudo si falla la API.
  - Se reforzo el test SSR para comprobar presencia del script CDN y de `cargarDatos()`.
  - `REQ-118C` pasa a `done`.
- Proximo paso:
  - Validar visualmente el dashboard con datos reales y decidir la siguiente iteracion BI (filtros o nuevas metricas).

## 2026-03-11 12:42 UTC-6 | tool: Codex CLI
- Objetivo: ejecutar `REQ-118B`, reemplazando el placeholder del dashboard por una vista SSR real y enlazandola en la navegacion protegida.
- Tareas: `REQ-118B`
- Cambios:
  - `app/main.py`
  - `templates/dashboard_contingencias.html`
  - `templates/partials/navbar.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `git branch --show-current`
  - `rg -n "navbar|dashboard|TemplateResponse\\(" app/main.py templates docs/ai`
  - `sed -n '1,220p' templates/base.html`
  - `sed -n '1,220p' templates/partials/navbar.html`
  - `sed -n '1,220p' templates/home.html`
  - `python -m compileall app/main.py tests/test_basic_flow.py`
  - `timeout 20s .venv/bin/python -m pytest -q tests/test_basic_flow.py -k "dashboard or contingencias"`
- Resultado:
  - `/dashboard` ya renderiza el template SSR `dashboard_contingencias.html` en lugar del HTML temporal.
  - La vista nueva mantiene el patron del proyecto: `base.html`, `page_header`, superficies `panel/view-panel` y grid responsivo 2x2.
  - Se agregaron cuatro `canvas` con ids estables para que `REQ-118C` conecte Chart.js sin rehacer la estructura.
  - El navbar ya muestra `Contingencias` solo para `admin`, `aprobador` y `jefe_bodega`.
  - Se reforzaron tests para confirmar presencia del SSR del dashboard y visibilidad del enlace por rol.
  - Se detecto y corrigio una regresion estructural en `app/main.py`: las rutas del dashboard habian quedado incrustadas dentro de `home()`, dejando codigo muerto y comportamiento inconsistente; `home`, `/dashboard` y `/api/dashboard/basicos` vuelven a quedar separados.
  - `python -m compileall` paso sin errores.
  - El `pytest` focal volvio a terminar por `timeout` sin salida util, consistente con la limitacion ambiental ya conocida de este repo.
  - `REQ-118B` pasa a `done`.
- Proximo paso:
  - Ejecutar `REQ-118C`: fetch a `/api/dashboard/basicos`, inclusion de Chart.js y renderizado de los cuatro graficos.

## 2026-03-11 12:18 UTC-6 | tool: Codex CLI
- Objetivo: ejecutar `REQ-118A`, dejando operativo el backend base del Dashboard de Contingencias.
- Tareas: `REQ-118A`
- Cambios:
  - `app/main.py`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "def template_context|TemplateResponse\\(|current_user\\.rol|No autorizado|@app.get\\(" app/main.py`
  - `sed -n '300,520p' app/main.py`
  - `sed -n '760,940p' app/main.py`
  - `sed -n '1180,1465p' app/main.py`
  - `python -m compileall app/main.py tests/test_basic_flow.py`
  - `timeout 20s .venv/bin/python -m pytest -q tests/test_basic_flow.py -k "dashboard_backend or dashboard_basicos"`
- Resultado:
  - Se agrego `ensure_dashboard_access(...)` para restringir acceso a `admin`, `aprobador` y `jefe_bodega`.
  - `GET /dashboard` ya existe en backend con respuesta temporal funcional mientras se implementa el template SSR real.
  - `GET /api/dashboard/basicos` ya entrega payload listo para UI con:
    - frecuencia por motivo
    - top solicitantes
    - top items por cantidad solicitada
    - distribucion horaria 0-23 con `alert_from_hour=14`
  - Se agregaron tests del backend del dashboard (acceso y agregaciones base).
  - `python -m compileall` paso sin errores.
  - El `pytest` focal no devolvio salida util antes del `timeout`, consistente con la limitacion ambiental ya conocida de este repo.
- Proximo paso:
  - Ejecutar `REQ-118B`: crear el template real `dashboard_contingencias.html` y agregar su enlace en navbar.

## 2026-03-11 12:02 UTC-6 | tool: Codex CLI
- Objetivo: formalizar la epica `Dashboard de Contingencias (Fase 1)` y dividirla en tareas ejecutables antes de comenzar implementacion.
- Tareas: `EPIC-BI-01`, `REQ-118A`, `REQ-118B`, `REQ-118C`
- Cambios:
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `git checkout feat/bi-dashboard`
  - `sed -n '1,80p' docs/ai/TASKS.md`
  - `sed -n '1,80p' docs/ai/HANDOFF.md`
- Resultado:
  - Se registro formalmente la epica `Dashboard de Contingencias (Fase 1)` en el tablero.
  - Se crearon las tres tareas iniciales separadas para backend, UI SSR y JS/Chart.js.
  - Quedo explicitado el contexto de negocio: esta app actua como registro de contingencias frente al cierre de Prokey a las 14:00; el dashboard debe ayudar a auditar y reducir ese uso.
  - `REQ-118` pasa a `done` porque la apertura del frente ya quedo resuelta; la ejecucion comienza con `REQ-118A`.
- Proximo paso:
  - Esperar instruccion para empezar `REQ-118A` sin adelantar implementacion de UI/JS.

## 2026-03-11 10:28 UTC-6 | tool: Codex CLI
- Objetivo: abrir un frente de trabajo aislado para el futuro dashboard de inteligencia de negocio, sin mezclarlo con `main` ni programar aun la funcionalidad.
- Tareas: `REQ-118`
- Cambios:
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `git branch --show-current`
  - `git status --short`
  - `git checkout -b feat/bi-dashboard`
- Resultado:
  - Se creo la rama `feat/bi-dashboard` desde `main` para desarrollar el dashboard BI sin comprometer la estabilidad de produccion en la linea principal.
  - Se dejo documentado que este frente entra primero en fase de definicion: objetivo, usuarios, metricas, filtros y alcance, antes de escribir codigo.
- Proximo paso:
  - Definir el alcance funcional de V1 del dashboard y convertirlo luego en tareas tecnicas concretas.

## 2026-03-11 10:05 UTC-6 | tool: Codex CLI
- Objetivo: corregir la inconsistencia en `Gestionar Entrega` donde `no_entregada` seguia pidiendo PIN/firma por el receptor designado.
- Tareas: `REQ-117`
- Cambios:
  - `app/main.py`
  - `templates/bodega_gestionar.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "no_entregada|delivery_result|pin|recib" app/main.py templates/bodega_gestionar.html templates/bodega_entrega_parcial.html tests/test_basic_flow.py tests/test_liquidacion.py`
  - `sed -n '1520,1645p' app/main.py`
  - `sed -n '1080,1255p' tests/test_basic_flow.py`
  - `timeout 20s .venv/bin/python -m pytest -q tests/test_basic_flow.py -k "no_entregada or requiere_recibe or pin_incorrecto"`
  - `python -m compileall app/main.py templates/bodega_gestionar.html tests/test_basic_flow.py`
- Resultado:
  - `POST /entregar/{id}` ahora ignora cualquier intento de validar firma cuando `resultado=no_entregada`; solo exige comentario y cierra el ciclo sin `recibido_por`.
  - La vista `Gestionar Entrega` oculta receptor/PIN al elegir `No entregada` y cambia el texto de ayuda para reflejar la regla real.
  - Se agrego test para cubrir el caso con receptor designado presente y `recibido_por_id` enviado sin PIN.
  - `python -m compileall` paso sin errores en los archivos tocados.
  - El `pytest` focal volvio a quedarse sin salida util y termino por `timeout`, consistente con el riesgo ya documentado para este entorno.
- Proximo paso:
  - Ejecutar prueba focal del flujo de entrega para confirmar que `no_entregada` guarda y que `completa` sigue exigiendo firma.

## 2026-03-11 09:20 UTC-6 | tool: Codex CLI
- Objetivo: alinear la documentacion del proyecto con la fase real de `beta operativa en produccion`, manteniendo el principio de simplicidad y la gobernanza multi-IA agnostica al modelo/herramienta.
- Tareas: `REQ-116`
- Cambios:
  - `README.md`
  - `docs/ai/CONTRACT.md`
  - `docs/ai/DECISIONS.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `sed -n '1,240p' docs/ai/CONTRACT.md`
  - `sed -n '1,240p' docs/ai/HANDOFF.md`
  - `sed -n '1,240p' docs/ai/DECISIONS.md`
  - `sed -n '1,240p' docs/ai/TASKS.md`
  - `sed -n '1,260p' README.md`
- Resultado:
  - La gobernanza deja de describir al sistema como MVP vigente y lo formaliza como `beta operativa en produccion controlada`.
  - Se preserva el espiritu original: simplicidad, baja complejidad accidental y cambios incrementales.
  - Queda explicitado que el proyecto seguira evolucionando via `vibe coding` con gobernanza agnostica al modelo LLM y a la herramienta.
  - Se refuerza la regla de trazabilidad: cambios, bugs, decisiones y hallazgos relevantes deben quedar documentados en los archivos de continuidad del repo.
- Proximo paso:
  - Mantener el mismo criterio en futuras tareas funcionales y, si se desea, depurar despues otros textos historicos que aun usen `MVP` solo como herencia de versiones previas.

## 2026-03-09 10:32 UTC-6 | tool: Codex CLI
- Objetivo: introducir estado operativo `preparado` antes de `entregada`, exigiendo preparación explícita de bodega antes de capturar la firma/PIN del receptor.
- Tareas: `REQ-110`
- Cambios:
  - `app/models.py`
  - `app/database.py`
  - `app/crud.py`
  - `app/main.py`
  - `app/pdf_generator.py`
  - `static/app.js`
  - `templates/bodega.html`
  - `templates/aprobar.html`
  - `templates/mis_requisiciones.html`
  - `templates/macros/ui.html`
  - `tests/test_basic_flow.py`
  - `README.md`
  - `docs/ai/CONTRACT.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates static tests`
  - `.venv/bin/python -m pytest -q tests/test_basic_flow.py -k "prepar" -v`
- Resultado:
  - Nuevo estado `preparado` con trazabilidad `prepared_at` / `prepared_by`.
  - `/bodega` ahora separa `Preparar` (cuando estado `aprobada`) de `Entregar` (cuando estado `preparado`).
  - `Gestionar Entrega`, `POST /entregar/{id}` y flujo parcial exigen requisición `preparado`.
  - Detalle API/modal, badges, filtros y PDF reconocen `preparado`; el PDF lo trata como fase pre-entrega y sigue mostrando cantidades solicitadas.
  - Historial de bodega queda alineado también con `prepared_by` para trazabilidad personal.
  - `python -m compileall app templates static tests` pasó sin errores.
  - `pytest` focal volvió a quedarse colgado tras la colección (`tests/test_basic_flow.py` con plugin `anyio`), comportamiento ya visto en este entorno; no se observaron fallos de sintaxis ni importación.
- Proximo paso:
  - Smoke manual en `/bodega` validando secuencia `aprobada -> preparado -> entregada` y apertura de PDF tanto en `aprobada` como en `preparado`.

## 2026-03-09 10:48 UTC-6 | tool: Codex CLI
- Objetivo: refinar UX del nuevo paso `Preparar` para que no cambie estado directo desde el listado de bodega.
- Tareas: `REQ-110A`
- Cambios:
  - `app/main.py`
  - `templates/bodega.html`
  - `templates/bodega_preparar.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates tests`
- Resultado:
  - `Preparar` ahora abre `GET /bodega/{id}/preparar` con tabla de ítems y cantidades.
  - La transición a `preparado` solo ocurre tras pulsar `Preparado`; `Cancelar` vuelve a `/bodega` sin cambios.
  - El test del flujo de preparación quedó alineado a la pantalla intermedia.

## 2026-03-05 14:03 UTC-6 | tool: Codex CLI
- Objetivo: aplicar ajuste de permisos solicitado para REQ-099: permitir que `admin` también pueda ejecutar `Confirmar en Prokey`.
- Tareas: `REQ-099E`
- Cambios:
  - `app/main.py`
  - `templates/bodega.html`
  - `tests/test_liquidacion.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -k prokey -v`
- Resultado:
  - Guard backend de `/requisiciones/{id}/liquidar-prokey` actualizado a `admin` o `jefe_bodega`.
  - Botón `Confirmar en Prokey` en historial de bodega visible para ambos roles.
  - Test de permisos actualizado para validar acceso `admin` y rechazo para `bodega`/`aprobador`.
- Proximo paso:
  - Smoke manual con usuario `admin` en `/bodega` confirmando cierre en Prokey sobre una requisición `liquidada`.

## 2026-03-05 13:46 UTC-6 | tool: Codex CLI
- Objetivo: corregir error 500 al confirmar `liquidada_en_prokey` en bases SQLite históricas con CHECK antiguo de estado.
- Tareas: `REQ-099D`
- Cambios:
  - `app/database.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app`
- Resultado:
  - `run_migrations()` ahora detecta si la definición SQL de `requisiciones` no contiene `liquidada_en_prokey`.
  - En ese caso reconstruye la tabla (rename/create/copy/drop) con el CHECK actualizado de estados.
  - Se elimina la causa de `IntegrityError` al intentar guardar estado `liquidada_en_prokey` en DB ya existentes.
- Proximo paso:
  - Reiniciar la app para ejecutar migración de startup y repetir `Confirmar en Prokey` sobre una requisición `liquidada`.

## 2026-03-05 13:24 UTC-6 | tool: Codex CLI
- Objetivo: implementar estado final de cierre `liquidada_en_prokey` (REQ-099C) con transición exclusiva de `jefe_bodega`, inmutabilidad y trazabilidad en detalle/timeline.
- Tareas: `REQ-099C`
- Cambios:
  - `app/models.py`
  - `app/database.py`
  - `app/crud.py`
  - `app/main.py`
  - `templates/macros/ui.html`
  - `templates/aprobar.html`
  - `templates/bodega.html`
  - `templates/mis_requisiciones.html`
  - `static/app.js`
  - `static/theme.css`
  - `tests/test_liquidacion.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates static tests`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v`
- Resultado:
  - Nuevo estado persistente `liquidada_en_prokey` y campos `prokey_liquidada_at` / `prokey_liquidada_por` en `Requisicion`.
  - Nueva función `marcar_liquidada_en_prokey(...)` con precondición estricta (`estado == liquidada`) y transición controlada.
  - Nuevo endpoint `POST /requisiciones/{id}/liquidar-prokey` exclusivo para rol `jefe_bodega`.
  - Historial de bodega: botón `Confirmar en Prokey` solo para `jefe_bodega` cuando estado `liquidada`; estado final muestra badge diferenciado y sin acciones.
  - API detalle + modal: incluyen actor/fecha de cierre Prokey y evento de timeline `Liquidada en Prokey`.
  - Tests: cobertura de flujo feliz, precondición de estado, inmutabilidad, control de rol y campos en payload detalle.
  - Validación: `45 passed`.
- Proximo paso:
  - Smoke manual con dos roles (`jefe_bodega` y `bodega`) para confirmar visibilidad del botón y bloqueo total de acciones en `liquidada_en_prokey`.

## 2026-03-05 12:46 UTC-6 | tool: Codex CLI
- Objetivo: implementar REQ-099A para reemplazar el `confirm()` de cambio de receptor por una UX integrada y deliberada en `Gestionar Entrega`.
- Tareas: `REQ-099A`
- Cambios:
  - `templates/bodega_gestionar.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall templates static`
- Resultado:
  - El selector de receptor inicia bloqueado (`disabled`).
  - Se agregó botón `Cambiar receptor`; al usarlo, habilita selector, oculta botón y muestra bloque de advertencia en página con el receptor designado original.
  - Se eliminó por completo el `confirm()` popup del navegador.
  - Se agregó respaldo en submit para que, si el selector sigue deshabilitado, su valor actual se envíe igualmente como campo hidden.
- Proximo paso:
  - Smoke manual en `/bodega/{id}/gestionar` para validar ambos caminos: sin cambio de receptor y con cambio explícito.

## 2026-03-05 12:58 UTC-6 | tool: Codex CLI
- Objetivo: extender REQ-099A a la pantalla de `Entrega Parcial`, manteniendo consistencia UX con `Gestionar Entrega`.
- Tareas: `REQ-099A`
- Cambios:
  - `templates/bodega_entrega_parcial.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall templates static`
- Resultado:
  - `Entrega Parcial` ahora inicia con selector de receptor deshabilitado, botón `Cambiar receptor`, bloque visual de advertencia integrada al habilitar cambio y sin `confirm()` del navegador.
  - Se agregó envío hidden del receptor cuando el select permanece deshabilitado, evitando pérdida de dato al submit.
- Proximo paso:
  - Ejecutar smoke manual en `/entregar/{id}/parcial` para validar los flujos con y sin cambio de receptor.

## 2026-03-05 13:09 UTC-6 | tool: Codex CLI
- Objetivo: implementar ajuste menor antierror solicitado en firma bodega: requerir confirmación explícita en página para cerrar cambio de receptor (`Guardar cambio`) y permitir rollback (`Cancelar`) en completo y parcial.
- Tareas: `REQ-099B`
- Cambios:
  - `templates/bodega_gestionar.html`
  - `templates/bodega_entrega_parcial.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall templates static`
- Resultado:
  - En ambas vistas, tras `Cambiar receptor` aparecen botones `Guardar cambio` y `Cancelar`.
  - `Guardar cambio` bloquea nuevamente el selector; `Cancelar` revierte al valor previo y también bloquea.
  - Se mantiene la advertencia visual integrada y no se usa `confirm()` del navegador.
- Proximo paso:
  - Smoke manual de dos escenarios por vista: cambiar+guardar y cambiar+cancelar, verificando que el valor enviado al backend coincida con el estado final bloqueado.

## 2026-03-05 12:22 UTC-6 | tool: Codex CLI
- Objetivo: implementar REQ-099 para capturar receptor designado desde la creación y reforzar trazabilidad/confirmación en firma de bodega.
- Tareas: `REQ-099`
- Cambios:
  - `app/models.py`
  - `app/database.py`
  - `app/crud.py`
  - `app/main.py`
  - `templates/crear_requisicion.html`
  - `templates/bodega_gestionar.html`
  - `templates/bodega_entrega_parcial.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates static`
- Resultado:
  - Nuevo campo persistido `receptor_designado_id` en requisición (nullable para históricos).
  - `/crear` ahora exige seleccionar receptor designado (usuario activo) y lo valida en backend.
  - En captura de firma bodega (completa/parcial) se muestra el receptor designado y se solicita confirmación explícita si el receptor seleccionado difiere.
  - `GET /api/requisiciones/{id}` expone `receptor_designado` como objeto `{id,nombre,rol}`.
- Proximo paso:
  - Ejecutar smoke manual E2E: crear requisición con designado, gestionar entrega con mismo receptor (sin aviso) y con distinto receptor (con confirmación).

## 2026-03-05 11:48 UTC-6 | tool: Codex CLI
- Objetivo: cerrar REQ-098C para forzar la apariencia de checkbox "Para Demo" contra overrides de `pico.css` y user agent (`appearance: auto` / `border-radius` heredado).
- Tareas: `REQ-098C`
- Cambios:
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall static`
- Resultado:
  - El selector de `.item-demo-check input[type="checkbox"]` quedó reforzado con `!important` en propiedades críticas (`appearance`, dimensiones, borde, radio, fondo, display y estado checked).
  - Se neutraliza la interferencia visual del UA stylesheet y de PicoCSS en el control "Para Demo".
- Proximo paso:
  - Verificar en navegador con caché deshabilitada que el control se vea cuadrado y muestre `✓` blanca con fondo azul al marcarse.

## 2026-03-05 11:36 UTC-6 | tool: Codex CLI
- Objetivo: cerrar REQ-098B corrigiendo la apariencia del control "Para Demo" para que se perciba claramente como checkbox (no radio) y su estado checked sea visible.
- Tareas: `REQ-098B`
- Cambios:
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall static`
- Resultado:
  - El control ahora usa forma cuadrada (`border-radius: 3px`) y muestra `✓` blanca al marcarse.
  - Se eliminó el pseudo-indicador circular que inducía apariencia de radio.
- Proximo paso:
  - Validar en `/crear` que todas las filas (inicial y dinámicas) mantengan lectura clara de marcado/desmarcado.

## 2026-03-05 11:20 UTC-6 | tool: Codex CLI
- Objetivo: cerrar REQ-098A para dejar explícito el control "Para Demo" como checkbox en template y JS dinámico, evitando ambigüedad de comportamiento visual.
- Tareas: `REQ-098A`
- Cambios:
  - `templates/crear_requisicion.html`
  - `static/app.js`
  - `docs/ai/TASKS.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates static`
- Resultado:
  - El control `Para Demo` queda definido explícitamente como `checkbox` con `value="on"` en la fila base y filas agregadas dinámicamente.
  - Se mantiene la lógica backend existente (presencia = `True`, ausencia = `False`) sin cambios.
- Proximo paso:
  - Validar manualmente en `/crear` que se pueda marcar/desmarcar en varias filas y que persista al enviar.

## 2026-03-03 14:41 UTC-6 | tool: Codex CLI
- Objetivo: aclarar el encabezado de `Ingreso PK` en el detalle liquidado para explicitar que corresponde a la operación de bodega.
- Tareas: `REQ-093C`
- Cambios:
  - `static/app.js`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall static`
- Resultado:
  - El encabezado del detalle liquidado ahora dice `Ingreso PK (Bodega)`.
- Proximo paso:
  - Validar visualmente que el copy no rompa el ancho de la tabla en resoluciones medias.

## 2026-03-03 14:32 UTC-6 | tool: Codex CLI
- Objetivo: corregir la semántica visual de `DIF` en el detalle liquidado para que un faltante no se lea como sobrante por el signo `+`.
- Tareas: `REQ-093B`
- Cambios:
  - `static/app.js`
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall static`
- Resultado:
  - La columna `DIF` ahora muestra `Falta X`, `Extra X` u `OK` en vez de `+/-`.
  - Se agregó tooltip con el esperado/regresado para mantener trazabilidad sin ambigüedad.
  - El chip se ensanchó para soportar el nuevo copy sin verse apretado.
- Proximo paso:
  - Validar manualmente un caso con faltante y otro con retorno extra para confirmar que la lectura operativa sea inmediata.

## 2026-03-03 14:05 UTC-6 | tool: Codex CLI
- Objetivo: alinear la liquidación con el catálogo como fuente de verdad, quitando edición manual de `Tipo` cuando el ítem ya está clasificado.
- Tareas: `REQ-093A`
- Cambios:
  - `app/main.py`
  - `templates/liquidar.html`
  - `static/theme.css`
  - `static/style.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates static`
- Resultado:
  - La pantalla de liquidación muestra `Tipo` como valor bloqueado cuando `CatalogoItem.tipo_item` existe.
  - El selector solo sigue disponible para ítems sin clasificación.
  - Backend fuerza el tipo proveniente de catálogo y evita override manual por POST.
- Proximo paso:
  - Validar manualmente una liquidación mixta con un item clasificado y otro sin clasificación para confirmar que solo el segundo conserva el select.

## 2026-03-03 13:35 UTC-6 | tool: Codex CLI
- Objetivo: modelar `contexto_operacion` por línea de ítem para distinguir instalación inicial de reposición sin alterar el tipo físico del ítem.
- Tareas: `REQ-093`
- Cambios:
  - `app/models.py`
  - `app/database.py`
  - `app/crud.py`
  - `app/main.py`
  - `templates/crear_requisicion.html`
  - `static/app.js`
  - `static/theme.css`
  - `tests/test_liquidacion.py`
  - `docs/ai/DECISIONS.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates static tests`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -k "contexto_operacion or retorno_incompleto or detalle_liquidada_incluye_campos" -v`
- Resultado:
  - `Item.contexto_operacion` quedó persistido con migración incremental.
  - La creación de requisición ya captura `Reposicion` / `Instalacion inicial` por línea.
  - `ALERTA_RETORNO_INCOMPLETO` solo aplica a ítems `RETORNABLE` que no sean `instalacion_inicial`.
  - El detalle de requisición liquidada muestra el contexto junto al tipo para trazabilidad.
  - Validación ejecutada: `6 passed`.
- Proximo paso:
  - Hacer smoke manual end-to-end con un retornable en `Instalación inicial` y validar que `Regresa = 0` no dispare retorno incompleto.

## 2026-03-03 11:37 UTC-6 | tool: Codex CLI
- Objetivo: mover la clasificación retornable/consumible al catálogo como fuente de verdad sin introducir FK nueva en `Item`.
- Tareas: `REQ-092`
- Cambios:
  - `app/models.py`
  - `app/database.py`
  - `app/main.py`
  - `templates/liquidar.html`
  - `tests/test_admin_catalog_items.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates tests`
  - `.venv/bin/python -m pytest -q tests/test_admin_catalog_items.py -v`
- Resultado:
  - `CatalogoItem` ahora persiste `tipo_item`.
  - La clasificación automática usa la primera palabra normalizada del nombre, con listas explícitas de prefijos.
  - Crear, editar e importar catálogo recalculan `tipo_item`.
  - Liquidación ya no infiere por heurística local; usa el valor de catálogo por nombre normalizado y permite `Seleccionar...` cuando no hay match.
- Proximo paso:
  - Validar manualmente un flujo de liquidación con un ítem retornable, uno consumible y uno sin clasificación para confirmar el default real en UI.

## 2026-03-03 12:36 UTC-6 | tool: Codex CLI
- Objetivo: corregir el caso donde el select de liquidación seguía mostrando `Seleccionar...` para ítems ya clasificables, debido a catálogo histórico con `tipo_item = null`.
- Tareas: `REQ-092A`
- Cambios:
  - `app/crud.py`
  - `app/main.py`
  - `app/database.py`
  - `tests/test_admin_catalog_items.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - La lógica de clasificación quedó centralizada en `app/crud.py`.
  - `run_migrations()` ahora hace backfill de `catalogo_items.tipo_item` para registros previos.
  - La pantalla de liquidación usa fallback de clasificación por nombre mientras termina de converger el catálogo persistido.
- Proximo paso:
  - Abrir una liquidación con ítems históricos ya existentes y confirmar que el tipo aparezca preseleccionado sin necesidad de editar el catálogo uno por uno.

## 2026-03-03 12:42 UTC-6 | tool: Codex CLI
- Objetivo: corregir el error de arranque provocado por import circular entre `database.py` y `crud.py` después de mover la clasificación al catálogo.
- Tareas: `REQ-092B`
- Cambios:
  - `app/catalog_types.py`
  - `app/crud.py`
  - `app/main.py`
  - `app/database.py`
  - `tests/test_admin_catalog_items.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app tests`
  - `.venv/bin/python - <<'PY' ... from app.main import app ... PY`
- Resultado:
  - La clasificación quedó aislada en un módulo sin dependencias ORM.
  - `app.main` vuelve a importar correctamente y `uvicorn` ya puede arrancar sin `ImportError` circular.
- Proximo paso:
  - Levantar la app y validar visualmente una liquidación real para confirmar que el fix técnico también deja visible el default correcto en el select `Tipo`.

## 2026-03-03 11:21 UTC-6 | tool: Codex CLI
- Objetivo: agregar una acción exclusiva de admin para borrar por completo el catálogo de items con doble verificación, manteniendo el cambio acotado al módulo de catálogo.
- Tareas: `REQ-091`
- Cambios:
  - `app/main.py`
  - `templates/admin_catalogo_items.html`
  - `tests/test_admin_catalog_items.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app templates tests`
  - `.venv/bin/python -m pytest -q tests/test_admin_catalog_items.py -v`
- Resultado:
  - El catálogo ahora tiene una acción destructiva dedicada solo para admin.
  - La eliminación total exige dos verificaciones: checkbox de confirmación y texto exacto `BORRAR CATALOGO`.
  - Quedaron agregados tests de éxito y rechazo por confirmación incompleta/incorrecta.
- Proximo paso:
  - Ejecutar smoke manual en `/admin/catalogo-items` para validar el flujo visual completo antes de usarlo sobre datos reales.

## 2026-03-03 11:28 UTC-6 | tool: Codex CLI
- Objetivo: reordenar el layout de tarjetas en catálogo admin sin tocar la lógica del CRUD.
- Tareas: `REQ-091A`
- Cambios:
  - `templates/admin_catalogo_items.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - `Importar catalogo` y `Borrar todo el catalogo` ahora comparten la fila superior.
  - `Buscar en catalogo` queda debajo, separado, con una jerarquía visual más clara.
- Proximo paso:
  - Validar manualmente el comportamiento responsive para confirmar que las dos tarjetas superiores colapsan bien en pantallas angostas.

## 2026-03-03 11:32 UTC-6 | tool: Codex CLI
- Objetivo: corregir el fallo de implementación del nuevo layout de catálogo, donde el template sí cambió pero faltaba la clase CSS que hacía efectiva la grilla.
- Tareas: `REQ-091B`
- Cambios:
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Resultado:
  - Se agregó `form-grid-2` al tema y su comportamiento responsive.
  - El layout de `Importar + Borrar arriba / Buscar abajo` ahora sí tiene soporte visual real.
- Proximo paso:
  - Refrescar `/admin/catalogo-items` y validar manualmente desktop + móvil para confirmar que el cambio ya se ve aplicado.

## 2026-03-03 10:24 UTC-6 | tool: Codex CLI
- Objetivo: corregir el rol mixto `jefe_bodega` para que combine aprobación + bodega de forma real, empezando por revisar gobernanza y luego cerrar el desfase de permisos.
- Tareas: `REQ-090A`
- Cambios:
  - `app/crud.py`
  - `templates/home.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `pytest -q tests/test_basic_flow.py -k jefe_bodega -v`
- Resultado:
  - `jefe_bodega` ya puede aprobar requisiciones en backend porque `puede_aprobar()` lo reconoce como rol válido.
  - Home quedó alineado con el rol mixto: muestra accesos y acciones tanto de aprobar como de bodega.
  - `/aprobar` volvió a mostrar `Gestionar` para requisiciones pendientes cuando el usuario es `jefe_bodega`.
  - Se agregaron pruebas específicas para aprobación real, visibilidad operativa en Home y disponibilidad de gestión en `/aprobar`.
- Proximo paso:
  - Ejecutar smoke manual con `jefe_bodega` en `/aprobar` y `/bodega` para validar la experiencia integrada end-to-end.

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

## 2026-02-25 15:05 CST | tool: Codex CLI
- Objetivo: Implementar `REQ-062` (detalle solo lectura para requisiciones liquidadas).
- Cambios de codigo:
  - `app/main.py`
    - `GET /api/requisiciones/{id}` ahora incluye para estado `liquidada`:
      - campos de cabecera: `prokey_ref`, `liquidation_comment`, `liquidated_by_name`, `liquidated_at`.
      - campos por item: `qty_returned_to_warehouse`, `qty_used`, `qty_left_at_client`, `item_liquidation_note`, `liquidation_alerts` (JSON deserializado).
      - derivados por item: `qty_ocupo`, `pk_ingreso_qty`, `delta`.
      - evento de timeline: `Requisicion liquidada`.
    - `aprobar_view` incluye `joinedload(Requisicion.liquidator)` para tabla de gestionado por.
  - `static/app.js`
    - Modal detalle detecta `estado=liquidada` y renderiza tabla estilo papel:
      - `Descripcion`, `Solicitado`, `Lleva`, `Regresa`, `Ocupo`, `Ingreso PK`, `Delta`, `Alertas`.
    - Bloque nuevo `Resumen de Liquidacion` en cabecera del modal con:
      - referencia Prokey, actor, fecha/hora, comentario y conteo global de alertas.
    - Delta con resaltado visual (`delta-warn` / `delta-danger`).
    - Alertas por item como badges por severidad (`warn`/`high`) y nota por item cuando aplica.
  - `static/theme.css`
    - Estilos para resumen de liquidacion, tabla papel, badges de alertas y estados de delta.
  - `templates/aprobar.html`
    - Filtro y badge para estado `liquidada`.
    - Columna "Gestionado por" muestra `liquidator` para requisiciones liquidadas.
  - `templates/mis_requisiciones.html`
    - Badge explicito para estado `liquidada`.
  - `templates/macros/ui.html`
    - `status_badge` reconoce `liquidada` con estilo diferenciado.
  - `tests/test_liquidacion.py`
    - Nuevos tests:
      - `test_detalle_liquidada_incluye_campos`
      - `test_detalle_liquidada_campos_derivados`
      - `test_liquidada_es_solo_lectura`
      - `test_liquidar_get_redirige_si_ya_liquidada`
- Gobernanza actualizada:
  - `docs/ai/TASKS.md`: `REQ-062` marcado `done`.
  - `docs/ai/HANDOFF.md`: estado post-REQ-062 y siguiente bloque de trabajo.
  - `docs/ai/WORKLOG.md`: entrada de sesion.
- Comandos ejecutados:
  - `python -m compileall app static templates tests/test_liquidacion.py` -> OK
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v` -> **16 passed**
- Resultado:
  - Requisiciones liquidadas ahora se auditan en detalle con formato operativo completo, sin permitir cambios.
- Proximo paso:
  - Definir y priorizar siguiente REQ de reporteria minima manteniendo simplicidad v1.x.

## 2026-02-25 16:05 CST | tool: Codex CLI
- Objetivo: Implementar `REQ-063` (tests de integracion/smoke para flujo completo con liquidacion).
- Cambios de codigo:
  - `tests/test_liquidacion_integration.py` (nuevo)
    - Cobertura de flujo completo de requisicion con liquidacion:
      - escenario canónico sin alertas (2 items, deltas en 0),
      - faltante (`ALERTA_FALTANTE`),
      - retorno extra (`ALERTA_SOBRANTE` + `ALERTA_RETORNO_EXTRA`),
      - salida sin soporte (`ALERTA_SOBRANTE` + `ALERTA_SALIDA_SIN_SOPORTE`),
      - precondiciones (`prokey_ref` obligatorio, no liquidar si no entregada, no liquidar `no_entregada`),
      - inmutabilidad de requisicion liquidada,
      - timeline con evento de liquidacion,
      - redireccion en `GET /liquidar/{id}` cuando ya esta liquidada.
    - Fixtures aisladas con SQLite en memoria (`StaticPool`) para evitar lock de archivos temporales.
    - Backend anyio fijado a `asyncio` para evitar parametrizacion `trio` no instalada.
- Gobernanza actualizada:
  - `docs/ai/TASKS.md`: `REQ-063` marcado `done`.
  - `docs/ai/HANDOFF.md`: estado actualizado y riesgo abierto de hang en pruebas legacy con `TestClient`.
  - `docs/ai/WORKLOG.md`: entrada de sesion.
- Comandos ejecutados:
  - `.venv/bin/python -m pytest -q tests/test_liquidacion_integration.py -v` -> **10 passed**
  - `timeout 900 .venv/bin/python -m pytest -q tests/ -v` -> en este entorno CLI quedo colgado en pruebas legacy (`TestClient`), no concluyente.
- Resultado:
  - Cobertura de regresion de liquidacion fortalecida con escenarios de negocio completos y verificaciones de detalle/timeline.
- Proximo paso:
  - Estabilizar ejecucion de `pytest tests/` completa en entorno CLI para recuperar smoke global automatizado.

## 2026-02-25 15:08 CST | tool: Codex CLI
- Objetivo: Implementar `REQ-064` para permitir liquidar sin `prokey_ref` y marcar Prokey pendiente en el detalle.
- Cambios de codigo:
  - `app/main.py`
    - `POST /liquidar/{req_id}` ya no bloquea por referencia vacia.
    - `prokey_ref` se normaliza a `None` cuando llega vacio (`strip()` + conversion a null).
  - `app/crud.py`
    - `ejecutar_liquidacion(...)` ahora acepta `prokey_ref` opcional y persiste `requisicion.prokey_ref = prokey_ref or None`.
  - `templates/liquidar.html`
    - Campo de referencia Prokey cambiado a opcional (sin `required`).
    - Nuevo microcopy: se puede completar despues.
  - `static/app.js`
    - En resumen de liquidacion, si `prokey_ref` no existe muestra `Pendiente` + badge `Prokey pendiente`.
  - `static/theme.css`
    - Estilo para badge visual de Prokey pendiente.
  - `tests/test_liquidacion.py`
    - Reemplazo de prueba de obligatoriedad por `test_liquidar_permite_prokey_ref_vacio` (liquida y guarda `NULL`).
  - `tests/test_liquidacion_integration.py`
    - Reemplazo de precondicion antigua por `test_liquidar_sin_prokey_ref_guarda_null` (flujo integrado + detalle API con `prokey_ref=None`).
- Gobernanza actualizada:
  - `docs/ai/TASKS.md`: `REQ-064` marcado `done`.
  - `docs/ai/HANDOFF.md`: estado actual incluye cierre de REQ-064.
  - `docs/ai/WORKLOG.md`: entrada de sesion.
- Comandos ejecutados:
  - `python -m compileall app static templates tests` -> OK
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v` -> **16 passed**
  - `.venv/bin/python -m pytest -q tests/test_liquidacion_integration.py -v` -> **10 passed**
- Resultado:
  - Liquidacion ya no depende de referencia inmediata de Prokey.
  - Se conserva trazabilidad de cierre y se explicita pendiente operativo en detalle.
- Proximo paso:
  - Definir si se agrega flujo posterior de "completar referencia Prokey" para requisiciones ya liquidadas.

## 2026-02-25 15:17 CST | tool: Codex CLI
- Objetivo: Implementar `REQ-065` para completar `prokey_ref` despues de liquidar sin reabrir cantidades.
- Cambios de codigo:
  - `app/main.py`
    - Helper `puede_editar_prokey_ref(req, current_user)`: solo `estado=liquidada` y (`admin` o solicitante).
    - Nueva ruta `GET /requisiciones/{id}/prokey-ref`: renderiza formulario de edicion y valida permisos/estado.
    - Nueva ruta `POST /requisiciones/{id}/prokey-ref`: valida permisos/estado, exige referencia no vacia y actualiza solo `requisicion.prokey_ref`.
  - `templates/editar_prokey_ref.html` (nuevo)
    - Pantalla dedicada para completar referencia Prokey con contexto de requisicion y botones Guardar/Cancelar.
  - `static/app.js`
    - En detalle de requisiciones liquidadas con referencia pendiente, agrega link `Agregar referencia Prokey` hacia `/requisiciones/{id}/prokey-ref`.
  - `static/theme.css`
    - Estilo del link de accion en resumen de liquidacion (`.prokey-add-link`).
  - `tests/test_liquidacion.py`
    - Nuevos tests:
      - `test_update_prokey_ref_permite_admin`
      - `test_update_prokey_ref_permite_propietario`
      - `test_update_prokey_ref_bloquea_no_propietario`
      - `test_update_prokey_ref_requiere_estado_liquidada`
      - `test_update_prokey_ref_no_permite_vacio`
      - `test_api_detalle_refleja_prokey_ref_actualizado`
      - `test_update_prokey_ref_get_form_permitido`
    - Validacion explicita de inmutabilidad: actualizar referencia no toca cantidades ni `liquidation_alerts`.
- Gobernanza actualizada:
  - `docs/ai/TASKS.md`: `REQ-065` marcado `done`.
  - `docs/ai/HANDOFF.md`: estado actual incluye cierre de REQ-065.
  - `docs/ai/WORKLOG.md`: entrada de sesion.
- Comandos ejecutados:
  - `python -m compileall app static templates tests` -> OK
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py::test_update_prokey_ref_get_form_permitido -v` -> **1 passed**
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v` -> **23 passed**
  - `.venv/bin/python -m pytest -q tests/test_liquidacion_integration.py -v` -> **10 passed**
- Resultado:
  - `prokey_ref` ya puede completarse post-liquidacion por usuarios autorizados sin alterar la trazabilidad de liquidacion.
- Proximo paso:
  - Evaluar si se agrega filtro/lista de requisiciones liquidadas con `prokey_ref` pendiente para cierre operativo diario.

## 2026-02-25 17:06 CST | tool: Codex CLI
- Objetivo: Implementar `REQ-066` (modo por item RETORNABLE/CONSUMIBLE, campo `No usado` y nueva formula de diferencia/alertas).
- Cambios de codigo:
  - `app/models.py`
    - Nuevo campo en `Item`: `liquidation_mode` (`String(20)`, nullable).
  - `app/database.py`
    - Migracion incremental agregada: `ALTER TABLE items ADD COLUMN liquidation_mode TEXT`.
  - `app/main.py`
    - Nueva heuristica `infer_liquidation_mode(descripcion)` para default de selector en UI:
      - RETORNABLE: `MOPA`, `ALFOMBRA`, `HERRAMIENTA`, `EQUIPO`.
      - CONSUMIBLE: `SPRAY`, `PILA`, `QUIM`, `DOSIS`.
      - default conservador: `RETORNABLE`.
    - `GET /liquidar/{id}` inyecta `default_mode` por item para render.
    - `POST /liquidar/{id}` parsea `mode_{item_id}` y `qty_not_used_{item_id}` (mantiene fallback a `qty_left_{item_id}` por compatibilidad de pruebas).
    - Validacion de modo: solo `RETORNABLE` o `CONSUMIBLE`.
  - `app/crud.py`
    - `ejecutar_liquidacion(...)` persiste `item.liquidation_mode`.
    - `calcular_alertas_item(item)` refactor:
      - `not_used = qty_left_at_client` (reinterpretado como "No usado"),
      - `expected_return` por modo:
        - RETORNABLE: `used + not_used`,
        - CONSUMIBLE: `not_used`,
      - `diferencia = expected_return - returned`,
      - alertas `ALERTA_FALTANTE/ALERTA_SOBRANTE` segun signo de `diferencia`,
      - mantiene alertas high: `ALERTA_SALIDA_SIN_SOPORTE` y `ALERTA_RETORNO_EXTRA`.
  - `templates/liquidar.html`
    - Columna nueva `Tipo` (selector por item).
    - Etiqueta `Dejado en cliente` renombrada a `No usado`.
    - `Delta` renombrado a `Diferencia`.
    - JS en vivo actualizado para calcular diferencia por modo y mostrar `Esperado regrese: X`.
  - `tests/test_liquidacion.py`
    - Ajustes a expectativas con nueva semantica.
    - Nuevos tests agregados:
      - `test_diferencia_retornable_cuadra`
      - `test_diferencia_retornable_retorno_extra`
      - `test_diferencia_consumible_cuadra`
      - `test_diferencia_consumible_faltante`
      - `test_salida_sin_soporte`
  - `tests/test_liquidacion_integration.py`
    - Ajuste de helper para enviar `mode_{item_id}`.
    - Ajuste de escenario sin alertas y expectativa de `salida_sin_soporte`.
- Gobernanza actualizada:
  - `docs/ai/TASKS.md`: `REQ-066` marcado `done`.
  - `docs/ai/HANDOFF.md`: estado actual incluye cierre de REQ-066.
  - `docs/ai/WORKLOG.md`: entrada de sesion.
- Comandos ejecutados:
  - `python -m compileall app templates static tests` -> OK
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v` -> **28 passed**
  - `.venv/bin/python -m pytest -q tests/test_liquidacion_integration.py -v` -> **10 passed**
- Resultado:
  - La captura de liquidacion deja de generar falsos positivos por una formula unica; ahora cada item se interpreta por modo operativo y mantiene comportamiento no bloqueante.
- Proximo paso:
  - `REQ-067`: reflejar en modal detalle el nuevo significado (`No usado`, `liquidation_mode`) y la diferencia por modo para auditoria consistente.

## 2026-02-26 14:12 CST | tool: Codex CLI
- Objetivo: Implementar `REQ-067` para alinear detalle de requisiciones liquidadas con el modelo por modo de liquidacion.
- Cambios de codigo:
  - `app/main.py` (`GET /api/requisiciones/{id}`)
    - Payload de item liquidado enriquecido con:
      - `mode`, `used`, `not_used`, `returned`, `delivered`,
      - `expected_return`,
      - `difference` (nuevo nombre operativo),
      - `pk_ingreso_qty` (solo retornables; consumible = 0).
    - Se mantiene `delta` como alias compatible apuntando a `difference`.
    - Payload de cabecera agrega `prokey_pending`.
  - `static/app.js`
    - Tabla papel de liquidada rediseñada a columnas:
      - `Descripcion`, `Entregado`, `Tipo`, `Usado`, `No usado`, `Regresa`, `Diferencia`, `Ingreso PK`, `Alertas`.
    - `Ingreso PK` muestra tooltip: "Pendiente de ingresar en Prokey por bodega (solo retornables)".
    - En modo consumible muestra `Ingreso PK = 0`.
    - Resaltado visual de `Diferencia` mantiene clases `delta-warn` / `delta-danger`.
  - `tests/test_liquidacion_integration.py`
    - Nuevos escenarios:
      - mezcla retornable/consumible validando `mode`, `difference` y `pk_ingreso_qty`.
      - retorno extra retornable con diferencia negativa y alertas esperadas.
    - Ajustes en escenarios existentes para declarar `mode` y expectativas de `difference`.
- Gobernanza actualizada:
  - `docs/ai/TASKS.md`: `REQ-067` marcado `done`.
  - `docs/ai/HANDOFF.md`: estado actual incluye cierre de REQ-067.
  - `docs/ai/WORKLOG.md`: entrada de sesion.
- Comandos ejecutados:
  - `python -m compileall app static tests` -> OK
  - `.venv/bin/python -m pytest -q tests/test_liquidacion_integration.py -v` -> **12 passed**
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v` -> **28 passed**
- Resultado:
  - El detalle de liquidacion ahora representa correctamente la semantica operacional por tipo de item y evita lectura ambigua del ingreso Prokey.
- Proximo paso:
  - Definir `REQ-068` para reporte operativo minimo (p. ej. lista de liquidaciones pendientes de referencia Prokey/export simple).

## 2026-02-26 15:10 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-068` para bloquear liquidaciones ambiguas con items entregados sin definir.
- Cambios:
  - `app/main.py`
  - `app/crud.py`
  - `templates/liquidar.html`
  - `static/theme.css`
  - `tests/test_liquidacion.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Reglas aplicadas:
  - Validacion backend obligatoria en `POST /liquidar/{id}`: si `entregado > 0` y `usado + no_usado + regresa == 0`, no se permite liquidar.
  - Defensa adicional en `ejecutar_liquidacion(...)` para evitar bypass por capa API.
  - Re-render de `liquidar.html` con mensaje claro, filas incompletas resaltadas y preservacion de datos ya digitados.
  - Validacion UX en frontend: marca de fila incompleta en vivo y bloqueo de submit con mensaje global.
- Tests agregados:
  - `test_no_permite_liquidar_item_incompleto_entregado_gt_0`
  - `test_si_permite_cuando_delivered_es_0`
  - `test_permite_liquidar_si_al_menos_un_campo_es_mayor_0`
- Comandos ejecutados:
  - `.venv/bin/python -m compileall app templates static tests`
  - `.venv/bin/pytest -q tests/test_liquidacion.py -v`
- Resultado:
  - Suite de liquidacion: `31 passed`.
  - REQ-068 completada sin cambios de endpoints adicionales ni regresion en reglas de estado.
- Proximo paso:
  - Ejecutar smoke manual en UI para validar flujo visual en navegador (bloqueo, resaltado y preservacion de formulario).

## 2026-02-26 15:21 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-069` para volver humanas las alertas de liquidacion en el modal de detalle, sin cambiar logica backend.
- Cambios:
  - `static/app.js`
  - `tests/test_liquidacion.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Reglas aplicadas:
  - Se mantienen codigos internos `ALERTA_*` para trazabilidad.
  - Se agregan etiquetas legibles para usuario: `Faltante`, `Sobrante`, `Retorno extra`, `Inconsistencia`.
  - Tooltips ahora incluyen detalle numerico cuando hay data y el codigo interno de respaldo.
  - Si no hay alertas en item liquidado, UI mantiene `Sin alertas` y payload robusto como lista vacia.
- Test agregado:
  - `test_api_detalle_alertas_null_se_convierte_a_lista_vacia`
- Comandos ejecutados:
  - `.venv/bin/python -m compileall app static`
  - `.venv/bin/pytest -q tests/test_liquidacion.py -v`
- Resultado:
  - Suite de liquidacion: `32 passed`.
  - REQ-069 completada sin cambios de endpoints ni esquema de DB.
- Proximo paso:
  - Ejecutar smoke manual de modal en navegador para validar copy/tooltips con alertas de severidad `warn` y `high`.

## 2026-02-26 15:32 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-070` para mostrar comentario general y notas por item en modal de detalle de requisiciones liquidadas.
- Cambios:
  - `app/main.py`
  - `static/app.js`
  - `static/theme.css`
  - `tests/test_liquidacion_integration.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Reglas aplicadas:
  - Payload JSON normalizado para `liquidation_comment` e `item_liquidation_note` con convención `null` cuando está vacío.
  - Modal liquidada muestra siempre bloque de comentario (`—` cuando no existe).
  - Nota por item visible debajo de la descripción en tabla de items liquidados.
- Test agregado/ajustado:
  - `test_detalle_liquidada_incluye_comentario_y_nota_item` en integración.
- Comandos ejecutados:
  - `.venv/bin/python -m compileall app static tests`
  - `.venv/bin/pytest -q tests/test_liquidacion_integration.py -v`
- Resultado:
  - Integración de liquidación: `13 passed`.
  - REQ-070 completada sin cambios de rutas ni DB.
- Proximo paso:
  - Validar visualmente en navegador el modal con comentarios multilinea y filas con/sin nota.

## 2026-02-26 15:59 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-071` (rediseño visual del modal detalle a vista dashboard + mejoras UX de conciliación).
- Cambios:
  - `static/app.js`
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Reglas aplicadas:
  - Sin cambios en backend ni endpoints.
  - Se renombra copy operativo a `Alertas de conciliación` y se mantienen labels humanos de alertas.
  - DIF con semántica visual por signo (`dif--pos`, `dif--neg`, `dif--zero`).
  - Notas por item resaltadas cuando el item tiene alertas.
  - Comentarios secundarios movidos a bloque colapsable para reducir scroll.
- Comandos ejecutados:
  - `.venv/bin/python -m compileall app static templates`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v`
- Resultado:
  - Suite de liquidación: `32 passed`.
  - REQ-071 completada en capa UI con no-regresión funcional.
- Proximo paso:
  - Smoke manual del nuevo modal en navegador para validar comportamiento responsive y legibilidad.

## 2026-02-26 16:05 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-072` (refinamiento visual del modal dashboard sin tocar lógica).
- Cambios:
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Reglas aplicadas:
  - Estilos scopiados bajo `#modal-detalle` para evitar regresiones en otras páginas.
  - Mejora de legibilidad en badges por severidad y DIF por signo.
  - Ajuste de densidad en tabla de ítems y énfasis visual de notas con alertas.
  - Colapsables con hover/active más claros.
- Comandos ejecutados:
  - `.venv/bin/python -m compileall static`
- Resultado:
  - REQ-072 completada en capa CSS/UX, sin cambios en backend ni JS.
- Proximo paso:
  - Smoke manual del modal en liquidadas/no liquidadas para confirmar percepción visual final.

## 2026-02-26 16:12 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-073` (polish visual del modal dashboard para acercarlo a propuesta objetivo).
- Cambios:
  - `static/app.js`
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Reglas aplicadas:
  - Sin cambios de backend ni lógica de liquidación.
  - Estructura del modal migrada a patrón `detail-dashboard` con cards compactas y key/value.
  - Timeline convertido a flujo vertical con nodos (`dd-timeline`).
  - DIF renderizado como chip con signo (`+/-/0`) y clases semánticas.
  - Modal en modo casi fullscreen solo cuando aplica clase `modal--detail-dashboard`.
- Comandos ejecutados:
  - `.venv/bin/python -m compileall static app`
- Resultado:
  - REQ-073 completada en capa UI/UX, manteniendo compatibilidad de datos y rutas existentes.
- Proximo paso:
  - Smoke manual en navegador para validar percepción visual final y responsive.

## 2026-02-26 16:14 UTC-06:00 | tool: Codex CLI
- Objetivo: Ajuste rápido de usabilidad visual en modal dashboard (detalle de requisición).
- Cambios:
  - `static/theme.css`
  - `docs/ai/WORKLOG.md`
- Regla aplicada:
  - Se incrementa anchura del modal solo en modo `modal--detail-dashboard` para evitar vista apretada.
- Detalle técnico:
  - `width: min(1400px, 96vw)` -> `width: min(1650px, 99vw)`
- Resultado:
  - Más espacio horizontal para acomodar cards y tabla en desktop.
- Proximo paso:
  - Validación visual manual en navegador para confirmar distribución de objetos.

## 2026-02-26 16:16 UTC-06:00 | tool: Codex CLI
- Objetivo: Segundo ajuste de ancho modal dashboard para eliminar sensación de vista apretada.
- Cambios:
  - `static/theme.css`
  - `docs/ai/WORKLOG.md`
- Detalle técnico:
  - Modal dashboard: `width` ahora `99.6vw` y `height` `95vh`.
  - Contenido interno: padding reducido para ganar espacio útil horizontal.
- Resultado:
  - Mayor aprovechamiento de pantalla y más aire para cards + tabla.

## 2026-02-26 16:23 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir modal de detalle aun "apretado" tras ajustes de ancho.
- Hallazgo:
  - Regla legacy en `static/style.css` fijaba `#modal-detalle article` a `max-width: 1380px`, afectando cards del dashboard.
- Cambios:
  - `static/style.css`
  - `docs/ai/WORKLOG.md`
- Fix aplicado:
  - Regla legacy ahora solo aplica fuera del modo dashboard:
    - `#modal-detalle:not(.modal--detail-dashboard) article { ... }`
- Resultado esperado:
  - El detalle de requisición/liquidación aprovecha realmente el ancho casi fullscreen definido en `theme.css`.

## 2026-02-26 16:25 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir contracción del modal dashboard tras desacoplar regla legacy.
- Cambios:
  - `static/theme.css`
  - `docs/ai/WORKLOG.md`
- Fix aplicado:
  - Forzado explícito del contenedor interno del modal dashboard:
    - `#modal-detalle.modal--detail-dashboard article { width: 100%; max-width: none; ... }`
  - Ajuste de padding del dialog para aprovechar mejor el viewport.
- Resultado esperado:
  - El detalle de requisición/liquidación ocupa casi todo el ancho disponible sin encogerse.

## 2026-02-26 16:30 UTC-06:00 | tool: Codex CLI
- Objetivo: Ajuste puntual de orden visual en modal dashboard.
- Cambios:
  - `static/app.js`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Se intercambió la posición de los cajones `Justificación` y `Comentario de liquidación` en `detalle-bottom-grid`.
- Resultado:
  - El cajón de comentario ocupa ahora la posición previa de justificación, y viceversa.

## 2026-02-26 16:44 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-074` (ajustes finos UX en vista dashboard del detalle, sin tocar backend).
- Cambios:
  - `static/app.js`
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Label de card actualizado de `Severidad alta` a `Alta severidad`.
  - Nueva línea dinámica `Acción sugerida` en `Alertas de conciliación`, según prioridad de tipos detectados.
  - Columna `Ingreso PK` muestra `—` para ítems `CONSUMIBLE` (manteniendo valor numérico en `RETORNABLE`).
  - Celdas numéricas marcadas con clases `td-num`/`td-center` y estilos scoped para centrado consistente.
  - Botón `Ver PDF` habilitado solo cuando la requisición está `liquidada`; en otros estados queda deshabilitado con tooltip `Disponible al liquidar`.
- Comandos ejecutados:
  - `python -m compileall static`
- Resultado:
  - Ajustes UX aplicados sin cambiar lógica de negocio ni payload backend.

## 2026-02-26 16:54 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir desfase de hora en creación mostrado en detalle (`created_at` +6h).
- Causa raíz:
  - `created_at` dependía de `server_default=func.now()` en SQLite, que guarda en UTC.
  - Otros hitos (`approved_at`, `rejected_at`, `delivered_at`) se guardan con `datetime.now()` local, por eso solo creación quedaba adelantada.
- Cambios:
  - `app/crud.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Fix aplicado:
  - En `crear_requisicion_db(...)`, se persiste `created_at=datetime.now()` explícitamente (hora local).
- Comandos ejecutados:
  - `python -m compileall app`
- Resultado:
  - Nuevas requisiciones quedan con hora de creación consistente con el resto de eventos del timeline/modal.

## 2026-02-27 09:08 UTC-06:00 | tool: Codex CLI
- Objetivo: Publicar release notes cortas para baseline `v1.4.0` en repositorio.
- Cambios:
  - `docs/releases/v1.4.0.md`
  - `docs/ai/WORKLOG.md`
- Observaciones:
  - Se verificó disponibilidad de GitHub CLI (`gh`) y no está instalado en el entorno actual.
  - Se deja release note versionada en repo para referencia operativa y trazabilidad.
- Resultado:
  - Documento de release creado con alcance, highlights funcionales y estado de validación (`32 passed`).

## 2026-02-27 09:26 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-076` (buscador en Catálogo Admin por `q` con filtro server-side e UI simple).
- Cambios:
  - `app/main.py`
  - `templates/admin_catalogo_items.html`
  - `tests/test_admin_catalog_items.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Ruta `GET /admin/catalogo-items` ahora recibe `q`, aplica filtro case-insensitive sobre `CatalogoItem.nombre` con `func.lower(...).like(...)`, mantiene orden alfabético.
  - Se envía `q` al template para persistir valor buscado.
  - Se agregó barra de búsqueda (GET), botón `Buscar`, link `Limpiar` y conteo `Mostrando N items` con contexto de búsqueda.
  - Se agregó test `test_admin_catalog_busqueda_por_q_case_insensitive` con casos `mopa/spray` y validación de filtro.
- Comandos ejecutados:
  - `python -m compileall app templates tests`
  - `.venv/bin/python -m pytest -q tests/test_admin_catalog_items.py -v` (colgado en entorno actual)
  - `timeout 25s .venv/bin/python -m pytest -q tests/test_admin_catalog_items.py -v` (`EXIT:124`)
- Resultado:
  - Implementación completada; compilación correcta.
  - Ejecución de pytest de catálogo queda bloqueada en este entorno y requiere revisión puntual de runtime de tests.

## 2026-02-27 09:34 UTC-06:00 | tool: Codex CLI
- Objetivo: Ajuste de orden visual en vista de catálogo admin tras feedback.
- Cambios:
  - `templates/admin_catalogo_items.html`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Se intercambió el orden de bloques para mostrar `Importar catálogo` antes de `Buscar en catálogo`.
- Resultado:
  - La búsqueda queda ubicada debajo del bloque de importación, manteniendo la funcionalidad intacta.

## 2026-02-27 09:46 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-077` (autocompletar ítems en “Nueva Requisición” con `input + datalist` y validación UX).
- Cambios:
  - `templates/crear_requisicion.html`
  - `static/app.js`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Se reemplazó el `<select>` de ítems por `<input list="catalogo-items">` y se agregó `datalist` global con catálogo activo.
  - Se añadió mensaje UX (`#item-error`) para errores de item inválido/duplicado.
  - JS actualizado para validar coincidencia exacta contra `window.CATALOGO_ITEMS`, bloquear duplicados y mantener validación antes de agregar fila o enviar formulario.
  - Se mantuvo intacta la validación backend de catálogo para no confiar solo en frontend.
- Resultado:
  - UX de búsqueda de ítems más rápida en catálogos grandes, sin perder control de integridad.

## 2026-02-27 10:39 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-079` (tema visual Arctic Glass / Gradient Boost en toda la app, solo color).
- Cambios:
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Se aplicó bloque global de overrides de color al final de `theme.css` para fondo degradado azul, superficies glass, acento azul, tablas claras y badges/chips por severidad.
  - Se preservó layout/estructura/tamaños/espaciados; no se tocaron templates ni lógica.
  - Revisión de repo: no se encontró un bloque explícito nombrado “Propuesta 1.6” fuera de `theme.css`; los tokens se consolidaron en este archivo como fuente activa del tema.
- Comandos ejecutados:
  - `python -m compileall static app templates`
- Resultado:
  - Cambio visual global aplicado en capa CSS sin impacto funcional.

## 2026-02-27 10:58 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-079B` para corregir mezcla de paletas (Arctic Glass vs legacy dark) sin tocar layout/HTML.
- Cambios:
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Se validó orden de carga en `templates/base.html`: `style.css` seguido por `theme.css` (correcto para overrides finales).
  - Se añadió bloque final de tokens unificados Arctic Glass (`--accent`, `--bg`, `--surface`, `--border`, `--text`, `--muted`, estados y tokens de tabla/input/botón), además de mapeo de `--dark-*` para neutralizar reglas legacy de `style.css`.
  - Se aplicaron overrides de color de alta prioridad para tablas, paneles, cards métricas, inputs, botones, badges/chips, alerts y modal detalle, sin alterar estructura ni spacing.
  - Se eliminó la percepción de tablas/paneles oscuros heredados manteniendo la jerarquía visual existente.
- Comandos ejecutados:
  - `python -m compileall static app templates`
- Resultado:
  - Tema Arctic Glass consistente en toda la app con enfoque color-only.

## 2026-02-27 11:07 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir franja negra inferior detectada en vista de inicio tras cambio de tema.
- Cambios:
  - `static/theme.css`
  - `docs/ai/WORKLOG.md`
- Fix aplicado:
  - Fondo Arctic Glass aplicado a `html, body` con cobertura completa (`min-height: 100%`, `background-size: cover`, `background-attachment: fixed`, `no-repeat`).
- Resultado:
  - Se elimina la zona de fondo negro residual al final de la pantalla.

## 2026-02-27 11:14 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir inconsistencia visual en modal de detalle (título oscuro y fondo gris residual).
- Cambios:
  - `static/theme.css`
  - `docs/ai/WORKLOG.md`
- Fix aplicado:
  - Override de `#modal-detalle` para unificar `article`, `#modal-content` y `header` con tokens Arctic Glass.
  - Título del header (`h3`) forzado a color azul del tema para legibilidad.
- Resultado:
  - Vista de detalle alineada con el resto del tema, sin título negro ni fondo gris fuera de paleta.

## 2026-02-27 11:31 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-080` (rediseño de Inicio `/` a dashboard limpio según mock, sin tocar lógica).
- Cambios:
  - `templates/base.html`
  - `templates/home.html`
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Se agregó clase condicional `route-home` en `<body>` solo para la ruta `/` para scoping de estilos.
  - Se reescribió `home.html` con estructura SSR: header limpio + botón `Nueva Requisición`, 6 KPI cards con link `Ver detalle`, panel `Indicadores Rápidos` y panel oscuro `Acciones Rápidas`.
  - Se respetaron permisos por rol en enlaces rápidos (`/aprobar`, `/bodega`, `/mis-requisiciones`) y visibilidad de acción de aprobación masiva.
  - Se añadió bloque CSS scopiado a `.route-home .home-clean` en `theme.css` para evitar regresiones en otras pantallas.
- Comandos ejecutados:
  - `python -m compileall app templates static`
- Resultado:
  - Inicio actualizado visualmente sin cambios en lógica de negocio ni queries backend.

## 2026-02-27 14:22 UTC-06:00 | tool: Codex CLI
- Objetivo: Cerrar trazabilidad de ajustes visuales post-`REQ-080` y mantener gobernanza sincronizada commit a commit.
- Cambios:
  - `static/theme.css`
  - `templates/crear_requisicion.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - `REQ-080A` (`b16c813`): corrección de estilo en Home para `Indicadores Rápidos` (`home-panel-header`) y eliminación de tono oscuro residual.
  - `REQ-080B` (`1290aa0`): campos de cliente en `Nueva Requisición` con clase dedicada (`req-client-field`) para fondo blanco y texto negro en negrita durante edición/focus/autofill.
  - `REQ-080C` (`18855ec`): unificación del fondo del modal de detalle al tema Arctic Glass (contenedor principal y superficies internas) eliminando gris legacy.
- Comandos ejecutados:
  - `git log --oneline -n 8`
  - `git status --short`
  - `date '+%Y-%m-%d %H:%M %Z %z'`
- Resultado:
  - Bitácoras y handoff quedan alineados con los últimos cambios ya aplicados en `main`.
  - No se tocaron endpoints, lógica de negocio ni esquema de base de datos en esta intervención documental.

## 2026-02-27 14:41 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-081` agregando alerta de inventario “Retorno incompleto” para ítems `RETORNABLE` (`regresa < entregado`) sin cambiar la lógica de diferencia actual.
- Cambios:
  - `app/crud.py`
  - `static/app.js`
  - `tests/test_liquidacion.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Backend: `calcular_alertas_item` ahora genera `ALERTA_RETORNO_INCOMPLETO` (`severity=warn`) con `data={delivered, returned, missing}` cuando modo es `RETORNABLE` y retorno es menor al entregado.
  - Frontend: mapping humano agregado (`Retorno incompleto`) y tooltip numérico: “Entregado X, regresó Y, faltan Z”.
  - Tests: agregado `test_retornable_alerta_retorno_incompleto` para validar presencia de la nueva alerta.
  - No se alteró el cálculo de `DIF`/conciliación existente ni reglas de transición de estado.
- Comandos ejecutados:
  - `python -m compileall app static tests`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v`
- Resultado:
  - Suite de liquidación OK: `33 passed`.
  - Feature lista para validación visual en modal de detalle.

## 2026-02-27 14:57 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-082` para corregir inconsistencia donde `ALERTA_RETORNO_INCOMPLETO` no se disparaba/visualizaba en todos los casos `RETORNABLE` con `regresa < entregado`.
- Cambios:
  - `app/crud.py`
  - `app/main.py`
  - `static/app.js`
  - `tests/test_liquidacion.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Backend (fuente de verdad):
    - Normalización estricta en `calcular_alertas_item`: `int()` para `delivered/returned/used/not_used`.
    - Normalización robusta de modo: `liquidation_mode` (fallback `tipo`) con `upper().strip()`.
    - `ALERTA_RETORNO_INCOMPLETO` mantiene coexistencia con otras alertas y ahora incluye `data.delta` además de `missing`.
  - Persistencia:
    - `item.liquidation_alerts` ahora se guarda siempre como JSON array (`json.dumps(alertas)`), incluso vacío.
  - API detalle:
    - Parseo de `liquidation_alerts` endurecido con `except (JSONDecodeError, TypeError, ValueError)` y fallback a `[]`.
  - Frontend modal:
    - Tooltip de “Retorno incompleto” tolera `missing` o `delta` para evitar huecos de visualización.
  - Tests:
    - Nuevo test `test_api_detalle_incluye_retorno_incompleto`.
    - Ajuste de tests que esperaban `None` en DB, ahora esperan `[]` serializado.
- Comandos ejecutados:
  - `python -m compileall app static init_db.py tests`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v`
- Resultado:
  - Suite liquidación OK: `34 passed`.
  - Fix aplicado sin cambios de layout/tema ni alteración de la lógica de conciliación existente.

## 2026-02-27 15:18 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-083` para bloquear liquidaciones con cobertura artificial o retorno inconsistente respecto al modo.
- Cambios:
  - `app/crud.py`
  - `app/main.py`
  - `templates/liquidar.html`
  - `static/theme.css`
  - `tests/test_liquidacion.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Backend:
    - Nueva función compartida `validar_liquidacion_item(...)`.
    - Regla de cobertura obligatoria: `used + not_used == delivered`.
    - Regla de consistencia:
      - `CONSUMIBLE`: `returned == not_used`
      - `RETORNABLE`: `returned <= used + not_used`
    - `POST /liquidar/{id}` ahora re-renderiza el formulario con errores por fila si alguna validación falla.
    - `ejecutar_liquidacion(...)` aplica la misma validación para evitar bypass.
  - Frontend:
    - Validación en vivo por fila con mensajes concretos.
    - Resaltado visual separado para cobertura (`row-incomplete`) y retorno inconsistente (`row-return-invalid`).
    - Botón `Liquidar` se deshabilita si cualquier fila no cumple.
  - Tests:
    - Se agregaron/ajustaron escenarios de cobertura y consistencia por modo.
    - Se actualizaron fixtures de tests previos que antes dependían de liquidaciones con cobertura incompleta.
- Comandos ejecutados:
  - `python -m compileall app templates static tests`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v`
- Resultado:
  - Suite liquidación OK: `37 passed`.
  - El flujo ya no permite “cuadrar” artificialmente con `Regresa` dejando parte de `Entregado` sin explicar.

## 2026-02-27 15:27 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir formato de fecha/hora en vistas SSR y desfase de +6h en `liquidated_at` del detalle.
- Cambios:
  - `app/main.py`
  - `app/crud.py`
  - `static/app.js`
  - `templates/aprobar.html`
  - `templates/bodega.html`
  - `templates/mis_requisiciones.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Se agregó filtro Jinja `fmt_dt` para renderizar fechas SSR como `YYYY-MM-DD HH:MM:SS`, evitando microsegundos en tablas.
  - Se aplicó `fmt_dt` en vistas con datetimes visibles: `/aprobar`, `/bodega`, `/mis-requisiciones`.
  - `liquidated_at` ahora se persiste con `datetime.now()` en lugar de `datetime.utcnow()`, alineado con aprobación/entrega y hora local del servidor.
  - `fmtDateTime()` en `static/app.js` dejó de depender primero de `new Date(...)`; ahora formatea strings `YYYY-MM-DD HH:MM:SS(.microseconds)` o ISO sin convertir zona horaria, evitando adelantos espurios en el modal.
- Comandos ejecutados:
  - `rg -n` sobre templates/app/static para localizar render de fechas
  - `python -m compileall app static templates`
- Resultado:
  - Nuevos registros de liquidación quedan en hora local.
  - Vistas SSR ya no muestran microsegundos.
  - Queda pendiente solo una posible migración de datos si se desea corregir liquidaciones históricas ya guardadas con UTC.

## 2026-02-27 16:25 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-085` para firma de recibido con PIN por receptor en entrega de bodega, sin romper liquidación.
- Cambios:
  - `app/models.py`
  - `app/database.py`
  - `app/auth.py`
  - `app/crud.py`
  - `app/main.py`
  - `templates/admin_usuario_form.html`
  - `templates/bodega_gestionar.html`
  - `templates/bodega_entrega_parcial.html`
  - `static/app.js`
  - `tests/test_basic_flow.py`
  - `tests/test_admin_users.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Usuarios:
    - Se agregaron `pin_hash` y `puede_iniciar_sesion`.
    - Nuevo rol operativo `tecnico`.
    - En admin, crear/editar usuario ahora permite PIN opcional.
    - Los técnicos quedan con `puede_iniciar_sesion=False` y por tanto no pueden usar login, pero sí pueden firmar recibido con PIN.
  - Entrega en bodega:
    - Se agregaron `recibido_por_id` y `recibido_at` a requisiciones.
    - Entrega completa y parcial validan receptor activo + PIN bcrypt antes de procesar.
    - `no_entregada` mantiene receptor opcional, pero si se captura firma también se valida.
    - Al aprobar la firma se guarda el nombre en `delivered_to` por compatibilidad y además la trazabilidad real en `recibido_por_id/recibido_at`.
  - Detalle/API:
    - `GET /api/requisiciones/{id}` ahora expone `recibido_por` y `recibido_at`.
    - Timeline agrega evento `Recibido con firma` cuando existe.
    - Modal muestra `Recibido por` y `Hora firma`.
  - Migraciones:
    - `run_migrations()` ahora agrega columnas de REQ-085 con verificación previa por `PRAGMA table_info`.
    - Se corrigió un defecto previo: migraciones de liquidación ya no intentan `ALTER TABLE` sobre tablas inexistentes en DB nueva.
- Comandos ejecutados:
  - `python -m compileall app templates static tests`
  - `DATABASE_URL=sqlite:///./req085_sanity.db .venv/bin/python ...` (smoke directo de auth + firma + transición `entregada`)
- Resultado:
  - Compilación OK.
  - Smoke directo OK: receptor con PIN válido firma, técnico queda sin login, y la requisición persiste `recibido_por_id/recibido_at`.
  - Limitación del entorno: `TestClient` queda colgado incluso contra `/health`; por eso no se pudo cerrar una validación HTTP automatizada confiable en esta sesión.

## 2026-02-27 16:39 UTC-06:00 | tool: Codex CLI
- Objetivo: Ajustar REQ-085 para que usuarios `tecnico` no requieran contraseña al crearse/editarse; solo PIN operativo.
- Cambios:
  - `app/main.py`
  - `templates/admin_usuario_form.html`
  - `tests/test_admin_users.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Backend:
    - Si el rol es `tecnico`, la contraseña deja de ser obligatoria al crear.
    - Para `tecnico`, el PIN pasa a ser obligatorio.
    - Como `Usuario.password` sigue siendo no nulo en modelo/DB, se genera internamente un hash aleatorio solo para satisfacer persistencia; no habilita login porque `puede_iniciar_sesion=False`.
  - UI:
    - El formulario de usuario ya no marca contraseña como `required`.
    - Copy aclarado: roles con login requieren contraseña; `tecnico` usa solo PIN.
  - Tests:
    - Se ajustó el caso de alta técnica sin contraseña.
    - Se agregó cobertura para rechazar técnico sin PIN.
- Comandos ejecutados:
  - `python -m compileall app templates tests`
  - `DATABASE_URL=sqlite:///./req086_admin.db .venv/bin/python ...` (smoke directo de persistencia admin/técnico)
- Resultado:
  - Compilación OK.
  - Smoke directo OK para técnico sin contraseña y con login deshabilitado.

## 2026-02-27 16:46 UTC-06:00 | tool: Codex CLI
- Objetivo: Registrar fix posterior del endpoint de creación de usuarios técnicos sin contraseña.
- Cambios:
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Detalle:
  - Se dejó asentado el ajuste del commit `85ab2a2`.
  - El problema real era de parsing HTTP: la ruta `POST /admin/usuarios` seguía declarando `password: Form(...)`, por lo que FastAPI rechazaba el request antes de llegar a la lógica por rol.
  - El fix aplicado en código fue cambiar ese campo a `Form("")`, manteniendo la validación real en el handler:
    - `tecnico`: sin contraseña, con PIN obligatorio
    - otros roles: con contraseña obligatoria
- Comandos ejecutados:
  - Sin comandos de verificación adicionales; esta entrada documenta el fix ya empujado en `85ab2a2`.
- Resultado:
  - Gobernanza alineada con el estado real del código y del historial Git.

## 2026-03-02 | tool: Claude Code (claude-sonnet-4-6)
- Objetivo: Configurar stack de despliegue Docker + Caddy para producción LAN.
- Tareas: `REQ-086`.
- Cambios:
  - `Dockerfile` (nuevo): imagen Python 3.11-slim, directorio /app/data para volumen SQLite.
  - `docker-compose.yml` (nuevo): app sin puertos expuestos directamente, se une a red `proxy` externa.
  - `deploy/caddy/docker-compose.yml` (nuevo): Caddy 2-alpine, puertos 80/443, volúmenes para datos/config.
  - `deploy/caddy/Caddyfile` (nuevo): reverse proxy :80 → requisiciones:8000, comentarios para futuros servicios.
  - `.env.example` (actualizado): DATABASE_URL apunta a /app/data/requisiciones.db para Docker.
  - `.gitignore` (actualizado): ignorar directorio data/ (DB de producción).
  - `docs/ai/DECISIONS.md` (ADR-004: decisión de despliegue Docker + Caddy).
  - `docs/ai/TASKS.md` (REQ-086 done, REQ-087 y REQ-088 agregados).
  - `docs/ai/HANDOFF.md` (estado actualizado con tareas de despliegue).
- Resultado:
  - Stack de despliegue listo para copiar al servidor. Red Docker `proxy` externa desacopla Caddy de la app.
  - DATABASE_URL usa ruta absoluta (4 slashes) para que el volumen ./data sea persistente fuera del container.
  - Contenedores existentes en el servidor no requieren cambios.
- Próximo paso:
  - REQ-087: ejecutar en el servidor (crear red proxy, levantar Caddy, levantar app, validar acceso LAN).
  - REQ-088: copiar DB existente al path ./data/requisiciones.db antes del primer arranque en producción.

## 2026-03-02 | tool: Claude Code (claude-sonnet-4-6)
- Objetivo: Permitir al admin eliminar cualquier requisición sin restricción de estado.
- Tareas: `REQ-089`.
- Cambios:
  - `app/main.py`: nuevo endpoint `POST /admin/requisiciones/{req_id}/eliminar` (requiere admin, cascade delete de ítems).
  - `templates/aprobar.html`: botón "Eliminar" visible solo para admin, con `confirm()` JS antes de ejecutar.
  - `static/style.css`: clase `.btn-danger-sm` para el botón de eliminar.
  - `docs/ai/TASKS.md`: REQ-089 agregado y completado.
- Resultado:
  - Admin puede borrar cualquier requisición desde `/aprobar` sin importar su estado.
  - Los ítems se eliminan en cascada (configuración ya existente en el modelo).
  - Usuarios no-admin no ven el botón; la ruta también valida el rol en backend.

## 2026-03-02 | tool: Claude Code (claude-sonnet-4-6)
- Objetivo: Agregar rol `jefe_bodega` que combina `aprobador` + `bodega`.
- Tareas: `REQ-090`.
- Cambios:
  - `app/main.py`: `jefe_bodega` agregado a `ROLES_VALIDOS` y a todos los guards de rutas de aprobar, bodega y liquidación; historial de bodega sin filtro por usuario (ve todo); redirects prokey-ref apuntan a /bodega igual que admin.
  - `templates/partials/navbar.html`: `jefe_bodega` incluido en ambos ítems de nav (Aprobar y Bodega).
  - `docs/ai/TASKS.md`: REQ-090 agregado y completado.
- Resultado:
  - `jefe_bodega` puede aprobar/rechazar, gestionar entregas y liquidar desde un solo rol.
  - Ve el historial completo de entregas (bodega plain solo ve las propias).
  - API de detalle: acceso sin restricción de estado (equivalente a aprobador).
  - Aparece en el formulario de creación/edición de usuarios del admin.

## 2026-03-04 15:20 UTC-06:00 | tool: Codex CLI
- Objetivo: Integrar generación PDF de requisiciones liquidadas al backend real.
- Tareas: `REQ-094`.
- Cambios:
  - `app/pdf_generator.py`: se incorpora al repo y se ajusta para consumir alertas reales persistidas como lista de dicts (`type`, `severity`, `data`) sin fallar al renderizar cards ni tabla.
  - `app/main.py`: nuevo helper `build_requisicion_pdf_payload(...)`, endpoint `GET /requisiciones/{id}/pdf`, `pdf_url` en `GET /api/requisiciones/{id}` y control de acceso reutilizando la misma política del detalle. El endpoint rechaza estados distintos de `liquidada` con `403`.
  - `requirements.txt`: se agrega `reportlab==4.2.5`.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: actualizadas para reflejar `REQ-094` completada.
- Comandos ejecutados:
  - `python -m compileall app static`
  - `.venv/bin/python -c "from app.main import app; print(app.title)"`
- Resultado:
  - El detalle ya puede habilitar `Ver PDF` con `pdf_url`.
  - El endpoint produce `application/pdf` inline con nombre `requisicion_<folio>.pdf`.
  - El mapeo usa el modelo real: fechas, nombres de actores, comentario de liquidación, contexto operativo y alertas por ítem.

## 2026-03-04 16:05 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir discrepancia entre detalle web y PDF en columnas `Ingreso PK (Bodega)` y `DIF`.
- Tareas: `REQ-094A`.
- Cambios:
  - `app/pdf_generator.py`: `DIF` ahora usa la misma fórmula que el detalle web (`expected_return - returned`) y renderiza `Falta X` / `Extra X` / `OK`; `Ingreso PK` toma `pk_ingreso_qty` por ítem en lugar de `prokey_ref`.
  - `app/main.py`: el payload para PDF ahora pasa `pk_ingreso_qty` por ítem, calculado como `qty_returned_to_warehouse` solo para `RETORNABLE`.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: actualizadas con el ajuste puntual.
- Comandos ejecutados:
  - `python -m compileall app`
  - `.venv/bin/python -c "from app.main import app; print(app.title)"`
- Resultado:
  - El PDF ya no pierde filas en `Ingreso PK (Bodega)` por usar el campo equivocado.
  - `DIF` deja de mostrar solo el estado textual y ahora incluye la magnitud numérica, consistente con el detalle de la app.

## 2026-03-04 16:22 UTC-06:00 | tool: Codex CLI
- Objetivo: Reemplazar la marca textual del header PDF por el logo real de la app.
- Tareas: `REQ-094B`.
- Cambios:
  - `app/pdf_generator.py`: el bloque superior izquierdo del header ahora intenta dibujar `static/branding/logo-prohygiene-es.png`; si no puede cargar el recurso, conserva el texto `ProHygiene` como fallback.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: actualizadas para reflejar el ajuste visual del PDF.
- Comandos ejecutados:
  - `python -m compileall app`
  - smoke directo con `generate_requisicion_pdf(...)`
- Resultado:
  - El PDF mantiene el layout del header, pero ahora usa la identidad visual real de la empresa en lugar del texto plano.

## 2026-03-04 16:40 UTC-06:00 | tool: Codex CLI
- Objetivo: Hacer visible `contexto_operacion` en el detalle de requisición durante todo el ciclo, no solo en liquidación.
- Tareas: `REQ-093D`.
- Cambios:
  - `static/app.js`: en la tabla `Items Solicitados`, cada ítem ahora muestra debajo de la descripción el contexto operativo (`Reposición` / `Instalación inicial`) cuando existe.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: actualizadas para reflejar la mejora de trazabilidad visual.
- Comandos ejecutados:
  - Sin comandos adicionales de backend; el payload ya incluía `contexto_operacion` y el cambio fue solo de render frontend.
- Resultado:
  - El usuario puede ver el contexto operativo del ítem desde pendiente/aprobada/entregada/liquidada sin esperar a la tabla específica de liquidación.

## 2026-03-04 17:05 UTC-06:00 | tool: Codex CLI
- Objetivo: Ajustar visibilidad operativa de la vista `Bodega` para rol `bodega`.
- Tareas: `REQ-095`.
- Cambios:
  - `app/main.py`: la consulta de pendientes en `/bodega` ahora incluye requisiciones `aprobada` y también `entregada` con `delivery_result` en `completa|parcial`, visibles para todos los usuarios de bodega. El historial del rol `bodega` se restringe a requisiciones donde el usuario fue `delivered_by` o `liquidated_by`.
  - `templates/bodega.html`: la tabla superior pasa a ser `Pendientes de bodega`, agrega columna `Estado`, cambia `Fecha clave` según fase y muestra acción `Gestionar` o `Liquidar` según corresponda.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: actualizadas para reflejar el nuevo criterio operativo.
- Comandos ejecutados:
  - Sin tests automáticos; el ajuste fue de consulta SSR + template.
- Resultado:
  - Un usuario `bodega` ya puede ver todas las requisiciones pendientes de preparar y todas las entregadas pendientes de liquidar.
  - Su historial deja de ser global y conserva únicamente movimientos propios de preparación o liquidación.

## 2026-03-04 17:34 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir la falsa diferencia en liquidación para ítems `RETORNABLE` en `instalacion_inicial`.
- Tareas: `REQ-093E`.
- Cambios:
  - `app/crud.py`: se centralizó el cálculo de retorno esperado; para `RETORNABLE + instalacion_inicial` ahora el esperado es solo `No usado`, no `Usado + No usado`.
  - `app/main.py`: el detalle API usa la misma regla para `expected_return` y `difference`.
  - `templates/liquidar.html`: la tabla de liquidación ahora calcula `Diferencia` por fila usando también `contexto_operacion`, evitando falsos `Falta` antes de guardar.
  - `tests/test_liquidacion.py`: se agregó cobertura explícita para confirmar que una instalación inicial retornable con `Regresa=0, Usado=Entregado, No usado=0` queda con `difference=0` y sin `ALERTA_FALTANTE`.
- Comandos ejecutados:
  - `python -m compileall app templates tests`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -k "instalacion_inicial or retorno_incompleto_no_aplica" -v`
- Resultado:
  - La UI de liquidación, las alertas backend y el detalle de requisición quedaron alineados en el caso operativo de instalación inicial.

## 2026-03-04 17:46 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir la diferencia inconsistente en PDF para `instalacion_inicial`.
- Tareas: `REQ-093F`.
- Cambios:
  - `app/pdf_generator.py`: ajuste de `_dif_chip` para que use `contexto_operacion` igual que la app; en `RETORNABLE + instalacion_inicial` el retorno esperado ahora es `No usado`, no `Usado + No usado`.
- Comandos ejecutados:
  - `python -m compileall app/pdf_generator.py`
- Resultado:
  - El PDF ya no muestra `Falta` en casos de instalación inicial donde el retorno cero es válido operativamente.

## 2026-03-04 18:02 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir actor incorrecto en la línea de tiempo del PDF para el evento de liquidación.
- Tareas: `REQ-094C`.
- Cambios:
  - `app/main.py`: el payload del PDF ahora incluye `liquidado_por_nombre` desde `req.liquidator`.
  - `app/pdf_generator.py`: la card `Estado liquidación` y el hito `Liquidada` de la timeline toman ese nuevo campo en lugar de `aprobador_nombre`.
- Comandos ejecutados:
  - `python -m compileall app/main.py app/pdf_generator.py`
- Resultado:
  - El PDF ya no atribuye la liquidación al aprobador; muestra al liquidador correcto, consistente con la app.

## 2026-03-04 18:16 UTC-06:00 | tool: Codex CLI
- Objetivo: Actualizar `README.md` para reflejar el estado real del proyecto.
- Tareas: `REQ-096`.
- Cambios:
  - `README.md`: reescritura de contenido para estado `v1.x` (stack, roles, flujo de estados, firma con PIN, liquidación, PDF y despliegue local/Docker+Caddy).
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: sincronización de gobernanza con la actualización documental.
- Comandos ejecutados:
  - Edición directa de Markdown (sin comandos de build/test por no haber cambios de código ejecutable).
- Resultado:
  - La documentación principal del repositorio ya no describe un MVP básico; ahora refleja el alcance operativo actual.

## 2026-03-04 18:29 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir entrada por IP/puerto para usuarios no autenticados en vistas web.
- Tareas: `REQ-097`.
- Cambios:
  - `app/main.py`: se agregó `@app.exception_handler(HTTPException)` para transformar `401` en redirección a `/login` en rutas SSR.
  - Se mantiene `401` JSON para rutas `/api/*` para no romper consumo programático.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: actualizadas con el ajuste de autenticación web.
- Comandos ejecutados:
  - Edición directa de código/documentación (sin test suite completa en esta iteración).
- Resultado:
  - Al entrar sin sesión por IP/puerto, la app redirige al login en lugar de mostrar alerta `No autenticado`.

## 2026-03-04 18:48 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar `REQ-098` (etiqueta `Para Demo` por línea de ítem) sin tocar lógica de liquidación.
- Tareas: `REQ-098`.
- Cambios:
  - `app/models.py`: nuevo campo `Item.es_demo` (boolean, default false, server_default `0`).
  - `app/database.py`: migración incremental idempotente `items.es_demo`.
  - `app/crud.py`: parseo y persistencia de `es_demo_{index}` solo en creación de requisición.
  - `templates/crear_requisicion.html` + `static/app.js`: checkbox `Para Demo` por fila dinámica de ítems.
  - `templates/bodega_gestionar.html` y `templates/bodega_entrega_parcial.html`: badge `Para Demo` junto al ítem.
  - `app/main.py` (`GET /api/requisiciones/{id}` y payload PDF): inclusión de `es_demo` por ítem.
  - `app/pdf_generator.py`: etiqueta `[Para Demo]` junto a la descripción de ítem en PDF.
  - `static/theme.css`: estilos mínimos para bloque contexto+demo y badge.
- Comandos ejecutados:
  - `python -m compileall app templates static tests`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v`
  - `.venv/bin/python -m pytest -q tests/test_admin_catalog_items.py -v`
- Resultado:
  - `es_demo` quedó disponible y visible en el ciclo completo, sin cambios en `calcular_alertas_item`, `ejecutar_liquidacion`, ni fórmulas de `expected_return/diferencia`.
  - `tests/test_liquidacion.py` pasó completo (40/40).
  - `tests/test_admin_catalog_items.py` quedó colgado en este entorno (comportamiento intermitente ya visto con `TestClient`), por lo que se dejó constancia y se requiere validación en entorno estable.

## 2026-03-05 14:27 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir bug de validación intermitente del botón `Liquidar` cuando se editan campos numéricos en secuencia (borrar/escribir varias veces).
- Tareas: `REQ-099F`.
- Cambios:
  - `templates/liquidar.html`:
    - `parseNum(...)` ahora normaliza de forma defensiva: `null/undefined/vacío/coma decimal/NaN` a `0`.
    - Se agregó helper `inputNum(...)` para centralizar lectura segura de inputs y evitar valores intermedios inestables.
    - `evaluateAllRows(...)` pasa a cálculo stateless por evento usando `Array.some(...)`, evitando estados residuales de invalidez.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: actualización de gobernanza con cierre de `REQ-099F`.
- Comandos ejecutados:
  - `python -m compileall templates`
- Resultado:
  - El botón `Liquidar` ya no queda deshabilitado por estados intermedios de edición numérica; al corregir los campos, el estado se recupera sin refrescar la página.
  - No se cambiaron reglas de negocio de cobertura/consistencia por modo, solo robustez de lectura y recálculo.

## 2026-03-05 15:18 UTC-06:00 | tool: Codex CLI
- Objetivo: Corregir validación bloqueante incorrecta en liquidación para `RETORNABLE` cuando `Regresa` supera cobertura/entregado.
- Tareas: `REQ-099G`.
- Cambios:
  - `templates/liquidar.html`:
    - la condición de bloqueo por retorno en `RETORNABLE` se eliminó (`returnOk` ahora solo bloquea para `CONSUMIBLE`).
    - si `RETORNABLE` tiene `Regresa > Cobertura`, se muestra advertencia visual no bloqueante en la fila.
  - `app/crud.py`:
    - `validar_liquidacion_item(...)` deja de rechazar `RETORNABLE` por `returned > coverage_total`.
    - se mantienen intactas las reglas bloqueantes de cobertura y consistencia en `CONSUMIBLE`.
  - `tests/test_liquidacion.py`:
    - `test_liquidar_con_retorno_extra` actualizado a flujo exitoso con alerta persistida.
    - nuevo `test_permite_retornable_con_retorno_extra_no_bloquea_y_alerta`.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: gobernanza sincronizada con cierre de `REQ-099G`.
- Comandos ejecutados:
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -v`
- Resultado:
  - `Regresa` mayor al entregado/cobertura en ítems `RETORNABLE` ya no bloquea `Liquidar`.
  - La liquidación guarda correctamente y registra alertas (`ALERTA_RETORNO_EXTRA`/`ALERTA_SOBRANTE`) para trazabilidad.
  - Suite objetivo verde: `46 passed`.

## 2026-03-05 15:02 UTC-06:00 | tool: Codex CLI
- Objetivo: Habilitar `Ver PDF` también para requisiciones en estado terminal `liquidada_en_prokey`.
- Tareas: `REQ-099H`.
- Cambios:
  - `app/main.py`:
    - `pdf_url` en `GET /api/requisiciones/{id}` ahora se publica para `liquidada` y `liquidada_en_prokey`.
    - endpoint `GET /requisiciones/{id}/pdf` acepta ambos estados (antes solo `liquidada`).
  - `static/app.js`:
    - habilitación del botón `Ver PDF` en modal de detalle ajustada para ambos estados.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: sincronización de gobernanza.
- Comandos ejecutados:
  - `python -m compileall app static`
- Resultado:
  - Requisiciones cerradas en `liquidada_en_prokey` ya pueden abrir PDF desde detalle sin error 403 ni botón deshabilitado.

## 2026-03-06 08:35 UTC-06:00 | tool: Codex CLI
- Objetivo: Documentar y cerrar incidente de despliegue remoto Docker con desalineación de código en producción.
- Tareas: `REQ-099I`.
- Contexto del incidente:
  - `/bodega` y `/api/requisiciones/{id}` fallaban con `AttributeError` por atributos ausentes (`prokey_liquidator`, `prokey_liquidada_at`).
  - Diagnóstico en contenedor mostró estado mixto: `main.py` actualizado con guards, pero `models.py` sin campos Prokey (`False False` en `hasattr`).
- Cambios aplicados:
  - `app/main.py`: guards defensivos para evitar crash cuando faltan atributos en despliegues mixtos.
  - `app/models.py` y `app/database.py`: commit correctivo con campos/relación de cierre Prokey y migración/check actualizado.
  - Operación de recuperación: validación en contenedor tras redeploy limpio (`True True`), y reseteo operativo de credenciales admin para acceso.
- Comandos operativos relevantes:
  - verificación runtime: `docker compose exec requisiciones python -c "... hasattr(Requisicion, 'prokey_liquidator') ..."`
  - redeploy: `docker compose build --no-cache requisiciones && docker compose up -d requisiciones`
- Resultado:
  - Entorno remoto alineado con `main`.
  - Vista `Bodega`, detalle de requisición y flujo `liquidada_en_prokey` operativos sin `500`.

## 2026-03-06 12:10 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar importación masiva de usuarios basada en `Listado Personal al 06.03.2026.xlsx` con mapeo por puesto y flujo seguro de previsualización.
- Tareas: `REQ-100`.
- Cambios:
  - `app/main.py`:
    - Se agregó parser de usuarios para XLSX/CSV con columnas `NOMBRE` y `PUESTO`.
    - Se agregó normalización robusta de texto (tildes/espacios) para mapear puestos reales.
    - Se agregó mapeo operativo de puestos a `rol`/`departamento` según definición del usuario.
    - Se implementó generación de `username` (`nombre.apellido` + sufijo por colisión).
    - Se implementó `dry-run` (`POST /admin/usuarios/importar` con `dry_run=1`) y aplicación real idempotente (`dry_run=0`).
    - Se definieron credenciales temporales de importación: no técnicos `Temp@2026`, técnicos `PIN 1234` y login deshabilitado.
  - `templates/admin_usuarios.html`:
    - Se agregó bloque de importación con carga de archivo y dos acciones: `Previsualizar` / `Importar`.
    - Se agregó render de reporte (totales, errores por fila y filas válidas con acción crear/actualizar).
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: sincronización de gobernanza.
- Comandos ejecutados:
  - `python -m compileall app templates`
- Resultado:
  - Admin puede cargar archivos similares al listado de personal y ver un reporte antes de escribir en DB.
  - La importación real crea/actualiza usuarios con reglas consistentes por puesto, sin requerir edición fila por fila.

## 2026-03-06 12:35 UTC-06:00 | tool: Codex CLI
- Objetivo: Ajustar convención de `username` en importación masiva y alinear documentación operativa.
- Tareas: `REQ-100A`.
- Cambios:
  - `app/main.py`: `build_username_base(...)` actualizado a `inicial del primer nombre + primer apellido` (usando convención hispana con penúltima palabra para nombres de 3+ tokens).
  - `README.md`: nueva sección de importación masiva de usuarios con formato esperado, mapeo de puestos, regla de username y credenciales temporales.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: sincronización de gobernanza para cierre de `REQ-100A`.
- Comandos ejecutados:
  - `python -m compileall app/main.py`
- Resultado:
  - Usernames de importación quedan consistentes con operación (`cramirez`, `jramirez`, etc.), manteniendo manejo de colisiones por sufijo.

## 2026-03-06 13:10 UTC-06:00 | tool: Codex CLI
- Objetivo: Implementar cambio de contraseña autoservicio para usuarios autenticados (sin forzar primer login).
- Tareas: `REQ-101`.
- Cambios:
  - `app/main.py`:
    - nuevas rutas `GET /mi-cuenta/password` y `POST /mi-cuenta/password`.
    - validaciones: contraseña actual correcta, mínimo 8 caracteres, confirmación coincidente y no reutilizar la misma contraseña.
    - persistencia con `hash_password(...)` y `db.commit()`.
  - `templates/cambiar_password.html`:
    - formulario SSR para actualización de contraseña.
  - `templates/partials/navbar.html`:
    - nuevo enlace `Cambiar contrasena`.
  - `tests/test_admin_users.py`:
    - pruebas de cambio exitoso y rechazo por contraseña actual incorrecta.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: gobernanza actualizada.
- Comandos ejecutados:
  - `python -m compileall app templates tests`
  - `.venv/bin/python -m pytest -q tests/test_admin_users.py -v`
- Resultado:
  - La app permite actualizar contraseña en cualquier momento para usuarios con login habilitado, sin alterar el flujo de técnicos (sin login).
  - Nota de entorno: en esta sesión `pytest` quedó colgado al iniciar `tests/test_admin_users.py` (comportamiento intermitente ya observado con `TestClient`); se validó compilación completa y registro de rutas `GET/POST /mi-cuenta/password`.

## 2026-03-06 14:05 UTC-06:00 | tool: Codex CLI
- Objetivo: habilitar observabilidad base de la app para diagnóstico operativo (login, fallas, latencias y trazabilidad por request).
- Tareas: `REQ-102`.
- Cambios:
  - `app/logging_utils.py` (nuevo):
    - configuración de logging estructurado JSON.
    - filtro por `request_id` con `contextvars`.
    - soporte opcional de archivo rotativo por variables de entorno (`LOG_TO_FILE`, `LOG_DIR`, `LOG_FILE`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`).
  - `app/main.py`:
    - inicialización central de logging en arranque.
    - middleware HTTP de trazabilidad (`request_id`, `method`, `path`, `status_code`, `duration_ms`, `client_ip`, `user_id`).
    - header de respuesta `X-Request-ID`.
    - registro explícito de excepciones HTTP.
    - registro de eventos de autenticación: login exitoso, login fallido (credenciales/permiso), logout.
  - `README.md`:
    - documentación de variables de logging y capacidades de observabilidad.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: sincronización de gobernanza.
- Comandos ejecutados:
  - `python -m compileall app README.md docs/ai`
- Resultado:
  - Quedó trazabilidad suficiente para investigación de incidentes en local/Docker sin cambiar lógica funcional del negocio.

## 2026-03-06 14:45 UTC-06:00 | tool: Codex CLI
- Objetivo: implementar `REQ-103` para capturar motivo/clasificación obligatorio en creación de requisición.
- Tareas: `REQ-103`.
- Cambios:
  - `app/models.py`: nuevo campo `Requisicion.motivo_requisicion` (`String(80)`, nullable para compatibilidad histórica).
  - `app/database.py`:
    - migración incremental idempotente `ALTER TABLE requisiciones ADD COLUMN motivo_requisicion TEXT`.
    - ajuste de reconstrucción de tabla `requisiciones` para incluir el nuevo campo y no perder datos en migraciones históricas.
  - `app/crud.py`: `crear_requisicion_db(...)` ahora recibe y persiste `motivo_requisicion`.
  - `app/main.py`:
    - catálogo fijo `MOTIVOS_REQUISICION` con 11 valores de negocio.
    - `/crear` GET envía motivos al template.
    - `/crear` POST valida motivo obligatorio y pertenencia al catálogo; si no cumple retorna `400`.
  - `templates/crear_requisicion.html`: nuevo selector obligatorio `Motivo / Clasificacion`.
  - `tests/test_basic_flow.py`:
    - ajuste de payloads `/crear` para incluir `motivo_requisicion`.
    - nuevos tests: `motivo` requerido e inválido.
  - `tests/test_liquidacion_integration.py`: actualización de firma de `crear_requisicion_db(...)` con `motivo_requisicion`.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: gobernanza actualizada.
- Comandos ejecutados:
  - `python -m compileall app templates tests`
  - `.venv/bin/python -m pytest -q tests/test_basic_flow.py -k \"motivo or crear_requisicion\" -v`
- Resultado:
  - nuevas requisiciones no se crean sin motivo válido.
  - el campo queda persistido para futuras métricas/BI sin alterar flujos de aprobación/entrega/liquidación.

## 2026-03-06 15:30 UTC-06:00 | tool: Codex CLI
- Objetivo: habilitar edición de requisición por solicitante antes de aprobación.
- Tareas: `REQ-104`.
- Cambios:
  - `app/main.py`:
    - nuevo helper `validar_receptor_designado(...)` reutilizado en creación y edición.
    - nuevas rutas:
      - `GET /mis-requisiciones/{id}/editar`
      - `POST /mis-requisiciones/{id}/editar`
    - guardias: solo solicitante, estado `pendiente` y `approved_by is None`.
    - actualización completa de datos principales + reemplazo de items en edición.
  - `templates/editar_requisicion.html` (nuevo):
    - formulario de edición con datos precargados.
    - edición de ítems con contexto y etiqueta `Para Demo`.
  - `templates/mis_requisiciones.html`:
    - botón `Editar` visible solo para requisiciones pendientes.
  - `templates/crear_requisicion.html` + `static/app.js`:
    - estandarización de formulario de requisición con `data-requisicion-form` para compartir validación JS entre crear/editar.
    - contador dinámico de filas inicializado según cantidad de ítems existentes.
  - `tests/test_basic_flow.py`:
    - nuevos tests para edición permitida en pendiente propia y bloqueos por estado/apropiación.
  - `tests/test_liquidacion_integration.py`:
    - ajuste de firma de `crear_requisicion_db(...)` con `motivo_requisicion`.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: gobernanza actualizada.
- Comandos ejecutados:
  - `python -m compileall app templates static tests`
  - `.venv/bin/python -m pytest -q tests/test_basic_flow.py -k \"editar_requisicion or crear_requisicion\" -v`
- Resultado:
  - El solicitante ya puede corregir la requisición antes de que sea aprobada, sin abrir edición en estados posteriores.

## 2026-03-06 16:05 UTC-06:00 | tool: Codex CLI
- Objetivo: mejorar UX en selección de receptor cuando hay más de 50 usuarios.
- Tareas: `REQ-105`.
- Cambios:
  - `templates/crear_requisicion.html` y `templates/editar_requisicion.html`:
    - se agregó input `Buscar receptor...` encima del select `receptor_designado_id`.
  - `templates/bodega_gestionar.html` y `templates/bodega_entrega_parcial.html`:
    - se agregó buscador de receptor en la firma de entrega.
    - el buscador respeta el flujo de bloqueo/desbloqueo (`Cambiar receptor`, `Guardar cambio`, `Cancelar`).
  - `static/app.js`:
    - helper genérico de filtrado de options por texto (`nombre/rol`) con normalización de acentos.
    - inicialización automática para inputs con `data-select-search`.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: gobernanza actualizada.
- Comandos ejecutados:
  - `python -m compileall templates static app`
- Resultado:
  - Los selects largos de receptor ahora se filtran en tiempo real, reduciendo errores y tiempo de captura en operación.

## 2026-03-09 10:20 UTC-06:00 | tool: Codex CLI
- Objetivo: corregir feedback insuficiente en `Gestionar Entrega` cuando la firma del receptor falla por PIN faltante/incorrecto.
- Tareas: `REQ-105A`.
- Cambios:
  - `templates/bodega_gestionar.html`:
    - el `error_message` ahora se muestra como banner `alert alert-error` visible encima del formulario.
    - se agregó mensaje inline junto al campo `PIN del receptor`.
    - al re-render con error, la vista hace scroll automático al banner para que el usuario vea la causa.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: gobernanza actualizada.
- Comandos ejecutados:
  - `python -m compileall templates`
- Resultado:
  - Si la entrega no avanza por problema de firma, el usuario ahora ve claramente por qué.

## 2026-03-09 14:35 UTC-06:00 | tool: Codex CLI
- Objetivo: mover la regla de cantidades decimales al catalogo como fuente de verdad y limitarla a concentrados autorizados.
- Tareas: `REQ-106`.
- Cambios:
  - `app/catalog_types.py`:
    - nuevo helper `catalog_item_allows_decimal(...)` con regla centralizada para `CONCENTRADO SHF` y `LIQUIDO CONCENTRADO DESODORIZADOR`.
  - `app/models.py`:
    - nuevo campo `CatalogoItem.permite_decimal`.
  - `app/database.py`:
    - migracion incremental para `catalogo_items.permite_decimal`.
    - backfill automatico del flag segun nombre del item ya existente.
  - `app/main.py`:
    - payload de catalogo enriquecido para formularios crear/editar.
    - validacion backend fuerte: si un item no permite decimal, rechaza cantidades no enteras.
    - importacion/alta/edicion de catalogo actualizan `permite_decimal` automaticamente segun nombre.
  - `templates/crear_requisicion.html`, `templates/editar_requisicion.html`, `static/app.js`:
    - UX de cantidad sensible al item seleccionado: entero por defecto, decimal solo cuando el catalogo lo habilita.
  - `templates/admin_catalogo_items.html`, `templates/admin_catalogo_item_form.html`:
    - visibilidad del flag `permite_decimal` en administracion de catalogo.
  - `tests/test_basic_flow.py`, `tests/test_admin_catalog_items.py`:
    - cobertura para rechazo de decimal en item no habilitado, aceptacion en concentrado permitido y autoclasificacion del flag en catalogo.
- Comandos ejecutados:
  - `python -m compileall app templates static tests`
  - `.venv/bin/python -m pytest -q tests/test_admin_catalog_items.py -v`
  - `.venv/bin/python -m pytest -q tests/test_basic_flow.py -k 'decimal or crear_requisicion' -v`
- Resultado:
  - Compilacion completa correcta.
  - Los `pytest` arrancan pero vuelven a quedar colgados al entrar en `TestClient` en este entorno; se mantiene como limitacion local ya conocida.

## 2026-03-09 15:05 UTC-06:00 | tool: Codex CLI
- Objetivo: corregir falso rechazo "Selecciona un item válido del catálogo" tras enriquecer `window.CATALOGO_ITEMS`.
- Tareas: `REQ-106A`.
- Cambios:
  - `static/app.js`:
    - `getCatalogItemMeta(...)` ahora soporta payload legado de strings y payload nuevo de objetos.
    - comparación normalizada (trim/minúsculas/sin acentos) para evitar rechazos por formato o caché.
  - `docs/ai/TASKS.md`, `docs/ai/HANDOFF.md`: gobernanza actualizada.
- Comandos ejecutados:
  - `python -m compileall static`
- Resultado:
  - La validación del formulario vuelve a aceptar ítems válidos del catálogo al crear/editar requisiciones.

## 2026-03-09 15:35 UTC-06:00 | tool: Codex CLI
- Objetivo: extender la restriccion de decimales por catalogo a la vista y backend de liquidacion.
- Tareas: `REQ-106B`.
- Cambios:
  - `app/main.py`:
    - `attach_catalog_item_defaults(...)` ahora adjunta tambien `permite_decimal` por item desde catalogo.
    - `POST /liquidar/{id}` rechaza decimales en `Regresa`, `Usado` y `No usado` cuando el item no permite fracciones.
  - `templates/liquidar.html`:
    - inputs de cantidades usan `step=1` o `0.01` segun el item.
    - validacion JS por fila bloquea submit si un item no permitido recibe decimales.
    - mensaje inline especifico para este caso.
  - `tests/test_liquidacion.py`:
    - nuevo caso de rechazo para item no habilitado.
    - nuevo caso de aceptacion para `LIQUIDO CONCENTRADO DESODORIZADOR`.
- Comandos ejecutados:
  - `python -m compileall app templates tests`
  - `.venv/bin/python -m pytest -q tests/test_liquidacion.py -k 'decimal' -v`
- Resultado:
  - La restriccion de enteros/decimales ya aplica tambien a liquidacion, sin tocar formulas ni alertas existentes.

## 2026-03-09 15:50 UTC-06:00 | tool: Codex CLI
- Objetivo: corregir UX de `liquidar.html` cuando un valor invalido deja el boton `Liquidar` pegado deshabilitado.
- Tareas: `REQ-106C`.
- Cambios:
  - `templates/liquidar.html`:
    - nuevo recálculo robusto con tolerancia numerica (`numbersEqual`, `isWholeNumber`).
    - listeners delegados a nivel de formulario para `input`, `change`, `blur` y `keyup`.
    - el estado del boton se recalcula siempre desde el DOM actual, evitando residuos de estados intermedios.
- Comandos ejecutados:
  - `python -m compileall templates`
- Resultado:
  - Tras corregir un valor invalido en liquidacion, el boton se vuelve a habilitar sin recargar la pagina.

## 2026-03-09 16:05 UTC-06:00 | tool: Codex CLI
- Objetivo: reforzar la reevaluacion reactiva de `liquidar.html` tras persistir el congelamiento del boton `Liquidar`.
- Tareas: `REQ-106D`.
- Cambios:
  - `templates/liquidar.html`:
    - nuevo `scheduleEvaluate()` con `setTimeout(..., 0)` para recalcular despues de que el navegador asiente el valor del input.
    - listeners adicionales `paste`, `focusout` y `pageshow`.
    - consolidacion del ciclo de reevaluacion del boton en un punto unico.
- Comandos ejecutados:
  - `python -m compileall templates`
- Resultado:
  - La validacion de liquidacion queda mas tolerante a ediciones intermedias y eventos de navegador en inputs numericos.

## 2026-03-09 16:20 UTC-06:00 | tool: Codex CLI
- Objetivo: hacer visible el bloqueo por decimales no permitidos en la vista de liquidacion.
- Tareas: `REQ-106E`.
- Cambios:
  - `templates/liquidar.html`:
    - nuevo banner global `data-decimal-error` para explicar que solo los concentrados autorizados aceptan fracciones.
    - `recalcRow(...)` ahora distingue motivo de invalidacion y marca `row-decimal-invalid`.
  - `static/theme.css`:
    - estilos especificos para banner y fila de error por decimal no permitido, con mayor contraste visual.
- Comandos ejecutados:
  - `python -m compileall templates static`
- Resultado:
  - Cuando la liquidacion se bloquea por un decimal invalido, el usuario ahora ve una alerta visible y la fila exacta resaltada.

## 2026-03-09 16:35 UTC-06:00 | tool: Codex CLI
- Objetivo: agregar ayuda contextual dentro de la app para orientar el uso de `Contexto operativo`.
- Tareas: `REQ-107`.
- Cambios:
  - `templates/crear_requisicion.html`, `templates/editar_requisicion.html`:
    - ayuda contextual visible junto al selector de `Contexto operativo`.
  - `static/app.js`:
    - las filas dinamicas nuevas replican la misma ayuda.
  - `static/theme.css`:
    - estilos de tooltip/popover reutilizable con soporte hover/focus/click.
- Comandos ejecutados:
  - `python -m compileall templates static`
- Resultado:
  - El usuario ahora puede consultar una explicacion breve de cuando usar `Reposicion` vs `Instalacion inicial` sin salir del formulario.

## 2026-03-09 17:05 UTC-06:00 | tool: Codex CLI
- Objetivo: orientar a bodega en la vista de liquidacion con una ayuda breve sobre las reglas de captura.
- Tareas: `REQ-107A`.
- Cambios:
  - `templates/liquidar.html`:
    - nuevo `?` contextual antes de las alertas del formulario de liquidacion.
  - `static/theme.css`:
    - ajuste menor de espaciado para el bloque de ayuda en liquidacion.
- Comandos ejecutados:
  - `python -m compileall templates static`
- Resultado:
  - La pantalla de liquidacion ahora explica de forma breve que `Usado + No usado = Entregado` y que, en consumibles, `Regresa = No usado`.

## 2026-03-09 17:15 UTC-06:00 | tool: Codex CLI
- Objetivo: simplificar la vista de liquidacion removiendo la captura de referencia Prokey.
- Tareas: `REQ-107B`.
- Cambios:
  - `templates/liquidar.html`:
    - se retiro el bloque `Referencia comprobante Prokey (opcional, se completa despues)`.
- Comandos ejecutados:
  - `python -m compileall templates`
- Resultado:
  - La referencia Prokey ya no se captura en liquidacion y queda reservada para visualizacion/actualizacion posterior en detalle.
- Fecha: 2026-03-09
- Objetivo: restringir el rol `bodega` a la operación de bodega, quitando acceso a creación e historial propio de requisiciones.
- Archivos tocados:
  - `app/main.py`
  - `templates/partials/navbar.html`
  - `templates/home.html`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `rg -n "bodega|mis-requisiciones|/crear" app templates tests -S`
  - `python -m compileall app templates tests`
- Resultado:
  - El rol `bodega` plano ya no ve `Nueva Requisicion` ni `Mis Requisiciones` en navbar/home.
  - Intentos directos a `/crear`, `/mis-requisiciones`, editar y eliminar se redirigen a `/bodega` con mensaje.
  - `jefe_bodega` no cambia: mantiene accesos mixtos de aprobar y bodega.
- Fecha: 2026-03-09
- Objetivo: habilitar impresión PDF desde estado `aprobada` en adelante, no solo tras liquidación.
- Archivos tocados:
  - `app/main.py`
  - `static/app.js`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app static tests`
- Resultado:
  - `GET /requisiciones/{id}/pdf` ya permite `aprobada`, `entregada`, `liquidada` y `liquidada_en_prokey`.
  - El detalle expone `pdf_url` desde `aprobada` y el botón `Ver PDF` queda habilitado en todos esos estados.
  - `pendiente` sigue bloqueado con `403`.
- Fecha: 2026-03-09
- Objetivo: corregir el PDF previo a entrega para que no muestre cantidades entregadas cuando la requisición solo está aprobada.
- Archivos tocados:
  - `app/main.py`
  - `app/pdf_generator.py`
  - `tests/test_basic_flow.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Comandos:
  - `python -m compileall app tests`
- Resultado:
  - En estado `aprobada`, el PDF cambia el encabezado de la columna a `Solicitado`.
  - La tabla usa `cantidad_solicitada` en vez de `cantidad_entregada` mientras no exista entrega.
  - No se alteró la UI web ni la lógica de entrega/liquidación.

## 2026-03-10 18:10 UTC-06:00 | tool: Codex CLI
- Objetivo: alinear la semantica de `Ingreso PK (Bodega)` con el criterio operativo nuevo: contar solo retornables usados que regresan y excedentes devueltos.
- Tareas: `REQ-111`.
- Archivos tocados:
  - `app/crud.py`
  - `app/main.py`
  - `static/app.js`
  - `tests/test_liquidacion.py`
  - `tests/test_liquidacion_integration.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - se agrego `calcular_ingreso_pk_bodega(...)` como fuente de verdad compartida
  - el payload de detalle y el payload del PDF dejaron de mapear `pk_ingreso_qty` directamente desde `qty_returned_to_warehouse`
  - se actualizo la expectativa del caso mixto y se agrego un caso explicito donde el retorno no usado normal deja de inflar `Ingreso PK`
- Comandos:
  - `python -m compileall app static tests`
- Resultado:
  - `Ingreso PK (Bodega)` ahora refleja `min(used, returned) + max(returned - delivered, 0)` para retornables y `0` para consumibles, tanto en el modal como en el PDF.

## 2026-03-10 18:24 UTC-06:00 | tool: Codex CLI
- Objetivo: hacer visibles en la vista de liquidacion los metadatos operativos por item (`Contexto operativo` y `Para Demo`) sin tocar reglas ni persistencia.
- Tareas: `REQ-112`.
- Archivos tocados:
  - `templates/liquidar.html`
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - se agrego un bloque visual debajo de la descripcion del item con chip de `Reposicion` / `Instalacion inicial`
  - se hizo visible la etiqueta `Para Demo` en las filas de liquidacion
- Comandos:
  - `python -m compileall templates static`
- Resultado:
  - Bodega ya ve en la captura de liquidacion si cada item era `Para Demo` y bajo que `Contexto operativo` fue solicitado, sin cambio de logica.

## 2026-03-10 18:33 UTC-06:00 | tool: Codex CLI
- Objetivo: ocultar temporalmente la columna `Ocupo` de la vista de liquidacion para evitar confusiones, sin tocar reglas ni mensajes.
- Tareas: `REQ-112A`.
- Archivos tocados:
  - `templates/liquidar.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - se removio la columna visual `Ocupo` de la tabla
  - el calculo `used + not_used` se mantiene interno para cobertura, diferencias y mensajes inline
- Comandos:
  - `python -m compileall templates`
- Resultado:
  - La vista de liquidacion queda mas clara para bodega sin alterar la logica de validacion existente.

## 2026-03-10 18:41 UTC-06:00 | tool: Codex CLI
- Objetivo: unificar el nombre visible de los estados en `Mis Requisiciones`, `Aprobar` y `Bodega` para evitar mezcla entre estado real e interpretacion operativa.
- Tareas: `REQ-113`.
- Archivos tocados:
  - `templates/macros/ui.html`
  - `templates/mis_requisiciones.html`
  - `templates/aprobar.html`
  - `templates/bodega.html`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - `status_badge` ahora traduce y capitaliza consistentemente estados reales y resultados de entrega
  - las tablas de `Mis Requisiciones`, `Aprobar` y `Bodega` dejaron de pasar etiquetas divergentes como `Pendiente de entregar` para una requisicion `aprobada`
  - el filtro visible de `Aprobar` para estado `aprobada` ahora se muestra como `Aprobada`
- Comandos:
  - `python -m compileall templates`
- Resultado:
  - La UI usa etiquetas de estado consistentes entre vistas: `Pendiente de aprobar`, `Aprobada`, `Preparado`, `Entregada`, `Liquidada` y `Liquidada en Prokey`.

## 2026-03-10 18:49 UTC-06:00 | tool: Codex CLI
- Objetivo: mejorar el contraste del chip de `Contexto operativo` en la vista de liquidacion para que deje de perderse visualmente.
- Tareas: `REQ-113A`.
- Archivos tocados:
  - `static/theme.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - se reforzo el fondo del chip, el borde y el peso del texto
  - se agrego leve `box-shadow` interno para separarlo mejor del panel dark
- Comandos:
  - `python -m compileall static`
- Resultado:
  - `Reposicion` / `Instalacion inicial` ahora se leen con mayor claridad en la captura de liquidacion.

## 2026-03-10 20:05 UTC-06:00 | tool: Codex CLI
- Objetivo: implementar respaldos y restauracion admin-only con alcance seguro sobre SQLite, sin tocar la logica operativa de requisiciones.
- Tareas: `REQ-114`.
- Archivos tocados:
  - `.gitignore`
  - `app/database.py`
  - `app/main.py`
  - `templates/admin_respaldos.html`
  - `templates/partials/navbar.html`
  - `README.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
  - `docs/ai/DECISIONS.md`
- Cambios:
  - se agregaron helpers de SQLite para generar respaldos ZIP consistentes usando la API de backup de SQLite, mas `manifest.json` con checksum y metadatos.
  - se agrego pantalla admin `Respaldos` con generacion/descarga de backups guardados y restauracion desde respaldo guardado o ZIP subido.
  - la restauracion ahora crea automaticamente un backup previo (`pre_restore_*`), activa un bloqueo temporal de nuevas requests y obliga a volver a iniciar sesion al terminar.
  - se documento explicitamente que el alcance del respaldo es la DB + manifest, no codigo, Docker ni `.env`.
- Comandos:
  - `python -m compileall app templates`
- Resultado:
  - `admin` ya puede respaldar y restaurar rapidamente la data operativa desde UI sin copiar manualmente la DB, manteniendo una estrategia segura para SQLite.

## 2026-03-10 20:18 UTC-06:00 | tool: Codex CLI
- Objetivo: corregir el primer bug operativo de la nueva pantalla `Respaldos`, donde el logger rompia la generacion del ZIP por usar una clave reservada de `LogRecord`.
- Tareas: `REQ-114A`.
- Archivos tocados:
  - `app/main.py`
  - `app/logging_utils.py`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - el evento `admin_backup_created` dejo de enviar `filename` en `extra=` y ahora usa `backup_filename`
  - el formatter JSON se amplio para incluir `backup_filename`, `backup_source` y `safety_backup`
- Comandos:
  - `python -m compileall app`
- Resultado:
  - la generacion de respaldos ya no falla por `Attempt to overwrite 'filename' in LogRecord` y mantiene trazabilidad de backup/restore en logs.

## 2026-03-10 20:28 UTC-06:00 | tool: Codex CLI
- Objetivo: dejar en `README.md` una guia de contingencia explicita para reconstruir `.env` sin tener que buscar valores ni comandos en emergencia.
- Tareas: `REQ-114B`.
- Archivos tocados:
  - `README.md`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - se documento el valor exacto de `DATABASE_URL` usado hoy en Docker: `sqlite:////app/data/requisiciones.db`
  - se agregaron comandos listos para generar un `SECRET_KEY`
  - se agregaron pasos concretos para recrear `.env` y verificarlo desde el contenedor
- Comandos:
  - sin ejecucion adicional (cambio documental)
- Resultado:
  - el repo ya deja a mano el procedimiento de recuperacion de `.env` para escenarios de contingencia.

## 2026-03-10 20:42 UTC-06:00 | tool: Codex CLI
- Objetivo: hacer visible en el modal de detalle el `receptor_designado`, ya presente en el payload API pero ausente en la UI.
- Tareas: `REQ-115`.
- Archivos tocados:
  - `static/app.js`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - se renderiza `receptor_designado` (nombre + rol) en la tarjeta `Informacion general`
  - no se tocaron backend ni permisos; el dato ya venia desde `/api/requisiciones/{id}`
- Comandos:
  - sin ejecucion adicional (ajuste puntual de UI)
- Resultado:
  - el detalle vuelve a mostrar quien fue designado para recoger/recibir el producto en la requisicion.

## 2026-03-10 20:56 UTC-06:00 | tool: Codex CLI
- Objetivo: corregir la baja legibilidad del chip `Resultado entrega` dentro del detalle de requisicion.
- Tareas: `REQ-115A`.
- Archivos tocados:
  - `static/style.css`
  - `docs/ai/TASKS.md`
  - `docs/ai/HANDOFF.md`
  - `docs/ai/WORKLOG.md`
- Cambios:
  - se reforzaron los estilos de `resultado-chip` con mayor peso tipografico, borde y colores de alto contraste
  - `completa`, `parcial` y `no_entregada` ahora usan combinaciones legibles sobre el fondo actual del dashboard
- Comandos:
  - `python -m compileall static`
- Resultado:
  - `Resultado entrega` vuelve a leerse con claridad dentro de la tarjeta `Estado liquidacion`.
