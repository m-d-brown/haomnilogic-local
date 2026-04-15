from __future__ import annotations

from typing import Any, Generator


class DiscoveryDict(dict[tuple[int, int], Any]):
    """Custom dict that yields 3-tuples from items() (id1, id2, value)."""

    def items(self) -> Generator[tuple[int, int, Any], None, None]:
        for key, value in super().items():
            yield (key[0], key[1], value)

    def __iter__(self) -> Generator[Any, None, None]:
        """Iterate over values, not keys, to match list-like behavior if needed."""
        for value in self.values():
            yield value
