from pathlib import Path
from typing import Optional
from ipm.project.env import new_virtualenv
from ipm.project.toml_file import add_yggdrasil, init_infini, init_pyproject
from ipm.typing import StrPath
from ipm.utils import freeze, urlparser, loader
from ipm.const import GITIGNORE, INDEX, INDEX_PATH, STORAGE, SRC_HOME
from ipm.logging import status, update, info, success, warning, error, confirm, ask
from ipm.exceptions import (
    FileTypeMismatch,
    TomlLoadFailed,
    FileNotFoundError,
    PackageExsitsError,
)
from ipm.utils.version import require_update
from ipm.models.ipk import InfiniProject, InfiniFrozenPackage

# from ipm.models.lock import PackageLock, ProjectLock
from ipm.models.index import Yggdrasil

import tomlkit
import shutil
import os
import configparser


# def check(source_path: StrPath, echo: bool = False) -> bool:
#     info("项目环境检查...", echo)

#     update("检查环境...")
#     lock = ProjectLock(
#         Path(source_path).resolve() / "infini.lock",
#         auto_load=False,
#     )
#     success("环境检查完毕.", echo)

#     update("写入依赖锁文件...", echo)
#     lock.init()
#     success("项目依赖锁写入完成.", echo)
#     return True


def init(target_path: StrPath, force: bool = False, echo: bool = False) -> bool:
    info("初始化规则包...", echo)
    update("检查环境...", echo)
    target_path = Path(target_path).resolve()
    if (toml_path := (target_path / "infini.toml")).exists() and not force:
        warning(
            f"无法在已经初始化的地址重新初始化, 如果你的确希望重新初始化, 请使用[bold red]`ipm init --force`[/bold red].",
            echo,
        )
        return False
    email = username = None
    gitconfig_path = Path.home().joinpath(".gitconfig")
    if gitconfig_path.exists():
        config = configparser.ConfigParser()
        config.read(str(gitconfig_path), encoding="utf-8")
        if "user" in config.sections():
            email = config["user"].get("email")
            username = config["user"].get("name")
    email = email or (os.getlogin() + "@example.com")
    username = username or os.getlogin()
    success("环境检查完毕.", echo)
    status.stop()

    name = ask("项目名称", default=target_path.name, echo=echo)
    version = ask("项目版本", default="0.1.0", echo=echo)
    description = ask(
        "项目简介", default=f"{target_path.name.upper()} 规则包", echo=echo
    )
    author_name = ask("作者名称", default=username, echo=echo)
    author_email = ask("作者邮箱", default=email, echo=echo)
    license = ask("开源协议", default="MIT", echo=echo)

    default_entries = ["__init__.py", f"{name}.py"]
    info("请选择你要使用的入口文件:", echo)
    for index, default_entry in enumerate(default_entries):
        info(f"[bold cyan]{index}[/bold cyan]. [green]{default_entry}[/green]", echo)
    entry_file = ask(
        "入口文件:",
        choices=[str(num) for num in range(len(default_entries))],
        default="0",
        echo=echo,
    )

    status.update("构建环境中...")
    status.start()

    init_infini(
        toml_path,
        target_path,
        name,
        version,
        description,
        author_name,
        author_email,
        license,
        entry_file,
        default_entries,
    )
    init_pyproject(
        target_path,
        name,
        version,
        description,
        author_name,
        author_email,
        license,
    )
    new_virtualenv(target_path)
    return True


def new(dist_path: StrPath, echo: bool = False) -> bool:
    info("新建规则包...", echo)

    update("检查环境...", echo)
    path = Path(dist_path).resolve()
    if path.exists():
        warning(
            f"路径 [blue]{path.relative_to(Path('.').resolve())}[/blue] 已经存在.", echo
        )
        return False
    path.mkdir(parents=True, exist_ok=True)
    success("环境检查完毕.", echo)

    init(path, echo=echo)

    success(f"规则包 [bold green]{path.name}[/bold green] 新建完成!", echo)
    return True


def build(source_path: StrPath, echo: bool = False) -> Optional[InfiniFrozenPackage]:
    info("构建规则包...", echo)
    update("检查构建环境...", echo)

    if not (Path(source_path).resolve() / "infini.toml").exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )

    try:
        ipk = InfiniProject(source_path)
    except TomlLoadFailed as e:
        return error(f"环境存在异常: {e}", echo)

    return freeze.build_ipk(ipk, echo)


