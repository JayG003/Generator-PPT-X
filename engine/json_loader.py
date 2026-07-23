"""Read and validate deck JSON into immutable, typed models.

Layering
--------
This is the *top* of the pipeline. It depends on ``utils`` and ``config`` and
on nothing else in the project: it must never import a renderer, a diagram or
matplotlib, so that a document can be validated without paying for the
rendering stack.

Validation depth
----------------
The loader validates *structure* -- the parts every consumer relies on: the
slide list, the discriminator field, titles, notes, and the shared shape of
graph data. It deliberately does **not** validate diagram ``params`` or graph
``options``, which stay as plain dictionaries and are checked by the module
that owns them. That keeps the loader from growing a branch for every one of
the hundreds of diagram types this project expects to carry; the trade-off is
that a bad parameter surfaces at render time rather than load time, which is
why every diagram is required to register a parameter schema of its own.

Compatibility
-------------
``schema_version`` is checked against ``SUPPORTED_SCHEMA_VERSIONS``. Fields
this build does not recognise are collected into ``Deck.warnings`` rather than
rejected, so a deck authored against a newer schema still opens.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Final, Mapping, Sequence

from config import SCHEMA_VERSION, SUPPORTED_SCHEMA_VERSIONS
from utils.file_utils import FileAccessError, read_text, resolve_path
from utils.json_utils import (
    JsonObject,
    JsonValidationError,
    as_array,
    as_boolean,
    as_color,
    as_enum,
    as_integer,
    as_number,
    as_number_array,
    as_string,
    as_string_array,
    child_path,
    map_array,
    optional_key,
    reject_unknown_keys,
    require_equal_length,
    require_key,
    require_object,
)

# ----------------------------------------------------------------------
# Vocabulary
# ----------------------------------------------------------------------

SLIDE_TYPES: Final[tuple[str, ...]] = (
    "title",
    "theory",
    "diagram",
    "graph",
    "table",
    "question",
)

GRAPH_TYPES: Final[tuple[str, ...]] = (
    "bar",
    "line",
    "pie",
    "scatter",
    "histogram",
)

BLOCK_STYLES: Final[tuple[str, ...]] = (
    "text",
    "bullet",
    "number",
    "note",
    "code",
    "formula",
)

QUESTION_KINDS: Final[tuple[str, ...]] = (
    "short",
    "long",
    "mcq",
    "truefalse",
    "numerical",
)

ALIGNMENTS: Final[tuple[str, ...]] = ("left", "center", "right")

MAX_BLOCK_LEVEL: Final[int] = 4
MAX_TABLE_COLUMNS: Final[int] = 12
MAX_TITLE_LENGTH: Final[int] = 300


class DeckLoadError(ValueError):
    """Raised when a deck document cannot be read or parsed."""


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class DeckMeta:
    title: str = ""
    subtitle: str = ""
    author: str = ""
    subject: str = ""
    institution: str = ""
    date: str = ""


@dataclass(frozen=True, slots=True)
class DeckTheme:
    """Optional per-deck overrides applied on top of ``config`` defaults."""

    primary: tuple[int, int, int] | None = None
    secondary: tuple[int, int, int] | None = None
    accent: tuple[int, int, int] | None = None
    text: tuple[int, int, int] | None = None
    background_image: str | None = None
    font_family: str | None = None


@dataclass(frozen=True, slots=True)
class ContentBlock:
    """One paragraph of body text with an indent level and a style."""

    text: str
    style: str = "bullet"
    level: int = 0
    bold: bool = False
    italic: bool = False


@dataclass(frozen=True, slots=True)
class GraphSeries:
    name: str
    values: tuple[float, ...] = ()
    points: tuple[tuple[float, float], ...] = ()
    color: tuple[int, int, int] | None = None


@dataclass(frozen=True, slots=True)
class GraphData:
    """Shared container for every graph family.

    Which members are populated depends on the graph type; each graph module
    asserts what it needs. ``labels`` drives categorical axes (bar, pie),
    ``series[].values`` carries magnitudes, ``series[].points`` carries xy
    pairs (line, scatter), and ``values`` carries a raw sample (histogram).
    """

    labels: tuple[str, ...] = ()
    series: tuple[GraphSeries, ...] = ()
    values: tuple[float, ...] = ()


@dataclass(frozen=True, slots=True)
class QuestionItem:
    text: str
    kind: str = "short"
    options: tuple[str, ...] = ()
    answer: str = ""
    marks: int = 0
    explanation: str = ""


@dataclass(frozen=True, slots=True)
class Slide:
    """A single slide.

    ``payload`` holds the type-specific model produced by the parser for this
    slide type. The dispatcher selects a renderer on ``type`` alone and hands
    the payload over without inspecting it.
    """

    type: str
    index: int
    title: str = ""
    subtitle: str = ""
    notes: str = ""
    background: str | None = None
    payload: Any = None


@dataclass(frozen=True, slots=True)
class TitlePayload:
    author: str = ""
    institution: str = ""
    date: str = ""


@dataclass(frozen=True, slots=True)
class TheoryPayload:
    blocks: tuple[ContentBlock, ...] = ()
    columns: int = 1
    image: str | None = None


@dataclass(frozen=True, slots=True)
class DiagramPayload:
    """``name`` is a dotted ``module.function`` key into the diagram registry."""

    name: str
    params: Mapping[str, Any] = field(default_factory=dict)
    caption: str = ""
    width: float | None = None
    height: float | None = None


@dataclass(frozen=True, slots=True)
class GraphPayload:
    kind: str
    data: GraphData
    options: Mapping[str, Any] = field(default_factory=dict)
    caption: str = ""


@dataclass(frozen=True, slots=True)
class TablePayload:
    headers: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()
    column_widths: tuple[float, ...] = ()
    align: str = "left"
    caption: str = ""


@dataclass(frozen=True, slots=True)
class QuestionPayload:
    items: tuple[QuestionItem, ...] = ()
    show_answers: bool = False
    numbered: bool = True


@dataclass(frozen=True, slots=True)
class Deck:
    schema_version: str
    meta: DeckMeta
    theme: DeckTheme
    slides: tuple[Slide, ...]
    warnings: tuple[str, ...] = ()

    def __len__(self) -> int:
        return len(self.slides)


# ----------------------------------------------------------------------
# Shared field parsing
# ----------------------------------------------------------------------

_COMMON_SLIDE_KEYS: Final[tuple[str, ...]] = (
    "type",
    "title",
    "subtitle",
    "notes",
    "background",
)


def _optional_string(obj: JsonObject, key: str, path: str) -> str:
    value = optional_key(obj, key, "", path)
    return as_string(value, child_path(path, key))


def _optional_color(
    obj: JsonObject, key: str, path: str
) -> tuple[int, int, int] | None:
    value = optional_key(obj, key, None, path)
    if value is None:
        return None
    return as_color(value, child_path(path, key))


def _parse_meta(value: Any, path: str) -> DeckMeta:
    if value is None:
        return DeckMeta()
    obj = require_object(value, path)
    return DeckMeta(
        title=_optional_string(obj, "title", path),
        subtitle=_optional_string(obj, "subtitle", path),
        author=_optional_string(obj, "author", path),
        subject=_optional_string(obj, "subject", path),
        institution=_optional_string(obj, "institution", path),
        date=_optional_string(obj, "date", path),
    )


def _parse_theme(value: Any, path: str) -> DeckTheme:
    if value is None:
        return DeckTheme()
    obj = require_object(value, path)
    background = optional_key(obj, "background_image", None, path)
    font = optional_key(obj, "font_family", None, path)
    return DeckTheme(
        primary=_optional_color(obj, "primary", path),
        secondary=_optional_color(obj, "secondary", path),
        accent=_optional_color(obj, "accent", path),
        text=_optional_color(obj, "text", path),
        background_image=(
            None
            if background is None
            else as_string(
                background, child_path(path, "background_image"),
                allow_empty=False,
            )
        ),
        font_family=(
            None
            if font is None
            else as_string(
                font, child_path(path, "font_family"), allow_empty=False
            )
        ),
    )


def _parse_block(value: Any, path: str) -> ContentBlock:
    """Accept a bare string as shorthand for a level-0 bullet."""
    if isinstance(value, str):
        return ContentBlock(text=value)

    obj = require_object(value, path)
    return ContentBlock(
        text=as_string(require_key(obj, "text", path), child_path(path, "text")),
        style=as_enum(
            optional_key(obj, "style", "bullet", path),
            BLOCK_STYLES,
            child_path(path, "style"),
        ),
        level=as_integer(
            optional_key(obj, "level", 0, path),
            child_path(path, "level"),
            minimum=0,
            maximum=MAX_BLOCK_LEVEL,
        ),
        bold=as_boolean(
            optional_key(obj, "bold", False, path), child_path(path, "bold")
        ),
        italic=as_boolean(
            optional_key(obj, "italic", False, path), child_path(path, "italic")
        ),
    )


def _parse_series(value: Any, path: str) -> GraphSeries:
    obj = require_object(value, path)
    raw_values = optional_key(obj, "values", None, path)
    raw_points = optional_key(obj, "points", None, path)

    values: tuple[float, ...] = ()
    points: tuple[tuple[float, float], ...] = ()

    if raw_values is not None:
        values = tuple(as_number_array(raw_values, child_path(path, "values")))
    if raw_points is not None:
        points = tuple(
            (pair[0], pair[1])
            for pair in map_array(
                raw_points,
                lambda item, item_path: (
                    as_number(
                        as_array(item, item_path, min_items=2, max_items=2)[0],
                        child_path(item_path, 0),
                    ),
                    as_number(
                        as_array(item, item_path, min_items=2, max_items=2)[1],
                        child_path(item_path, 1),
                    ),
                ),
                child_path(path, "points"),
            )
        )

    if not values and not points:
        raise JsonValidationError(
            path, "a series must define either 'values' or 'points'"
        )

    return GraphSeries(
        name=_optional_string(obj, "name", path),
        values=values,
        points=points,
        color=_optional_color(obj, "color", path),
    )


def _parse_graph_data(value: Any, path: str) -> GraphData:
    obj = require_object(value, path)

    labels = tuple(
        as_string_array(optional_key(obj, "labels", [], path),
                        child_path(path, "labels"))
    )
    values = tuple(
        as_number_array(optional_key(obj, "values", [], path),
                        child_path(path, "values"))
    )

    raw_series = optional_key(obj, "series", None, path)
    if raw_series is None:
        series: tuple[GraphSeries, ...] = ()
    else:
        series = tuple(
            map_array(
                raw_series, _parse_series, child_path(path, "series"),
                min_items=1,
            )
        )

    if not series and not values:
        raise JsonValidationError(
            path, "graph data must define either 'series' or 'values'"
        )

    if labels:
        for index, item in enumerate(series):
            if item.values:
                require_equal_length(
                    labels,
                    item.values,
                    child_path(path, "labels"),
                    child_path(child_path(path, "series"), index) + ".values",
                )

    return GraphData(labels=labels, series=series, values=values)


def _parse_question(value: Any, path: str) -> QuestionItem:
    if isinstance(value, str):
        return QuestionItem(text=value)

    obj = require_object(value, path)
    kind = as_enum(
        optional_key(obj, "kind", "short", path),
        QUESTION_KINDS,
        child_path(path, "kind"),
    )
    options = tuple(
        as_string_array(
            optional_key(obj, "options", [], path),
            child_path(path, "options"),
        )
    )
    if kind == "mcq" and len(options) < 2:
        raise JsonValidationError(
            child_path(path, "options"),
            "an 'mcq' question requires at least two options",
        )

    return QuestionItem(
        text=as_string(
            require_key(obj, "text", path),
            child_path(path, "text"),
            allow_empty=False,
        ),
        kind=kind,
        options=options,
        answer=_optional_string(obj, "answer", path),
        marks=as_integer(
            optional_key(obj, "marks", 0, path),
            child_path(path, "marks"),
            minimum=0,
        ),
        explanation=_optional_string(obj, "explanation", path),
    )


# ----------------------------------------------------------------------
# Slide payload parsers
# ----------------------------------------------------------------------


def _parse_title_payload(obj: JsonObject, path: str) -> TitlePayload:
    return TitlePayload(
        author=_optional_string(obj, "author", path),
        institution=_optional_string(obj, "institution", path),
        date=_optional_string(obj, "date", path),
    )


def _parse_theory_payload(obj: JsonObject, path: str) -> TheoryPayload:
    raw_body = optional_key(obj, "body", [], path)
    image = optional_key(obj, "image", None, path)
    return TheoryPayload(
        blocks=tuple(
            map_array(raw_body, _parse_block, child_path(path, "body"))
        ),
        columns=as_integer(
            optional_key(obj, "columns", 1, path),
            child_path(path, "columns"),
            minimum=1,
            maximum=2,
        ),
        image=(
            None
            if image is None
            else as_string(
                image, child_path(path, "image"), allow_empty=False
            )
        ),
    )


def _parse_diagram_payload(obj: JsonObject, path: str) -> DiagramPayload:
    name = as_string(
        require_key(obj, "diagram", path),
        child_path(path, "diagram"),
        allow_empty=False,
    )
    if "." not in name:
        raise JsonValidationError(
            child_path(path, "diagram"),
            f"expected a 'module.function' name such as 'geometry.ladder', "
            f"got '{name}'",
        )

    params = require_object(
        optional_key(obj, "params", {}, path), child_path(path, "params")
    )
    width = optional_key(obj, "width", None, path)
    height = optional_key(obj, "height", None, path)

    return DiagramPayload(
        name=name,
        params=dict(params),
        caption=_optional_string(obj, "caption", path),
        width=(
            None
            if width is None
            else as_number(width, child_path(path, "width"), minimum=0.5)
        ),
        height=(
            None
            if height is None
            else as_number(height, child_path(path, "height"), minimum=0.5)
        ),
    )


def _parse_graph_payload(obj: JsonObject, path: str) -> GraphPayload:
    kind = as_enum(
        require_key(obj, "graph", path), GRAPH_TYPES, child_path(path, "graph")
    )
    options = require_object(
        optional_key(obj, "options", {}, path), child_path(path, "options")
    )
    return GraphPayload(
        kind=kind,
        data=_parse_graph_data(
            require_key(obj, "data", path), child_path(path, "data")
        ),
        options=dict(options),
        caption=_optional_string(obj, "caption", path),
    )


def _parse_table_payload(obj: JsonObject, path: str) -> TablePayload:
    headers = tuple(
        as_string_array(
            optional_key(obj, "headers", [], path),
            child_path(path, "headers"),
        )
    )
    rows_path = child_path(path, "rows")
    rows = tuple(
        tuple(
            as_string(cell, child_path(row_path, cell_index))
            if isinstance(cell, str)
            else _stringify_cell(cell, child_path(row_path, cell_index))
            for cell_index, cell in enumerate(
                as_array(row, row_path, max_items=MAX_TABLE_COLUMNS)
            )
        )
        for row, row_path in (
            (item, child_path(rows_path, index))
            for index, item in enumerate(
                as_array(optional_key(obj, "rows", [], path), rows_path)
            )
        )
    )

    if headers:
        for index, row in enumerate(rows):
            require_equal_length(
                headers, row, child_path(path, "headers"),
                child_path(rows_path, index),
            )

    widths = tuple(
        as_number_array(
            optional_key(obj, "column_widths", [], path),
            child_path(path, "column_widths"),
            minimum=0.0,
        )
    )
    if widths and headers:
        require_equal_length(
            headers, widths, child_path(path, "headers"),
            child_path(path, "column_widths"),
        )

    return TablePayload(
        headers=headers,
        rows=rows,
        column_widths=widths,
        align=as_enum(
            optional_key(obj, "align", "left", path),
            ALIGNMENTS,
            child_path(path, "align"),
        ),
        caption=_optional_string(obj, "caption", path),
    )


def _stringify_cell(value: Any, path: str) -> str:
    """Accept numbers and booleans in table cells; reject nested containers."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, float)):
        return f"{value:g}"
    raise JsonValidationError(
        path, "table cells must be a string, number, boolean or null"
    )


