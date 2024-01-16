from multilogging import multilogger
from .const import DEBUG

logger = multilogger(name="IPM", level="DEBUG" if DEBUG else "INFO", notime=True)


def info(message: str, echo: bool = True) -> None:
    return logger.info(message) if echo else None


def success(message: str, echo: bool = True) -> None:
    return logger.success(message) if echo else None
