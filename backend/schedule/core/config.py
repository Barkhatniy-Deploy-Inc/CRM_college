import logging
from logging.config import dictConfig

class LogConfig:
    """
    Logging configuration for the application.
    """
    LOGGING_LEVEL = logging.INFO
    LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @staticmethod
    def configure_logging():
        dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': LogConfig.LOGGING_FORMAT,
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout',
                },
            },
            'root': {
                'level': LogConfig.LOGGING_LEVEL,
                'handlers': ['console'],
            },
        })
