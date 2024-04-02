from datetime import datetime
from pathlib import Path
from distlib.version import SemanticVersion
from typing import Optional

from ipm.const import INDEX, VUE_CODE
from ipm.models.lock import PackageLock, ProjectLock
from ipm.project.env import new_virtualenv
from ipm.project.toml_file import (
    add_yggdrasil,
    init_infini,
    init_pyproject,
    remove_yggdrasil,
)
from ipm.typing import StrPath
from ipm.utils import freeze, loader
from ipm.utils.git import get_user_name_email, git_init, git_tag
from ipm.logging import confirm, status, statusup, info, success, warning, error, ask
from ipm.exceptions import (
    EnvironmentError,
    ProjectError,
    TomlLoadFailed,
    FileNotFoundError,
    NameError,
    RuntimeError,
)
from ipm.models.ipk import InfiniProject
from ipm.models.index import Yggdrasil

from infini.loader import Loader

import shutil
import sys
import re
import importlib
import subprocess
import tomlkit
import json


def lock(target_path: StrPath, echo: bool = False) -> bool:
    info("生成项目锁...", echo)

    statusup("检查环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    success("环境检查完毕.", echo)

    statusup("写入依赖锁文件...", echo)
    lock = ProjectLock.init_from_project(project)
    lock.dump()
    success("项目依赖锁写入完成.", echo)
    return True


def check(target_path: StrPath, echo: bool = False) -> bool:
    info("检查项目环境...", echo)
    statusup("检查基础环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    success("环境检查完毕.", echo)

    statusup("同步世界树中...", echo)
    global_lock = PackageLock()
    for index in project.yggdrasils.values():
        statusup(f"同步世界树: [green]{index}[/]...", echo)
        if not (yggdrasil := global_lock.get_yggdrasil_by_index(index)):
            Yggdrasil.init(index)
        else:
            yggdrasil.sync()
        success(f"世界树 [green]{index}[/] 同步完毕.", echo)

    if not lock(target_path, echo=echo):
        return False

    return True


def tag(target_path: StrPath, tag: str, echo: bool = False):
    info(f"更新规则包版本号为: [bold green]{tag}[/]", echo)
    tag = tag.lstrip("v")

    statusup("检查环境中...", echo)
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
        statusup("处理 Git 标签中...", echo)
        git_tag(toml_path.parent, tag)
        success(f"标签 [bold green]{tag}[/] 已写入.", echo)

    return True


def init(target_path: StrPath, force: bool = False, echo: bool = False) -> bool:
    info("初始化规则包...", echo)
    statusup("检查环境...", echo)
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

    standalone = confirm("对项目进行分发?", default=True) if echo else True
    init_git = confirm("初始化 Git 仓库?", default=True) if echo else True
    init_virtualenv = confirm("创建虚拟环境?", default=True) if echo else False
    sync_now = confirm("立刻同步环境?", default=True) if echo else False

    status.start()
    statusup("构建环境中...", echo)

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

    if sync_now:
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

    statusup("检查环境...", echo)
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


def build(target_path: StrPath, echo: bool = False) -> bool:
    info("构建规则包...", echo)
    statusup("检查构建环境...", echo)

    if not (Path(target_path).resolve() / "infini.toml").exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )

    try:
        ipk = InfiniProject(target_path)
    except TomlLoadFailed as e:
        error(f"环境存在异常: {e}", echo)
        return False

    update("开始构建规则包...", echo)
    ifp = freeze.build_ipk(ipk)
    success(f"文件 SHA256 值为 [purple]{ifp.hash}[/purple].", echo)
    success(
        f"包 [bold green]{ifp.name}[/bold green] [yellow]{ifp.version}[/yellow] 构建成功.",
        echo,
    )
    return True


def extract(
    source_path: StrPath,
    hash: Optional[str] = None,
    dist_path: Optional[StrPath] = None,
    echo: bool = False,
) -> bool:
    info("解压缩规则包...", echo)
    dist_path = (
        Path(dist_path).resolve() if dist_path else Path(source_path).resolve().parent
    )
    freeze.extract_ipk(source_path, dist_path, hash=hash)
    return True


def yggdrasil_add(
    target_path: StrPath, name: str, index: str, echo: bool = False
) -> bool:
    info(f"新增世界树: [bold green]{name}[/]", echo)
    statusup("检查环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    success("环境检查完毕.", echo)
    statusup("同步世界树中...", echo)
    Yggdrasil.init(index)
    add_yggdrasil(toml_path, name, index)
    success("更改均已写入文件.", echo)
    return True


def yggdrasil_remove(target_path: StrPath, name: str, echo: bool = False) -> bool:
    info(f"新增世界树: [bold green]{name}[/]", echo)
    statusup("检查环境中...", echo)
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
    statusup("检查环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    global_lock = PackageLock()
    success("环境检查完毕.", echo)

    statusup("检查世界树中...", echo)
    ygd = (
        Yggdrasil.init(index or INDEX)
        if not global_lock.has_index(index or INDEX)
        else global_lock.get_yggdrasil_by_index(index or INDEX)
    )
    if not ygd:
        raise ProjectError("世界树检查失败！")

    splited_name = name.split("==")  # TODO 支持 >= <= > < 标识
    name = splited_name[0]

    if len(splited_name) > 1:
        version = splited_name[1]
    else:
        version = ygd.get_lastest_version(name)

    if not version:
        raise ProjectError(f"无法找到一个匹配 [red]{name}[/] 的版本。")

    check(target_path, echo=echo)

    statusup("处理 Infini 项目依赖锁...", echo)
    project.require(
        name,
        version=version,
        path=path,
        yggdrasil=yggdrasil,
        index=index,
    )
    project.dump()
    success("项目文件写入完成.", echo)

    install(target_path, echo=echo)

    success("规则包依赖新增完成.", echo)
    return True


def unrequire(target_path: StrPath, name: str, echo: bool = False):
    info(f"删除规则包依赖: [bold green]{name}[/bold green]", echo)
    statusup("处理 Infini 项目依赖锁...", echo)
    project = InfiniProject()
    project.unrequire(name)
    project.dump()
    success("项目文件写入完成.", echo)
    check(target_path, echo=echo)
    success("规则包依赖删除完成.", echo)
    return True


def add(target_path, name: str, echo: bool = False) -> bool:
    info(f"新增环境依赖项: [bold green]{name}[/bold green]", echo)
    statusup("检查环境中...", echo)
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

    statusup("安装依赖中...", echo)

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
    statusup("检查环境中...", echo)
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
    info(f"同步依赖环境...", echo)
    statusup("检查环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    lock = ProjectLock(target_path)
    if not lock._lock_path.exists():
        raise FileNotFoundError(
            "文件[red]infini.lock[/]不存在！请先执行[bold red]`.ipm lock`[/]生成锁文件！"
        )
    global_lock = PackageLock()
    if not shutil.which("pdm"):
        raise EnvironmentError(
            "IPM 未能在环境中找到 [bold green]PDM[/] 安装, 请确保 PDM 在环境中被正确安装. "
            "你可以使用`[bold green]pipx install pdm[/]`来安装此包管理器."
        )
    success("环境检查完毕.", echo)

    statusup("同步依赖环境中...", echo)
    for requirement in lock.requirements:
        if not requirement.is_local():
            if global_lock.has_frozen_package(requirement.name, requirement.version):
                continue
            statusup(
                f"下载 [bold green]{requirement.name}[/] [bold yellow]{requirement.version}[/]...",
                echo,
            )
            ifp = loader.load_from_remote(
                requirement.name,
                requirement.yggdrasil.index.rstrip("/") + (requirement.url or ""),
                requirement.hash or "",
            )
            global_lock.add_frozen_package(
                requirement.name,
                requirement.version,
                requirement.hash or "",
                requirement.yggdrasil.index,
                str(ifp._source_path),
            )
            success(
                f"[bold green]{requirement.name} {requirement.version}[/] 安装完成！",
                echo,
            )
    statusup("同步依赖环境中...", echo)
    dependencies = []
    for name, version in project.dependencies.items():
        if version == "*":
            dependencies.append(name)
        else:
            dependencies.append(f"{name}{version}")
    if dependencies:
        statusup(
            "安装依赖: "
            + ", ".join(
                ["[bold green]" + dependency + "[/]" for dependency in dependencies]
            )
            + "...",
            echo,
        )
        if (
            result := subprocess.run(
                ["pdm", "add", *dependencies],
                cwd=target_path,
                capture_output=True,
                text=True,
            )
        ).returncode != 0:
            error(result.stderr.strip("\n"), echo)
            raise RuntimeError("PDM 异常退出, 指令忽略.")
        success("依赖安装完成！", echo)
    else:
        success("未检测到任何依赖，忽略任务。", echo)

    success("依赖环境同步完毕！", echo)
    return True


def install(target_path: StrPath, echo: bool = False) -> bool:
    info("安装规则包环境中...", echo)
    statusup("检查环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    project = InfiniProject(toml_path.parent)
    global_lock = PackageLock()
    if not shutil.which("pdm"):
        raise EnvironmentError(
            "IPM 未能在环境中找到 [bold green]PDM[/] 安装, 请确保 PDM 在环境中被正确安装. "
            "你可以使用`[bold green]pipx install pdm[/]`来安装此包管理器."
        )
    success("环境检查完毕.", echo)

    check(target_path, echo)
    sync(target_path, echo)

    statusup("安装依赖中...", echo)
    lock = ProjectLock(target_path)
    packages_path = toml_path.parent.joinpath("packages")
    packages_path.mkdir(parents=True, exist_ok=True)
    ProjectLock.init_from_project(project, packages_path)
    for requirement in lock.requirements:
        try:
            prj = InfiniProject(packages_path.joinpath(requirement.name))
            if prj.version >= requirement.version:
                continue
        except:
            pass
        path = global_lock.get_frozen_package_path(
            requirement.name, requirement.version
        )
        if not path:
            raise ProjectError(
                f"无法找到依赖 [red]{requirement.name} {requirement.version}[/]."
            )
        prj = freeze.extract_ipk(path, packages_path, hash=requirement.hash)
        shutil.move(
            str(prj._source_path), str(prj._source_path.parent.joinpath(prj.name))
        )

    return True


def doc(
    target_path: StrPath,
    type: str,
    dist: StrPath,
    submodule: bool = False,
    echo: bool = False,
) -> bool:
    info("构建项目文档...", echo)
    if type.lower() != "vue":
        raise EnvironmentError("目前仅支持 Vue 部署！")

    statusup("准备环境中...", echo)
    if not (toml_path := Path(target_path).joinpath("infini.toml")).exists():
        raise FileNotFoundError(
            f"文件 [green]infini.toml[/green] 尚未被初始化, 你可以使用[bold green]`ipm init`[/bold green]来初始化项目."
        )
    if not submodule and not shutil.which("npm"):
        raise EnvironmentError(
            "IPM 未能在环境中找到 [bold green]Node.js[/] 安装, 请确保 NPM 在环境中被正确安装. "
            "你可以前往`[green]https://nodejs.org/en/download[/]`来安装此包管理器."
        )
    project = InfiniProject(toml_path.parent)
    loader = Loader()
    loader.close()
    if toml_path.parent.joinpath("src", "__init__.py").exists():
        sys.path.append(str(target_path))
        module = importlib.import_module("src")
    else:
        sys.path.append(str(toml_path.parent.joinpath("src")))
        module = importlib.import_module(project.name)
    loader.load_from_module(module)
    dist_path = Path(dist).resolve()
    dist_path.mkdir(parents=True, exist_ok=True)
    success("环境准备完毕.", echo)

    if submodule:
        docs = json.loads(loader.doc.dumps())
        docs["metadata"] = project.metadata
        docs["readme"] = project.readme
        docs["doc_create_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dist_path.joinpath("index.json").write_text(json.dumps(docs), encoding="utf-8")
        dist_path.joinpath("index.vue").write_text(VUE_CODE, encoding="utf-8")
    else:
        raise ProjectError("未被支持。")
    return True


def update(target_path: StrPath, echo: bool = False) -> bool:
    info("更新依赖环境...", echo)
    statusup("检查环境中...", echo)
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

    statusup("更新依赖中...", echo)
    for requirement in project.requirements:
        lastest_version = requirement.yggdrasil.get_lastest_version(requirement.name)
        if not lastest_version:
            raise ProjectError(f"包 [bold red]{requirement.name}[/] 被从世界树燃烧了。")
        if SemanticVersion(lastest_version) > SemanticVersion(requirement.version):
            project.require(requirement.name, version=lastest_version)
            success(
                f"将 [bold green]{requirement.version}[/] 升级到 [bold yellow]{lastest_version}[/].",
                echo,
            )

    check(target_path, echo)
    sync(target_path, echo)

    install(target_path, echo)
    return True
