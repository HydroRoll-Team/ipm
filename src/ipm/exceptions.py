class IpmException(Exception):
    """IPM Base Exception"""


class FileException(IpmException):
    """IPM File Base Exception"""


class TomlLoadFailed(FileException):
    """Failed to load `infini.toml`"""


class LockLoadFailed(FileException):
    """Failed to load `infini.lock`"""


class FileNotFoundError(FileException, FileNotFoundError):
    """Raises when file not founded"""


class FileExistsError(FileException, FileExistsError):
    """Raises when file not founded"""


class SyntaxError(IpmException, SyntaxError):
    """Syntax Error in config file"""


class HashException(IpmException):
    """Exception occured in hashing"""


class VerifyFailed(IpmException):
    """Failed to verify ipk file"""


class FileTypeMismatch(IpmException):
    """Ipk file type mismatch"""


class PackageExsitsError(IpmException):
    """Package already installed"""
