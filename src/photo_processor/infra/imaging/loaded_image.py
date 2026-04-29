from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class LoadedImage:
    image: object
    image_format: str | None

