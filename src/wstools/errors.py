import logging


class BotCommandError(Exception):
    """User-facing command error that can be safely shown in Discord."""

    log_level = logging.INFO


class ProxyGenerationError(BotCommandError):
    """Raised when proxy generation cannot complete for a requested deck or card."""

    log_level = logging.WARNING
