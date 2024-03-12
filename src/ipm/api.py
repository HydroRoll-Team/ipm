from pathlib import Path
from typing import Optional

from ipm.models.lock import ProjectLock
from ipm.project.env import new_virtualenv
from ipm.project.toml_file import (
    add_yggdrasil,
    init_infini,
    init_pyproject,
    remove_yggdrasil,
)
from ipm.typing import StrPath
from ipm.utils import freeze
from ipm.utils.git import get_user_name_email, git_init, git_tag
from ipm.logging import confirm, status, update, info, success, warning, error, ask
from ipm.exceptions import (
    EnvironmentError,
    TomlLoadFailed,
    FileNotFoundError,
    NameError,
    RuntimeError,
)
from ipm.models.ipk import InfiniProject, InfiniFrozenPackage
from ipm.models.index import Yggdrasil

import shutil
import re
import subprocess
import tomlkit


def lock(target_path: StrPath, echo: bool = False) -> bool:
    info("项目环境检查...", echo)

    update("检查环境中...")
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    success("环境检查完毕.", echo)

    update("写入依赖锁文件...", echo)
    lock = ProjectLock.init_from_project(project)
    lock.dump()
    success("项目依赖锁写入完成.", echo)
    return True


def check(target_path: StrPath, echo: bool = False) -> bool:
    if not lock(target_path, echo=echo):
        return False

    update("处理环境配置中...", echo)
    warning("同步指令暂未被实装, 忽略.", echo)
    return True


def tag(target_path: StrPath, tag: str, echo: bool = False):
    info(f"更新规则包版本号为: [bold green]{tag}[/]", echo)
    tag = tag.lstrip("v")

    update("检查环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    if not (project_path := Path(target_path).joinpath("pyproject.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]pyproject.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    success("环境检查完毕.", echo)

    infini_project = tomlkit.load(toml_path.open("r", encoding="utf-8"))
    py_project = tomlkit.load(project_path.open("r", encoding="utf-8"))
    infini_project["project"]["version"] = tag  # type: ignore
    py_project["project"]["version"] = tag  # type: ignore

    toml_file = toml_path.open("w", encoding="utf-8")
    project_file = project_path.open("w", encoding="utf-8")
    tomlkit.dump(infini_project, toml_file)
    tomlkit.dump(py_project, project_file)
    toml_file.close()
    project_file.close()

    success("项目文件写入完成.", echo)

    if toml_path.parent.joinpath(".git").is_dir():
        update("处理 Git 标签中...", echo)
        git_tag(toml_path.parent, tag)
        success(f"标签 [bold green]{tag}[/] 已写入.", echo)

    return True


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
    username, email = get_user_name_email()
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

    standalone = confirm("是否为项目分发", default=True)
    init_git = confirm("初始化 Git 仓库", default=True)
    init_virtualenv = confirm(f"为 [bold green]{name}[/] 虚拟环境", default=True)

    update("构建环境中...", echo)

    init_infini(
        toml_path=toml_path,
        target_path=target_path,
        name=name,
        version=version,
        description=description,
        author_name=author_name,
        author_email=author_email,
        license=license,
        entry_file=entry_file,
        default_entries=default_entries,
    )
    init_pyproject(
        target_path=target_path,
        name=name,
        version=version,
        description=description,
        author_name=author_name,
        author_email=author_email,
        license=license,
        standalone=standalone,
    )

    if init_virtualenv:
        new_virtualenv(target_path)

    if (
        result := subprocess.run(
            ["pdm", "install"],
            cwd=target_path,
            capture_output=True,
            text=True,
        )
    ).returncode != 0:
        error(result.stderr.strip("\n"), echo)
        raise RuntimeError("PDM 异常退出, 指令忽略.")

    if init_git:
        git_init(target_path)

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

    if not init(path, echo=echo):
        return False

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
    source_path: StrPath, dist_path: Optional[StrPath] = None, echo: bool = False
) -> Optional[InfiniProject]:
    info("解压缩规则包...", echo)
    dist_path = (
        Path(dist_path).resolve() if dist_path else Path(source_path).resolve().parent
    )
    return freeze.extract_ipk(source_path, dist_path, echo)