def _parse_question_payload(obj: JsonObject, path: str) -> QuestionPayload:
    raw_items = optional_key(obj, "questions", [], path)
    return QuestionPayload(
        items=tuple(
            map_array(
                raw_items, _parse_question, child_path(path, "questions"),
                min_items=1,
            )
        ),
        show_answers=as_boolean(
            optional_key(obj, "show_answers", False, path),
            child_path(path, "show_answers"),
        ),
        numbered=as_boolean(
            optional_key(obj, "numbered", True, path),
            child_path(path, "numbered"),
        ),
    )


_PAYLOAD_PARSERS: Final[dict[str, Any]] = {
    "title": _parse_title_payload,
    "theory": _parse_theory_payload,
    "diagram": _parse_diagram_payload,
    "graph": _parse_graph_payload,
    "table": _parse_table_payload,
    "question": _parse_question_payload,
}

_PAYLOAD_KEYS: Final[dict[str, tuple[str, ...]]] = {
    "title": ("author", "institution", "date"),
    "theory": ("body", "columns", "image"),
    "diagram": ("diagram", "params", "caption", "width", "height"),
    "graph": ("graph", "data", "options", "caption"),
    "table": ("headers", "rows", "column_widths", "align", "caption"),
    "question": ("questions", "show_answers", "numbered"),
}


