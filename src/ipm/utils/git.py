from pathlib import Path
from git import Repo

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