def yggdrasil_add(
    target_path: StrPath, name: str, index: str, echo: bool = False
) -> bool:
    info(f"新增世界树: [bold green]{name}[/]", echo)
    update("检查环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    success("环境检查完毕.", echo)
    update("同步世界树中...", echo)
    yggdrasil = Yggdrasil(index)
    # yggdrasil.sync()
    warning("世界树同步模块未实装, 忽略.", echo)

    add_yggdrasil(toml_path, name, index)
    success("更改均已写入文件.", echo)
    return True


def yggdrasil_remove(target_path: StrPath, name: str, echo: bool = False) -> bool:
    info(f"新增世界树: [bold green]{name}[/]", echo)
    update("检查环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    success("环境检查完毕.", echo)
    remove_yggdrasil(project, name)
    success("更改均已写入文件.", echo)
    return True


def require(
    target_path: StrPath,
    name: str,
    *,
    path: Optional[str] = None,
    yggdrasil: Optional[str] = None,
    index: Optional[str] = None,
    echo: bool = False,
) -> bool:
    info(f"新增规则包依赖: [bold green]{name}[/bold green]", echo)
    status.start()
    status.update("检查环境中...")
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    success("环境检查完毕.", echo)

    splited_name = name.split("==")  # TODO 支持 >= <= > < 标识
    name = splited_name[0]

    if len(splited_name) > 1:
        version = splited_name[1]
    else:
        version = "*"

    status.update("处理 Infini 项目依赖锁...")
    project.require(
        name,
        version=version,
        path=path,
        yggdrasil=yggdrasil,
        index=index,
    )
    project.dump()
    success("项目文件写入完成.", echo)
    check(target_path, echo=echo)
    # sync()
    success("规则包依赖新增完成.", echo)
    return True


def unrequire(target_path: StrPath, name: str, echo: bool = False):
    info(f"删除规则包依赖: [bold green]{name}[/bold green]", echo)
    update("处理 Infini 项目依赖锁...", echo)
    project = InfiniProject()
    project.unrequire(name)
    project.dump()
    success("项目文件写入完成.", echo)
    check(target_path, echo=echo)
    success("规则包依赖删除完成.", echo)
    return True


def add(target_path, name: str, echo: bool = False) -> bool:
    info(f"新增环境依赖项: [bold green]{name}[/bold green]", echo)
    status.start()
    status.update("检查环境中...")
    if not (
        match := re.match(r"^((?:[a-zA-Z_-]|\d)+)(?:([>=<]+\d+(?:[.]\d+)*))?$", name)
    ):
        raise NameError(f"版本号 [bold red]{name}[/] 不合法.")
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    if not shutil.which("pdm"):
        raise EnvironmentError(
            "IPM 未能在环境中找到 [bold green]PDM[/] 安装, 请确保 PDM 在环境中被正确安装. "
            "你可以使用`[bold green]pipx install pdm[/]`来安装此包管理器."
        )
    success("环境检查完毕.", echo)

    status.update("安装依赖中...")

    name = match.group(1)
    version = match.group(2)
    project.add(name, version or "*")
    if (
        result := subprocess.run(
            ["pdm", "add", name],
            cwd=target_path,
            capture_output=True,
            text=True,
        )
    ).returncode != 0:
        error(result.stderr.strip("\n"), echo)
        raise RuntimeError("PDM 异常退出, 指令忽略.")

    project.dump()
    success("项目文件写入完成.", echo)
    return True


def remove(target_path: StrPath, name: str, echo: bool = False):
    info(f"删除环境依赖项: [bold green]{name}[/bold green]", echo)
    status.start()
    status.update("检查环境中...")
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    if not shutil.which("pdm"):
        raise EnvironmentError(
            "IPM 未能在环境中找到 [bold green]PDM[/] 安装, 请确保 PDM 在环境中被正确安装. "
            "你可以使用`[bold green]pipx install pdm[/]`来安装此包管理器."
        )
    success("环境检查完毕.", echo)
    project.remove(name)

    if (
        result := subprocess.run(
            ["pdm", "remove", name],
            cwd=target_path,
            capture_output=True,
            text=True,
        )
    ).returncode != 0:
        error(result.stderr.strip("\n"), echo)
        raise RuntimeError("PDM 异常退出, 指令忽略.")

    project.dump()
    success("项目文件写入完成.", echo)
    return True


def sync(target_path: StrPath, echo: bool = False) -> bool:
    ...
    return True