def extract(
    source_path: StrPath, dist_path: StrPath | None = None, echo: bool = False
) -> Optional[InfiniProject]:
    info("解压缩规则包...", echo)
    dist_path = (
        Path(dist_path).resolve() if dist_path else Path(source_path).resolve().parent
    )
    return freeze.extract_ipk(source_path, dist_path, echo)


def yggdrasil_add(source_path: StrPath, name: str, index: str, echo: bool = False) -> bool:
    info(f"新增世界树: [bold green]{name}[/]")
    status.start()
    status.update("检查环境中...")
    if not (toml_path := Path(source_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    success("环境检查完毕.", echo)
    status.update("同步世界树中...")
    yggdrasil = Yggdrasil(index)
    yggdrasil.sync()

    add_yggdrasil(toml_path, name, index)
    success("更改均已写入文件.", echo)
    return True


# def install(
#     uri: str,
#     index: str = "",
#     upgrade: bool = False,
#     force: bool = False,
#     echo: bool = False,
# ) -> None:
#     info(f"安装规则包 [bold green]{uri}[/bold green]...", echo)

#     update("初始化 [bold green]IPM[/bold green] 环境...", echo)
#     SRC_HOME.mkdir(parents=True, exist_ok=True)
#     index = index or INDEX
#     lock = PackageLock()

#     if uri.split("==")[0].isalpha():
#         # TODO 兼容 >= <= > < 等标识符
#         splited_uri = uri.split("==")
#         name = splited_uri[0]
#         if len(splited_uri) == 1:
#             version = None
#         else:
#             version = splited_uri[1]

#         yggdrasil = Yggdrasil(index)

#         if not (lock_index := lock.get_index(index)):
#             yggdrasil.sync()
#             lock.add_index(index, yggdrasil.host, yggdrasil.uuid, dump=True)
#         else:
#             yggdrasil.init(INDEX_PATH / lock_index["uuid"])

#         if not (remote_ifp := yggdrasil.get(name, version=version)):
#             return warning(
#                 f"未能在世界树[{yggdrasil.index}]中搜寻到规则包[{uri}].", echo
#             )

#         ifp = loader.load_from_remote(
#             name,
#             baseurl=index,
#             filename=remote_ifp["source"],
#             echo=echo,
#         )
#     elif urlparser.is_valid_url(uri):
#         filename = uri.rstrip("/").rpartition("/")[-1]
#         ifp = loader.load_from_remote(
#             "temp",
#             uri.rstrip("/").rpartition("/")[0],
#             filename,
#             echo=echo,
#         )
#     else:
#         path = Path(uri).resolve()
#         update(f"检查文件 [blue]{path}[/blue]...", echo)
#         if not path.exists():
#             raise FileNotFoundError("给定的 URI 路径不存在!")

#         if uri.endswith(".ipk"):
#             ifp = loader.load_from_local(path)
#         else:
#             raise FileTypeMismatch("文件类型与预期[.ipk]不匹配.")

#     if lock.has_package(ifp.name):
#         exists_version = lock.get_package(ifp.name)["version"]
#         if require_update(exists_version, ifp.version):
#             if not upgrade:
#                 raise PackageExsitsError(
#                     f"已经安装了 [bold green]{ifp.name}[/bold green] [yellow]{exists_version}[/yellow], 使用[[blue]--upgrade[/blue]]参数进行升级."
#                 )
#             else:
#                 info(f"发现已经安装的[{ifp.name}={exists_version}], 卸载中...")
#                 uninstall(ifp.name, is_confirm=True, echo=echo)
#                 success(f"[{ifp.name}={exists_version}]卸载完成.")
#         else:
#             if not force:
#                 raise PackageExsitsError(
#                     f"已经安装了 [bold green]{ifp.name}[/bold green] [yellow]{exists_version}[/yellow], 使用[[red]--force[/red]]参数进行强制覆盖."
#                 )
#             else:
#                 info(
#                     f"发现已经安装的 [bold green]{ifp.name}[/bold green] [yellow]{exists_version}[/yellow], 卸载中..."
#                 )
#                 uninstall(ifp.name, is_confirm=True, echo=echo)
#                 success(
#                     f"[bold green]{ifp.name}[/bold green] [yellow]{exists_version}[/yellow]卸载完成..."
#                 )
#         lock.load(auto_completion=True)

#     update(
#         f"安装 [bold green]{ifp.name}[/bold green] [yellow]{ifp.version}[/yellow] 中...",
#         echo,
#     )
#     ipk = extract(
#         STORAGE / ifp.name / ifp.default_name, SRC_HOME, echo
#     )  # TODO 安装依赖规则包
#     success(
#         f"成功安装 [bold green]{ifp.name}[/bold green] [yellow]{ifp.version}[/yellow].",
#         echo,
#     )

#     update("处理全局锁...", echo)
#     if not lock.has_storage(ifp.name):
#         lock.add_storage(ifp, dump=True)
#     lock.add_package(ipk, dump=True)
#     success("全局锁已处理完毕.", echo)

#     success(f"包[{ipk.name}]成功安装在 [blue]{ipk._source_path}[/blue].", echo)


# def uninstall(name: str, is_confirm: bool = False, echo: bool = False) -> bool:
#     lock = PackageLock()
#     path = SRC_HOME / name.strip()

#     if not (install_info := lock.get_package(name)):
#         warning(
#             f"由于 [bold green]{name}[/bold green]未被安装, 故忽略卸载操作.", echo
#         )
#         return False

#     info(
#         f"发现已经安装的 [bold green]{name}[/bold green] [yellow]{install_info['version']}[/yellow].",
#         echo,
#     )
#     update(
#         f"卸载 [bold green]{name}[/bold green] [yellow]{install_info['version']}[/yellow]..."
#     )
#     warning(f"将会清理: [blue]{path}[/blue]", echo)
#     is_confirm: bool = (
#         True if (confirm("你确定要继续?") if not is_confirm else is_confirm) else False
#     )
#     if is_confirm:
#         shutil.rmtree(SRC_HOME / name, ignore_errors=True)
#     else:
#         info("忽略.", echo)
#         return False

#     lock.remove_package(name, dump=True)
#     success(
#         f"规则包 [bold green]{name}[/bold green] [yellow]{install_info['version']}[/yellow] 卸载完成!",
#         echo,
#     )
#     return True


# def require(name: str, index: str = "", echo: bool = False) -> None:
#     info(f"新增规则包依赖: [bold green]{name}[/bold green]", echo)
#     update("检查环境中...", echo)
#     pkg_lock = PackageLock()
#     lock = ProjectLock()
#     ipk = InfiniProject()
#     success("环境检查完毕.", echo)

#     splited_name = name.split("==")  # TODO 支持 >= <= > < 标识
#     name = splited_name[0]

#     if len(splited_name) > 1:
#         version = splited_name[1]
#     else:
#         version = None

#     if not pkg_lock.has_package(name):
#         info(f"检测到需要依赖的规则包[{name}]不存在, 安装中...", echo)
#         install(
#             f"name=={version}" if version else name,
#             index=index,
#             upgrade=True,
#             force=True,
#             echo=True,
#         )

#     info("处理 Infini 项目依赖锁...", echo)
#     ipk.require(name, version, dump=True)
#     lock.require(name, version, dump=True)  # TODO 使用check替代
#     success("规则包依赖新增完成.", echo)
#     return True


# def unrequire(name: str, echo: bool = False):
#     info(f"删除规则包依赖: [bold green]{name}[/bold green]", echo)
#     info("处理 Infini 项目依赖锁...", echo)
#     ipk = InfiniProject()
#     lock = ProjectLock()

#     ipk.unrequire(name, dump=True)
#     lock.unrequire(name, dump=True)
#     success("规则包依赖删除完成.", echo)
#     return True


# def add(name: str, index: str = "", echo: bool = False) -> None:
#     info("检查环境中...", echo)
#     pkg_lock = PackageLock()
#     lock = ProjectLock()
#     ipk = InfiniProject()
#     info("环境检查完毕.", echo)

#     splited_name = name.split("==")  # TODO 支持 >= <= > < 标识
#     name = splited_name[0]

#     if len(splited_name) > 1:
#         version = splited_name[1]
#     else:
#         version = None

#     if not pkg_lock.has_package(name):
#         # TODO pip 环境安装
#         ...

#     info("处理 Infini 项目依赖锁...", echo)
#     ipk.add(name, version, dump=True)
#     lock.add(name, version, dump=True)
#     success("环境依赖新增完成.", echo)


# def remove(name: str, echo: bool = False):
#     info("处理 Infini 项目依赖锁...", echo)
#     ipk = InfiniProject()
#     lock = ProjectLock()

#     ipk.remove(name, dump=True)
#     lock.remove(name, dump=True)
#     success("环境依赖删除完成.", echo)
