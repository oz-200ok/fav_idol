import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname:<8} {asctime} [{module}:{lineno}] {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "server_file": {
            "level": "INFO",  # INFO 레벨 이상만 기록
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "server.log"),
            "maxBytes": 1024 * 1024,  # 1MB
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "error.log"),
            "maxBytes": 1024 * 1024,  # 1MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "server_file", "error_file"],
            "level": "INFO",
            "propagate": True,
        },
    },
    "root": {  # 기본 로깅 설정 (INFO 레벨 이상)
        "handlers": ["server_file", "error_file"],
        "level": "INFO",
    },
}