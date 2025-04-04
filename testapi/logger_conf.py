from testapi import app_settings

log_level = "DEBUG" if app_settings.debug_mode else app_settings.log_level

log_config = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        "default": {
            "format": app_settings.standard_log_format,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "class": "jsonformatter.JsonFormatter",
            "format": app_settings.json_log_format,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    handlers={
        "default": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "json" if app_settings.api_log_type == "json" else "default",
        }
    },
    loggers={
        app_settings.logger_name: {
            "handlers": ["default"],
            "propagate": False,
            "level": log_level,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "propagate": False,
            "level": log_level,
        },
        "uvicorn.error": {
            "handlers": ["default"],
            "propagate": False,
            "level": log_level,
        },
        "": {
            "handlers": ["default"],
            "propagate": False,
            "level": log_level,
        },
    },
)
