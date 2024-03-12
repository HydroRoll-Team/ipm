from pathlib import Path
from abc import ABCMeta, abstractmethod
from typing import Optional
from ipm.typing import Dict, List, StrPath, Any, Package, Index, Storage
from ipm.const import IPM_PATH, ATTENTIONS, SRC_HOME
from ipm.exceptions import SyntaxError, FileNotFoundError
from ipm.utils.uuid import generate_uuid
from tomlkit import TOMLDocument
from typing import TYPE_CHECKING

import tomlkit

if TYPE_CHECKING:
    from ipm.models import ipk


class IPMLock(metaclass=ABCMeta):
    """IPM 锁基类"""

    _lock_path: Path
    metadata: Dict[str, str]

    def __init__(self, source_path: StrPath) -> None:
        self._lock_path = Path(source_path).resolve().joinpath("infini.lock")
        self._data = self.read()

    def read(self) -> TOMLDocument:
        if not self._lock_path.exists():
            return tomlkit.document()
        return tomlkit.load(self._lock_path.open("r", encoding="utf-8"))

    def dumps(self) -> str:
        return tomlkit.dumps(self._data)

    def dump(self) -> None:
        doc = tomlkit.document()
        for attention in ATTENTIONS:
            doc.add(tomlkit.comment(attention))
        doc.update(self._data)
        return tomlkit.dump(
            doc, self._lock_path.open("w", encoding="utf-8"), sort_keys=True
        )


class PackageLock(IPMLock):
    """全局包锁"""

    def __init__(self, source_path: Optional[StrPath] = None) -> None:
        super().__init__(source_path=source_path or IPM_PATH)


#     def load(self, auto_completion: bool = True) -> None:
#         if not self.source_path.exists():
#             if auto_completion:
#                 self.metadata = {
#                     "host": socket.gethostname(),
#                     "uuid": generate_uuid(),
#                 }
#                 self.indexes = []
#                 self.packages = []
#                 self.storages = []
#                 self.dumps()
#             else:
#                 raise FileNotFoundError(f"锁文件不存在!")
#         else:
#             loaded_data = toml.load(self.source_path.open("r", encoding="utf-8"))

#             if "metadata" not in loaded_data.keys():
#                 if not auto_completion:
#                     raise SyntaxError(f"锁文件缺失[metadata]项.")
#                 else:
#                     self.metadata = {
#                         "host": socket.gethostname(),
#                         "uuid": generate_uuid(),
#                     }
#             else:
#                 self.metadata = loaded_data["metadata"]

#             if "uuid" not in self.metadata.keys():
#                 if auto_completion:
#                     self.metadata["uuid"] = generate_uuid()
#                 else:
#                     raise SyntaxError(f"锁文件[metadata]项缺失[uuid]项.")

#             self.indexes = (
#                 loaded_data["indexes"] if "indexes" in loaded_data.keys() else []
#             )
#             self.packages = (
#                 loaded_data["packages"] if "packages" in loaded_data.keys() else []
#             )
#             self.storages = (
#                 loaded_data["storages"] if "storages" in loaded_data.keys() else []
#             )

#     def dumps(self) -> dict:
#         return {
#             "metadata": self.metadata,
#             "indexes": self.indexes,
#             "packages": self.packages,
#             "storages": self.storages,
#         }

#     def add_index(
#         self, index_uri: str, host: str, uuid: str, dump: bool = False
#     ) -> str:
#         for index in self.indexes:
#             if "index" not in index.keys():
#                 raise SyntaxError("异常的锁文件!")
#             if index["index"] == index_uri:
#                 self.storages.remove(index)
#                 break

#         self.indexes.append(
#             {
#                 "index": index_uri,
#                 "host": host,
#                 "uuid": uuid,
#             }
#         )
#         return self.dump() if dump else ""

#     def remove_index(self, uuid: str, dump: bool = False) -> str:
#         uuid = uuid.strip()
#         for index in self.indexes:
#             if "name" not in index.keys():
#                 raise SyntaxError("异常的锁文件!")
#             if index["name"] == uuid:
#                 self.packages.remove(index)
#                 break
#         return self.dump() if dump else ""

#     def get_index(self, index_uri: str) -> Index | None:
#         index_uri = index_uri.strip()
#         for index in self.indexes:
#             if index["index"] == index_uri:
#                 return index
#         return None

