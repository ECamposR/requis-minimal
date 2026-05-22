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
| Pendiente | `/bodega` | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Pendiente | Preparar requisición | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Pendiente | Gestionar entrega | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Pendiente | Entrega parcial | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |
| Pendiente | Modal de detalle | Pendiente | Pendiente | Pendiente | Pendiente | Pendiente |

## Criterios de aceptación final
- Bodega puede operar desde móvil sin scroll horizontal global crítico.
- Escritorio no tiene regresiones evidentes.
- No se detectan bloqueos en preparar/entregar/parcial.
- Modal de detalle no bloquea operación básica.
- Hallazgos menores quedan documentados.
