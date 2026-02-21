import logging

from template_github_copilot.settings import get_project_settings


def get_logger(
    name: str = "default",
    log_level: str = get_project_settings().project_log_level,
) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name (str): The name of the logger.
        log_level (str): The logging level.
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
