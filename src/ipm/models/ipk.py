from pathlib import Path
from typing import Any, Optional, Union
from tomlkit.toml_document import TOMLDocument

from ipm.const import INDEX
from ipm.utils.hash import ifp_hash
from ipm.models.index import Yggdrasil
from ipm.models.lock import PackageLock
from ipm.typing import List, Dict, Literal, StrPath
from ipm.exceptions import ProjectError, TomlLoadFailed

import tomlkit
import abc


global_lock = PackageLock()


class Author:
    name: str
    email: str

    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email


class Authors:
    authors: List[Author] = []

    def __init__(self, authors: List[Dict[Literal["name", "email"], str]]) -> None:
        for author in authors:
            self.authors.append(Author(author["name"], author["email"]))

    @property
    def first(self) -> Optional[Author]:
        return None if not self.authors else self.authors[0]


class Requirement:
    name: str
    version: str
    path: Optional[str]
    yggdrasil: Yggdrasil

    def __init__(
        self,
        name: str,
        version: str,
        path: Optional[str] = None,
        yggdrasil: Optional[Yggdrasil] = None,
    ) -> None:
        yggdrasil = yggdrasil or global_lock.get_yggdrasil_by_index(INDEX)
        if not yggdrasil:
            raise ProjectError("未能找到任何世界树地址，请先添加一个世界树地址。")
        self.name = name
        self.version = version
        self.path = path
        self.yggdrasil = yggdrasil

    def is_local(self) -> bool:
        return bool(self.path)


class Requirements(List[Requirement]):
    def __init__(
        self,
        dependencies: Dict[str, Union[Dict, str]],
        yggdrasils: Optional[Dict[str, Yggdrasil]] = None,
    ) -> None:
        path = yggdrasil = version = None
        for name, dependency in dependencies.items():
            if isinstance(dependency, str):
                self.append(Requirement(name=name, version=dependency))
            else:
                for key, value in dependency.items():
                    if key == "index":
                        yggdrasil = global_lock.get_yggdrasil_by_index(value)
                    elif key == "yggdrasil":
                        yggdrasil = (yggdrasils or {}).get(value)
                        if not yggdrasil:
                            raise ValueError(f"未知的世界树标识符: '{value}'")
                    elif key == "path":
                        path = value
                    elif key == "version":
                        version = value
                    else:
                        raise ValueError(f"未知的依赖项键值: '{key}'")
                self.append(
                    Requirement(
                        name=name,
                        version=version or "*",
                        path=path,
                        yggdrasil=yggdrasil,
                    )
                )


class InfiniPackage(metaclass=abc.ABCMeta):
    @property
    def default_name(self) -> str:
        return f"{self.name}-{self.version}"

    @property
    def hash_name(self) -> str:
        return f"{self.name}-{self.version}.ipk.hash"

    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def version(self) -> str:
        raise NotImplementedError


class InfiniProject(InfiniPackage):
    def __init__(self, path: StrPath = ".") -> None:
        self._source_path = Path(path).resolve()
        self._toml_path = self._source_path / "infini.toml"

        if not self._source_path.exists():
            raise TomlLoadFailed(f"入口路径[{self._source_path}]不存在.")
        elif not self._toml_path.exists():
            raise TomlLoadFailed(
                f"项目文件[infini.toml]不存在, 请先使用`[bold green]ipm init[/]`初始化!"
            )

        self._data = self.read()
        if "project" not in self._data:
            raise TomlLoadFailed(f"项目文件[infini.toml]中不存在元数据!")

    def read(self) -> TOMLDocument:
        if not self._toml_path.exists():
            return tomlkit.document()
        return tomlkit.load(self._toml_path.open("r", encoding="utf-8"))

    def dumps(self) -> str:
        return tomlkit.dumps(self._data)

    def dump(self) -> None:
        return tomlkit.dump(self._data, self._toml_path.open("w", encoding="utf-8"))

    def require(
        self,
        name: str,
        *,
        version: Optional[str] = None,
        path: Optional[str] = None,
        yggdrasil: Optional[str] = None,
        index: Optional[str] = None,
    ) -> None:
        if version and not any([path, yggdrasil, index]):
            self._data["requirements"][name] = version  # type: ignore
            return
        requirement = tomlkit.inline_table()
        requirement.add("version", version) if version else None
        requirement.add("path", path) if path else None
        requirement.add("yggdrasil", yggdrasil) if yggdrasil else None
        requirement.add("index", index) if index else None
        if not requirement:
            raise ValueError("")
        self._data["requirements"].update({name: requirement})  # type: ignore

    def unrequire(self, name: str) -> None:
        if name not in self._data.get("requirements", {}):
            raise ProjectError(f"规则包 [bold green]{name}[/] 不在规则包依赖中.")
        self._data["requirements"].remove(name)  # type: ignore

    def add(self, name: str, version: str) -> None:
        denpendencies = self.dependencies
        denpendencies.update({name: version})
        self._data["dependencies"] = denpendencies

    def remove(self, name: str) -> None:
        if name not in self._data.get("dependencies", {}):
            raise ProjectError(f"规则包 [bold green]{name}[/] 不在规则包依赖中.")
        self._data["dependencies"].remove(name)  # type: ignore

    @property
    def plain_dict(self) -> TOMLDocument:
        return self._data

    @property
    def metadata(self) -> dict:
        return self._data["project"]  # type: ignore

    @property
    def readme(self) -> str:
        project = self._data.get("project")
        if not project:
            raise ProjectError("项目文件中不存在`project`项!")
        path = self._source_path.joinpath(project["readme"])
        if not path.exists():
            raise ProjectError("配置文件中的自述文件不存在!")
        return path.read_text(encoding="utf-8")

    @property
    def name(self) -> str:
        return self._data["project"]["name"]  # type: ignore

    @property
    def version(self) -> str:
        return self._data["project"]["version"]  # type: ignore

    @property
    def description(self) -> str:
        return self._data["project"]["description"]  # type: ignore

    @property
    def authors(self) -> Authors:
        return Authors(self._data["project"]["authors"])  # type: ignore

    @property
    def homepage(self) -> str:
        return self._data["project"]["urls"]["homepage"]  # type: ignore

    @property
    def unzip(self) -> Union[str, int]:
        return self._data["project"]["unzip"]  # type: ignore

    @property
    def license(self) -> str:
        return self._data["project"]["license"]  # type: ignore

    @property
    def dependencies(self) -> Dict[str, Any]:
        return self._data.get("dependencies", {})  # type: ignore

    @property
    def requirements(self) -> Requirements:
        return Requirements(
            self._data.get("requirements") or {}, yggdrasils=self.yggdrasils
        )

    @property
    def yggdrasils(self) -> Dict[str, str]:
        res = {name: index for name, index in self._data.get("yggdrasils", {}).items()}
        res.update({"official": INDEX})
        return res

    @property
    def topics(self) -> List[str]:
        return self._data["project"]["topics"]  # type: ignore


class InfiniFrozenPackage(InfiniPackage):
    def __init__(self, source_path: Union[str, Path], name: str, version: str) -> None:
        self._source_path = Path(source_path).resolve()
        self._name = name
        self._version = version

    def __hash__(self) -> str:
        return ifp_hash(self._source_path)

    @property
    def hash(self) -> str:
        return self.hash

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version
