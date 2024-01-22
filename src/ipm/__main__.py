from . import api
from .exceptions import IpmException
from .logging import logger
import typer

main = typer.Typer(
    name="ipm", help="Infini 包管理器", no_args_is_help=True, add_completion=False
)


@main.command()
def install(
    uri: str = typer.Argument(help="Infini 包的统一资源标识符"),
    index: str = typer.Option(None, help="IPM 包服务器"),
    upgrade: bool = typer.Option(False, "--upgrade", "-u", help="更新 Infini 包", is_flag=True),
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


if __name__ == "__main__":
    main()
