from pathlib import Path
from abc import ABCMeta, abstractmethod
from . import ipk
from ..typing import Dict, List, StrPath, Any, Package, Index, Storage
from ..const import IPM_PATH, ATTENSION
from ..exceptions import SyntaxError, FileNotFoundError
from ..utils.uuid import generate_uuid

import toml
import socket


class IpmLock(metaclass=ABCMeta):
    """IPM 锁基类"""

    source_path: Path
    metadata: Dict[str, str]

    def __init__(self, source_path: StrPath, auto_load: bool = True) -> None:
        IPM_PATH.mkdir(parents=True, exist_ok=True)
        self.source_path = source_path
        return self.load() if auto_load else None

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def dumps(self) -> dict:
        raise NotImplementedError

    def dump(self) -> str:
        data_to_dump = ATTENSION + toml.dumps(self.dumps())
        source_file = self.source_path.open("w", encoding="utf-8")
        source_file.write(data_to_dump)
        source_file.close()
        return data_to_dump


class PackageLock(IpmLock):
    """全局包锁"""

    indexes: List[Dict[str, Any]]
    packages: List[Dict[str, Any]]
    storages: List[Dict[str, Any]]

    def __init__(self, source_path: StrPath | None = None) -> None:
        super().__init__(source_path=source_path or IPM_PATH / "infini.lock")

    def load(self, auto_completion: bool = True) -> None:
        if not self.source_path.exists():
            if auto_completion:
                self.metadata = {
                    "host": socket.gethostname(),
                    "uuid": generate_uuid(),
                }
                self.indexes = []
                self.packages = []
                self.storages = []
                self.dumps()
            else:
                raise FileNotFoundError(f"锁文件不存在!")
        else:
            loaded_data = toml.load(self.source_path.open("r", encoding="utf-8"))

            if "metadata" not in loaded_data.keys():
                if not auto_completion:
                    raise SyntaxError(f"锁文件缺失[metadata]项.")
                else:
                    self.metadata = {
                        "host": socket.gethostname(),
                        "uuid": generate_uuid(),
                    }
            else:
                self.metadata = loaded_data["metadata"]

            if "uuid" not in self.metadata.keys():
                if auto_completion:
                    self.metadata["uuid"] = generate_uuid()
                else:
                    raise SyntaxError(f"锁文件[metadata]项缺失[uuid]项.")

            self.indexes = (
                loaded_data["indexes"] if "indexes" in loaded_data.keys() else []
            )
            self.packages = (
                loaded_data["packages"] if "packages" in loaded_data.keys() else []
            )
            self.storages = (
                loaded_data["storages"] if "storages" in loaded_data.keys() else []
            )

    def dumps(self) -> dict:
        return {
            "metadata": self.metadata,
            "indexes": self.indexes,
            "packages": self.packages,
            "storages": self.storages,
        }

    def add_index(
        self, index_uri: str, host: str, uuid: str, dump: bool = False
    ) -> str:
        for index in self.indexes:
            if "index" not in index.keys():
                raise SyntaxError("异常的锁文件!")
            if index["index"] == index_uri:
                self.storages.remove(index)
                break

        self.indexes.append(
            {
                "index": index_uri,
                "host": host,
                "uuid": uuid,
            }
        )
        return self.dump() if dump else ""

    def remove_index(self, uuid: str, dump: bool = False) -> str:
        uuid = uuid.strip()
        for index in self.indexes:
            if "name" not in index.keys():
                raise SyntaxError("异常的锁文件!")
            if index["name"] == uuid:
                self.packages.remove(index)
                break
        return self.dump() if dump else ""

    def get_index(self, index_uri: str) -> Index | None:
        index_uri = index_uri.strip()
        for index in self.indexes:
            if index["index"] == index_uri:
                return index
        return None

    def has_index(self, index_uri: str) -> bool:
        index_uri = index_uri.strip()
        for index in self.indexes:
            if index["index"] == index_uri:
                return True
        return False

    def add_package(self, ipk: "ipk.InfiniProject", dump: bool = False) -> str:
        for package in self.packages:
            if "name" not in package.keys():
                raise SyntaxError("异常的锁文件!")
            if package["name"] == ipk.name:
                self.storages.remove(package)
                break

        self.packages.append(
            {
                "name": ipk.name,
                "version": ipk.version,
                "description": ipk.description,
                "requirements": ipk.requirements,
                "dependencies": ipk.dependencies,
            }
        )
        return self.dump() if dump else ""

    def get_package(self, name: str) -> Package | None:
        name = name.strip()
        for package in self.packages:
            if package["name"] == name:
                return package
        return None

    def has_package(self, name: str) -> bool:
        name = name.strip()
        for package in self.packages:
            if package["name"] == name:
                return True
        return False

    def remove_package(self, name: str, dump: bool = False) -> str:
        name = name.strip()
        for package in self.packages:
            if "name" not in package.keys():
                raise SyntaxError("异常的锁文件!")
            if package["name"] == name:
                self.packages.remove(package)
                break
        return self.dump() if dump else ""

    def add_storage(self, ifp: "ipk.InfiniFrozenPackage", dump: bool = False) -> str:
        for storage in self.storages:
            if "name" not in storage.keys():
                raise SyntaxError("异常的锁文件!")
            if storage["name"] == ifp.name and storage["version"] == ifp.version:
                self.storages.remove(storage)
                break

        self.storages.append(
            {
                "name": ifp.name,
                "version": ifp.version,
                "hash": ifp.hash,
                "source": f"storage/{ifp.name}/{ifp.default_name}",
            }
        )
        return self.dump() if dump else ""

    def remove_storage(self, name: str, dump: bool = False) -> str:
        name = name.strip()
        for storage in self.storages:
            if "name" not in storage.keys():
                raise SyntaxError("异常的锁文件!")
            if storage["name"] == name:
                self.storages.remove(storage)
                break
        return self.dump() if dump else ""

    def get_storage(self, name: str) -> Storage | None:
        name = name.strip()
        for storage in self.storages:
            if storage["name"] == name:
                return storage
        return None

    def get_particular_storage(
        self, name: str, version: str | None = None
    ) -> Storage | None:
        name = name.strip()
        for storage in self.storages:
            if storage["name"] == name and (
                version is None or storage["version"] == version
            ):
                return storage
        return None

    def has_storage(self, name: str) -> bool:
        name = name.strip()
        for storage in self.storages:
            if storage["name"] == name:
                return True
        return False


