"""Filesystem helpers.

Two invariants this module exists to protect:

* **Atomicity.** A generation run that dies halfway must never leave a
  half-written ``.pptx`` or a truncated cached PNG that a later run trusts.
  Everything is written to a temporary file in the *same* directory and then
  ``os.replace``-d, which is atomic on POSIX and on NTFS.
* **Containment.** Paths that arrive from JSON (background images, icons,
  logos) are resolved against a declared root and rejected if they escape it,
  so a template cannot read ``../../../etc/passwd``.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable, Iterator

from config import BASE_DIR, CACHE_DIR, OUTPUT_DIR

_INVALID_NAME_CHARS = '<>:"/\\|?*'
_MAX_STEM_LENGTH = 120


class FileAccessError(OSError):
    """Raised when a path is unusable, unreadable or outside its root."""


# ----------------------------------------------------------------------
# Resolution and containment
# ----------------------------------------------------------------------


def resolve_path(path: str | os.PathLike[str]) -> Path:
    """Expand ``~`` and environment variables, then make the path absolute."""
    text = os.path.expandvars(str(path))
    candidate = Path(text).expanduser()
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate
    return candidate.resolve()


def is_within(path: str | os.PathLike[str], root: str | os.PathLike[str]) -> bool:
    """Return whether ``path`` lies inside ``root`` after resolution."""
    try:
        resolve_path(path).relative_to(resolve_path(root))
    except ValueError:
        return False
    return True


def resolve_within(
    path: str | os.PathLike[str],
    root: str | os.PathLike[str],
    *,
    description: str = "path",
) -> Path:
    """Resolve ``path`` and require that it stay inside ``root``."""
    resolved = resolve_path(path)
    if not is_within(resolved, root):
        raise FileAccessError(
            f"{description} '{path}' resolves outside the permitted "
            f"directory '{resolve_path(root)}'"
        )
    return resolved


def require_file(
    path: str | os.PathLike[str],
    *,
    description: str = "file",
) -> Path:
    """Resolve ``path`` and require that it exist and be a regular file."""
    resolved = resolve_path(path)
    if not resolved.exists():
        raise FileAccessError(f"{description} not found: {resolved}")
    if not resolved.is_file():
        raise FileAccessError(f"{description} is not a file: {resolved}")
    return resolved


def require_directory(
    path: str | os.PathLike[str],
    *,
    description: str = "directory",
) -> Path:
    resolved = resolve_path(path)
    if not resolved.exists():
        raise FileAccessError(f"{description} not found: {resolved}")
    if not resolved.is_dir():
        raise FileAccessError(f"{description} is not a directory: {resolved}")
    return resolved


def ensure_directory(path: str | os.PathLike[str]) -> Path:
    """Create ``path`` and its parents if absent, and return it."""
    resolved = resolve_path(path)
    try:
        resolved.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise FileAccessError(
            f"could not create directory '{resolved}': {error}"
        ) from error
    return resolved


def ensure_parent(path: str | os.PathLike[str]) -> Path:
    resolved = resolve_path(path)
    ensure_directory(resolved.parent)
    return resolved


def output_dir() -> Path:
    return ensure_directory(OUTPUT_DIR)


def cache_dir() -> Path:
    return ensure_directory(CACHE_DIR)


# ----------------------------------------------------------------------
# Names
# ----------------------------------------------------------------------


def sanitize_filename(name: str, *, fallback: str = "untitled") -> str:
    """Reduce arbitrary text to a filename that is legal on every platform."""
    cleaned = "".join(
        "_" if char in _INVALID_NAME_CHARS or ord(char) < 32 else char
        for char in name
    ).strip(" .")
    cleaned = "_".join(cleaned.split())
    if len(cleaned) > _MAX_STEM_LENGTH:
        cleaned = cleaned[:_MAX_STEM_LENGTH].rstrip("_")
    return cleaned or fallback


def with_suffix(path: str | os.PathLike[str], suffix: str) -> Path:
    """Force an extension, adding the leading dot if the caller omitted it."""
    normalised = suffix if suffix.startswith(".") else f".{suffix}"
    return resolve_path(path).with_suffix(normalised)


def unique_path(path: str | os.PathLike[str]) -> Path:
    """Return ``path`` if free, else append ``_1``, ``_2`` ... until it is.

    Used so that regenerating a deck never silently destroys the previous one
    when the caller has asked not to overwrite.
    """
    resolved = resolve_path(path)
    if not resolved.exists():
        return resolved
    stem, suffix, parent = resolved.stem, resolved.suffix, resolved.parent
    index = 1
    while True:
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


# ----------------------------------------------------------------------
# Atomic writes
# ----------------------------------------------------------------------


def atomic_write_bytes(path: str | os.PathLike[str], data: bytes) -> Path:
    """Write ``data`` to ``path`` atomically."""
    target = ensure_parent(path)
    handle, temporary = tempfile.mkstemp(
        dir=str(target.parent), prefix=f".{target.name}.", suffix=".tmp"
    )
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    except OSError as error:
        remove_file(temporary)
        raise FileAccessError(
            f"could not write '{target}': {error}"
        ) from error
    return target


def atomic_write_text(
    path: str | os.PathLike[str],
    text: str,
    *,
    encoding: str = "utf-8",
) -> Path:
    return atomic_write_bytes(path, text.encode(encoding))


def atomic_write_json(
    path: str | os.PathLike[str],
    payload: Any,
    *,
    indent: int = 2,
) -> Path:
    return atomic_write_text(
        path,
        json.dumps(payload, indent=indent, ensure_ascii=False) + "\n",
    )


def read_text(
    path: str | os.PathLike[str],
    *,
    encoding: str = "utf-8",
    description: str = "file",
) -> str:
    resolved = require_file(path, description=description)
    try:
        return resolved.read_text(encoding=encoding)
    except UnicodeDecodeError as error:
        raise FileAccessError(
            f"{description} '{resolved}' is not valid {encoding} text: {error}"
        ) from error
    except OSError as error:
        raise FileAccessError(
            f"could not read '{resolved}': {error}"
        ) from error


def read_bytes(
    path: str | os.PathLike[str],
    *,
    description: str = "file",
) -> bytes:
    resolved = require_file(path, description=description)
    try:
        return resolved.read_bytes()
    except OSError as error:
        raise FileAccessError(
            f"could not read '{resolved}': {error}"
        ) from error


# ----------------------------------------------------------------------
# Removal
# ----------------------------------------------------------------------


def remove_file(path: str | os.PathLike[str]) -> bool:
    """Delete a file, returning whether anything was removed."""
    try:
        Path(path).unlink()
    except FileNotFoundError:
        return False
    except OSError:
        return False
    return True


def remove_directory(path: str | os.PathLike[str]) -> bool:
    resolved = resolve_path(path)
    if not resolved.exists():
        return False
    shutil.rmtree(resolved, ignore_errors=True)
    return True


def clear_directory(
    path: str | os.PathLike[str],
    *,
    pattern: str = "*",
) -> int:
    """Delete the contents of a directory without removing it."""
    resolved = resolve_path(path)
    if not resolved.is_dir():
        return 0
    removed = 0
    for entry in resolved.glob(pattern):
        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=True)
            removed += 1
        elif remove_file(entry):
            removed += 1
    return removed


# ----------------------------------------------------------------------
# Inspection
# ----------------------------------------------------------------------


def file_size(path: str | os.PathLike[str]) -> int:
    try:
        return resolve_path(path).stat().st_size
    except OSError:
        return 0


def directory_size(path: str | os.PathLike[str]) -> int:
    """Total size in bytes of every regular file beneath ``path``."""
    total = 0
    for entry in iter_files(path):
        total += file_size(entry)
    return total


def iter_files(
    path: str | os.PathLike[str],
    *,
    pattern: str = "*",
) -> Iterator[Path]:
    resolved = resolve_path(path)
    if not resolved.is_dir():
        return
    for entry in resolved.rglob(pattern):
        if entry.is_file():
            yield entry


def list_files(
    path: str | os.PathLike[str],
    *,
    extensions: Iterable[str] | None = None,
) -> list[Path]:
    """Sorted regular files directly inside ``path``, optionally filtered."""
    resolved = resolve_path(path)
    if not resolved.is_dir():
        return []
    allowed = (
        None
        if extensions is None
        else {
            item.lower() if item.startswith(".") else f".{item.lower()}"
            for item in extensions
        }
    )
    return sorted(
        entry
        for entry in resolved.iterdir()
        if entry.is_file()
        and (allowed is None or entry.suffix.lower() in allowed)
    )


def human_size(num_bytes: int) -> str:
    """Format a byte count for display in the GUI and logs."""
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0 or unit == "GB":
            precision = 0 if unit == "B" else 1
            return f"{size:.{precision}f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"


__all__ = [
    "FileAccessError",
    "resolve_path",
    "is_within",
    "resolve_within",
    "require_file",
    "require_directory",
    "ensure_directory",
    "ensure_parent",
    "output_dir",
    "cache_dir",
    "sanitize_filename",
    "with_suffix",
    "unique_path",
    "atomic_write_bytes",
    "atomic_write_text",
    "atomic_write_json",
    "read_text",
    "read_bytes",
    "remove_file",
    "remove_directory",
    "clear_directory",
    "file_size",
    "directory_size",
    "iter_files",
    "list_files",
    "human_size",
]