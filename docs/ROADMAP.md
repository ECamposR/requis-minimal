# Roadmap operativo

## Objetivo del roadmap
Ordenar el estado actual del sistema y mejorar la operación móvil de bodega sin alterar la lógica de negocio.

## Fase 0 - Documentación y estabilización
- Actualizar `README.md`.
- Crear `docs/ESTADO_ACTUAL.md`.
- Crear el blueprint móvil de bodega.
- Actualizar la documentación de continuidad IA.
- Identificar y corregir errores menores documentales.

## Fase 1 - Adaptación móvil de bodega
- `/bodega`
- Preparar requisición
- Gestionar entrega
- Entrega parcial
- Modal de detalle solo si bloquea el uso móvil

## Fase 2 - Pulido y pruebas
- Pruebas manuales en escritorio.
- Pruebas manuales en móvil.
- Pruebas SSR básicas si aplica.
- Revisión de regresiones visuales.
- Actualización final de documentación.

## Principios de trabajo
- Cambios pequeños.
- No romper escritorio.
- No cambiar reglas de negocio.
- No cambiar endpoints.
- No introducir frameworks.
- Mantener simplicidad.

## Fuera de alcance actual
- Migraciones de infraestructura.
- Cambio de base de datos.
- Refactor arquitectónico grande.
- Framework frontend nuevo.
- Rediseño completo de toda la aplicación.
- Nuevas funciones de inventario no solicitadas.

## Criterios de cierre
Se considera terminado cuando:
- La documentación está consistente.
- Bodega es usable en móvil.
- Escritorio sigue sin regresiones.
- Los flujos principales están probados.
- El handoff está actualizado.