# ----------------------------------------------------------------------
# Slide and deck assembly
# ----------------------------------------------------------------------


def _parse_slide(value: Any, path: str, index: int, warnings: list[str]) -> Slide:
    obj = require_object(value, path)
    slide_type = as_enum(
        require_key(obj, "type", path), SLIDE_TYPES, child_path(path, "type")
    )

    background = optional_key(obj, "background", None, path)
    allowed = _COMMON_SLIDE_KEYS + _PAYLOAD_KEYS[slide_type]
    warnings.extend(
        f"{path}: ignoring unrecognised field '{key}'"
        for key in reject_unknown_keys(obj, allowed, path)
    )

    return Slide(
        type=slide_type,
        index=index,
        title=as_string(
            optional_key(obj, "title", "", path),
            child_path(path, "title"),
            max_length=MAX_TITLE_LENGTH,
        ),
        subtitle=_optional_string(obj, "subtitle", path),
        notes=_optional_string(obj, "notes", path),
        background=(
            None
            if background is None
            else as_string(
                background, child_path(path, "background"), allow_empty=False
            )
        ),
        payload=_PAYLOAD_PARSERS[slide_type](obj, path),
    )


def _check_schema_version(document: JsonObject, warnings: list[str]) -> str:
    raw = optional_key(document, "schema_version", SCHEMA_VERSION)
    version = as_string(raw, "schema_version", allow_empty=False)
    if version not in SUPPORTED_SCHEMA_VERSIONS:
        major = version.split(".", 1)[0]
        supported_majors = {
            item.split(".", 1)[0] for item in SUPPORTED_SCHEMA_VERSIONS
        }
        if major not in supported_majors:
            raise JsonValidationError(
                "schema_version",
                f"'{version}' is not supported by this build "
                f"(supported: {', '.join(SUPPORTED_SCHEMA_VERSIONS)})",
            )
        warnings.append(
            f"schema_version '{version}' is newer than this build "
            f"({SCHEMA_VERSION}); unknown fields will be ignored"
        )
    return version


