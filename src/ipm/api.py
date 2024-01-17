from pathlib import Path
from .typing import StrPath
from .utils import freeze, urlparser, loader
from .models.ipk import InfiniPackage
from .exceptions import FileTypeMismatch, TomlLoadFailed, FileNotFoundError
from .const import INDEX, HOME
from .logging import info, success


def new(dist_path: StrPath, echo: bool = False) -> None:
    ...


def build(source_path: StrPath, echo: bool = False) -> None:
    info("检查构建环境...", echo)
    try:
        ipk = InfiniPackage(source_path)
        info(f"包[{ipk.name}]构建环境载入完毕.", echo)
    except TomlLoadFailed as error:
        error(f"环境存在异常: {error}", echo)
        return
    freeze.build_ipk(ipk)


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
    index = index if index else INDEX

    if uri.isalpha():
        ...
    elif urlparser.is_valid_url(uri):
        filename = uri.rstrip("/").split("/")[-1]
        ipk = loader.load(
            "temp",
            uri.rstrip("/").rsplit("/")[0],
            filename,
        )
    else:
        info(f"检定给定的 URI 地址[{uri}]为本地路径.", echo)
        path = Path(uri).resolve()
        if not path.exists():
            raise FileNotFoundError("给定的 URI 路径不存在!")

        if uri.endswith(".ipk"):
            info("安装中...", echo)
            ipk = extract(Path(uri).resolve(), HOME, echo)
        else:
            raise FileTypeMismatch("文件类型与预期[.ipk]不匹配.")

    success(f"包[{ipk.name}]成功安装在[{ipk.source_path}].", echo)


def uninstall(ipk: str | InfiniPackage):
    ...
