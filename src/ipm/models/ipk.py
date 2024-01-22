from pathlib import Path
from . import lock
from ..typing import List, Dict, Literal
from ..exceptions import SyntaxError, TomlLoadFailed

import toml


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

    requirements: dict
    dependencies: dict

    lock: lock.ProjectLock

    def __init__(self, path: str | Path = ".") -> None:
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
        # self.lock = ProjectLock
        # TODO 项目锁

    def export_dict(self) -> dict:
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
