#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_CONTAINER="${APP_CONTAINER:-requisiciones}"
CADDY_CONTAINER="${CADDY_CONTAINER:-caddy}"
APP_DB_PATH="${APP_DB_PATH:-/app/data/requisiciones.db}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/backups/full}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/req-backup-${TIMESTAMP}-XXXXXX")"
STAGING_DIR="$WORK_DIR/requisiciones_backup_${TIMESTAMP}"
ARCHIVE_PATH="$OUTPUT_DIR/requisiciones_prod_${TIMESTAMP}.tar.gz"

cleanup() {
    rm -rf "$WORK_DIR"
}
trap cleanup EXIT

log() {
    printf '[backup] %s\n' "$*"
}

docker_container_running() {
    local container_name="$1"
    docker inspect -f '{{.State.Running}}' "$container_name" >/dev/null 2>&1
}

mkdir -p "$STAGING_DIR" "$OUTPUT_DIR"
mkdir -p "$STAGING_DIR/app" "$STAGING_DIR/caddy" "$STAGING_DIR/meta"

log "Preparando snapshot productivo en $STAGING_DIR"

if docker_container_running "$APP_CONTAINER"; then
    log "Contenedor $APP_CONTAINER detectado; generando snapshot consistente de SQLite"
    SNAPSHOT_IN_CONTAINER="/tmp/requisiciones_snapshot_${TIMESTAMP}.db"
    docker exec "$APP_CONTAINER" python -c "
import sqlite3
source = sqlite3.connect('$APP_DB_PATH', timeout=30)
target = sqlite3.connect('$SNAPSHOT_IN_CONTAINER', timeout=30)
source.backup(target)
target.close()
source.close()
"
    docker cp "${APP_CONTAINER}:${SNAPSHOT_IN_CONTAINER}" "$STAGING_DIR/app/requisiciones.db"
    docker exec "$APP_CONTAINER" rm -f "$SNAPSHOT_IN_CONTAINER"
else
    HOST_DB_PATH="$ROOT_DIR/data/$(basename "$APP_DB_PATH")"
    if [[ ! -f "$HOST_DB_PATH" ]]; then
        echo "No se encontró el contenedor $APP_CONTAINER en ejecución ni la base en $HOST_DB_PATH" >&2
        exit 1
    fi
    log "Contenedor $APP_CONTAINER no está corriendo; copiando DB directa desde host"
    cp "$HOST_DB_PATH" "$STAGING_DIR/app/requisiciones.db"
fi

for path in ".env" "docker-compose.yml" "Dockerfile" "README.md"; do
    if [[ -f "$ROOT_DIR/$path" ]]; then
        cp "$ROOT_DIR/$path" "$STAGING_DIR/app/"
    fi
done

if [[ -f "$ROOT_DIR/deploy/caddy/Caddyfile" ]]; then
    cp "$ROOT_DIR/deploy/caddy/Caddyfile" "$STAGING_DIR/caddy/"
fi
if [[ -f "$ROOT_DIR/deploy/caddy/docker-compose.yml" ]]; then
    cp "$ROOT_DIR/deploy/caddy/docker-compose.yml" "$STAGING_DIR/caddy/"
fi

if docker_container_running "$CADDY_CONTAINER"; then
    log "Copiando estado de Caddy desde contenedor $CADDY_CONTAINER"
    mkdir -p "$STAGING_DIR/caddy/data" "$STAGING_DIR/caddy/config"
    docker cp "${CADDY_CONTAINER}:/data/." "$STAGING_DIR/caddy/data/" || true
    docker cp "${CADDY_CONTAINER}:/config/." "$STAGING_DIR/caddy/config/" || true
fi

{
    echo "backup_timestamp=$TIMESTAMP"
    echo "host=$(hostname)"
    echo "root_dir=$ROOT_DIR"
    echo "app_container=$APP_CONTAINER"
    echo "caddy_container=$CADDY_CONTAINER"
    echo "app_db_path=$APP_DB_PATH"
    echo "archive_path=$ARCHIVE_PATH"
    echo "git_branch=$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
    echo "git_commit=$(git -C "$ROOT_DIR" rev-parse HEAD 2>/dev/null || echo 'unknown')"
    echo "git_tag=$(git -C "$ROOT_DIR" describe --tags --always 2>/dev/null || echo 'unknown')"
    echo
    echo "[docker_ps]"
    docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
} > "$STAGING_DIR/meta/manifest.txt"

if command -v sha256sum >/dev/null 2>&1; then
    (
        cd "$STAGING_DIR"
        find . -type f ! -name 'checksums.sha256' -print0 | sort -z | xargs -0 sha256sum > "$STAGING_DIR/meta/checksums.sha256"
    )
fi

log "Empaquetando respaldo en $ARCHIVE_PATH"
tar -C "$WORK_DIR" -czf "$ARCHIVE_PATH" "$(basename "$STAGING_DIR")"

log "Respaldo creado correctamente"
log "Archivo: $ARCHIVE_PATH"
