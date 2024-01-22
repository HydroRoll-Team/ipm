from pathlib import Path
from urllib.parse import urlparse
from .lock import PackageLock
from ..const import INDEX_PATH
from ..typing import Storage
from ..exceptions import LockLoadFailed

import requests
import tempfile
import shutil


class Yggdrasil:
    source_path: Path

    host: str
    uuid: str
    index: str
    lock: PackageLock

    def __init__(self, index: str) -> None:
        INDEX_PATH.mkdir(parents=True, exist_ok=True)
        self.index = index.rstrip("/") + "/"

    def sync(self, echo: bool = False):  # TODO 输出内容
        lock_bytes = requests.get(self.index + "infini.lock").content

        temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir.name).resolve()
        temp_lock_path = temp_path / "infini.lock"

        temp_lock_file = temp_lock_path.open("wb")
        temp_lock_file.write(lock_bytes)
        temp_lock_file.close()

        temp_lock = PackageLock(temp_lock_path)

        if "uuid" not in temp_lock.metadata.keys():
            temp_dir.cleanup()
            raise LockLoadFailed(f"地址[{self.index}]不是合法的世界树服务器.")

        self.uuid = temp_lock.metadata["uuid"]
        self.host = temp_lock.metadata.get("host") or urlparse(self.index).netloc
        self.source_path = INDEX_PATH / self.uuid

        self.source_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(temp_lock_path, self.source_path)
        self.lock = PackageLock(self.source_path / "infini.lock")

    def get(self, name: str, version: str | None = None) -> Storage | None:
        return self.lock.get_particular_storage(name, version)
