from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class UserInfo:
    id: str
    name: str


class BotContext(ABC):
    @abstractmethod
    async def reply(self, text: str, **kwargs) -> None:
        ...

    @abstractmethod
    async def reply_file(
        self,
        data: bytes,
        *,
        filename: str,
        content: str | None = None,
        **kwargs,
    ) -> None:
        ...

    @property
    @abstractmethod
    def locale(self) -> str:
        ...

    @property
    @abstractmethod
    def user(self) -> UserInfo:
        ...
