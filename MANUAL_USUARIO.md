# Manual de Usuario Final
## Sistema Interno de Requisiciones (v1.x)

## 1. Objetivo del sistema
Este sistema permite gestionar requisiciones internas de material desde la creación hasta el cierre operativo en Prokey, con trazabilidad completa por usuario, fechas y estados.

## 2. Roles y qué puede hacer cada uno
1. `user` (solicitante): crea requisiciones, consulta su historial y detalle.
2. `aprobador`: aprueba o rechaza requisiciones pendientes.
3. `bodega`: prepara entregas, registra firma con PIN, liquida requisiciones.
4. `jefe_bodega`: combina permisos de `aprobador` y `bodega`, y puede confirmar cierre en Prokey.
5. `admin`: control total (usuarios, catálogo, aprobación, bodega, cierre en Prokey, etc.).
6. `tecnico`: usuario operativo para firma de recibido (PIN), sin inicio de sesión.

## 3. Flujo completo de estados
1. `pendiente`
2. `aprobada` o `rechazada`
3. `entregada`
4. `liquidada`
5. `liquidada_en_prokey` (estado final, inmutable)

## 4. Inicio de sesión
1. Ingrese usuario y contraseña en `/login`.
2. Si no tiene sesión e intenta abrir otra ruta web, el sistema redirige a login.
3. Usuarios inactivos o sin permiso de iniciar sesión no pueden entrar.

## 5. Crear una requisición
Ruta principal: `Nueva Requisición`.

1. Complete datos del cliente:
   1. Código cliente.
   2. Nombre cliente.
   3. Ruta principal.
2. Seleccione `Receptor designado` (obligatorio).
3. Ingrese la justificación.
4. Agregue ítems:
   1. Escriba ítem usando autocompletado del catálogo activo.
   2. Indique cantidad.
   3. Defina contexto operativo por ítem:
      1. `Reposición` (default).
      2. `Instalación inicial`.
   4. Marque `Para Demo` si aplica.
5. Envíe la requisición.

Notas:
1. No se permiten ítems duplicados en la misma requisición.
2. No se aceptan ítems fuera de catálogo.
3. El contexto operativo es por ítem, no global.

## 6. Aprobación y rechazo
Ruta principal: `Aprobar`.

1. El aprobador revisa datos e ítems.
2. Puede:
   1. Aprobar.
   2. Rechazar (con razón/comentario).
3. Todo queda en timeline con actor y hora.

## 7. Operación de bodega (entrega)
Ruta principal: `Bodega`.

1. Bodega ve pendientes de preparar y de liquidar.
2. Al gestionar entrega:
   1. Selecciona resultado: `completa`, `parcial` o `no_entregada`.
   2. Firma de recibido:
      1. Receptor y PIN.
      2. Si cambia el receptor designado, debe hacerlo explícitamente con controles de cambio.
3. Entrega parcial permite definir cantidades entregadas por ítem.
4. Resultado exitoso cambia estado a `entregada`.

## 8. Liquidación (cierre de bodega)
Ruta principal: botón `Liquidar` en requisiciones entregadas.

Por ítem se registra:
1. `Regresa`
2. `Usado`
3. `No usado`
4. `Tipo` (`RETORNABLE` o `CONSUMIBLE`; si catálogo ya lo define, va bloqueado)
5. Nota opcional

Reglas clave:
1. Cobertura obligatoria: `Usado + No usado = Entregado`.
2. En `CONSUMIBLE`: `Regresa = No usado`.
3. En `RETORNABLE`: devolución mayor a cobertura/entregado ya no bloquea; se guarda con alerta.
4. Alertas no bloqueantes se guardan por ítem para trazabilidad.
5. Puede liquidarse sin referencia Prokey.

Resultado:
1. Estado pasa a `liquidada`.
2. Se guarda quién liquidó y cuándo.

## 9. Confirmación final en Prokey
Solo `jefe_bodega` y `admin`.

1. En requisiciones `liquidada`, use `Confirmar en Prokey`.
2. Estado cambia a `liquidada_en_prokey`.
3. Se registra actor y fecha de confirmación.
4. Desde ese estado ya no hay cambios operativos.

## 10. Referencia Prokey
1. Puede quedar pendiente al liquidar.
2. Luego puede completarse desde pantalla dedicada de referencia.
3. Permisos para edición de referencia:
   1. `admin`
   2. Solicitante propietario de la requisición liquidada

## 11. Detalle de requisición
Disponible desde listados con botón `Ver`.

Muestra:
1. Información general.
2. Estado y actores.
3. Línea de tiempo completa.
4. Tabla de ítems.
5. En liquidadas:
   1. Tipo y contexto operativo por ítem.
   2. Diferencia (`DIF`) con lectura operativa (`Falta`, `Extra`, `OK`).
   3. Ingreso PK (Bodega).
   4. Alertas humanizadas con tooltip.
   5. Comentario de liquidación y notas por ítem.
6. Badge `Para Demo` cuando aplique.

## 12. PDF de requisición
1. Botón `Ver PDF` en detalle.
2. Disponible en estados:
   1. `liquidada`
   2. `liquidada_en_prokey`
3. Incluye:
   1. Datos de cabecera.
   2. Estado/actores.
   3. Timeline.
   4. Ítems con contexto, alertas, DIF e ingreso PK.
4. Se abre en línea en el navegador.

## 13. Catálogo (admin)
Funciones principales:
1. Buscar ítems.
2. Importar catálogo por archivo.
3. Activar/desactivar ítems.
4. Borrar todo el catálogo con doble confirmación (acción sensible).
5. Clasificación automática de tipo de ítem (`RETORNABLE`/`CONSUMIBLE`) para defaults de liquidación.

## 14. Usuarios (admin)
1. Crear, editar, activar/desactivar usuarios.
2. Definir rol y departamento.
3. Configurar PIN para firma.
4. Técnicos:
   1. Sin login.
   2. Con PIN operativo para recibido.

## 15. Recomendaciones operativas
1. Completar siempre justificaciones y notas cuando haya excepciones.
2. Verificar receptor designado antes de firmar.
3. Usar contexto correcto por ítem (`Reposición` vs `Instalación inicial`).
4. Revisar alertas antes de confirmar liquidación.
5. Confirmar en Prokey solo cuando el proceso externo esté realmente cerrado.

## 16. Errores comunes y cómo resolverlos
1. “No autenticado”: vuelva a iniciar sesión.
2. No aparece botón de acción: revisar estado de requisición y rol del usuario.
3. No permite liquidar: revisar cobertura y reglas de consumible.
4. PIN incorrecto: validar receptor seleccionado y su PIN.
5. Ítem no válido al crear: seleccionar desde autocompletado de catálogo activo.
6. PDF deshabilitado: verificar que la requisición esté `liquidada` o `liquidada_en_prokey`.
