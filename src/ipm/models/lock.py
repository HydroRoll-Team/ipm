from pathlib import Path
from abc import ABCMeta
from . import ipk
from ..typing import Dict, List, StrPath, Any
from ..const import IPM_PATH, ATTENSION
from ..exceptions import SyntaxError

import toml


class IpmLock(metaclass=ABCMeta):
    metadata: Dict[str, str]
    packages: List[Dict[str, Any]]
    source_path: Path

    def __init__(self, source_path: StrPath = IPM_PATH / "infini.lock") -> None:
        IPM_PATH.mkdir(parents=True, exist_ok=True)
        self.source_path = source_path
        self.load()

    def load(self):
        if not self.source_path.exists():
            self.metadata = {}
            self.packages = []
            source_file = self.source_path.open("w", encoding="utf-8")
            source_file.write(ATTENSION + toml.dumps(self.dumps()))
            source_file.close()
        else:
            loaded_data = toml.load(self.source_path.open("r", encoding="utf-8"))
            self.metadata = (
                loaded_data["metadata"] if "metadata" in loaded_data.keys() else {}
            )
            self.packages = (
                loaded_data["packages"] if "packages" in loaded_data.keys() else []
            )

    def dumps(self) -> dict:
        return {"metadata": self.metadata, "packages": self.packages}

    def dump(self) -> str:
        data_to_dump = ATTENSION + toml.dumps(self.dumps())
        source_file = self.source_path.open("w", encoding="utf-8")
        source_file.write(data_to_dump)
        source_file.close()


class PackageLock(IpmLock):
    """全局包锁"""

    def __init__(self) -> None:
        super().__init__()

    def add(self, ifp: "ipk.InfiniFrozenPackage", dump: bool = False) -> str:
        self.packages.append(
            {
                "name": ifp.name,
                "version": ifp.version,
                "hash": ifp.hash,
            }
        )
        return self.dump() if dump else ""

    def remove(self, name: str, dump: bool = False) -> str:
        name = name.strip()
        for package in self.packages:
            if "name" not in package.keys():
                raise SyntaxError("异常的锁文件!")
            if package["name"] == name:
                self.packages.remove(package)
                break
        return self.dump() if dump else ""

    def get_ipk(self, name: str) -> dict | None:
        name = name.strip()
        for package in self.packages:
            if package["name"] == name:
                return package
        return None

    def has_ipk(self, name: str) -> bool:
        name = name.strip()
        for package in self.packages:
            if package["name"] == name:
                return True
        return False


class ProjectLock:
    ...
