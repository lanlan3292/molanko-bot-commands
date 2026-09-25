from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class UserInfo:
    id: str
    name: str
    username: str | None = None
    display_name: str | None = None

    def __post_init__(self):
        if self.username is None:
            self.username = self.id

        if self.display_name is None:
            self.display_name = self.name


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
