import logging

from template_github_copilot.loggers import get_logger


def test_get_logger_returns_logger():
    """get_logger should return a logging.Logger instance."""
    logger = get_logger("test_logger_instance")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger_instance"


def test_get_logger_default_name():
    """get_logger with no name should use 'default'."""
    logger = get_logger()
    assert logger.name == "default"


def test_get_logger_has_handler():
    """get_logger should attach a StreamHandler."""
    logger = get_logger("test_handler_check")
    assert len(logger.handlers) >= 1
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_get_logger_does_not_duplicate_handlers():
    """Calling get_logger twice for the same name should not add duplicate handlers."""
    name = "test_no_dup_handlers"
    logger1 = get_logger(name)
    handler_count = len(logger1.handlers)
    logger2 = get_logger(name)
    assert logger1 is logger2
    assert len(logger2.handlers) == handler_count


def test_get_logger_custom_level():
    """get_logger should respect a custom log level."""
    logger = get_logger("test_custom_level", log_level="DEBUG")
    assert logger.level == logging.DEBUG


def test_get_logger_formatter():
    """The handler should have the expected formatter pattern."""
    logger = get_logger("test_formatter")
    handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
    fmt = handler.formatter
    assert fmt is not None
    assert fmt._fmt is not None
    assert "%(asctime)s" in fmt._fmt
    assert "%(levelname)" in fmt._fmt
