from pathlib import Path
from .freeze import extract_ipk
from ..const import STORAGE
from ..models.ipk import InfiniFrozenPackage

import requests
import tempfile
import shutil


def load_from_remote(
    name: str, baseurl: str = "", filename: str = ""
) -> InfiniFrozenPackage:
    ipk_bytes = requests.get(baseurl.rstrip("/") + "/" + filename).content
    hash_bytes = requests.get(baseurl.rstrip("/") + "/" + filename + ".hash").content

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name).resolve()

    ipk_path = temp_path / f"{name}.ipk"
    ipk_file = ipk_path.open("w+b")
    ipk_file.write(ipk_bytes)
    ipk_file.close()

    hash_path = temp_path / f"{name}.ipk.hash"
    hash_file = hash_path.open("w+b")
    hash_file.write(hash_bytes)
    hash_file.close()

    temp_ipk = extract_ipk(ipk_file, temp_path)
    move_to = STORAGE / temp_ipk.name
    move_to.mkdir(parents=True, exist_ok=True)

    shutil.copy2(ipk_file, move_to / temp_ipk.default_name)
    shutil.copy2(hash_file, move_to / (temp_ipk.default_name + ".hash"))

    ifp = InfiniFrozenPackage(
        move_to / temp_ipk.default_name, name=temp_ipk.name, version=temp_ipk.version
    )

    temp_dir.cleanup()
    return ifp


def load_from_local(source_path: Path) -> InfiniFrozenPackage:
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name).resolve()

    temp_ipk = extract_ipk(source_path, temp_path)
    move_to = STORAGE / temp_ipk.name
    move_to.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source_path, move_to)
    shutil.copy2(source_path.parent / (source_path.name + ".hash"), move_to)

    ifp = InfiniFrozenPackage(
        move_to / temp_ipk.default_name, name=temp_ipk.name, version=temp_ipk.version
    )

    temp_dir.cleanup()
    return ifp
