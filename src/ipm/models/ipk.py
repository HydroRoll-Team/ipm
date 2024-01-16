from pathlib import Path
from ..typing import List, Dict, Literal
from ..exceptions import SyntaxError

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

    name: str
    version: str
    description: str
    authors: Authors
    license: str

    def __init__(self, path: str | Path = ".") -> None:
        self.source_path = Path(path).resolve()
        toml_path = self.source_path / "infini.toml"

        data_load = toml.load(toml_path.open("r", encoding="utf-8"))
        if "infini" not in data_load.keys():
            raise SyntaxError("配置文件中缺少[infini]项.")

        infini: dict = data_load["infini"]
        self.name = infini.get("name") or ""
        self.version = infini.get("version") or ""
        self.description = infini.get("description") or ""
        self.authors = Authors(infini.get("authors") or [])
        self.license = infini.get("license") or "MIT"

    @property
    def default_name(self) -> str:
        return f"{self.name}-{self.version}.ipk"

    @property
    def hash_name(self) -> str:
        return f"{self.name}-{self.version}.ipk.hash"

    # @property
    # def home_p


class InfiniFrozenPackage:
    source_path: Path

    name: str
    version: str
    description: str
    authors: Authors
    license: str

    def __init__(self, source_path: str | Path, **kwargs) -> None:
        self.source_path = Path(source_path).resolve()

        self.name = kwargs.get("name") or ""
        self.version = kwargs.get("version") or ""
        self.description = kwargs.get("description") or ""
        self.authors = Authors(kwargs.get("authors") or [])
        self.license = kwargs.get("license") or "MIT"

    @property
    def hash_name(self) -> str:
        return f"{self.source_path.name}.hash"
