from pathlib import Path
from ipm.utils.freeze import extract_ipk
from ipm.const import STORAGE
from ipm.models.ipk import InfiniFrozenPackage

import requests
import tempfile
import shutil


def load_from_remote(name: str, url, hash: str) -> InfiniFrozenPackage:
    ipk_bytes = requests.get(url).content

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name).resolve()

    ipk_path = temp_path / f"{name}.ipk"
    ipk_file = ipk_path.open("w+b")
    ipk_file.write(ipk_bytes)
    ipk_file.close()

    temp_ipk = extract_ipk(ipk_path, temp_path, hash=hash)
    if not temp_ipk:
        raise RuntimeError("解压时出现异常.")

    STORAGE.mkdir(parents=True, exist_ok=True)
    move_to = STORAGE.joinpath(temp_ipk.default_name + ".ipk")

    shutil.copy2(ipk_path, move_to)

    ifp = InfiniFrozenPackage(move_to, name=temp_ipk.name, version=temp_ipk.version)

    temp_dir.cleanup()
    return ifp


def load_from_local(source_path: Path) -> InfiniFrozenPackage:
    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name).resolve()

    temp_ipk = extract_ipk(source_path, temp_path)
    if not temp_ipk:
        raise RuntimeError("解压时出现异常.")
    move_to = STORAGE / temp_ipk.name
    move_to.mkdir(parents=True, exist_ok=True)

    shutil.copy2(source_path, move_to)
    shutil.copy2(source_path.parent / (source_path.name + ".hash"), move_to)

    ifp = InfiniFrozenPackage(
        move_to.joinpath(temp_ipk.default_name + ".ipk"),
        name=temp_ipk.name,
        version=temp_ipk.version,
    )

    temp_dir.cleanup()
    return ifp