#     def has_index(self, index_uri: str) -> bool:
#         index_uri = index_uri.strip()
#         for index in self.indexes:
#             if index["index"] == index_uri:
#                 return True
#         return False

#     def add_package(self, ipk: "ipk.InfiniProject", dump: bool = False) -> str:
#         for package in self.packages:
#             if "name" not in package.keys():
#                 raise SyntaxError("异常的锁文件!")
#             if package["name"] == ipk.name:
#                 self.storages.remove(package)
#                 break

#         self.packages.append(
#             {
#                 "name": ipk.name,
#                 "version": ipk.version,
#                 "description": ipk.description,
#                 "requirements": ipk.requirements,
#                 "dependencies": ipk.dependencies,
#             }
#         )
#         return self.dump() if dump else ""

#     def get_package(self, name: str) -> Package | None:
#         name = name.strip()
#         for package in self.packages:
#             if package["name"] == name:
#                 return package
#         return None

#     def has_package(self, name: str) -> bool:
#         name = name.strip()
#         for package in self.packages:
#             if package["name"] == name:
#                 return True
#         return False

#     def remove_package(self, name: str, dump: bool = False) -> str:
#         name = name.strip()
#         for package in self.packages:
#             if "name" not in package.keys():
#                 raise SyntaxError("异常的锁文件!")
#             if package["name"] == name:
#                 self.packages.remove(package)
#                 break
#         return self.dump() if dump else ""

#     def add_storage(self, ifp: "ipk.InfiniFrozenPackage", dump: bool = False) -> str:
#         for storage in self.storages:
#             if "name" not in storage.keys():
#                 raise SyntaxError("异常的锁文件!")
#             if storage["name"] == ifp.name and storage["version"] == ifp.version:
#                 self.storages.remove(storage)
#                 break

#         self.storages.append(
#             {
#                 "name": ifp.name,
#                 "version": ifp.version,
#                 "hash": ifp.hash,
#                 "source": f"storage/{ifp.name}/{ifp.default_name}",
#             }
#         )
#         return self.dump() if dump else ""

#     def remove_storage(self, name: str, dump: bool = False) -> str:
#         name = name.strip()
#         for storage in self.storages:
#             if "name" not in storage.keys():
#                 raise SyntaxError("异常的锁文件!")
#             if storage["name"] == name:
#                 self.storages.remove(storage)
#                 break
#         return self.dump() if dump else ""

#     def get_storage(self, name: str) -> Storage | None:
#         name = name.strip()
#         for storage in self.storages:
#             if storage["name"] == name:
#                 return storage
#         return None

#     def get_particular_storage(
#         self, name: str, version: str | None = None
#     ) -> Storage | None:
#         name = name.strip()
#         for storage in self.storages:
#             if storage["name"] == name and (
#                 version is None or storage["version"] == version
#             ):
#                 return storage
#         return None

#     def has_storage(self, name: str) -> bool:
#         name = name.strip()
#         for storage in self.storages:
#             if storage["name"] == name:
#                 return True
#         return False

#     def get_ipk(self, name: str) -> "ipk.InfiniProject":
#         return ipk.InfiniProject(Path(SRC_HOME / name.strip()).resolve())


class ProjectLock(IPMLock):
    """IPM 项目锁"""

    def __init__(self, source_path: Optional[StrPath] = None) -> None:
        super().__init__(
            source_path=source_path or Path.cwd(),
        )

    @staticmethod
    def init_from_project(project: "ipk.InfiniProject") -> "ProjectLock":
        lock = ProjectLock(project._source_path)
        lock._data = tomlkit.document()

        metadata = tomlkit.table()
        metadata.add("name", project.name)
        metadata.add("version", project.version)
        metadata.add("description", project.description)
        metadata.add("license", project.license)
        lock._data.add("metadata", metadata)

        for requirement in project.requirements:
            packages = tomlkit.aot()
            if requirement.is_local():
                packages.append(
                    tomlkit.item(
                        {
                            "name": requirement.name,
                            "version": requirement.version,
                            "path": requirement.path,
                        }
                    )
                )
            else:
                packages.append(
                    tomlkit.item(
                        {
                            "name": requirement.name,
                            "version": requirement.version,
                            "yggdrasil": requirement.yggdrasil.index,
                        }
                    )
                )
            lock._data.add("packages", packages)

        return lock
