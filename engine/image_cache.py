"""Content-addressed cache for rendered diagrams and graphs.

Why content-addressed
---------------------
The key is a hash of *what was rendered* -- the renderer name plus its fully
normalised parameters plus the output size and DPI -- never a slide index. A
diagram repeated across forty revision slides therefore renders once, and a
deck regenerated after an unrelated text edit reuses every image from the
previous run.

Two tiers
---------
* **Memory** -- an LRU of PNG byte strings, bounded by both entry count and
  total bytes so a deck full of large figures cannot exhaust an 8 GB laptop.
* **Disk** -- files under ``output/.cache``, surviving between runs.

Only encoded PNG bytes are stored, never matplotlib figures. A cached figure
would keep its Agg canvas and the whole pyplot state alive; a few hundred of
those is gigabytes. PNG bytes for a 200 dpi diagram are tens of kilobytes.

Normalisation
-------------
``build_key`` sorts mappings and coerces integral floats so that ``{"a": 1,
"b": 2}`` and ``{"b": 2.0, "a": 1}`` hash identically. Without this the hit
rate collapses on decks whose JSON was machine-generated with unstable key
order.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Final, Mapping, Sequence

from config import (
    CACHE_DIR,
    IMAGE_CACHE_ENABLED,
    IMAGE_CACHE_MAX_BYTES,
    IMAGE_CACHE_MAX_ENTRIES,
)
from utils.file_utils import (
    atomic_write_bytes,
    ensure_directory,
    file_size,
    human_size,
    iter_files,
    remove_file,
)

_HASH_LENGTH: Final[int] = 16
_KEY_ENCODING: Final[str] = "utf-8"
_CACHE_SUFFIX: Final[str] = ".png"


@dataclass(slots=True)
class CacheStats:
    """Counters for diagnostics; cheap enough to keep on always."""

    memory_hits: int = 0
    disk_hits: int = 0
    misses: int = 0
    evictions: int = 0
    stored_bytes: int = 0

    @property
    def lookups(self) -> int:
        return self.memory_hits + self.disk_hits + self.misses

    @property
    def hit_rate(self) -> float:
        return 0.0 if not self.lookups else (
            (self.memory_hits + self.disk_hits) / self.lookups
        )

    def describe(self) -> str:
        return (
            f"{self.lookups} lookup(s), {self.hit_rate:.0%} hit rate "
            f"({self.memory_hits} memory, {self.disk_hits} disk, "
            f"{self.misses} miss), {human_size(self.stored_bytes)} held, "
            f"{self.evictions} eviction(s)"
        )


def _normalise(value: Any) -> Any:
    """Reduce a value to a form whose JSON encoding is order-independent."""
    if isinstance(value, Mapping):
        return {str(key): _normalise(value[key]) for key in sorted(value, key=str)}
    if isinstance(value, (list, tuple)):
        return [_normalise(item) for item in value]
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else round(value, 9)
    if isinstance(value, (int, str)):
        return value
    if isinstance(value, Path):
        return str(value)
    return repr(value)


def build_key(namespace: str, *parts: Any, **fields: Any) -> str:
    """Build a stable cache key from a renderer name and its inputs.

    ``namespace`` should identify the renderer (``"diagram:geometry.ladder"``,
    ``"graph:bar"``). Positional ``parts`` and keyword ``fields`` carry the
    parameters. Anything that changes the pixels -- size, DPI, theme colours --
    must be passed in, or two different images will collide on one key.
    """
    if not namespace:
        raise ValueError("cache namespace must not be empty")

    payload = {
        "ns": namespace,
        "args": [_normalise(part) for part in parts],
        "kw": _normalise(fields),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.blake2b(
        encoded.encode(_KEY_ENCODING), digest_size=_HASH_LENGTH
    ).hexdigest()
    return f"{_safe_namespace(namespace)}-{digest}"


def _safe_namespace(namespace: str) -> str:
    """Keep the namespace legible in filenames without making it unsafe."""
    cleaned = "".join(
        char if char.isalnum() or char in "-_." else "_" for char in namespace
    )
    return cleaned[:48].strip("_") or "cache"


class ImageCache:
    """Two-tier LRU cache of encoded PNG bytes.

    Instances are thread-safe. The project renders on one thread today, but the
    GUI runs generation on a worker and a future batch mode may fan out; a
    single lock costs nothing measurable against a matplotlib render.
    """

    def __init__(
        self,
        directory: str | os.PathLike[str] = CACHE_DIR,
        *,
        enabled: bool = IMAGE_CACHE_ENABLED,
        max_entries: int = IMAGE_CACHE_MAX_ENTRIES,
        max_bytes: int = IMAGE_CACHE_MAX_BYTES,
        use_disk: bool = True,
    ) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be at least 1")
        if max_bytes < 1:
            raise ValueError("max_bytes must be at least 1")

        self.enabled = enabled
        self.use_disk = use_disk
        self.max_entries = max_entries
        self.max_bytes = max_bytes
        self.stats = CacheStats()

        self._directory = Path(directory)
        self._memory: OrderedDict[str, bytes] = OrderedDict()
        self._memory_bytes = 0
        self._lock = threading.RLock()

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------

    @property
    def directory(self) -> Path:
        return self._directory

    def path_for(self, key: str) -> Path:
        """Absolute path a key maps to on disk, whether or not it exists."""
        return self._directory / f"{key}{_CACHE_SUFFIX}"

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get(self, key: str) -> bytes | None:
        """Return cached PNG bytes, promoting a disk hit into memory."""
        if not self.enabled:
            return None

        with self._lock:
            cached = self._memory.get(key)
            if cached is not None:
                self._memory.move_to_end(key)
                self.stats.memory_hits += 1
                return cached

        if not self.use_disk:
            with self._lock:
                self.stats.misses += 1
            return None

        path = self.path_for(key)
        try:
            data = path.read_bytes()
        except OSError:
            with self._lock:
                self.stats.misses += 1
            return None

        with self._lock:
            self.stats.disk_hits += 1
            self._remember(key, data)
        return data

    def has(self, key: str) -> bool:
        with self._lock:
            if key in self._memory:
                return True
        return self.use_disk and self.path_for(key).is_file()

    # ------------------------------------------------------------------
    # Storage
    # ------------------------------------------------------------------

    def put(self, key: str, data: bytes) -> Path | None:
        """Store PNG bytes; returns the disk path when one was written."""
        if not self.enabled or not data:
            return None

        with self._lock:
            self._remember(key, data)
            self.stats.stored_bytes += len(data)

        if not self.use_disk:
            return None

        ensure_directory(self._directory)
        return atomic_write_bytes(self.path_for(key), data)

    def get_or_create(
        self,
        key: str,
        producer: Callable[[], bytes],
    ) -> bytes:
        """Return the cached image, or call ``producer`` and cache its result.

        This is the only method renderers should need. Keeping the miss path
        inside the cache means no caller can forget to store what it rendered.
        """
        cached = self.get(key)
        if cached is not None:
            return cached

        data = producer()
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError(
                f"producer for '{key}' returned {type(data).__name__}, "
                "expected PNG bytes"
            )
        if not data:
            raise ValueError(f"producer for '{key}' returned no image data")

        payload = bytes(data)
        self.put(key, payload)
        return payload

    def get_or_create_file(
        self,
        key: str,
        producer: Callable[[], bytes],
    ) -> Path:
        """Like :meth:`get_or_create` but guarantees a file on disk.

        ``python-pptx`` accepts a file path or a stream; a path lets it read
        the image lazily instead of holding every picture in memory at once,
        which is the difference that keeps large decks flat in RSS.
        """
        path = self.path_for(key)
        if self.enabled and self.use_disk and path.is_file():
            with self._lock:
                self.stats.disk_hits += 1
            return path

        data = self.get_or_create(key, producer)
        ensure_directory(self._directory)
        return atomic_write_bytes(path, data)

    # ------------------------------------------------------------------
    # Eviction
    # ------------------------------------------------------------------

    def _remember(self, key: str, data: bytes) -> None:
        """Insert into the memory tier and evict until within both bounds."""
        existing = self._memory.pop(key, None)
        if existing is not None:
            self._memory_bytes -= len(existing)

        self._memory[key] = data
        self._memory_bytes += len(data)
        self._evict()

    def _evict(self) -> None:
        while self._memory and (
            len(self._memory) > self.max_entries
            or self._memory_bytes > self.max_bytes
        ):
            _, evicted = self._memory.popitem(last=False)
            self._memory_bytes -= len(evicted)
            self.stats.evictions += 1

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def release_memory(self) -> None:
        """Drop the memory tier, keeping disk entries.

        Called between decks so a long-running GUI session does not accumulate
        images from presentations the user has finished with.
        """
        with self._lock:
            self._memory.clear()
            self._memory_bytes = 0

    def clear(self, *, disk: bool = True) -> int:
        """Empty the cache; returns the number of disk files removed."""
        self.release_memory()
        if not disk:
            return 0
        removed = 0
        for entry in iter_files(self._directory, pattern=f"*{_CACHE_SUFFIX}"):
            if remove_file(entry):
                removed += 1
        return removed

    def prune(self, keep: Sequence[str] | None = None) -> int:
        """Delete disk entries whose key is not in ``keep``.

        Run after a successful generation with the keys that deck used, so the
        cache directory tracks current templates instead of growing forever.
        """
        if not self.use_disk:
            return 0
        wanted = set(keep or ())
        removed = 0
        for entry in iter_files(self._directory, pattern=f"*{_CACHE_SUFFIX}"):
            if entry.stem not in wanted and remove_file(entry):
                removed += 1
        return removed

    def disk_usage(self) -> int:
        return sum(
            file_size(entry)
            for entry in iter_files(self._directory, pattern=f"*{_CACHE_SUFFIX}")
        )

    def memory_usage(self) -> int:
        with self._lock:
            return self._memory_bytes

    def describe(self) -> str:
        return (
            f"ImageCache({'on' if self.enabled else 'off'}) "
            f"{len(self._memory)}/{self.max_entries} in memory, "
            f"{human_size(self.memory_usage())} resident -- {self.stats.describe()}"
        )

    def __len__(self) -> int:
        with self._lock:
            return len(self._memory)

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and self.has(key)


_default_cache: ImageCache | None = None
_default_lock = threading.Lock()


def default_cache() -> ImageCache:
    """Process-wide cache shared by every renderer.

    Lazily created so that merely importing the engine does not touch the
    filesystem -- which matters for the test-suite and for read-only installs.
    """
    global _default_cache
    if _default_cache is None:
        with _default_lock:
            if _default_cache is None:
                _default_cache = ImageCache()
    return _default_cache


__all__ = [
    "CacheStats",
    "ImageCache",
    "build_key",
    "default_cache",
]