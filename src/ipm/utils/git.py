from pathlib import Path
from ipm.exceptions import RuntimeError
from git import GitCommandError, Repo

import os


def get_user_name_email():
    try:
        repo = Repo()
        config = repo.config_reader(config_level="global")
        return (
            config.get_value("user", "name", os.getlogin()),
            config.get_value("user", "email", os.getlogin() + "@example.com"),
        )
    except:
        return "user", "user@email.com"


def git_init(target_path: Path):
    return Repo.init(target_path)


def git_tag(target_path: Path, tag: str):
    repo = Repo(target_path)
    try:
        repo.create_tag("v" + tag)
    except GitCommandError as err:
        raise RuntimeError(f"创建 Tag 时出现异常: [red]{err.stderr.strip("\n ")}[/]")
