from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ImageInfo:
    width: int
    height: int
    mode: str
    image_format: str | None = None

    @property
    def size(self) -> tuple[int, int]:
        return self.width, self.height

