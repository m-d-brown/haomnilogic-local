from enum import Enum
from typing import TypeVar

T = TypeVar("T", bound="PrettyEnum")

class PrettyEnum(Enum):
    def pretty(self) -> str:
        return self.name.replace("_", " ").title()

    @classmethod
    def from_pretty(cls: type[T], name: str) -> T:
        return cls[name.upper().replace(" ", "_")]
