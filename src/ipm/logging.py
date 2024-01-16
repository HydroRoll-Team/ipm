from multilogging import multilogger
from .const import DEBUG

logger = multilogger(name="IPM", level="DEBUG" if DEBUG else "INFO")
