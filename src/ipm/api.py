from pathlib import Path
from .typing import StrPath
from .utils import freeze, urlparser, loader
from .exceptions import FileTypeMismatch, TomlLoadFailed, FileNotFoundError
from .const import INDEX, STORAGE, SRC_HOME
from .logging import info, success, warning, error
from .models.ipk import InfiniProject, InfiniFrozenPackage
from .models.lock import PackageLock
from .models.index import Yggdrasil

import toml
import shutil


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
        ipk = InfiniProject(source_path)
        info(f"包[{ipk.name}]构建环境载入完毕.", echo)
    except TomlLoadFailed as e:
        return error(f"环境存在异常: {e}", echo)
    return freeze.build_ipk(ipk, echo)


def extract(
    source_path: StrPath, dist_path: StrPath | None = None, echo: bool = False
) -> InfiniProject:
    dist_path = (
        Path(dist_path).resolve() if dist_path else Path(source_path).resolve().parent
    )
    return freeze.extract_ipk(source_path, dist_path, echo)


def install(uri: str, index: str = "", echo: bool = False) -> None:
    info("正在初始化 IPM 环境...", echo)

    SRC_HOME.mkdir(parents=True, exist_ok=True)
    index = index or INDEX
    lock = PackageLock()

    if uri.isalpha():
        yggdrasil = Yggdrasil(index)
        if not lock.get_index(index):
            yggdrasil.sync()
            lock.add_index(index, yggdrasil.host, yggdrasil.uuid, dump=True)

        if not (remote_ifp := yggdrasil.get(uri)):  # TODO 特定版本的捕获
            return warning(f"未能在世界树[{yggdrasil.index}]中搜寻到规则包[{uri}].", echo)

        ifp = loader.load_from_remote(
            uri,
            baseurl=index + remote_ifp["name"],
            filename=remote_ifp["storage"],
            echo=echo,
        )
    elif urlparser.is_valid_url(uri):
        info(f"检定给定的 URI 地址[{uri}]为远程路径.", echo)
        filename = uri.rstrip("/").rpartition("/")[-1]
        ifp = loader.load_from_remote(
            "temp",
            uri.rstrip("/").rpartition("/")[0],
            filename,
            echo=echo,
        )
    else:
        info(f"检定给定的 URI 地址[{uri}]为本地路径.", echo)
        path = Path(uri).resolve()
        if not path.exists():
            raise FileNotFoundError("给定的 URI 路径不存在!")

        if uri.endswith(".ipk"):
            ifp = loader.load_from_local(path)
        else:
            raise FileTypeMismatch("文件类型与预期[.ipk]不匹配.")

    if lock.has_package(ifp.name):
        raise  # TODO

    info(f"开始安装[{ifp.name}]中...", echo)
    ipk = extract(STORAGE / ifp.name / ifp.default_name, SRC_HOME, echo)
    info("正在处理全局包锁...", echo)
    if not lock.has_storage(ifp.name):
        lock.add_storage(ifp, dump=True)
    lock.add_package(ipk, dump=True)
    info("全局锁已处理完毕.", echo)

    success(f"包[{ipk.name}]成功安装在[{ipk.source_path}].", echo)


def uninstall(name: str, confirm: bool = False, echo: bool = False) -> None:
    lock = PackageLock()
    path = SRC_HOME / name.strip()

    if not (install_info := lock.get_package(name)):
        return warning(f"由于[{name}]未被安装, 故忽略卸载操作.", echo)

    info(f"发现已经安装的[{name}]版本[{install_info['version']}]:", echo)
    info(f"  将会清理: {path}", echo)
    confirm: bool = (
        True
        if (input("你确定要继续 (Y/n) ").upper() in ("", "Y") if not confirm else confirm)
        else False
    )
    if confirm:
        shutil.rmtree(SRC_HOME / name, ignore_errors=True)
    else:
        return info("忽略.", echo)

    lock.remove_package(name, dump=True)
    success(f"规则包[{name}]卸载完成!", echo)
