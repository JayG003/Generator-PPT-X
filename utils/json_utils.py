"""Dependency-free JSON validation helpers.

The project deliberately avoids ``jsonschema``: it adds three transitive
dependencies (one of them a compiled extension) for a feature set we only
partially need, and its default error messages omit the JSON path that makes
a failure actionable.

Every accessor here takes a ``path`` string describing where in the document
the value lives, so a failure deep inside a slide reports
``slides[3].data.series[0].values[2]`` rather than "invalid value".
"""

from __future__ import annotations

from numbers import Real
from typing import Any, Callable, Iterable, Mapping, Sequence, TypeVar

T = TypeVar("T")

JsonValue = Any
JsonObject = Mapping[str, Any]

_MISSING = object()


class JsonValidationError(ValueError):
    """Raised when a JSON document violates the project schema."""

    def __init__(self, path: str, message: str) -> None:
        self.path = path
        self.message = message
        super().__init__(f"{path or '<root>'}: {message}")


def child_path(path: str, key: str | int) -> str:
    """Build the path of a nested member."""
    if isinstance(key, int):
        return f"{path}[{key}]"
    return f"{path}.{key}" if path else key


def _type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, Real):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, Mapping):
        return "object"
    if isinstance(value, Sequence):
        return "array"
    return type(value).__name__


# ----------------------------------------------------------------------
# Presence
# ----------------------------------------------------------------------


def require_object(value: JsonValue, path: str = "") -> JsonObject:
    if not isinstance(value, Mapping):
        raise JsonValidationError(
            path, f"expected an object, got {_type_name(value)}"
        )
    return value


def require_key(obj: JsonObject, key: str, path: str = "") -> Any:
    require_object(obj, path)
    if key not in obj:
        raise JsonValidationError(
            child_path(path, key), "required field is missing"
        )
    return obj[key]


def optional_key(
    obj: JsonObject,
    key: str,
    default: T = None,
    path: str = "",
) -> Any | T:
    require_object(obj, path)
    value = obj.get(key, _MISSING)
    if value is _MISSING or value is None:
        return default
    return value


def reject_unknown_keys(
    obj: JsonObject,
    allowed: Iterable[str],
    path: str = "",
    *,
    strict: bool = False,
) -> list[str]:
    """Report keys outside ``allowed``.

    Unknown keys are ignored by default. Forward compatibility matters more
    than strictness here: a deck authored against a newer schema should still
    open, minus the features this build does not understand. ``strict`` is
    available for the test-suite and for authoring tools.
    """
    unknown = [key for key in obj if key not in set(allowed)]
    if unknown and strict:
        raise JsonValidationError(
            path, f"unknown field(s): {', '.join(sorted(unknown))}"
        )
    return sorted(unknown)


# ----------------------------------------------------------------------
# Scalars
# ----------------------------------------------------------------------


def as_string(
    value: JsonValue,
    path: str = "",
    *,
    allow_empty: bool = True,
    max_length: int | None = None,
) -> str:
    if not isinstance(value, str):
        raise JsonValidationError(
            path, f"expected a string, got {_type_name(value)}"
        )
    if not allow_empty and not value.strip():
        raise JsonValidationError(path, "must not be empty")
    if max_length is not None and len(value) > max_length:
        raise JsonValidationError(
            path, f"must be at most {max_length} characters, got {len(value)}"
        )
    return value


