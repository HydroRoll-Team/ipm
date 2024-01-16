class IpmException(Exception):
    """IPM Base Exception"""


class FileNotFoundError(IpmException, FileNotFoundError):
    """Raises when file not founded"""


class FileExistsError(IpmException, FileExistsError):
    """Raises when file not founded"""


class SyntaxError(IpmException, SyntaxError):
    """Syntax Error in config file"""


class HashException(IpmException):
    """Exception occured in hashing"""


class VerifyFailed(IpmException):
    """Failed to verify ipk file"""


class FileTypeMismatch(IpmException):
    """Ipk file type mismatch"""
