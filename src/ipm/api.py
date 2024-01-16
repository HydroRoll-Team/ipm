from pathlib import Path
from .typing import StrPath
from .utils import freeze, urlparser, loader
from .models.ipk import InfiniPackage
from .exceptions import FileTypeMismatch
from .const import INDEX, HOME

import os


def build(source_path: StrPath) -> None:
    freeze.build_ipk(InfiniPackage(source_path))


def extract(source_path: StrPath, dist_path: StrPath | None = None) -> None:
    dist_path = (
        Path(dist_path).resolve() if dist_path else Path(source_path).resolve().parent
    )
    freeze.extract_ipk(source_path, dist_path)


def install(uri: str, index: str = "") -> None:
    HOME.mkdir(parents=True, exist_ok=True)
    index = index if index else INDEX

    if os.path.isabs(uri):
        if uri.endswith(".ipk"):
            extract(Path(uri).resolve(), HOME)
        else:
            raise FileTypeMismatch("文件类型与预期[.ipk]不匹配.")
    elif urlparser.is_valid_url(uri):
        filename = uri.rstrip("/").split("/")[-1]
        loader.load(
            "temp",
            uri.rstrip("/").rsplit("/")[0],
            filename,
        )
    elif uri.isalpha():
        ...
    else:
        raise FileTypeMismatch("URI指向未知的位置.")
