from __future__ import annotations

from dataclasses import dataclass

from photo_processor.config.translations import TRANSLATIONS


@dataclass(slots=True)
class Translator:
    language: str = "en"

    def set_language(self, language: str) -> None:
        if language in TRANSLATIONS:
            self.language = language

    def text(self, key: str) -> str:
        language_map = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        return language_map.get(key, TRANSLATIONS["en"].get(key, key))
