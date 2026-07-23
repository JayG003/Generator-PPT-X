"""Shared plumbing for every graph family.

What lives here
---------------
Everything that is identical across bar, line, pie, scatter and histogram:
option parsing and validation, canvas creation and teardown, colour cycling,
and axis decoration (titles, labels, legend, grid, tick formatting).

Each graph module is then left with only the part that differs -- the call
that actually puts marks on the axes. That is what keeps rule 1 honest: a
change to how legends are placed is one edit here, not five.

Contract
--------
A graph module exposes::

    def render(data: GraphData, options: GraphOptions, canvas) -> None

It draws onto the supplied canvas and returns nothing. It never creates a
figure, never saves, never closes, and never touches the cache. Lifecycle is
owned by :func:`render_to_bytes`, so no graph module can leak a figure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Final, Iterator, Mapping, Sequence

from config import (
    GRAPH_HEIGHT,
    GRAPH_WIDTH,
    IMAGE_DPI,
    SERIES_PALETTE,
)
from drawing.canvas import DrawingCanvas
from engine.json_loader import GraphData, GraphSeries
from utils.json_utils import (
    JsonObject,
    JsonValidationError,
    as_boolean,
    as_color,
    as_enum,
    as_integer,
    as_number,
    as_string,
    child_path,
    optional_key,
    require_object,
)

LEGEND_POSITIONS: Final[tuple[str, ...]] = (
    "best",
    "upper right",
    "upper left",
    "lower left",
    "lower right",
    "right",
    "center left",
    "center right",
    "lower center",
    "upper center",
    "center",
)

GRID_AXES: Final[tuple[str, ...]] = ("both", "x", "y", "none")

_TITLE_FONT_SIZE: Final[int] = 15
_LABEL_FONT_SIZE: Final[int] = 12
_TICK_FONT_SIZE: Final[int] = 10
_LEGEND_FONT_SIZE: Final[int] = 10
_GRID_ALPHA: Final[float] = 0.35
_GRID_WIDTH: Final[float] = 0.7
_SPINE_COLOR: Final[str] = "#9aa0a6"
_TEXT_COLOR: Final[str] = "#282828"

_COMMON_OPTION_KEYS: Final[tuple[str, ...]] = (
    "title",
    "x_label",
    "y_label",
    "legend",
    "legend_position",
    "grid",
    "grid_axis",
    "x_limits",
    "y_limits",
    "value_labels",
    "value_format",
    "colors",
    "width",
    "height",
    "dpi",
    "tick_rotation",
)


class GraphError(ValueError):
    """Raised when graph data and the requested graph type are incompatible."""


def _rgb_to_hex(color: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*color)


@dataclass(frozen=True, slots=True)
class GraphOptions:
    """Validated, type-specific-agnostic rendering options.

    Extra keys survive in :attr:`extra` so a graph module can read its own
    options (``bins``, ``stacked``, ``explode`` ...) without this class having
    to know about every family -- the same registry principle the diagram
    layer uses.
    """

    title: str = ""
    x_label: str = ""
    y_label: str = ""
    legend: bool | None = None
    legend_position: str = "best"
    grid: bool = True
    grid_axis: str = "y"
    x_limits: tuple[float, float] | None = None
    y_limits: tuple[float, float] | None = None
    value_labels: bool = False
    value_format: str = "{:g}"
    colors: tuple[str, ...] = ()
    width: float = GRAPH_WIDTH.inches
    height: float = GRAPH_HEIGHT.inches
    dpi: int = IMAGE_DPI
    tick_rotation: float = 0.0
    extra: Mapping[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.extra is None:
            object.__setattr__(self, "extra", {})

    # -- typed accessors for family-specific options -------------------

    def get_bool(self, key: str, default: bool = False) -> bool:
        value = self.extra.get(key)
        if value is None:
            return default
        return as_boolean(value, child_path("options", key))

    def get_int(
        self,
        key: str,
        default: int,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> int:
        value = self.extra.get(key)
        if value is None:
            return default
        return as_integer(
            value, child_path("options", key), minimum=minimum, maximum=maximum
        )

    def get_number(
        self,
        key: str,
        default: float,
        *,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> float:
        value = self.extra.get(key)
        if value is None:
            return default
        return as_number(
            value, child_path("options", key), minimum=minimum, maximum=maximum
        )

    def get_string(self, key: str, default: str = "") -> str:
        value = self.extra.get(key)
        if value is None:
            return default
        return as_string(value, child_path("options", key))

    def get_enum(self, key: str, allowed: Sequence[str], default: str) -> str:
        value = self.extra.get(key)
        if value is None:
            return default
        return as_enum(value, allowed, child_path("options", key))

    def get_number_list(self, key: str) -> tuple[float, ...]:
        value = self.extra.get(key)
        if value is None:
            return ()
        path = child_path("options", key)
        if not isinstance(value, (list, tuple)):
            raise JsonValidationError(path, "expected an array of numbers")
        return tuple(
            as_number(item, child_path(path, index))
            for index, item in enumerate(value)
        )

    def format_value(self, value: float) -> str:
        try:
            return self.value_format.format(value)
        except (ValueError, KeyError, IndexError) as error:
            raise JsonValidationError(
                "options.value_format",
                f"invalid format string '{self.value_format}': {error}",
            ) from error


def _parse_limits(
    value: Any, path: str
) -> tuple[float, float] | None:
    if value is None:
        return None
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise JsonValidationError(
            path, "expected a two-element array [minimum, maximum]"
        )
    low = as_number(value[0], child_path(path, 0))
    high = as_number(value[1], child_path(path, 1))
    if low >= high:
        raise JsonValidationError(
            path, f"minimum must be less than maximum, got [{low}, {high}]"
        )
    return (low, high)


def parse_options(raw: Mapping[str, Any] | None) -> GraphOptions:
    """Validate the shared option keys and retain the rest in ``extra``."""
    obj: JsonObject = require_object(raw or {}, "options")
    path = "options"

    legend_raw = optional_key(obj, "legend", None, path)
    colors_raw = optional_key(obj, "colors", [], path)
    if not isinstance(colors_raw, (list, tuple)):
        raise JsonValidationError(
            child_path(path, "colors"), "expected an array of colours"
        )

    return GraphOptions(
        title=as_string(
            optional_key(obj, "title", "", path), child_path(path, "title")
        ),
        x_label=as_string(
            optional_key(obj, "x_label", "", path), child_path(path, "x_label")
        ),
        y_label=as_string(
            optional_key(obj, "y_label", "", path), child_path(path, "y_label")
        ),
        legend=(
            None
            if legend_raw is None
            else as_boolean(legend_raw, child_path(path, "legend"))
        ),
        legend_position=as_enum(
            optional_key(obj, "legend_position", "best", path),
            LEGEND_POSITIONS,
            child_path(path, "legend_position"),
        ),
        grid=as_boolean(
            optional_key(obj, "grid", True, path), child_path(path, "grid")
        ),
        grid_axis=as_enum(
            optional_key(obj, "grid_axis", "y", path),
            GRID_AXES,
            child_path(path, "grid_axis"),
        ),
        x_limits=_parse_limits(
            optional_key(obj, "x_limits", None, path),
            child_path(path, "x_limits"),
        ),
        y_limits=_parse_limits(
            optional_key(obj, "y_limits", None, path),
            child_path(path, "y_limits"),
        ),
        value_labels=as_boolean(
            optional_key(obj, "value_labels", False, path),
            child_path(path, "value_labels"),
        ),
        value_format=as_string(
            optional_key(obj, "value_format", "{:g}", path),
            child_path(path, "value_format"),
            allow_empty=False,
        ),
        colors=tuple(
            _rgb_to_hex(as_color(item, child_path(child_path(path, "colors"), index)))
            for index, item in enumerate(colors_raw)
        ),
        width=as_number(
            optional_key(obj, "width", GRAPH_WIDTH.inches, path),
            child_path(path, "width"),
            minimum=1.0,
            maximum=40.0,
        ),
        height=as_number(
            optional_key(obj, "height", GRAPH_HEIGHT.inches, path),
            child_path(path, "height"),
            minimum=1.0,
            maximum=40.0,
        ),
        dpi=as_integer(
            optional_key(obj, "dpi", IMAGE_DPI, path),
            child_path(path, "dpi"),
            minimum=72,
            maximum=600,
        ),
        tick_rotation=as_number(
            optional_key(obj, "tick_rotation", 0.0, path),
            child_path(path, "tick_rotation"),
            minimum=-90.0,
            maximum=90.0,
        ),
        extra={
            key: value
            for key, value in obj.items()
            if key not in _COMMON_OPTION_KEYS
        },
    )


# ----------------------------------------------------------------------
# Colours
# ----------------------------------------------------------------------


def palette_colors(count: int, options: GraphOptions) -> list[str]:
    """Colours for ``count`` marks: explicit options first, then the palette.

    Cycles rather than failing when fewer colours are supplied than needed, so
    a deck with a two-colour brand override still renders a six-series chart.
    """
    if count < 0:
        raise ValueError("count must not be negative")

    source = list(options.colors) or [
        _rgb_to_hex(tuple(color)) for color in SERIES_PALETTE
    ]
    return [source[index % len(source)] for index in range(count)]


def series_colors(data: GraphData, options: GraphOptions) -> list[str]:
    """Per-series colours, honouring any colour set on the series itself."""
    defaults = palette_colors(len(data.series), options)
    return [
        _rgb_to_hex(item.color) if item.color else defaults[index]
        for index, item in enumerate(data.series)
    ]


# ----------------------------------------------------------------------
# Data access helpers
# ----------------------------------------------------------------------


def require_series(data: GraphData, kind: str) -> tuple[GraphSeries, ...]:
    if not data.series:
        raise GraphError(
            f"a '{kind}' graph requires 'data.series'; none was supplied"
        )
    return data.series


def require_values(data: GraphData, kind: str) -> tuple[float, ...]:
    """Raw sample for distribution graphs, accepting a single series as well."""
    if data.values:
        return data.values
    if len(data.series) == 1 and data.series[0].values:
        return data.series[0].values
    raise GraphError(
        f"a '{kind}' graph requires 'data.values' or exactly one series "
        f"carrying 'values'"
    )


def require_points(
    series: GraphSeries, kind: str, index: int
) -> tuple[tuple[float, float], ...]:
    """xy pairs for a series, synthesising an index axis from bare values."""
    if series.points:
        return series.points
    if series.values:
        return tuple(
            (float(position), value)
            for position, value in enumerate(series.values)
        )
    raise GraphError(
        f"series {index} of a '{kind}' graph has neither 'points' nor 'values'"
    )


def category_labels(data: GraphData, count: int) -> list[str]:
    """Labels for a categorical axis, filling gaps with 1-based positions."""
    labels = list(data.labels)
    if len(labels) >= count:
        return labels[:count]
    return labels + [str(index + 1) for index in range(len(labels), count)]


def show_legend(data: GraphData, options: GraphOptions) -> bool:
    """Default the legend on only when it carries information."""
    if options.legend is not None:
        return options.legend
    named = [item for item in data.series if item.name]
    return len(named) > 1


# ----------------------------------------------------------------------
# Canvas lifecycle and decoration
# ----------------------------------------------------------------------


def create_canvas(options: GraphOptions) -> DrawingCanvas:
    """A canvas configured for data plotting rather than geometry.

    Graphs need auto aspect and visible axes; the canvas defaults suit
    diagrams, where equal aspect and hidden axes are correct.
    """
    canvas = DrawingCanvas(
        width=options.width,
        height=options.height,
        dpi=options.dpi,
    )
    canvas.set_equal_aspect(False)
    canvas.show_axes()
    return canvas


def decorate(canvas: DrawingCanvas, data: GraphData, options: GraphOptions) -> None:
    """Apply titles, labels, limits, grid, legend and spine styling.

    Called once by :func:`render_to_bytes` after the graph module has drawn,
    so every family gets identical chrome for free.
    """
    axis = canvas.get_axis()

    if options.title:
        axis.set_title(
            options.title,
            fontsize=_TITLE_FONT_SIZE,
            fontweight="bold",
            color=_TEXT_COLOR,
            pad=12,
        )
    if options.x_label:
        axis.set_xlabel(
            options.x_label, fontsize=_LABEL_FONT_SIZE, color=_TEXT_COLOR
        )
    if options.y_label:
        axis.set_ylabel(
            options.y_label, fontsize=_LABEL_FONT_SIZE, color=_TEXT_COLOR
        )

    if options.x_limits:
        axis.set_xlim(*options.x_limits)
    if options.y_limits:
        axis.set_ylim(*options.y_limits)

    axis.tick_params(
        axis="both",
        labelsize=_TICK_FONT_SIZE,
        colors=_TEXT_COLOR,
        length=4,
    )
    if options.tick_rotation:
        for label in axis.get_xticklabels():
            label.set_rotation(options.tick_rotation)
            label.set_horizontalalignment(
                "right" if options.tick_rotation > 0 else "left"
            )

    for side in ("top", "right"):
        axis.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        axis.spines[side].set_color(_SPINE_COLOR)
        axis.spines[side].set_linewidth(0.9)

    if options.grid and options.grid_axis != "none":
        axis.set_axisbelow(True)
        axis.grid(
            visible=True,
            axis=options.grid_axis,
            alpha=_GRID_ALPHA,
            linewidth=_GRID_WIDTH,
        )
    else:
        axis.grid(False)

    if show_legend(data, options) and axis.get_legend_handles_labels()[0]:
        axis.legend(
            loc=options.legend_position,
            fontsize=_LEGEND_FONT_SIZE,
            frameon=False,
        )


def annotate_values(
    canvas: DrawingCanvas,
    positions: Sequence[tuple[float, float]],
    values: Sequence[float],
    options: GraphOptions,
    *,
    offset: float = 0.0,
    ha: str = "center",
    va: str = "bottom",
) -> None:
    """Write value labels beside marks, shared by bar/line/scatter."""
    if not options.value_labels:
        return
    axis = canvas.get_axis()
    for (x, y), value in zip(positions, values):
        axis.annotate(
            options.format_value(value),
            (x, y + offset),
            ha=ha,
            va=va,
            fontsize=_TICK_FONT_SIZE,
            color=_TEXT_COLOR,
        )


GraphDrawer = Callable[[GraphData, GraphOptions, DrawingCanvas], None]


def render_to_bytes(
    drawer: GraphDrawer,
    data: GraphData,
    options: GraphOptions,
) -> bytes:
    """Run a graph module's drawer and return encoded PNG bytes.

    Owns the whole figure lifecycle. The ``finally`` is the point of the
    function: a drawer that raises must still not leak its figure, and a
    thousand-slide deck must not depend on every graph module remembering to
    clean up after itself.
    """
    canvas = create_canvas(options)
    try:
        drawer(data, options, canvas)
        decorate(canvas, data, options)
        canvas.get_figure().tight_layout()
        return canvas.save_to_bytes()
    finally:
        canvas.close()


def iter_series_with_color(
    data: GraphData, options: GraphOptions
) -> Iterator[tuple[int, GraphSeries, str]]:
    """Convenience loop used by bar, line and scatter."""
    colors = series_colors(data, options)
    for index, item in enumerate(data.series):
        yield index, item, colors[index]


__all__ = [
    "GraphError",
    "GraphOptions",
    "GraphDrawer",
    "LEGEND_POSITIONS",
    "GRID_AXES",
    "parse_options",
    "palette_colors",
    "series_colors",
    "require_series",
    "require_values",
    "require_points",
    "category_labels",
    "show_legend",
    "create_canvas",
    "decorate",
    "annotate_values",
    "render_to_bytes",
    "iter_series_with_color",
]