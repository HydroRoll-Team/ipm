from ipm.const import GITIGNORE
from ipm.exceptions import ProjectError
from ipm.models.ipk import InfiniProject
from pathlib import Path
from typing import List

import tomlkit


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
    toml_path = target_path.joinpath("infini.toml")
    if toml_path.exists():
        toml_data = tomlkit.loads(toml_path.read_text(encoding="utf-8"))
    else:
        toml_data = tomlkit.document()
    toml_file = toml_path.open("w", encoding="utf-8")
    project = toml_data.get("project", tomlkit.table())
    project["name"] = name
    project["version"] = version
    project["description"] = description
    author = tomlkit.array()
    author.add_line({"name": author_name, "email": author_email})
    author.multiline(True)
    project["authors"] = author
    project["license"] = license
    project["readme"] = "README.md"
    toml_data["project"] = project
    toml_data["requirements"] = tomlkit.table()
    toml_data["dependencies"] = tomlkit.table()
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
                "# Documents at https://docs.hydroroll.team/ipm\n\n"
                "from .events import register as events_register\n"
                "from .handlers import register as handlers_register\n"
                "from .interceptors import register as interceptors_register\n\n"
                '__all__ = ["events_register", "handlers_register", "interceptors_register"]'
            )
        if not events_filepath.exists():
            events_filepath.write_text(
                "# Initialized `events.py` generated by ipm.\n"
                "# Regists your text events and regist global variables here.\n"
                "# Documents at https://docs.hydroroll.team/ipm\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )
        if not handlers_filepath.exists():
            handlers_filepath.write_text(
                "# Initialized `handlers.py` generated by ipm.\n"
                "# Regists your handlers here.\n"
                "# Documents at https://docs.hydroroll.team/ipm\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )
        if not interceptors_filepath.exists():
            interceptors_filepath.write_text(
                "# Initialized `interceptors.py` generated by ipm.\n"
                "# Regists your pre-interceptors and interceptors here.\n"
                "# Documents at https://docs.hydroroll.team/ipm\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )
    else:
        entry_filepath = source_path.joinpath(default_entries[int(entry_file)])
        if not entry_filepath.exists():
            entry_filepath.write_text(
                f"# Initialized `{source_path.name}` generated by ipm.\n"
                "# Documents at https://docs.hydroroll.team/ipm\n\n"
                "from infini.register import Register\n\n\n"
                "register = Register()\n"
            )

    readme_filepath = target_path.joinpath("README.md")
    if not readme_filepath.exists():
        readme_filepath.write_text(f"# {name.upper()} 规则包文档", encoding="utf-8")


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


def remove_yggdrasil(project: InfiniProject, name: str):
    if "yggdrasils" not in project._data:
        raise ProjectError("项目文件缺乏 [bold red]yggdrasils[/] 项.")
    else:
        yggdrasils = project._data["yggdrasils"]
        if name not in yggdrasils.keys():  # type: ignore
            raise ProjectError(f"世界树 [bold red]{name}[/] 未注册, 忽略操作.")
    project.dump()


def init_pyproject(
    target_path: Path,
    name: str,
    version: str,
    description: str,
    author_name: str,
    author_email: str,
    license: str,
    standalone: bool,
):
    toml_path = target_path.joinpath("pyproject.toml")
    if toml_path.exists():
        toml_data = tomlkit.loads(toml_path.read_text(encoding="utf-8"))
    else:
        toml_data = tomlkit.document()
    toml_file = toml_path.open("w", encoding="utf-8")
    project = toml_data.get("project", tomlkit.table())
    project["name"] = name
    project["version"] = version
    project["description"] = description
    author = tomlkit.array()
    author.add_line({"name": author_name, "email": author_email})
    author.multiline(True)
    project["authors"] = author
    license_table = tomlkit.inline_table()
    license_table.update({"text": license})
    project["license"] = license_table
    project["dependencies"] = tomlkit.array('["infini>2.1.0"]')
    project["requires-python"] = ">=3.8"
    project["readme"] = "README.md"

    tool = tomlkit.table(True)
    pdm = tomlkit.table(True)
    if standalone:
        pdm.add("distribution", True)
    dev_dependencies = tomlkit.table()
    dev_dependencies.add("dev", tomlkit.array('["pytest"]'))
    pdm.append("dev-dependencies", dev_dependencies)
    tool.append("pdm", pdm)

    toml_data["project"] = project
    toml_data["tool"] = tool
    tomlkit.dump(toml_data, toml_file)
    toml_file.close()
