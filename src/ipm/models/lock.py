from pathlib import Path
from abc import ABCMeta
from typing import Any, List, Optional
from ipm.models.requirement import Requirement
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
                self._data["index"] = indexes
                break
        else:
            aot = tomlkit.aot()
            aot.append(tomlkit.item({"url": index, "uuid": uuid, "lock": lock_path}))
            self._data.add("index", aot)
        self.dump()
        return True

    def has_index(self, index: Any) -> bool:
        for i in self._data.get("index", tomlkit.aot()):
            if i["url"].strip("/") == index.strip("/"):
                return True
        else:
            return False

    def get_all_indexes(self) -> List["Yggdrasil"]:
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

    def has_frozen_package(self, name: str, version: str) -> bool:
        data = self._data.unwrap()
        for package in data.get("package", []):
            if package["name"] == name and package["version"] == version:
                return True
        return False

    def add_frozen_package(
        self, name: str, version: str, hash: str, yggdrasil: str, path: str
    ):
        aot = tomlkit.aot()
        aot.append(
            tomlkit.item(
                {
                    "name": name,
                    "version": version,
                    "hash": hash,
                    "yggdrasil": yggdrasil,
                    "path": path,
                }
            )
        )
        self._data.add("package", aot)
        self.dump()

    def get_frozen_package_path(self, name: str, version: str) -> Optional[Path]:
        data = self._data.unwrap()
        for package in data.get("package", []):
            if package["name"] == name and package["version"] == version:
                return Path(package["path"])
        return


class ProjectLock(IPMLock):
    """IPM 项目锁"""

    def __init__(self, source_path: Optional[StrPath] = None) -> None:
        super().__init__(
            source_path=source_path or Path.cwd(),
        )

    @staticmethod
    def init_from_project(
        project: "ipk.InfiniProject", dist_path: Optional[Path] = None
    ) -> "ProjectLock":
        from ipm.utils.resolve import get_requirements_by_project

        lock = ProjectLock(dist_path or project._source_path)
        lock._data = tomlkit.document()

        metadata = tomlkit.table()
        metadata.add("name", project.name)
        metadata.add("version", project.version)
        metadata.add("description", project.description)
        metadata.add("license", project.license)
        lock._data.add("metadata", metadata)

        packages = tomlkit.aot()
        requirements = get_requirements_by_project(project)

        for requirement in requirements:
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
                            "url": requirement.url,
                        }
                    )
                )
        lock._data.add("package", packages)

        return lock

    @property
    def requirements(self) -> List[Requirement]:
        from ipm.models.lock import PackageLock

        global_lock = PackageLock()
        return [
            Requirement(
                package["name"],
                package["version"],
                path=package.get("path"),
                url=package.get("url"),
                yggdrasil=global_lock.get_yggdrasil_by_index(package.get("yggdrasil")),
            )
            for package in self._data.unwrap().get("package", [])
        ]
