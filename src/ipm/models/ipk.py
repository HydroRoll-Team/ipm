from pathlib import Path
from . import lock
from ..typing import List, Dict, Literal, StrPath, Any
from ..exceptions import SyntaxError, TomlLoadFailed

import toml

ProjectLock = lock.ProjectLock


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
    source_path: Path

    name: str | None
    version: str | None

    @property
    def default_name(self) -> str:
        return f"{self.name}-{self.version}.ipk"

    @property
    def hash_name(self) -> str:
        return f"{self.name}-{self.version}.ipk.hash"


class InfiniProject(InfiniPackage):
    name: str
    version: str
    description: str
    authors: Authors
    license: str

    requirements: Dict[str, Any]
    dependencies: Dict[str, Any]

    def __init__(self, path: StrPath = ".") -> None:
        self.source_path = Path(path).resolve()
        toml_path = self.source_path / "infini.toml"

        try:
            data_load = toml.load(toml_path.open("r", encoding="utf-8"))
        except Exception as error:
            raise TomlLoadFailed(f"项目文件[infini.toml]导入失败: {error}") from error

        if "infini" not in data_load.keys():
            raise SyntaxError("配置文件中缺少[infini]项.")

        infini: dict = data_load["infini"]
        self.name = infini.get("name") or ""
        self.version = infini.get("version") or ""
        self.description = infini.get("description") or ""
        self.authors = Authors(infini.get("authors") or [])
        self.license = infini.get("license") or "MIT"

        self.requirements = data_load["requirements"]
        self.dependencies = data_load["dependencies"]

    def dumps(self) -> dict:
        return {
            "infini": {
                "name": self.source_path.name,
                "version": self.version,
                "description": self.description,
                "authors": [
                    {"name": author.name, "email": author.email}
                    for author in self.authors.authors
                ],
                "license": self.license,
            },
            "requirements": self.requirements,
            "dependencies": self.dependencies,
        }

    def dump(self) -> str:
        return toml.dump(
            self.dumps(), (self.source_path / "infini.toml").open("w", encoding="utf-8")
        )

    def require(self, name: str, version: str, dump: bool = False) -> None:
        for requirement in self.requirements.keys():
            if requirement == name:
                self.requirements.pop(name)
                break

        self.requirements[name] = version or "latest"
        self.dump() if dump else ""

    def unrequire(self, name: str, dump: bool = False) -> None:
        name = name.strip()
        for requirement in self.requirements:
            if requirement == name:
                self.requirements.pop(name)
                break
        self.dump() if dump else ""

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
        self.dump() if dump else ""

    def remove(self, name: str, dump: bool = False) -> None:
        name = name.strip()
        for dependency in self.dependencies:
            if "name" not in dependency.keys():
                raise SyntaxError("异常的锁文件!")
            if dependency["name"] == name:
                self.dependencies.remove(dependency)
                break
        self.dump() if dump else ""


class InfiniFrozenPackage(InfiniPackage):
    name: str | None
    version: str | None
    hash: str

    def __init__(self, source_path: str | Path, **kwargs) -> None:
        self.source_path = Path(source_path).resolve()

        self.hash = (
            (self.source_path.parent / (source_path.name + ".hash")).read_bytes().hex()
        )

        self.name = kwargs.get("name")
        self.version = kwargs.get("version")

    @property
    def hash_name(self) -> str:
        return f"{self.source_path.name}.hash"
