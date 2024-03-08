class IPMException(Exception):
    """IPM Base Exception"""


class FileException(IPMException):
    """IPM File Base Exception"""


class ProjectError(FileException):
    """Exceptions on `infini.toml` project file"""


class TomlLoadFailed(FileException):
    """Failed to load `infini.toml`"""


class LockLoadFailed(FileException):
    """Failed to load `infini.lock`"""


class FileNotFoundError(FileException, FileNotFoundError):
    """Raises when file not founded"""


class FileExistsError(FileException, FileExistsError):
    """Raises when file not founded"""


class SyntaxError(IPMException, SyntaxError):
    """Syntax Error in config file"""


class HashException(IPMException):
    """Exception occured in hashing"""


class VerifyFailed(IPMException):
    """Failed to verify ipk file"""


class FileTypeMismatch(IPMException):
    """Ipk file type mismatch"""


class PackageExsitsError(IPMException):
    """Package already installed"""
