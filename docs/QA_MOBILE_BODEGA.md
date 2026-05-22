# Checklist QA móvil - Bodega

## Objetivo
Validar la primera ronda móvil de bodega sin cambiar la lógica funcional ni el flujo backend ya implementado.

## Alcance
- `/bodega`
- Preparar requisición
- Gestionar entrega completa
- Gestionar entrega parcial
- No entregada
- Cambio de receptor
- PIN del receptor
- Modal de detalle solo como evaluación

## Fuera de alcance
- `liquidar.html`
- Rediseño completo del modal
- Cambios backend
- Cambios JS
- Cambios de permisos
- Cambios de endpoints

## Entornos de prueba sugeridos
- Chrome DevTools con ancho móvil
- Móvil real si está disponible
- Escritorio normal para verificar que no hubo regresiones

## Checklist escritorio
- Confirmar que las tablas siguen visibles.
- Confirmar que los filtros siguen funcionando.
- Confirmar que los botones siguen funcionando.
- Confirmar que el detalle sigue abriendo.
- Confirmar que preparación, entrega y entrega parcial siguen igual visualmente en escritorio.

## Checklist móvil - `/bodega`
- Cargar la pestaña Bodega.
- Validar filtros.
- Validar cards de requisiciones.
- Validar `# Req`.
- Validar contraste y legibilidad.
- Validar `Ver detalle`.
- Validar acciones según estado.

## Checklist móvil - Preparar requisición
- Abrir una requisición aprobada.
- Validar datos generales.
- Validar cards de ítems.
- Validar cantidades.
- Validar badge `Para Demo` si aplica.
- Validar botón `Preparado`.
- Validar `Cancelar`.

## Checklist móvil - Gestionar entrega
- Abrir una requisición preparada.
- Validar items aprobados.
- Validar resultado `completa`.
- Validar resultado `parcial`.
- Validar resultado `no_entregada`.
- Validar receptor designado.
- Validar cambio de receptor.
- Validar PIN.
- Validar comentario.
- Validar `Guardar resultado`.

## Checklist móvil - Entrega parcial
- Validar una sola fuente de inputs.
- Validar cantidad entregada por ítem.
- Validar `min` / `max` / `step` / `required`.
- Validar receptor.
- Validar PIN.
- Validar comentario requerido.
- Validar submit.

## Checklist móvil - Modal de detalle
- Abrir detalle desde una card móvil.
- Validar información general.
- Validar timeline.
- Validar items solicitados/liquidados.
- Confirmar que si hay scroll horizontal, queda contenido dentro del bloque de tabla.
- Validar botón `Ver PDF`.

## Registro de hallazgos manuales

| Fecha | Vista | Dispositivo/ancho | Hallazgo | Severidad | Acción recomendada | Estado |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-22 | `/bodega` | Chrome DevTools móvil | Cards móviles legibles; navegación y acciones visibles | Baja | Mantener como aprobado | Aprobado |
| 2026-05-22 | Preparar requisición | Chrome DevTools móvil | Layout móvil legible; cards de ítems y CTA coherentes | Baja | Mantener como aprobado | Aprobado |
| 2026-05-22 | Gestionar entrega | Chrome DevTools móvil | Flujo completo validado con receptor, PIN, comentario y retorno | Baja | Mantener como aprobado | Aprobado |
| 2026-05-22 | Entrega parcial | Chrome DevTools móvil | Flujo completo validado con una sola fuente de inputs y submit correcto | Baja | Mantener como aprobado | Aprobado |
| 2026-05-22 | Modal de detalle | Chrome DevTools móvil | Modal usable; la tabla interna conserva scroll contenido | Baja | Mantener como aceptado para esta ronda | Aceptado |
| 2026-05-22 | Todas las Requisiciones | Chrome DevTools móvil | Tabla global rota en móvil; se oculta y se muestra aviso para usar Bodega | Menor | Mantenerla como vista de escritorio en esta ronda | Resuelto |

## Criterios de aceptación final
- Bodega puede operar desde móvil sin scroll horizontal global crítico.
- Escritorio no tiene regresiones evidentes.
- No se detectan bloqueos en preparar/entregar/parcial.
- Modal de detalle no bloquea operación básica.
- Hallazgos menores quedan documentados.
- La primera ronda móvil de bodega queda lista para merge desde la perspectiva de QA manual.
