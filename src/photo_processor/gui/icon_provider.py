from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path


def _bundle_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[2]


def _asset_path(name: str) -> Path:
    return _bundle_root() / "photo_processor" / "gui" / "assets" / name


@lru_cache(maxsize=8)
def app_icon_path() -> str:
    return str(_asset_path("app_camera.svg"))


@lru_cache(maxsize=8)
def help_icon_path() -> str:
    return str(_asset_path("help_circle.svg"))


@lru_cache(maxsize=8)
def about_icon_path() -> str:
    return str(_asset_path("about_alert.svg"))


@lru_cache(maxsize=8)
def flag_en_path() -> str:
    return str(_asset_path("flag_en.svg"))


@lru_cache(maxsize=8)
def flag_ru_path() -> str:
    return str(_asset_path("flag_ru.svg"))


@lru_cache(maxsize=8)
def flag_he_path() -> str:
    return str(_asset_path("flag_he.svg"))


def build_icon(path: str):
    try:
        from PySide6.QtGui import QIcon
    except ImportError:  # pragma: no cover - depends on environment
        raise RuntimeError("PySide6 is required to construct GUI icons.")

    return QIcon(path)