def as_number(
    value: JsonValue,
    path: str = "",
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise JsonValidationError(
            path, f"expected a number, got {_type_name(value)}"
        )
    number = float(value)
    if minimum is not None and number < minimum:
        raise JsonValidationError(path, f"must be >= {minimum}, got {number}")
    if maximum is not None and number > maximum:
        raise JsonValidationError(path, f"must be <= {maximum}, got {number}")
    return number


def as_integer(
    value: JsonValue,
    path: str = "",
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise JsonValidationError(
            path, f"expected an integer, got {_type_name(value)}"
        )
    if float(value) != int(value):
        raise JsonValidationError(path, f"expected a whole number, got {value}")
    number = int(value)
    if minimum is not None and number < minimum:
        raise JsonValidationError(path, f"must be >= {minimum}, got {number}")
    if maximum is not None and number > maximum:
        raise JsonValidationError(path, f"must be <= {maximum}, got {number}")
    return number


def as_boolean(value: JsonValue, path: str = "") -> bool:
    if not isinstance(value, bool):
        raise JsonValidationError(
            path, f"expected a boolean, got {_type_name(value)}"
        )
    return value


def as_enum(
    value: JsonValue,
    allowed: Sequence[str],
    path: str = "",
    *,
    case_sensitive: bool = False,
) -> str:
    text = as_string(value, path)
    candidate = text if case_sensitive else text.lower()
    table = {item if case_sensitive else item.lower(): item for item in allowed}
    if candidate not in table:
        raise JsonValidationError(
            path,
            f"must be one of {', '.join(allowed)}; got '{text}'",
        )
    return table[candidate]


# ----------------------------------------------------------------------
# Collections
# ----------------------------------------------------------------------


def as_array(
    value: JsonValue,
    path: str = "",
    *,
    min_items: int = 0,
    max_items: int | None = None,
) -> list[Any]:
    if isinstance(value, (str, bytes, Mapping)) or not isinstance(
        value, Sequence
    ):
        raise JsonValidationError(
            path, f"expected an array, got {_type_name(value)}"
        )
    items = list(value)
    if len(items) < min_items:
        raise JsonValidationError(
            path, f"must contain at least {min_items} item(s), got {len(items)}"
        )
    if max_items is not None and len(items) > max_items:
        raise JsonValidationError(
            path, f"must contain at most {max_items} item(s), got {len(items)}"
        )
    return items


def map_array(
    value: JsonValue,
    parser: Callable[[Any, str], T],
    path: str = "",
    *,
    min_items: int = 0,
    max_items: int | None = None,
) -> list[T]:
    """Parse every element, tagging failures with their index."""
    items = as_array(value, path, min_items=min_items, max_items=max_items)
    return [
        parser(item, child_path(path, index))
        for index, item in enumerate(items)
    ]


def as_number_array(
    value: JsonValue,
    path: str = "",
    *,
    min_items: int = 0,
    minimum: float | None = None,
) -> list[float]:
    return map_array(
        value,
        lambda item, item_path: as_number(item, item_path, minimum=minimum),
        path,
        min_items=min_items,
    )


def as_string_array(
    value: JsonValue,
    path: str = "",
    *,
    min_items: int = 0,
    allow_empty: bool = True,
) -> list[str]:
    return map_array(
        value,
        lambda item, item_path: as_string(
            item, item_path, allow_empty=allow_empty
        ),
        path,
        min_items=min_items,
    )


def as_point(value: JsonValue, path: str = "") -> tuple[float, float]:
    items = as_array(value, path, min_items=2, max_items=2)
    return (
        as_number(items[0], child_path(path, 0)),
        as_number(items[1], child_path(path, 1)),
    )


def as_point_array(
    value: JsonValue,
    path: str = "",
    *,
    min_items: int = 0,
) -> list[tuple[float, float]]:
    return map_array(value, as_point, path, min_items=min_items)


# ----------------------------------------------------------------------
# Cross-field checks
# ----------------------------------------------------------------------


def require_equal_length(
    first: Sequence[Any],
    second: Sequence[Any],
    first_path: str,
    second_path: str,
) -> None:
    if len(first) != len(second):
        raise JsonValidationError(
            second_path,
            f"must have the same number of items as {first_path} "
            f"({len(first)}), got {len(second)}",
        )


def require_one_of(
    obj: JsonObject,
    keys: Sequence[str],
    path: str = "",
) -> str:
    present = [key for key in keys if obj.get(key) is not None]
    if not present:
        raise JsonValidationError(
            path, f"exactly one of {', '.join(keys)} is required"
        )
    if len(present) > 1:
        raise JsonValidationError(
            path,
            f"only one of {', '.join(keys)} may be set; "
            f"got {', '.join(present)}",
        )
    return present[0]


def as_color(value: JsonValue, path: str = "") -> tuple[int, int, int]:
    """Accept ``"#RRGGBB"``, ``"#RGB"`` or ``[r, g, b]``."""
    if isinstance(value, str):
        text = value.strip().lstrip("#")
        if len(text) == 3:
            text = "".join(char * 2 for char in text)
        if len(text) != 6:
            raise JsonValidationError(
                path, f"expected a hex colour like '#2196F3', got '{value}'"
            )
        try:
            return (
                int(text[0:2], 16),
                int(text[2:4], 16),
                int(text[4:6], 16),
            )
        except ValueError as error:
            raise JsonValidationError(
                path, f"invalid hex colour '{value}'"
            ) from error

    channels = as_array(value, path, min_items=3, max_items=3)
    return (
        as_integer(channels[0], child_path(path, 0), minimum=0, maximum=255),
        as_integer(channels[1], child_path(path, 1), minimum=0, maximum=255),
        as_integer(channels[2], child_path(path, 2), minimum=0, maximum=255),
    )


__all__ = [
    "JsonValidationError",
    "JsonObject",
    "JsonValue",
    "child_path",
    "require_object",
    "require_key",
    "optional_key",
    "reject_unknown_keys",
    "as_string",
    "as_number",
    "as_integer",
    "as_boolean",
    "as_enum",
    "as_array",
    "map_array",
    "as_number_array",
    "as_string_array",
    "as_point",
    "as_point_array",
    "require_equal_length",
    "require_one_of",
    "as_color",
]