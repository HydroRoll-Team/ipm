from pathlib import Path
from typing import (
    Literal as Literal,
    List as List,
    Dict as Dict,
    Any as Any,
    AnyStr as AnyStr,
)

StrPath = str | Path
Index = Dict[Literal["index", "host", "uuid"], str]
Package = Dict[
    Literal["name", "version", "description", "requirements", "dependencies"], str
]
Storage = Dict[Literal["name", "version", "hash", "source"], str]
