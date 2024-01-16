from pathlib import Path
from .freeze import extract_ipk
from ..const import HOME
from ..models.ipk import InfiniPackage

import requests
import tempfile


def load(name: str, baseurl: str = "", filename: str = "") -> InfiniPackage:
    ipk_bytes = requests.get(baseurl.rstrip("/") + "/" + filename).content
    hash_bytes = requests.get(baseurl.rstrip("/") + "/" + filename + ".hash").content

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name).resolve()

    ipk_file = (temp_path / f"{name}.ipk").open("w+b")
    ipk_file.write(ipk_bytes)
    ipk_file.close()

    hash_file = (temp_path / f"{name}.ipk.hash").open("w+b")
    hash_file.write(hash_bytes)
    hash_file.close()

    ipk = extract_ipk(ipk_file, HOME)
    temp_dir.cleanup()
    return ipk
