import logging
from src import config

def configure_logging():
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format=config.LOG_FORMAT,
        filename=config.LOG_FILENAME if config.LOG_FILENAME else None,
        filemode='a'
    )
    logger=logging.getLogger(__name__)
    return logger