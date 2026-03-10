import contextvars
import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> None:
    _request_id_ctx.set(request_id)


def get_request_id() -> str:
    return _request_id_ctx.get("-")


def clear_request_id() -> None:
    _request_id_ctx.set("-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }

        for key in (
            "event",
            "user_id",
            "username",
            "role",
            "backup_filename",
            "backup_source",
            "safety_backup",
            "path",
            "method",
            "status_code",
            "duration_ms",
            "client_ip",
            "reason",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


def setup_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    log_to_file = os.getenv("LOG_TO_FILE", "0").strip() in {"1", "true", "TRUE", "yes", "YES"}
    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    log_file = log_dir / os.getenv("LOG_FILE", "app.log")
    max_bytes = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "5"))

    root = logging.getLogger()
    root.setLevel(level)
    for handler in list(root.handlers):
        if getattr(handler, "_app_log_handler", False):
            root.removeHandler(handler)

    formatter = JsonFormatter()
    req_filter = RequestIdFilter()

    console = logging.StreamHandler()
    console._app_log_handler = True  # type: ignore[attr-defined]
    console.setLevel(level)
    console.setFormatter(formatter)
    console.addFilter(req_filter)
    root.addHandler(console)

    if log_to_file:
        log_dir.mkdir(parents=True, exist_ok=True)
        rotating_file = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        rotating_file._app_log_handler = True  # type: ignore[attr-defined]
        rotating_file.setLevel(level)
        rotating_file.setFormatter(formatter)
        rotating_file.addFilter(req_filter)
        root.addHandler(rotating_file)
