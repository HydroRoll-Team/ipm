from pathlib import Path
from ..exceptions import FileNotFoundError, VerifyFailed
from ..models.ipk import InfiniProject, InfiniFrozenPackage
from ..typing import StrPath
from ..logging import update, info, success, error
from .hash import ifp_hash, ifp_verify
from . import _freeze

import tempfile
import shutil


def build_ipk(ipk: InfiniProject, echo: bool = False) -> InfiniFrozenPackage:
    update("构建开发环境...", echo)
    build_dir = ipk.source_path / "build"
    src_path = ipk.source_path / "src"
    dist_path = ipk.source_path / "dist"
    ifp_path = dist_path / ipk.default_name

    if not ipk.source_path.exists():
        raise FileNotFoundError(f"文件或文件夹 [blue]{ipk.source_path.resolve()}[/blue]]不存在!")
    if build_dir.exists():
        update("清理构建环境...")
        shutil.rmtree(build_dir, ignore_errors=True)
        success("构建环境清理完毕.")

    dist_path.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)
    success("开发环境构建完毕.", echo)

    update("复制工程文件...", echo)
    shutil.copytree(src_path, build_dir / "src")
    shutil.copy2(ipk.source_path / "infini.toml", build_dir / "infini.toml")
    success("工程文件复制完毕.", echo)

    update("打包 [bold green]ipk[/bold green]文件...", echo)
    _freeze.create_tar_gz(
        str(build_dir),
        str(ifp_path),
    )
    success(f"打包文件已存至 [blue]{ifp_path}[/blue].", echo)

    update("创建 SHA256 验证文件...", echo)
    hash_bytes = ifp_hash(ifp_path)
    info(f"文件 SHA256 值为 [purple]{hash_bytes.hex()}[/purple].", echo)

    (dist_path / ipk.hash_name).write_bytes(hash_bytes)
    success(
        f"包 [bold green]{ipk.name}[/bold green] [yellow]{ipk.version}[/yellow] 构建成功.",
        echo,
    )

    return InfiniFrozenPackage(source_path=ifp_path, **{"name": ipk.name})


def extract_ipk(
    source_path: StrPath, dist_path: StrPath, echo: bool = False
) -> InfiniProject:
    ifp_path = Path(source_path).resolve()
    dist_path = Path(dist_path).resolve()
    hash_path = ifp_path.parent / (ifp_path.name + ".hash")

    if not hash_path.exists():
        raise VerifyFailed(f"哈希文件 [blue]{hash_path}[/blue] 不存在!")

    update("文件校验...")
    if not ifp_verify(ifp_path, hash_path.read_bytes()):
        raise VerifyFailed("文件完整性验证失败!")
    success("文件校验成功.")

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name).resolve() / "ifp"
    info(f"创建临时目录 [blue]{temp_dir}[/blue].")

    update(f"解压 [blue]{ifp_path}[/blue]...", echo)
    _freeze.extract_tar_gz(str(ifp_path), str(temp_path))
    temp_pkg = InfiniProject(temp_path)
    dist_pkg_path = dist_path / temp_pkg.name
    success(
        f"[bold green]{temp_pkg.name}[/bold green] [yellow]{temp_pkg.version}[/yellow] 已解压至缓存目录.",
        echo,
    )

    if dist_pkg_path.exists():
        update("目标路径已存在, 清理旧文件...", echo)
        try:
            shutil.rmtree(dist_pkg_path)
        except Exception as err:
            return error(err)
        success("旧规则包项目文件清理完毕.", echo)

    update(f"迁移文件至目标目录...", echo)
    shutil.move(temp_path, dist_pkg_path)
    success(f"文件已迁移至 [blue]{dist_pkg_path}[/blue].", echo)

    update(f"清理临时文件...", echo)
    temp_dir.cleanup()
    success(f"临时文件清理完毕.", echo)
    return InfiniProject(dist_pkg_path)
