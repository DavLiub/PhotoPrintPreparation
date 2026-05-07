from __future__ import annotations

import sys
from pathlib import Path


def load_optional_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            import os

            os.environ.setdefault(key, value)


def resolve_cloud_oauth_env_paths() -> list[Path]:
    candidates = [
        Path.cwd() / "config" / "cloud_oauth.env",
        Path.cwd() / "cloud_oauth.env",
    ]

    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.extend(
            [
                exe_dir / "config" / "cloud_oauth.env",
                exe_dir / "cloud_oauth.env",
            ]
        )
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            meipass_dir = Path(meipass)
            candidates.extend(
                [
                    meipass_dir / "config" / "cloud_oauth.env",
                    meipass_dir / "cloud_oauth.env",
                ]
            )
    else:
        project_root = Path(__file__).resolve().parents[3]
        candidates.extend(
            [
                project_root / "config" / "cloud_oauth.env",
                project_root / "cloud_oauth.env",
            ]
        )

    unique_paths: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        normalized = candidate.resolve(strict=False)
        if normalized in seen:
            continue
        seen.add(normalized)
        unique_paths.append(normalized)
    return unique_paths


def load_cloud_oauth_env() -> None:
    for path in resolve_cloud_oauth_env_paths():
        load_optional_env_file(path)
