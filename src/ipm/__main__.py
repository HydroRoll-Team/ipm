from pathlib import Path
from ipm import api
from ipm.exceptions import IPMException
from ipm.logging import status, error, tada

import typer

status.start()
main = typer.Typer(
    name="ipm", help="Infini 包管理器", no_args_is_help=True, add_completion=False
)


@main.command()
def lock():
    """从项目文件构建锁文件"""
    try:
        if api.lock(".", echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def check():
    """检查 Infini 项目并创建项目锁"""
    try:
        if api.check(".", echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def tag(tag: str = typer.Argument(help="版本号标签")):
    """设置规则包版本号"""
    try:
        if api.tag(Path.cwd(), tag, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def extract(
    package: str = typer.Argument(help="Infini 项目路径"),
    dist: str = typer.Option(".", help="特定的解压路径"),
):
    """解压缩 Infini 包"""
    try:
        if api.extract(package, dist, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def init(force: bool = typer.Option(None, "--force", "-f", help="强制初始化")):
    """初始化一个 Infini 项目"""
    try:
        if api.init(".", force, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def new(package: str = typer.Argument(help="Infini 项目路径")):
    """新建一个 Infini 项目"""
    try:
        if api.new(package, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def build(package: str = typer.Argument(".", help="Infini 项目路径")):
    """打包 Infini 规则包"""
    try:
        if api.build(package, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


yggdrasil = typer.Typer(
    name="yggdrasil",
    help="Infini 包世界树管理",
    no_args_is_help=True,
    add_completion=False,
)


@yggdrasil.command("add")
def yggdrasil_add(
    name: str = typer.Argument(help="世界树名称"),
    index: str = typer.Argument(help="世界树地址"),
):
    """新增世界树地址"""
    try:
        if api.yggdrasil_add(Path.cwd(), name, index, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@yggdrasil.command("remove")
def yggdrasil_remove(
    name: str = typer.Argument(help="世界树名称"),
):
    """移除世界树地址"""
    try:
        if api.yggdrasil_remove(Path.cwd(), name, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def require(
    name: str = typer.Argument(help="Infini 包名"),
    path: str = typer.Option(None, help="Infini 包本地路径"),
    yggdrasil: str = typer.Option(None, help="世界树服务器名称"),
    index: str = typer.Option(None, help="世界树服务器地址"),
):
    """新增规则包依赖"""
    try:
        if api.require(
            Path.cwd(),
            name,
            path=path,
            yggdrasil=yggdrasil,
            index=index,
            echo=True,
        ):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def unrequire(name: str = typer.Argument(help="Infini 包名")):
    """删除规则包依赖"""
    try:
        if api.unrequire(Path.cwd(), name, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def add(name: str = typer.Argument(help="Infini 包名")):
    """新增环境依赖"""
    try:
        if api.add(Path.cwd(), name, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def remove(name: str = typer.Argument(help="Infini 包名")):
    """删除环境依赖"""
    try:
        if api.remove(Path.cwd(), name, echo=True):
            tada()
    except IPMException as err:
        error(str(err), echo=True)
    finally:
        status.stop()


@main.command()
def update():
    """更新 Infini 依赖"""
    raise NotImplementedError


main.add_typer(yggdrasil)

if __name__ == "__main__":
    main()
