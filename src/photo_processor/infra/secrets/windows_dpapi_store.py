from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path


class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


class WindowsDPAPISecretStore:
    def __init__(
        self,
        root_dir: Path,
        protect: callable | None = None,
        unprotect: callable | None = None,
    ) -> None:
        self.root_dir = root_dir
        self._protect = protect or _protect_bytes_for_current_user
        self._unprotect = unprotect or _unprotect_bytes_for_current_user

    def load_secret(self, key: str) -> str | None:
        path = self._path_for_key(key)
        if not path.exists():
            return None
        encrypted = path.read_bytes()
        return self._unprotect(encrypted).decode("utf-8")

    def save_secret(self, key: str, value: str) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        path = self._path_for_key(key)
        path.write_bytes(self._protect(value.encode("utf-8")))

    def delete_secret(self, key: str) -> None:
        path = self._path_for_key(key)
        if path.exists():
            path.unlink()

    def _path_for_key(self, key: str) -> Path:
        safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in key)
        return self.root_dir / f"{safe_name}.bin"


def _protect_bytes_for_current_user(data: bytes) -> bytes:
    if not hasattr(ctypes, "windll"):
        raise RuntimeError("Windows DPAPI secret storage is only available on Windows.")

    in_blob = _bytes_to_blob(data)
    out_blob = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    ):
        raise ctypes.WinError()
    try:
        return _blob_to_bytes(out_blob)
    finally:
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)


def _unprotect_bytes_for_current_user(data: bytes) -> bytes:
    if not hasattr(ctypes, "windll"):
        raise RuntimeError("Windows DPAPI secret storage is only available on Windows.")

    in_blob = _bytes_to_blob(data)
    out_blob = DATA_BLOB()
    if not ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        None,
        None,
        None,
        0,
        ctypes.byref(out_blob),
    ):
        raise ctypes.WinError()
    try:
        return _blob_to_bytes(out_blob)
    finally:
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)


def _bytes_to_blob(data: bytes) -> DATA_BLOB:
    buffer = ctypes.create_string_buffer(data)
    blob = DATA_BLOB()
    blob.cbData = len(data)
    blob.pbData = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte))
    blob._buffer = buffer  # type: ignore[attr-defined]
    return blob


def _blob_to_bytes(blob: DATA_BLOB) -> bytes:
    return ctypes.string_at(blob.pbData, blob.cbData)
