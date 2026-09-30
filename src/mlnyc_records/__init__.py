import logging
import logging.config

import click
from dotenv import load_dotenv

from mlnyc_records.commands import build_records

logger = logging.getLogger("mlnyc_records")


def get_log_config():
    log_format = "%(app)s-%(asctime)s-%(filename)s-%(lineno)d-%(levelname)s-%(message)s"
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "file": {"format": log_format, "defaults": {"app": "mln_data_transform"}},
            "simple": {"format": log_format, "defaults": {"app": "mln_data_transform"}},
        },
        "handlers": {
            "stream": {
                "class": "logging.StreamHandler",
                "formatter": "simple",
                "level": "DEBUG",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "file",
                "level": "DEBUG",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 3,
                "filename": "mlnyc_records.log",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "mlnyc_records": {
                "handlers": ["stream", "file"],
                "level": "DEBUG",
                "propagate": True,
            }
        },
    }
    return config


@click.group()
def mlnyc_records() -> None:
    """CLI for creating MARC record for MLNYC teacher sets."""
    load_dotenv()
    logger_dict = get_log_config()
    logging.config.dictConfig(logger_dict)
    pass


@mlnyc_records.command("build", short_help="Build new Teacher Set records")
def build_teacher_set_bibs() -> None:
    build_records()


def main():
    mlnyc_records()
