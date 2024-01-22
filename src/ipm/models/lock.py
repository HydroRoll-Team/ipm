from pathlib import Path
from abc import ABCMeta
from . import ipk
from ..typing import Dict, List, StrPath, Any
from ..const import IPM_PATH, ATTENSION
from ..exceptions import SyntaxError
from ..utils.uuid import generate_uuid

import toml
import socket


class IpmLock(metaclass=ABCMeta):
    metadata: Dict[str, str]
    indexes: List[Dict[str, Any]]
    packages: List[Dict[str, Any]]
    storages: List[Dict[str, Any]]
    source_path: Path

    def __init__(self, source_path: StrPath = IPM_PATH / "infini.lock") -> None:
        IPM_PATH.mkdir(parents=True, exist_ok=True)
        self.source_path = source_path
        self.load()

    def load(self):
        if not self.source_path.exists():
            self.metadata = {
                "host": socket.gethostname(),
                "uuid": generate_uuid(),
            }
            self.indexes = []
            self.packages = []
            self.storages = []
            self.dumps()
        else:
            loaded_data = toml.load(self.source_path.open("r", encoding="utf-8"))
            self.metadata = (
                loaded_data["metadata"]
                if "metadata" in loaded_data.keys()
                else {
                    "host": socket.gethostname(),
                    "uuid": generate_uuid(),
                }
            )
            if "uuid" not in self.metadata.keys():
                self.metadata = {
                    "host": socket.gethostname(),
                    "uuid": generate_uuid(),
                }
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

    def dump(self) -> str:
        data_to_dump = ATTENSION + toml.dumps(self.dumps())
        source_file = self.source_path.open("w", encoding="utf-8")
        source_file.write(data_to_dump)
        source_file.close()


class PackageLock(IpmLock):
    """全局包锁"""

    def __init__(self) -> None:
        super().__init__()

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

    def get_index(self, index_uri: str) -> dict | None:
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
            if (
                package["name"] == ipk.name and package["version"] == ipk.version
            ):  # TODO 同名包处理
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

    def get_package(self, name: str) -> dict | None:
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

    def get_storage(self, name: str) -> dict | None:
        name = name.strip()
        for storage in self.storages:
            if storage["name"] == name:
                return storage
        return None

    def has_storage(self, name: str) -> bool:
        name = name.strip()
        for storage in self.storages:
            if storage["name"] == name:
                return True
        return False


class ProjectLock:
    ...
