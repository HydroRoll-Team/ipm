from pathlib import Path
from typing import Optional
from ipm.exceptions import FileNotFoundError, VerifyFailed
from ipm.models.ipk import InfiniProject, InfiniFrozenPackage
from ipm.typing import StrPath
from ipm.utils.hash import ifp_verify
from ipm.utils import _freeze

import tempfile
import shutil


def build_ipk(ipk: InfiniProject) -> InfiniFrozenPackage:
    arcname = f"{ipk.name}-{ipk.version}"
    build_dir = ipk._source_path.joinpath(".ipm-build")
    build_dir.joinpath(".gitignore").write_text("*\n")
    arc_dir = build_dir.joinpath(arcname)
    src_path = ipk._source_path / "src"
    dist_path = ipk._source_path / "dist"
    ifp_path = dist_path.joinpath(ipk.default_name + ".ipk")

    if not ipk._source_path.exists():
        raise FileNotFoundError(
            f"文件或文件夹 [blue]{ipk._source_path.resolve()}[/blue]]不存在!"
        )
    if build_dir.exists() or dist_path.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
        shutil.rmtree(dist_path, ignore_errors=True)

    dist_path.mkdir(parents=True, exist_ok=True)
    arc_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(src_path, arc_dir.joinpath("src"))
    shutil.copy2(ipk._source_path / "infini.toml", arc_dir / "infini.toml")
    shutil.copy2(
        ipk._source_path.joinpath("pyproject.toml"), arc_dir.joinpath("pyproject.toml")
    )
    shutil.copy2(
        ipk._source_path.joinpath(ipk.readme_file), arc_dir.joinpath(ipk.readme_file)
    )

    _freeze.create_tar_gz(
        str(build_dir),
        str(ifp_path),
    )
    shutil.copy2(ifp_path, dist_path.joinpath(ipk.default_name + ".tar.gz"))

    return InfiniFrozenPackage(ifp_path, ipk.name, version=ipk.version)


def extract_ipk(
    source_path: StrPath,
    dist_path: StrPath,
    hash: Optional[str] = None,
) -> InfiniProject:
    ifp_path = Path(source_path).resolve()
    dist_path = Path(dist_path).resolve()

    if hash and not ifp_verify(ifp_path, hash):
        raise VerifyFailed("文件完整性验证失败!")

    temp_dir = tempfile.TemporaryDirectory()
    temp_path = Path(temp_dir.name).resolve() / "ifp"

    _freeze.extract_tar_gz(str(ifp_path), str(temp_path))

    arc_path = next(temp_path.iterdir())
    temp_pkg = InfiniProject(arc_path)
    dist_pkg_path = dist_path.joinpath(temp_pkg.default_name)

    if dist_pkg_path.exists():
        shutil.rmtree(dist_pkg_path)

    shutil.move(arc_path, dist_path)

    temp_dir.cleanup()
    return InfiniProject(dist_pkg_path)
