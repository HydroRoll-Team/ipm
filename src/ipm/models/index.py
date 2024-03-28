from pathlib import Path
from typing import Any, Literal, Optional
from ipm.const import INDEX_PATH
from ipm.exceptions import LockLoadFailed
from ipm.models.lock import PackageLock
from ipm.typing import Dict

import requests
import tempfile
import shutil
import json


class Yggdrasil:
    def __init__(self, index: str, uuid: str) -> None:
        self.index = index.rstrip("/") + "/"
        self._source_path = INDEX_PATH.joinpath(uuid)
        self._data = self.read()

    def read(self) -> Dict:
        if not self._source_path.exists():
            self._source_path.parent.mkdir(parents=True, exist_ok=True)
            return {}
        return json.load(
            self._source_path.joinpath("packages.json").open("r", encoding="utf-8")
        )

    def dump(self) -> None:
        json.dump(self._data, self._source_path.open("w", encoding="utf-8"))

    @staticmethod
    def try_loads(path: Path) -> Dict | Literal[False]:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def check(source_path: Path):
        """检查一个索引文件是否合法"""
        if not (packages := Yggdrasil.try_loads(source_path)):
            return False
        return packages

    @staticmethod
    def init(index: str) -> "Yggdrasil":
        lock_bytes = requests.get(
            index.rstrip("/") + "/" + "json/packages.json"
        ).content

        temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir.name).resolve()
        temp_lock_path = temp_path / "packages.json"

        temp_lock_file = temp_lock_path.open("wb")
        temp_lock_file.write(lock_bytes)
        temp_lock_file.close()

        if not (packages := Yggdrasil.check(temp_lock_path)):
            raise LockLoadFailed(f"地址 [red]{index}[/] 不是合法的世界树服务器.")

        if "uuid" not in packages["metadata"].keys():
            temp_dir.cleanup()
            raise LockLoadFailed(f"地址[{index}]不是合法的世界树服务器.")
        uuid = packages["metadata"]["uuid"]

        source_path = INDEX_PATH.joinpath(uuid)
        source_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(temp_lock_path, source_path.joinpath("packages.json"))
        temp_dir.cleanup()

        lock = PackageLock()
        lock.update_index(index, uuid, str(source_path))
        return Yggdrasil(index, uuid)

    def sync(self):
        yggdrasil = Yggdrasil.init(self.index)
        self._source_path = yggdrasil._source_path
        self._data = yggdrasil._data

    def get_url(self, name: str, version: Optional[str]) -> Optional[str]:
        """从本地读取规则包下载链接"""
        if name not in self.packages:
            return None
        package = self.packages[name]
        match_version = version or package["latestVersion"]
        for distribution in package["distributions"]:
            if distribution["version"] == match_version:
                return distribution["download_url"]

    def get_hash(self, name: str, version: str) -> Optional[str]:
        """从本地获取规则包哈希值"""
        if name not in self.packages:
            return None
        package = self.packages[name]
        match_version = version or package["latestVersion"]
        for distribution in package["distributions"]:
            if distribution["version"] == match_version:
                return distribution["hash"]

    @property
    def uuid(self) -> str:
        """世界树唯一标识"""
        return self._data["metadata"]["uuid"]

    @property
    def packages(self) -> Dict[str, Any]:
        return self._data["packages"]
