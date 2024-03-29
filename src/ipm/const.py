from pathlib import Path

# 控制参数
DEBUG = False

# 初始化参数
# INDEX = "http://localhost:5173/"
INDEX = "https://yggdrasil.noctisynth.org/"
IPM_PATH = Path.home() / ".ipm"
SRC_HOME = IPM_PATH / "src"
STORAGE = IPM_PATH / "storage"
INDEX_PATH = IPM_PATH / "index"

# 文本参数
ATTENTIONS = (
    "This file is @generated by IPM.",
    "It is not intended for manual editing.",
)
GITIGNORE = """# Initialized `.gitignores` @generated by IPM.
# Python
__pycache__/
*.pyc

# Builds
.ipm-build/
dist/

# Distribution / packaging
eggs/
.eggs/
downloads/
develop-eggs/
sdist/
*.egg-info/
wheels/
*.egg
MANIFEST

# pyenv
#   For a library or package, you might want to ignore these files since the code is
#   intended to run in multiple environments; otherwise, check them in:
# .python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# poetry
#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.
#   This is especially recommended for binary packages to ensure reproducibility, and is more
#   commonly ignored for libraries.
#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control
#poetry.lock

# pdm
#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.
#pdm.lock
#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it
#   in version control.
#   https://pdm-project.org/#use-with-ide
.pdm.toml
.pdm-python
.pdm-build/

# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm
__pypackages__/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
"""
