from pathlib import Path
from .typing import StrPath
from .utils import freeze, urlparser
from .models.ipk import InfiniPackage
from .exceptions import FileTypeMismatch
from .const import INDEX

import os
import requests
import tempfile


def build(source_path: StrPath):
    freeze.build_ipk(InfiniPackage(source_path))


def extract(source_path: StrPath, dist_path: StrPath | None = None):
    dist_path = (
        Path(dist_path).resolve() if dist_path else Path(source_path).resolve().parent
    )
    freeze.extract_ipk(source_path, dist_path)


def install(uri: str, index: str | None = ""):
    home = Path.home() / ".ipm" / "src"
    home.mkdir(parents=True, exist_ok=True)
    index = index if index else INDEX

    if os.path.isabs(uri):
        if uri.endswith(".ipk"):
            extract(Path(uri).resolve(), home)
        else:
            raise FileTypeMismatch("文件类型与预期[.ipk]不匹配.")
    elif urlparser.is_valid_url(uri):
        ipk_bytes = requests.get(uri).content
        hash_bytes = requests.get(uri.rstrip("/") + ".hash").content

        temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir.name).resolve()

        ipk_file = (temp_path / "temp.ipk").open("w+b")
        ipk_file.write(ipk_bytes)
        ipk_file.close()

        hash_file = (temp_path / "temp.ipk.hash").open("w+b")
        hash_file.write(hash_bytes)
        hash_file.close()

        extract(ipk_file, home)
        temp_dir.cleanup()
    elif uri.isalpha():
        ...
    else:
        raise FileTypeMismatch("URI指向未知的位置.")
