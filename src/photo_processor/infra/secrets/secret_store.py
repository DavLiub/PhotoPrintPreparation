from __future__ import annotations

from typing import Protocol


class SecretStore(Protocol):
    def load_secret(self, key: str) -> str | None:
        ...

    def save_secret(self, key: str, value: str) -> None:
        ...

    def delete_secret(self, key: str) -> None:
        ...
