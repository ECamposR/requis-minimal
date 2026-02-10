# Requisiciones MVP

MVP interno para gestionar requisiciones de inventario en LAN.

## Stack
- FastAPI
- SQLAlchemy + SQLite
- Jinja2 + PicoCSS + Vanilla JS

## Arranque rapido
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Tests
```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q tests/test_basic_flow.py
```

## Usuarios de prueba
- `admin / admin123`
- `juan.perez / password`
- `carlos.lopez / password`
- `jose.bodega / password`

## Gobernanza multi-IA
Ver:
- `docs/ai/CONTRACT.md`
- `docs/ai/HANDOFF.md`
- `docs/ai/TASKS.md`
- `docs/ai/WORKLOG.md`
- `docs/ai/DECISIONS.md`

## Operacion LAN
- Guia de despliegue y backup: `docs/LAN_DEPLOY.md`
