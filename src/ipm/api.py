from pathlib import Path
from .typing import StrPath
from .utils import freeze, urlparser, loader
from .models.ipk import InfiniPackage
from .exceptions import FileTypeMismatch
from .const import INDEX, HOME
from .logging import info, success

import os


def build(source_path: StrPath, echo: bool = False) -> None:
    freeze.build_ipk(InfiniPackage(source_path))


def extract(
    source_path: StrPath, dist_path: StrPath | None = None, echo: bool = False
) -> InfiniPackage:
    dist_path = (
        Path(dist_path).resolve() if dist_path else Path(source_path).resolve().parent
    )
    return freeze.extract_ipk(source_path, dist_path, echo)


def install(uri: str, index: str = "", echo: bool = False) -> None:
    info("正在初始化 IPM 环境...", echo)

    HOME.mkdir(parents=True, exist_ok=True)
    index = index or INDEX

    if os.path.isabs(uri):
        info(f"检定给定的 URI 地址[{uri}]为本地路径.", echo)
        if not uri.endswith(".ipk"):
            raise FileTypeMismatch("文件类型与预期[.ipk]不匹配.")
        info("安装中...", echo)
        ipk = extract(Path(uri).resolve(), HOME, echo)
    elif urlparser.is_valid_url(uri):
        filename = uri.rstrip("/").split("/")[-1]
        ipk = loader.load(
            "temp",
            uri.rstrip("/").rsplit("/")[0],
            filename,
        )
    elif uri.isalpha():
        ...
    else:
        raise FileTypeMismatch("URI指向未知的位置.")

    success(f"包[{ipk.name}]成功安装在[{ipk.source_path}].", echo)
