"""Pie and donut charts.

The odd one out: a pie has no axes, so this module hides the chrome that
``graphs.base.decorate`` applies to every other family. That is handled by
turning the axis off here rather than by adding a "does this graph have axes"
flag to base -- one line in the module that knows, instead of a branch in the
module that should not care.

Data
----
Takes the first series' ``values``, or ``data.values`` directly. Multiple
series are meaningless for a pie and are rejected rather than silently
truncated, because silently charting only the first series of three is the
kind of error that reaches a printed handout.

Options consumed here
---------------------
``donut``         bool    render as a ring
``donut_width``   number  ring thickness as a fraction of the radius
``percent``       bool    label wedges with percentages
``show_values``   bool    label wedges with raw values instead
``percent_format`` string format string for the percentage text
``explode``       array   per-wedge radial offset
``explode_max``   bool    offset the largest wedge automatically
``start_angle``   number  degrees anticlockwise from the x axis
``clockwise``     bool    lay wedges out clockwise
``labels_inside`` bool    place wedge labels inside the pie
``min_percent``   number  wedges below this share are merged into "Other"
"""

from __future__ import annotations

from typing import Final, Sequence

from drawing.canvas import DrawingCanvas
from engine.json_loader import GraphData
from graphs.base import (
    GraphError,
    GraphOptions,
    category_labels,
    palette_colors,
    parse_options,
    render_to_bytes,
)

KIND: Final[str] = "pie"

_DEFAULT_START_ANGLE: Final[float] = 90.0
_DEFAULT_DONUT_WIDTH: Final[float] = 0.42
_DEFAULT_EXPLODE: Final[float] = 0.06
_LABEL_DISTANCE: Final[float] = 1.06
_INSIDE_DISTANCE: Final[float] = 0.62
_PERCENT_DISTANCE: Final[float] = 0.72
_WEDGE_EDGE_COLOR: Final[str] = "#ffffff"
_WEDGE_EDGE_WIDTH: Final[float] = 1.4
_LABEL_FONT_SIZE: Final[int] = 11
_TITLE_FONT_SIZE: Final[int] = 15
_TEXT_COLOR: Final[str] = "#282828"
_OTHER_LABEL: Final[str] = "Other"


def _extract(data: GraphData) -> tuple[float, ...]:
    """Pull the single value set a pie represents."""
    if len(data.series) > 1:
        raise GraphError(
            f"a '{KIND}' graph represents one set of values but "
            f"{len(data.series)} series were supplied; split them across "
            f"separate slides"
        )
    if data.series:
        values = data.series[0].values
        if not values:
            raise GraphError(
                f"the series of a '{KIND}' graph must supply 'values'"
            )
        return values
    if data.values:
        return data.values
    raise GraphError(
        f"a '{KIND}' graph requires 'data.values' or a single series "
        f"carrying 'values'"
    )


def _validate(values: Sequence[float]) -> None:
    if any(value < 0 for value in values):
        raise GraphError(
            f"a '{KIND}' graph cannot represent negative values; "
            f"use a bar graph instead"
        )
    if sum(values) <= 0:
        raise GraphError(f"the values of a '{KIND}' graph must sum above zero")


def _merge_small(
    values: Sequence[float],
    labels: Sequence[str],
    threshold: float,
) -> tuple[list[float], list[str]]:
    """Fold wedges below ``threshold`` percent into a single "Other" slice.

    A pie with thirty two-percent slivers is unreadable; merging is the only
    honest way to keep it legible without dropping data.
    """
    if threshold <= 0:
        return list(values), list(labels)

    total = sum(values)
    kept_values: list[float] = []
    kept_labels: list[str] = []
    merged = 0.0

    for value, label in zip(values, labels):
        if total and (value / total) * 100.0 < threshold:
            merged += value
        else:
            kept_values.append(value)
            kept_labels.append(label)

    if merged > 0:
        kept_values.append(merged)
        kept_labels.append(_OTHER_LABEL)

    return (kept_values, kept_labels) if kept_values else (
        list(values),
        list(labels),
    )


def _explode_offsets(
    values: Sequence[float], options: GraphOptions
) -> list[float] | None:
    explicit = options.get_number_list("explode")
    if explicit:
        if len(explicit) != len(values):
            raise GraphError(
                f"'explode' has {len(explicit)} entries but the graph has "
                f"{len(values)} wedges"
            )
        return list(explicit)

    if options.get_bool("explode_max") and values:
        largest = max(range(len(values)), key=lambda index: values[index])
        return [
            _DEFAULT_EXPLODE if index == largest else 0.0
            for index in range(len(values))
        ]

    return None


def render(
    data: GraphData,
    options: GraphOptions,
    canvas: DrawingCanvas,
) -> None:
    """Draw a pie or donut onto ``canvas``."""
    values = _extract(data)
    _validate(values)

    labels = category_labels(data, len(values))
    values, labels = _merge_small(
        values, labels, options.get_number("min_percent", 0.0, minimum=0.0, maximum=50.0)
    )

    axis = canvas.get_axis()

    donut = options.get_bool("donut")
    donut_width = options.get_number(
        "donut_width", _DEFAULT_DONUT_WIDTH, minimum=0.05, maximum=1.0
    )
    show_percent = options.get_bool("percent", True)
    show_values = options.get_bool("show_values")
    percent_format = options.get_string("percent_format", "%.1f%%")
    start_angle = options.get_number(
        "start_angle", _DEFAULT_START_ANGLE, minimum=-360.0, maximum=360.0
    )
    clockwise = options.get_bool("clockwise", True)
    labels_inside = options.get_bool("labels_inside")

    total = sum(values)

    if show_values:
        def autopct(percent: float) -> str:
            return options.format_value(percent * total / 100.0)
    elif show_percent:
        def autopct(percent: float) -> str:
            return percent_format % percent
    else:
        autopct = None  # type: ignore[assignment]

    wedges, texts, *rest = axis.pie(
        values,
        labels=labels,
        colors=palette_colors(len(values), options),
        explode=_explode_offsets(values, options),
        startangle=start_angle,
        counterclock=not clockwise,
        autopct=autopct,
        pctdistance=_PERCENT_DISTANCE,
        labeldistance=(
            _INSIDE_DISTANCE if labels_inside else _LABEL_DISTANCE
        ),
        wedgeprops={
            "width": donut_width if donut else None,
            "edgecolor": _WEDGE_EDGE_COLOR,
            "linewidth": _WEDGE_EDGE_WIDTH,
        },
        textprops={
            "fontsize": _LABEL_FONT_SIZE,
            "color": _TEXT_COLOR,
        },
    )

    if rest:
        for label in rest[0]:
            label.set_color(_WEDGE_EDGE_COLOR if not donut else _TEXT_COLOR)
            label.set_fontweight("bold")

    axis.set_aspect("equal")
    axis.set_axis_off()

    if options.title:
        axis.set_title(
            options.title,
            fontsize=_TITLE_FONT_SIZE,
            fontweight="bold",
            color=_TEXT_COLOR,
            pad=12,
        )

    if options.legend:
        axis.legend(
            wedges,
            labels,
            loc=options.legend_position,
            fontsize=_LABEL_FONT_SIZE,
            frameon=False,
        )
        for text in texts:
            text.set_visible(False)


def render_bytes(data: GraphData, options: dict | GraphOptions | None = None) -> bytes:
    """Convenience entry point for callers holding a raw options mapping."""
    resolved = (
        options if isinstance(options, GraphOptions) else parse_options(options)
    )
    return render_to_bytes(render, data, resolved)


__all__ = ["KIND", "render", "render_bytes"]