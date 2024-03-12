from pathlib import Path
from virtualenv.run.session import Session

import virtualenv
import os


def new_virtualenv(target_path: Path) -> Session:
    session = virtualenv.cli_run([str(target_path.joinpath(".venv"))])
    target_path.joinpath(".pdm-python").write_text(
        str(
            target_path.joinpath(".venv", "Scripts", "python.exe")
            if os.name == "nt"
            else target_path.joinpath("bin", "python")
        )
    )
    return session
