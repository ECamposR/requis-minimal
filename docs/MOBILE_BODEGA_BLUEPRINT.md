# Blueprint móvil para bodega

## Objetivo
Hacer usable el flujo operativo de bodega en móviles sin cambiar la lógica de negocio. El foco es permitir que el personal trabaje mientras se mueve por almacén o zona de preparación, con interacción rápida y legible en pantallas pequeñas.

## Usuarios principales
- `bodega`: usa el flujo diario de preparación, entrega, entrega parcial y liquidación.
- `jefe_bodega`: usa el mismo flujo y además puede ejecutar cierres y acciones operativas adicionales según permisos.

## Dispositivos esperados
El diseño debe funcionar en móviles de uso operativo y en equipos táctiles pequeños. Se asume uso en movimiento, lectura rápida y necesidad de botones grandes, claros y fáciles de tocar con una sola mano.

## Principios de diseño
- Mobile-first para bodega.
- Escritorio se conserva.
- Cards en móvil, tablas en escritorio.
- Acciones principales visibles.
- Botones táctiles grandes.
- Mínima información necesaria.
- Sin cambios de reglas de negocio.
- Sin frameworks nuevos.

## Vistas incluidas
1. `/bodega`
2. `/bodega/{id}/preparar`
3. `/bodega/{id}/gestionar`
4. `/entregar/{id}/parcial`
5. Modal de detalle solo si afecta el uso móvil

## Vista `/bodega`
En móvil, cada requisición debe mostrarse como una card compacta con:
- Folio.
- Estado.
- Cliente.
- Solicitante.
- Departamento.
- Fecha clave.
- Justificación resumida.
- Acción principal.
- Botón de detalle.

La card debe priorizar lectura rápida y acceso inmediato a la acción operativa más probable.

## Vista Preparar Requisición
La experiencia debe sentirse como un checklist visual simple, con:
- Folio.
- Cliente y ruta si están disponibles.
- Solicitante.
- Ítems en cards.
- Cantidad destacada.
- Badge `Para Demo`.
- Contexto operativo si está disponible.
- Botón `Marcar como preparado`.

Si se agregan checks por ítem en una primera versión, deben ser solo visuales y no persistentes.

## Vista Gestionar Entrega
El layout móvil debe priorizar:
- Resultado.
- Receptor designado.
- Cambio de receptor.
- PIN.
- Comentario.
- Botón `Guardar resultado`.

La interacción debe evitar campos dispersos y reducir la necesidad de scroll innecesario.

## Vista Entrega Parcial
Cada ítem debe representarse como card con:
- Descripción.
- Cantidad solicitada.
- Input de cantidad entregada.
- Receptor.
- PIN.
- Comentario requerido.
- Botón `Confirmar entrega parcial`.

La jerarquía visual debe dejar claro qué cantidad se está editando y cuál es la acción final de confirmación.

## Modal de detalle
Solo se revisará si el modal bloquea el uso móvil o impide completar una acción principal. No debe convertirse en una nueva superficie compleja por defecto.

## Criterios de aceptación
- Sin scroll horizontal innecesario.
- Botones cómodos y táctiles.
- Acción principal clara en cada vista.
- Mismo flujo backend.
- Escritorio sin regresiones.
- Formularios conservan endpoints y nombres de campos.

## Fuera de alcance
- Escaneo QR.
- Persistencia de checklist por ítem.
- Inventario en tiempo real.
- Rediseño completo del sistema.
- Cambio de stack frontend.
- Cambios de infraestructura.

## Plan de implementación sugerido
1. `/bodega` con cards móviles.
2. `preparar requisición`.
3. `gestionar entrega`.
4. `entrega parcial`.
5. Modal de detalle si aplica.
6. Pruebas y documentación final.
