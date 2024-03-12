from pathlib import Path
from ipm.const import INDEX_PATH
from ipm.exceptions import LockLoadFailed
from ipm.models.lock import PackageLock

import tomlkit
import requests
import tempfile
import shutil


class Yggdrasil:
    """此对象内所有方法均为示例方法，可以按照需求和开发奇怪进行微调"""

    def __init__(self, index: str) -> None:
        self.index = index.rstrip("/") + "/"
        self._data = self.read()

    def read(self) -> tomlkit.TOMLDocument:
        """示例方法，读取一个本地的世界树索引文件"""
        if not self._source_path.exists():
            self._source_path.parent.mkdir(parents=True, exist_ok=True)
            return tomlkit.document()
        return tomlkit.load(self._source_path.open("r", encoding="utf-8"))

    def dump(self) -> None:
        """示例方法，将修改保存在本地"""
        tomlkit.dump(self._data, self._source_path.open("w", encoding="utf-8"))

    @staticmethod
    def check(source_path: Path):
        """检查一个索引文件是否合法"""
        raise NotImplementedError

    def sync(self):
        """示例方法，下载或同步索引文件"""
        lock_bytes = requests.get(
            self.index + "infini.lock"
        ).content  # 索引文件地址，这里的lock仅作示例

        temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir.name).resolve()
        temp_lock_path = temp_path / "infini.lock"  # 索引文件地址，这里的lock仅作示例

        temp_lock_file = temp_lock_path.open("wb")
        temp_lock_file.write(lock_bytes)
        temp_lock_file.close()

        Yggdrasil.check(temp_lock_path)  # 检查索引文件合法性

        temp_lock = PackageLock(temp_lock_path)

        if "uuid" not in temp_lock.metadata.keys():
            temp_dir.cleanup()
            raise LockLoadFailed(f"地址[{self.index}]不是合法的世界树服务器.")

        self._source_path = INDEX_PATH / temp_lock.metadata["uuid"]
        self._source_path.mkdir(parents=True, exist_ok=True)

        shutil.copy2(temp_lock_path, self._source_path)
        temp_dir.cleanup()

    def get_url(self, name: str, version: str) -> str:
        """从本地读取规则包下载链接"""
        raise NotImplementedError

    def get_hash(self, name: str, version: str) -> str:
        """从本地获取规则包哈希值"""
        raise NotImplementedError

    @property
    def uuid(self) -> str:
        """世界树唯一标识"""
        raise NotImplementedError
