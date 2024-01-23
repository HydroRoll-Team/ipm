from . import api
from .exceptions import IpmException
from .logging import logger
import typer

main = typer.Typer(
    name="ipm", help="Infini 包管理器", no_args_is_help=True, add_completion=False
)


@main.command()
def check():
    """分析 Infini 项目并创建项目锁"""
    try:
        api.check(".")
    except IpmException as error:
        logger.error(error)


@main.command()
def install(
    uri: str = typer.Argument(help="Infini 包的统一资源标识符"),
    index: str = typer.Option(None, help="世界树服务器地址"),
    upgrade: bool = typer.Option(False, "--upgrade", "-u", help="更新 Infini 包"),
    force: bool = typer.Option(False, "--force", "-f", help="强制安装"),
):
    """安装一个 Infini 规则包到此计算机"""
    try:
        api.install(uri, index, upgrade=upgrade, force=force, echo=True)
    except IpmException as error:
        logger.error(error)


@main.command()
def extract(
    package: str = typer.Argument(help="Infini 项目路径"),
    dist: str = typer.Option(".", help="特定的解压路径"),
):
    """解压缩 Infini 包"""
    try:
        api.extract(package, dist, echo=True)
    except IpmException as error:
        logger.error(error)


@main.command()
def init(force: bool = typer.Option(None, "--force", "-f", help="强制初始化")):
    """初始化一个 Infini 项目"""
    try:
        api.init(".", force, echo=True)
    except IpmException as error:
        logger.error(error)


@main.command()
def new(package: str = typer.Argument(help="Infini 项目路径")):
    """新建一个 Infini 项目"""
    try:
        api.new(package, echo=True)
    except IpmException as error:
        logger.error(error)


@main.command()
def build(package: str = typer.Argument(".", help="Infini 项目路径")):
    """打包 Infini 规则包"""
    try:
        api.build(package, echo=True)
    except IpmException as error:
        logger.error(error)


@main.command()
def uninstall(package: str = typer.Argument(help="Infini 项目路径")):
    """卸载 Infini 规则包"""
    try:
        api.uninstall(package, echo=True)
    except IpmException as error:
        logger.error(error)


@main.command()
def require(
    name: str = typer.Argument(help="Infini 包名"),
    index: str = typer.Option(None, help="世界树服务器地址"),
):
    """新增规则包依赖"""
    try:
        api.require(name, index, echo=True)
    except IpmException as error:
        logger.error(error)


@main.command()
def unrequire(name: str = typer.Argument(help="Infini 包名")):
    """删除规则包依赖"""
    try:
        api.unrequire(name)
    except IpmException as error:
        logger.error(error)


@main.command()
def add(
    name: str = typer.Argument(help="Infini 包名"),
    index: str = typer.Option(None, help="世界树服务器地址"),
):
    """新增环境依赖"""
    try:
        api.add(name, index=index)
    except IpmException as error:
        logger.error(error)


@main.command()
def remove(name: str = typer.Argument(help="Infini 包名")):
    """删除环境依赖"""
    try:
        api.remove(name)
    except IpmException as error:
        logger.error(error)


# TODO
@main.command()
def collect():
    ...


# TODO
@main.command()
def update():
    ...


if __name__ == "__main__":
    main()