class ProjectLock(IpmLock):
    """IPM 项目锁"""

    requirements: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]

    def __init__(self, source_path: StrPath | None = None) -> None:
        super().__init__(source_path=source_path or Path(".").resolve() / "infini.lock")

    def _init(self) -> None:
        # TODO 实现搜索下一级依赖
        ...

    def init(self) -> None:
        pkg = ipk.InfiniProject()
        self.metadata = {
            "name": pkg.name,
            "version": pkg.version,
            "description": pkg.description,
            "license": pkg.license,
        }
        self.requirements = [
            {"name": name, "version": version or "latest"}
            for name, version in pkg.requirements.values()
        ]
        self.dependencies = [
            {"name": name, "version": version or "latest"}
            for name, version in pkg.dependencies.values()
        ]
        self._init()
        self.dumps()

    def load(self) -> None:
        pkg = ipk.InfiniProject()

        if not self.source_path.exists():
            self.init()
        else:
            loaded_data = toml.load(self.source_path.open("r", encoding="utf-8"))

            self.metadata = (
                loaded_data["metadata"]
                if "metadata" in loaded_data.keys()
                else {
                    "name": pkg.name,
                    "version": pkg.version,
                    "description": pkg.description,
                    "license": pkg.license,
                }
            )
            self.requirements = (
                loaded_data["requirements"]
                if "requirements" in loaded_data.keys()
                else []
            )
            self.dependencies = (
                loaded_data["dependencies"]
                if "dependencies" in loaded_data.keys()
                else []
            )

    def dumps(self) -> Dict:
        return {
            "metadata": self.metadata,
            "requirements": self.requirements,
            "dependencies": self.dependencies,
        }

    def require(self, name: str, version: str, dump: bool = False) -> None:
        # TODO 依赖的依赖检索
        for requirement in self.requirements:
            if "name" not in requirement.keys():
                raise SyntaxError("异常的锁文件!")
            if requirement["name"] == name:
                self.requirements.remove(requirement)
                break

        self.requirements.append(
            {
                "name": name,
                "version": version,
            }
        )
        return self.dump() if dump else ""

    def unrequire(self, name: str, dump: bool = False) -> None:
        name = name.strip()
        for requirement in self.requirements:
            if "name" not in requirement.keys():
                raise SyntaxError("异常的锁文件!")
            if requirement["name"] == name:
                self.requirements.remove(requirement)
                break
        return self.dump() if dump else ""

    def add(self, name: str, version: str, dump: bool = False) -> None:
        for dependency in self.dependencies:
            if "name" not in dependency.keys():
                raise SyntaxError("异常的锁文件!")
            if dependency["name"] == name:
                self.dependencies.remove(dependency)
                break

        self.dependencies.append(
            {
                "name": name,
                "version": version,
            }
        )
        return self.dump() if dump else ""

    def remove(self, name: str, dump: bool = False) -> None:
        name = name.strip()
        for dependency in self.dependencies:
            if "name" not in dependency.keys():
                raise SyntaxError("异常的锁文件!")
            if dependency["name"] == name:
                self.dependencies.remove(dependency)
                break
        return self.dump() if dump else ""
