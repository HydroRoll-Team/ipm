from multilogging import multilogger
from .const import DEBUG

logger = multilogger(name="IPM", level="DEBUG" if DEBUG else "INFO", notime=True)


def info(message: str, echo: bool = False) -> None:
    return logger.info(message) if echo else None


def success(message: str, echo: bool = False) -> None:
    return logger.success(message) if echo else None


def warning(message: str, echo: bool = False) -> None:
    return logger.warning(message) if echo else None


def error(message: str, echo: bool = False) -> None:
    return logger.error(message) if echo else None
