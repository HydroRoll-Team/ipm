from ipm.const import GITIGNORE
from pathlib import Path
from typing import List
from tomlkit.items import Table

import tomlkit

from ipm.models.ipk import InfiniProject


def init_infini(
    toml_path: Path,
    target_path: Path,
    name: str,
    version: str,
    description: str,
    author_name: str,
    author_email: str,
    license: str,
    entry_file: str,
    default_entries: List[str],
) -> None:
    toml_file = toml_path.open("w", encoding="utf-8")
    toml_data = tomlkit.document()
    project = tomlkit.table()
    project.add("name", name)
    project.add("version", version)
    project.add("description", description)
    author = tomlkit.array()
    author.add_line({"name": author_name, "email": author_email})
    author.multiline(True)
    project.add("authors", author)
    project.add("license", license)
    toml_data.add("project", project)
    toml_data.add("requirements", tomlkit.table())
    toml_data.add("dependencies", tomlkit.table())
    tomlkit.dump(toml_data, toml_file)
    toml_file.close()

    source_path = target_path.joinpath("src")
    gitignore_filepath = target_path.joinpath(".gitignore")
    source_path.mkdir(parents=True, exist_ok=True)
    if not gitignore_filepath.exists():
        (target_path / ".gitignore").write_text(GITIGNORE)

    if entry_file == "0":
        init_filepath = source_path.joinpath("__init__.py")
        events_filepath = source_path.joinpath("events.py")
        handlers_filepath = source_path.joinpath("handlers.py")
        interceptors_filepath = source_path.joinpath("interceptors.py")

        if not init_filepath.exists():
            init_filepath.write_text(
                "# Initialized `events.py` generated by ipm.\n"
                "# Regists your text events and regist global variables here.\n"
                "# Documents at https://ipm.hydroroll.team/\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )
        if not events_filepath.exists():
            events_filepath.write_text(
                "# Initialized `events.py` generated by ipm.\n"
                "# Regists your text events and regist global variables here.\n"
                "# Documents at https://ipm.hydroroll.team/\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )
        if not handlers_filepath.exists():
            handlers_filepath.write_text(
                "# Initialized `handlers.py` generated by ipm.\n"
                "# Regists your handlers here.\n"
                "# Documents at https://ipm.hydroroll.team/\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )
        if not interceptors_filepath.exists():
            interceptors_filepath.write_text(
                "# Initialized `interceptors.py` generated by ipm.\n"
                "# Regists your pre-interceptors and interceptors here.\n"
                "# Documents at https://ipm.hydroroll.team/\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )
    else:
        entry_filepath = source_path.joinpath(default_entries[int(entry_file)])
        if not entry_filepath.exists():
            entry_filepath.write_text(
                f"# Initialized `{source_path.name}` generated by ipm.\n"
                "# Documents at https://ipm.hydroroll.team/\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )


def add_yggdrasil(toml_path: Path, name: str, index: str):
    project = InfiniProject(toml_path.parent)
    if "yggdrasils" not in project._data:
        yggdrasils = tomlkit.table()
        yggdrasils.update({name: index})
        project._data.add("yggdrasils", yggdrasils)
    else:
        yggdrasils = project._data["yggdrasils"]
        yggdrasils[name] = index  # type: ignore
    project.dump()


def init_pyproject(
    target_path: Path,
    name: str,
    version: str,
    description: str,
    author_name: str,
    author_email: str,
    license: str,
):
    toml_file = target_path.joinpath("pyproject.toml").open("w", encoding="utf-8")
    toml_data = tomlkit.document()
    project = tomlkit.table()
    project.add("name", name)
    project.add("version", version)
    project.add("description", description)
    author = tomlkit.array()
    author.add_line({"name": author_name, "email": author_email})
    author.multiline(True)
    project.add("authors", author)
    license_table = tomlkit.inline_table()
    license_table.update({"text": license})
    project.add("license", license_table)
    project.add("dependencies", tomlkit.array())
    project.add("requires-python", ">=3.8")
    project.add("readme", "README.md")

    tool = tomlkit.table(True)
    pdm = tomlkit.table(True)
    pdm.add("distribution", True)
    dev_dependencies = tomlkit.table()
    dev_dependencies.add("dev", tomlkit.array('["pytest>=8.0.2"]'))
    pdm.append("dev-dependencies", dev_dependencies)
    tool.append("pdm", pdm)

    toml_data.add("project", project)
    toml_data.add("tool", tool)
    tomlkit.dump(toml_data, toml_file)
    toml_file.close()
