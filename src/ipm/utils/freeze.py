from pathlib import Path
from ..exceptions import FileNotFoundError, VerifyFailed
from ..models.ipk import InfiniPackage, InfiniFrozenPackage
from ..typing import StrPath
from ..logging import logger, info, success
from .hash import ifp_hash, ifp_verify
from . import _freeze

import tempfile
import shutil


def build_ipk(ipk: InfiniPackage) -> InfiniFrozenPackage:
    build_dir = ipk.source_path / ".build"
    src_path = ipk.source_path / "src"
    dist_path = ipk.source_path / "dist"
    ifp_path = dist_path / ipk.default_name

    if not ipk.source_path.exists():
        raise FileNotFoundError(f"文件或文件夹[{ipk.source_path.resolve()}]不存在!")
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)

    dist_path.mkdir(parents=True, exist_ok=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(src_path, build_dir / "src")
    shutil.copy2(ipk.source_path / "infini.toml", build_dir / "infini.toml")

    _freeze.create_tar_gz(
        str(build_dir),
        str(ifp_path),
    )

    (dist_path / ipk.hash_name).write_bytes(ifp_hash(ifp_path))

    return InfiniFrozenPackage(source_path=ifp_path, **{"name": ipk.name})


def extract_ipk(
    source_path: StrPath, dist_path: str | Path, echo: bool = False
) -> InfiniPackage:
    ifp_path = Path(source_path).resolve()
    dist_path = Path(dist_path).resolve()
    hash_path = ifp_path.parent / (ifp_path.name + ".hash")

    if not hash_path.exists():
        raise VerifyFailed("哈希文件不存在!")

    if not ifp_verify(ifp_path, hash_path.read_bytes()):
        raise VerifyFailed("文件完整性验证失败!")

    temp_dir = tempfile.TemporaryDirectory()

    temp_path = Path(temp_dir.name).resolve() / "ifp"
    info(f"创建临时目录[{temp_dir}], 开始解压...", echo)
    _freeze.extract_tar_gz(str(ifp_path), str(temp_path))
    temp_pkg = InfiniPackage(temp_path)
    dist_pkg_path = dist_path / temp_pkg.name
    success(f"包[{temp_pkg.name}]解压完成.", echo)

    if dist_pkg_path.exists():
        info("目标路径已存在, 清理旧文件...", echo)
        try:
            shutil.rmtree(dist_pkg_path)
        except Exception as error:
            logger.exception(error) if echo else logger.error(error)
        success("旧规则包清理完毕.", echo)

    info(f"迁移文件至安装目录中...", echo)
    shutil.move(temp_path, dist_pkg_path)
    info(f"任务完成, 开始清理临时文件...", echo)
    temp_dir.cleanup()
    info(f"临时文件清理完毕.", echo)
    return InfiniPackage(dist_pkg_path)
