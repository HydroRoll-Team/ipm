from pathlib import Path
from .typing import StrPath
from .utils import freeze, urlparser, loader
from .models.ipk import InfiniPackage, InfiniFrozenPackage
from .exceptions import FileTypeMismatch, TomlLoadFailed, FileNotFoundError
from .const import INDEX, SRC_HOME
from .logging import info, success, warning, error

import toml


def init(source_path: StrPath, force: bool = False, echo: bool = False) -> None:
    source_path = Path(source_path).resolve()
    if (toml_path := (source_path / "infini.toml")).exists() and not force:
        warning(f"无法在已经初始化的地址重新初始化, 如果你的确希望重新初始化, 请使用[ipm init --force].", echo)

    toml_file = toml_path.open("w", encoding="utf-8")
    toml.dump(
        {
            "infini": {
                "name": source_path.name,
                "version": "0.1.0",
                "description": "COC 规则包",
                "license": "MIT",
            },
            "requirements": {},
            "dependencies": {},
        },
        toml_file,
    )
    toml_file.close()

    (source_path / "src").mkdir(parents=True, exist_ok=True)
    (source_path / "src" / "__init__.py").write_text(
        "# Initialized `__init__.py` generated by ipm."
    )


def new(dist_path: StrPath, echo: bool = False) -> None:
    info("初始化环境中...")
    path = Path(dist_path).resolve()
    if path.exists():
        return warning(f"路径[{path}]已经存在.", echo)
    path.mkdir(parents=True, exist_ok=True)
    return init(path, echo=echo)


def build(source_path: StrPath, echo: bool = False) -> InfiniFrozenPackage:
    info("检查构建环境...", echo)
    try:
        ipk = InfiniPackage(source_path)
        info(f"包[{ipk.name}]构建环境载入完毕.", echo)
    except TomlLoadFailed as e:
        return error(f"环境存在异常: {e}", echo)
    return freeze.build_ipk(ipk, echo)


def extract(
    source_path: StrPath, dist_path: StrPath | None = None, echo: bool = False
) -> InfiniPackage:
    dist_path = (
        Path(dist_path).resolve() if dist_path else Path(source_path).resolve().parent
    )
    return freeze.extract_ipk(source_path, dist_path, echo)


def install(uri: str, index: str = "", echo: bool = False) -> None:
    info("正在初始化 IPM 环境...", echo)

    SRC_HOME.mkdir(parents=True, exist_ok=True)
    index = index or INDEX

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
            ipk = extract(Path(uri).resolve(), SRC_HOME, echo)
        else:
            raise FileTypeMismatch("文件类型与预期[.ipk]不匹配.")

    success(f"包[{ipk.name}]成功安装在[{ipk.source_path}].", echo)


def uninstall(ipk: str | InfiniPackage):
    ...
