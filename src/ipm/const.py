from pathlib import Path

# 控制参数
DEBUG = False

# 初始化参数
INDEX = "https://ipm.hydroroll.team/index/"
IPM_PATH = Path.home() / ".ipm"
SRC_HOME = IPM_PATH / "src"
STORAGE = IPM_PATH / "storage"
INDEX_PATH = IPM_PATH / "index"

# 文本参数
ATTENSION = """# This file is @generated by IPM.
# It is not intended for manual editing.\n\n"""
