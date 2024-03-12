from pathlib import Path
from ipm.utils.freeze import extract_ipk
from ipm.const import STORAGE
from ipm.logging import info, success
from ipm.models.ipk import InfiniFrozenPackage

import requests
import tempfile
import shutil


def load_from_remote(
    name: str, baseurl: str = "", filename: str = "", echo: bool = False
) -> InfiniFrozenPackage:
    ipk_uri = baseurl.rstrip("/") + "/" + filename
    hash_uri = baseurl.rstrip("/") + "/" + filename + ".hash"
    info(f"开始下载[.ipk]文件[{ipk_uri}]...", echo)
    ipk_bytes = requests.get(ipk_uri).content
    info(f"开始下载哈希验证文件[{hash_uri}]...", echo)
    hash_bytes = requests.get(hash_uri).content

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name).resolve()
    info(f"创建临时目录[{temp_dir}], 开始释放文件...", echo)

    ipk_path = temp_path / f"{name}.ipk"
    ipk_file = ipk_path.open("w+b")
    ipk_file.write(ipk_bytes)
    ipk_file.close()

    hash_path = temp_path / f"{name}.ipk.hash"
    hash_file = hash_path.open("w+b")
    hash_file.write(hash_bytes)
    hash_file.close()

    info("解压中...", echo)
    temp_ipk = extract_ipk(ipk_path, temp_path)
    if not temp_ipk:
        raise RuntimeError("解压时出现异常.")
    success(f"包[{temp_ipk.name}]解压完成.")
    move_to = STORAGE / temp_ipk.name
    move_to.mkdir(parents=True, exist_ok=True)

    info("转存缓存文件中...", echo)
    shutil.copy2(ipk_path, move_to / temp_ipk.default_name)
    shutil.copy2(hash_path, move_to / (temp_ipk.default_name + ".hash"))
    info(f"缓存文件转存至[{move_to}]完毕.", echo)

    ifp = InfiniFrozenPackage(
        move_to / temp_ipk.default_name, name=temp_ipk.name, version=temp_ipk.version
    )

    info("任务完成, 开始清理下载临时文件...")
    temp_dir.cleanup()
    info("下载临时文件清理完毕.")
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
        move_to.joinpath(temp_ipk.default_name + ".ipk"), name=temp_ipk.name, version=temp_ipk.version
    )

    temp_dir.cleanup()
    return ifp
