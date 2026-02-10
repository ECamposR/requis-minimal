# Guia Breve de Despliegue LAN y Backup

## 1. Preparacion
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
```

## 2. Levantar servicio en LAN
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Acceso:
- Local: `http://127.0.0.1:8000`
- LAN: `http://<IP_LOCAL>:8000`

## 3. Operacion minima recomendada
- Mantener el proceso con `tmux` o servicio systemd.
- Restringir acceso a red local (firewall/router).
- Cambiar credenciales iniciales despues de pruebas.

## 4. Backup operativo
Base de datos:
- Archivo principal: `requisiciones.db`

Backup manual:
```bash
cp requisiciones.db backups/requisiciones_$(date +%Y%m%d_%H%M%S).db
```

Backup diario (cron ejemplo):
```cron
0 2 * * * cp /ruta/requisiciones.db /ruta/backups/requisiciones_$(date +\%Y\%m\%d).db
```

## 5. Recuperacion basica
1. Detener aplicacion.
2. Reemplazar `requisiciones.db` con respaldo.
3. Levantar aplicacion nuevamente.
