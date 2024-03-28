from pathlib import Path
from abc import ABCMeta
from typing import List, Optional
from ipm.typing import Dict, StrPath
from ipm.const import IPM_PATH, ATTENTIONS
from tomlkit import TOMLDocument
from typing import TYPE_CHECKING

import tomlkit

if TYPE_CHECKING:
    from ipm.models import ipk
    from ipm.models.index import Yggdrasil
    from ipm.models.ipk import InfiniFrozenPackage


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

    def update_index(self, index: str, uuid: str, lock_path: str) -> bool:
        indexes = self._data.get("index", tomlkit.aot())
        for i in indexes:
            if i["uuid"] == uuid:
                i["url"] = index
                i["lock"] = lock_path
                break
        else:
            indexes.append(
                tomlkit.item({"url": index, "uuid": uuid, "lock": lock_path})
            )
        self._data["index"] = indexes
        self.dump()
        return True

    def get_all(self) -> List["Yggdrasil"]:
        from ipm.models.index import Yggdrasil

        if "index" not in self._data.keys():
            return []
        res = []
        for index in self._data["index"]:  # type: ignore
            res.append(Yggdrasil(index["url"], index["uuid"]))
        return res

    def get_yggdrasil_by_index(self, index: str) -> Optional["Yggdrasil"]:
        from ipm.models.index import Yggdrasil

        indexes = self._data.get("index", [])
        for i in indexes:
            if i["url"] == index:
                return Yggdrasil(i["url"], i["uuid"])
        return None

    def has_package(self, filename: str): ...

    def add_frozen_package(self, ifp: "InfiniFrozenPackage"): ...


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

        packages = tomlkit.aot()
        for requirement in project.requirements:
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
