from typing import Optional, Union
from ipm.const import INDEX
from ipm.exceptions import ProjectError
from ipm.models.index import Yggdrasil
from ipm.typing import Dict, List


class Requirement:
    name: str
    version: str
    path: Optional[str]
    yggdrasil: Yggdrasil
    url: Optional[str]
    hash: Optional[str]

    def __init__(
        self,
        name: str,
        version: str,
        url: Optional[str] = None,
        path: Optional[str] = None,
        yggdrasil: Optional[Yggdrasil] = None,
        hash: Optional[str] = None,
    ) -> None:
        from ipm.models.lock import PackageLock

        global_lock = PackageLock()
        yggdrasil = yggdrasil or global_lock.get_yggdrasil_by_index(INDEX)
        if not yggdrasil:
            raise ProjectError("未能找到任何世界树地址，请先添加一个世界树地址。")
        self.name = name
        self.version = version
        self.path = path
        self.url = url or yggdrasil.get_url(name, version)
        if not self.url:
            raise ProjectError(
                f"规则包 [bold red]{name}[/] 不存在版本 [bold yellow]{version}[/]"
            )
        self.yggdrasil = yggdrasil
        self.hash = hash

    def __eq__(self, __value: "Requirement") -> bool:
        return (
            __value.name == self.name
            and __value.version == self.version
            and __value.yggdrasil.index == self.yggdrasil.index
        )

    def is_local(self) -> bool:
        return bool(self.path)

    def as_dict(self) -> dict:
        if self.is_local():
            return {
                "name": self.name,
                "version": self.version,
                "path": self.path,
            }
        else:
            return {
                "name": self.name,
                "version": self.version,
                "yggdrasil": self.yggdrasil.index,
                "url": self.url,
            }


class Requirements(List[Requirement]):
    def __init__(
        self,
        requirements: Dict[str, Union[Dict, str]],
        yggdrasils: Optional[Dict[str, Optional[Yggdrasil]]] = None,
    ) -> None:
        from ipm.models.lock import PackageLock

        global_lock = PackageLock()
        url = path = yggdrasil = version = None
        for name, requirement in requirements.items():
            if isinstance(requirement, str):
                self.append(Requirement(name=name, version=requirement))
            else:
                for key, value in requirement.items():
                    if key == "index":
                        yggdrasil = global_lock.get_yggdrasil_by_index(value)
                    elif key == "url":
                        url = value
                    elif key == "yggdrasil":
                        yggdrasil = (yggdrasils or {}).get(value)
                        if not yggdrasil:
                            raise ValueError(f"未知的世界树标识符: '{value}'")
                    elif key == "path":
                        path = value
                    elif key == "version":
                        version = value
                    else:
                        raise ValueError(f"未知的依赖项键值: '{key}'")
                self.append(
                    Requirement(
                        name=name,
                        version=version or "*",
                        path=path,
                        url=url,
                        yggdrasil=yggdrasil,
                    )
                )
