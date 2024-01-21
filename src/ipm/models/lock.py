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

    def __init__(self, source_path: StrPath = IPM_PATH / "inifni.lock") -> None:
        IPM_PATH.mkdir(parents=True, exist_ok=True)
        self.source_path = source_path
        self.load()

    def load(self):
        if not self.source_path.exists():
            self.source_path.write_text(ATTENSION)
            self.packages = {}
        else:
            loaded_data = toml.load(self.source_path.open("r", encoding="utf-8"))
            self.packages = loaded_data["package"]

    def dumps(self) -> dict:
        return {"metadata": self.metadata, "packages": self.packages}

    def dump(self) -> str:
        return toml.dump(self.source_path.open("w+", encoding="utf-8"))


class PackageLock(IpmLock):
    """全局包锁"""

    def __init__(self) -> None:
        super().__init__()

    def add(self, ipk: "ipk.InfiniPackage", dump: bool = False) -> str:
        self.packages.append({"name": ipk.name, "version": ipk.version})
        return self.dump() if dump else ""

    def remove(self, name: str) -> None:
        name = name.strip()
        for package in self.packages:
            if "name" not in package.keys():
                raise SyntaxError("异常的锁文件!")
            if package["name"] == name:
                self.packages.remove(package)
                return

    def has_ipk(self, name: str) -> bool:
        name = name.strip()
        for package in self.packages:
            if package["name"] == name:
                return True
        return False


class ProjectLock:
    ...
