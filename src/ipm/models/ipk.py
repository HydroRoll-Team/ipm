from pathlib import Path
from typing import Optional, Union
from tomlkit.toml_document import TOMLDocument
from ipm.models import lock
from ipm.typing import List, Dict, Literal, StrPath
from ipm.exceptions import SyntaxError, TomlLoadFailed

import tomlkit

# ProjectLock = lock.ProjectLock


class Author:
    name: str
    email: str

    def __init__(self, name: str, email: str) -> None:
        self.name = name
        self.email = email


class Authors:
    authors: list[Author] = []

    def __init__(self, authors: List[Dict[Literal["name", "email"], str]]) -> None:
        for author in authors:
            self.authors.append(Author(author["name"], author["email"]))

    @property
    def first(self) -> Author | None:
        return None if not self.authors else self.authors[0]


class InfiniPackage:
    _source_path: Path

    name: str | None
    version: str | None

    @property
    def default_name(self) -> str:
        return f"{self.name}-{self.version}.ipk"

    @property
    def hash_name(self) -> str:
        return f"{self.name}-{self.version}.ipk.hash"


class InfiniProject(InfiniPackage):
    # name: str
    # version: str
    # description: str
    # authors: Authors
    # license: str

    # requirements: Dict[str, Any]
    # dependencies: Dict[str, Any]

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

    @property
    def plain_dict(self) -> TOMLDocument:
        return self._data

    @property
    def name(self) -> str:
        project = self._data["project"]
        if not (name := project.get("name")):  # type: ignore
            raise ValueError("项目文件不存在`name`属性.")
        return name


class InfiniFrozenPackage(InfiniPackage):
    name: str | None
    version: str | None
    hash: str

    def __init__(self, source_path: Union[str, Path], **kwargs) -> None:
        self._source_path = Path(source_path).resolve()

        self.hash = (
            (self._source_path.parent / (self._source_path.name + ".hash"))
            .read_bytes()
            .hex()
        )

        self.name = kwargs.get("name")
        self.version = kwargs.get("version")

    @property
    def hash_name(self) -> str:
        return f"{self._source_path.name}.hash"
