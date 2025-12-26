import logging
import sys
import json
from datetime import datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach any extra attributes set on the record
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_record.update(record.extra)

        # Include exception info if present
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(log_record, default=str)


def configure_logging(logging_config: dict | None):
    """Configure root logging using a simple JSON formatter.

    logging_config: dict from config file. Expected keys:
      - level: INFO/DEBUG/etc
      - service: service name to include
      - console.enabled: bool
    """
    cfg = logging_config or {}
    level_name = cfg.get("level", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)

    root = logging.getLogger()
    # Clear existing handlers to avoid duplicate logs during reloads
    for h in list(root.handlers):
        root.removeHandler(h)

    formatter = JsonFormatter()

    console_cfg = cfg.get("console", {})
    if console_cfg.get("enabled", True):
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(level)
        ch.setFormatter(formatter)
        root.addHandler(ch)

    root.setLevel(level)

    # Add service name as a convenience on root logger
    service = cfg.get("service")
    if service:
        # attach a small helper to add service name in extra when logging from helpers
        root = logging.getLogger()
        root = logging.LoggerAdapter(root, {"service": service})

    # Keep a module-level reference for tests or further usage
    return logging.getLogger()