def parse_deck(document: Any) -> Deck:
    """Validate an already-decoded JSON document and build a :class:`Deck`."""
    obj = require_object(document, "")
    warnings: list[str] = []

    version = _check_schema_version(obj, warnings)
    warnings.extend(
        f"ignoring unrecognised top-level field '{key}'"
        for key in reject_unknown_keys(
            obj, ("schema_version", "meta", "theme", "slides")
        )
    )

    raw_slides = require_key(obj, "slides", "")
    slides = tuple(
        _parse_slide(item, child_path("slides", index), index, warnings)
        for index, item in enumerate(
            as_array(raw_slides, "slides", min_items=1)
        )
    )

    return Deck(
        schema_version=version,
        meta=_parse_meta(optional_key(obj, "meta", None), "meta"),
        theme=_parse_theme(optional_key(obj, "theme", None), "theme"),
        slides=slides,
        warnings=tuple(warnings),
    )


def load_deck_from_string(text: str, *, source: str = "<string>") -> Deck:
    """Decode and validate deck JSON held in memory."""
    try:
        document = json.loads(text)
    except json.JSONDecodeError as error:
        raise DeckLoadError(
            f"{source} is not valid JSON: line {error.lineno}, "
            f"column {error.colno}: {error.msg}"
        ) from error

    try:
        return parse_deck(document)
    except JsonValidationError as error:
        raise DeckLoadError(f"{source}: {error}") from error


