# Checklist Ejecutable MVP (CLI + Vibecoding)

Uso: copiar este checklist al iniciar cada sesion de Codex/Claude/Gemini CLI.

## A. Pre-flight (2 min)
- [ ] Leer `docs/ai/CONTRACT.md` (decisiones congeladas).
- [ ] Leer `docs/ai/HANDOFF.md` (estado real y siguiente paso).
- [ ] Tomar 1 tarea `todo` en `docs/ai/TASKS.md` y pasarla a `in_progress`.
- [ ] Confirmar que no se cambia el alcance MVP.

## B. Implementacion (ciclo corto)
- [ ] Implementar solo 1 tarea por ciclo.
- [ ] Mantener cambios chicos (1-4 archivos por tarea).
- [ ] Evitar nuevas dependencias salvo necesidad real.
- [ ] Validar permisos por rol y transicion de estado.

## C. Verificacion minima
- [ ] `python -m compileall app init_db.py`
- [ ] Arranque local:
  - [ ] `python init_db.py`
  - [ ] `uvicorn app.main:app --reload`
- [ ] Probar flujo afectado en navegador (caso feliz + permiso denegado).

## D. Cierre de sesion (handoff)
- [ ] Actualizar `docs/ai/WORKLOG.md` (que se hizo + comandos).
- [ ] Actualizar `docs/ai/TASKS.md` (`done`/`blocked` + siguiente tarea).
- [ ] Actualizar `docs/ai/HANDOFF.md` (proximo paso exacto).
- [ ] Si hubo decision de arquitectura: registrar en `docs/ai/DECISIONS.md`.

---

# Revision de Simplicidad: Estructura Actual vs Minima Necesaria

## Mantener (si, necesario)
- `app/main.py`: rutas y orquestacion web.
- `app/database.py`: engine/sesion DB.
- `app/models.py`: modelo de datos.
- `app/auth.py`: login/sesion/usuario actual.
- `app/crud.py`: logica de persistencia y reglas de negocio basicas.
- `templates/` y `static/`: UI SSR simple.
- `init_db.py`: bootstrap de DB y usuarios base.
- `requirements.txt`, `.env.example`, `README.md`.
- `docs/ai/*`: continuidad multi-IA.

## Opcional (si vuelve a crecer API)
- Crear `app/schemas.py` solo cuando tengas varios endpoints JSON y necesites contratos estrictos.
- Mientras predomine SSR + un JSON simple, no hace falta ese archivo.

## No necesario para este MVP
- Docker/compose
- Alembic/migraciones formales (todavia)
- colas/background jobs
- arquitectura por capas complejas (services/repositories separados extra)
- sistema de permisos declarativo sofisticado

## Estructura minima recomendada (ultra simple)
```text
app/
  main.py
  database.py
  models.py
  auth.py
  crud.py
templates/
static/
init_db.py
requirements.txt
.env.example
README.md
docs/ai/
```

## Regla practica
Si un archivo nuevo no elimina complejidad neta o no reduce bugs, no se crea.
