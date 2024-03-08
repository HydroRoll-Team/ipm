from pathlib import Path
from urllib.parse import urlparse
from ..const import INDEX_PATH
from ..typing import Storage
from ..logging import info, success
from ..exceptions import LockLoadFailed

import requests
import tempfile
import shutil


class Yggdrasil:
    source_path: Path

    host: str
    uuid: str
    index: str

    def __init__(self, index: str) -> None:
        INDEX_PATH.mkdir(parents=True, exist_ok=True)
        self.index = index.rstrip("/") + "/"

    # def init(self, source_path: Path):
    #     self.source_path = source_path
    #     self.lock = PackageLock(self.source_path / "infini.lock")
    #     self.uuid = self.lock.metadata["uuid"]
    #     self.host = self.lock.metadata.get("host") or urlparse(self.index).netloc

    def sync(self, echo: bool = False): ...

    #     info(f"正在从世界树[{self.index}]同步...", echo)
    #     lock_bytes = requests.get(self.index + "infini.lock").content

    #     temp_dir = tempfile.TemporaryDirectory()
    #     temp_path = Path(temp_dir.name).resolve()
    #     temp_lock_path = temp_path / "infini.lock"

    #     temp_lock_file = temp_lock_path.open("wb")
    #     temp_lock_file.write(lock_bytes)
    #     temp_lock_file.close()

    #     temp_lock = PackageLock(temp_lock_path)

    #     if "uuid" not in temp_lock.metadata.keys():
    #         temp_dir.cleanup()
    #         raise LockLoadFailed(f"地址[{self.index}]不是合法的世界树服务器.")

    #     self.source_path = INDEX_PATH / temp_lock.metadata["uuid"]
    #     self.source_path.mkdir(parents=True, exist_ok=True)

    #     shutil.copy2(temp_lock_path, self.source_path)
    #     temp_dir.cleanup()
    #     self.init(self.source_path)
    #     success(f"成功建立与世界树[{self.host}]的连接.")

    # def get(self, name: str, version: str | None = None) -> Storage | None:
    #     return self.lock.get_particular_storage(name, version)