def load_deck(path: str | os.PathLike[str]) -> Deck:
    """Read, decode and validate a deck JSON file."""
    resolved = resolve_path(path)
    try:
        text = read_text(resolved, description="deck JSON")
    except FileAccessError as error:
        raise DeckLoadError(str(error)) from error
    return load_deck_from_string(text, source=str(resolved))


def slides_of_type(deck: Deck, slide_type: str) -> tuple[Slide, ...]:
    """Filter helper used by tooling and the test-suite."""
    return tuple(slide for slide in deck.slides if slide.type == slide_type)


def summarise(deck: Deck) -> str:
    """One-line description for logs and the GUI status bar."""
    counts: dict[str, int] = {}
    for slide in deck.slides:
        counts[slide.type] = counts.get(slide.type, 0) + 1
    breakdown = ", ".join(
        f"{count} {name}" for name, count in sorted(counts.items())
    )
    return f"{len(deck.slides)} slide(s): {breakdown}"


__all__ = [
    "DeckLoadError",
    "SLIDE_TYPES",
    "GRAPH_TYPES",
    "BLOCK_STYLES",
    "QUESTION_KINDS",
    "Deck",
    "DeckMeta",
    "DeckTheme",
    "Slide",
    "ContentBlock",
    "GraphSeries",
    "GraphData",
    "QuestionItem",
    "TitlePayload",
    "TheoryPayload",
    "DiagramPayload",
    "GraphPayload",
    "TablePayload",
    "QuestionPayload",
    "parse_deck",
    "load_deck",
    "load_deck_from_string",
    "slides_of_type",
    "summarise",
]