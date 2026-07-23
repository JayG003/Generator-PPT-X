"""Scatter plots, including bubble charts and least-squares trend lines.

Options consumed here
---------------------
``marker``        string  matplotlib marker code
``marker_size``   number  area of each point in points squared
``sizes``         array   per-point areas, producing a bubble chart
``size_range``    array   [min, max] area the ``sizes`` values map onto
``alpha``         number  point opacity, worth lowering on dense data
``edge``          bool    outline each point
``trend``         bool    fit and draw a least-squares line per series
``trend_style``   string  solid | dashed | dotted | dashdot
``show_equation`` bool    label the trend line with its equation and r squared
``jitter``        number  random horizontal spread, for overlapping categories
``point_labels``  array   per-point text annotations

The regression is ordinary least squares computed in closed form. It is a
dozen lines of arithmetic; importing numpy.polyfit for it would add a hard
numpy dependency to a module that otherwise needs none.
"""

from __future__ import annotations

import math
import random
from typing import Final, Sequence

from drawing.canvas import DrawingCanvas
from engine.json_loader import GraphData
from graphs.base import (
    GraphError,
    GraphOptions,
    iter_series_with_color,
    parse_options,
    render_to_bytes,
    require_points,
    require_series,
)

KIND: Final[str] = "scatter"

TREND_STYLES: Final[dict[str, str]] = {
    "solid": "-",
    "dashed": "--",
    "dotted": ":",
    "dashdot": "-.",
}

_DEFAULT_MARKER: Final[str] = "o"
_DEFAULT_MARKER_SIZE: Final[float] = 55.0
_DEFAULT_ALPHA: Final[float] = 0.85
_DEFAULT_SIZE_RANGE: Final[tuple[float, float]] = (30.0, 420.0)
_TREND_WIDTH: Final[float] = 1.8
_TREND_ALPHA: Final[float] = 0.9
_EDGE_COLOR: Final[str] = "#ffffff"
_EDGE_WIDTH: Final[float] = 0.7
_LABEL_FONT_SIZE: Final[int] = 9
_LABEL_PAD: Final[float] = 6.0
_TEXT_COLOR: Final[str] = "#282828"
_JITTER_SEED: Final[int] = 20260722


def linear_fit(
    points: Sequence[tuple[float, float]]
) -> tuple[float, float, float]:
    """Ordinary least squares fit, returning ``(slope, intercept, r_squared)``.

    Returns a zero-slope line through the mean when x has no variance, which
    is the only defensible answer for a vertical point cloud and avoids a
    division by zero on data a student may well paste in.
    """
    count = len(points)
    if count < 2:
        raise GraphError("a trend line needs at least two points")

    mean_x = sum(point[0] for point in points) / count
    mean_y = sum(point[1] for point in points) / count

    variance_x = sum((point[0] - mean_x) ** 2 for point in points)
    if variance_x == 0.0:
        return (0.0, mean_y, 0.0)

    covariance = sum(
        (point[0] - mean_x) * (point[1] - mean_y) for point in points
    )
    slope = covariance / variance_x
    intercept = mean_y - slope * mean_x

    total = sum((point[1] - mean_y) ** 2 for point in points)
    residual = sum(
        (point[1] - (slope * point[0] + intercept)) ** 2 for point in points
    )
    r_squared = 1.0 if total == 0.0 else max(0.0, 1.0 - residual / total)

    return (slope, intercept, r_squared)


def _scale_sizes(
    values: Sequence[float],
    low: float,
    high: float,
) -> list[float]:
    """Map raw magnitudes onto a visible area range.

    Areas rather than radii, because perceived quantity tracks the area of a
    disc; scaling the radius linearly exaggerates large values quadratically.
    """
    if not values:
        return []
    smallest = min(values)
    largest = max(values)
    if largest == smallest:
        midpoint = (low + high) / 2.0
        return [midpoint] * len(values)
    span = largest - smallest
    return [low + (value - smallest) / span * (high - low) for value in values]


def _resolve_sizes(
    options: GraphOptions,
    count: int,
) -> list[float] | float:
    raw = options.get_number_list("sizes")
    if not raw:
        return options.get_number(
            "marker_size", _DEFAULT_MARKER_SIZE, minimum=1.0, maximum=4000.0
        )

    if len(raw) != count:
        raise GraphError(
            f"'sizes' has {len(raw)} entries but the series has {count} points"
        )
    if any(value < 0 for value in raw):
        raise GraphError("'sizes' values must not be negative")

    bounds = options.get_number_list("size_range") or _DEFAULT_SIZE_RANGE
    if len(bounds) != 2 or bounds[0] <= 0 or bounds[1] <= bounds[0]:
        raise GraphError(
            "'size_range' must be [minimum, maximum] with 0 < minimum < maximum"
        )
    return _scale_sizes(raw, bounds[0], bounds[1])


def _draw_trend(
    canvas: DrawingCanvas,
    points: Sequence[tuple[float, float]],
    color: str,
    options: GraphOptions,
) -> None:
    if len(points) < 2:
        return

    slope, intercept, r_squared = linear_fit(points)
    axis = canvas.get_axis()

    xs = [point[0] for point in points]
    low, high = min(xs), max(xs)
    if low == high:
        return

    style = TREND_STYLES[
        options.get_enum("trend_style", tuple(TREND_STYLES), "dashed")
    ]
    axis.plot(
        [low, high],
        [slope * low + intercept, slope * high + intercept],
        linestyle=style,
        linewidth=_TREND_WIDTH,
        color=color,
        alpha=_TREND_ALPHA,
    )

    if options.get_bool("show_equation"):
        sign = "+" if intercept >= 0 else "-"
        axis.annotate(
            f"y = {slope:.3g}x {sign} {abs(intercept):.3g}   "
            f"R\u00b2 = {r_squared:.3f}",
            (high, slope * high + intercept),
            xytext=(-_LABEL_PAD, _LABEL_PAD),
            textcoords="offset points",
            ha="right",
            va="bottom",
            fontsize=_LABEL_FONT_SIZE,
            color=color,
        )


def _point_labels(options: GraphOptions, count: int) -> list[str]:
    raw = options.extra.get("point_labels")
    if raw is None:
        return []
    if not isinstance(raw, (list, tuple)):
        raise GraphError("'point_labels' must be an array of strings")
    if len(raw) != count:
        raise GraphError(
            f"'point_labels' has {len(raw)} entries but the series has "
            f"{count} points"
        )
    return [str(item) for item in raw]


def render(
    data: GraphData,
    options: GraphOptions,
    canvas: DrawingCanvas,
) -> None:
    """Draw point clouds onto ``canvas``."""
    require_series(data, KIND)

    axis = canvas.get_axis()

    marker = options.get_string("marker", _DEFAULT_MARKER)
    alpha = options.get_number(
        "alpha", _DEFAULT_ALPHA, minimum=0.05, maximum=1.0
    )
    edge = options.get_bool("edge", True)
    trend = options.get_bool("trend")
    jitter = options.get_number("jitter", 0.0, minimum=0.0, maximum=5.0)

    noise = random.Random(_JITTER_SEED) if jitter else None

    if options.get_number_list("sizes") and len(data.series) > 1:
        raise GraphError(
            "'sizes' applies to a single series; supply one series or drop it"
        )

    for index, series, color in iter_series_with_color(data, options):
        points = require_points(series, KIND, index)

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        if noise is not None:
            xs = [value + noise.uniform(-jitter, jitter) for value in xs]

        axis.scatter(
            xs,
            ys,
            s=_resolve_sizes(options, len(points)),
            marker=marker,
            color=color,
            alpha=alpha,
            label=series.name or None,
            edgecolors=_EDGE_COLOR if edge else "none",
            linewidths=_EDGE_WIDTH if edge else 0.0,
            zorder=3,
        )

        if trend:
            _draw_trend(canvas, points, color, options)

        for label, x, y in zip(_point_labels(options, len(points)), xs, ys):
            axis.annotate(
                label,
                (x, y),
                xytext=(0, _LABEL_PAD),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=_LABEL_FONT_SIZE,
                color=_TEXT_COLOR,
            )

        if options.value_labels:
            for x, y in zip(xs, ys):
                axis.annotate(
                    f"({options.format_value(x)}, {options.format_value(y)})",
                    (x, y),
                    xytext=(0, _LABEL_PAD),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=_LABEL_FONT_SIZE,
                    color=_TEXT_COLOR,
                )


def render_bytes(data: GraphData, options: dict | GraphOptions | None = None) -> bytes:
    """Convenience entry point for callers holding a raw options mapping."""
    resolved = (
        options if isinstance(options, GraphOptions) else parse_options(options)
    )
    return render_to_bytes(render, data, resolved)


__all__ = ["KIND", "TREND_STYLES", "linear_fit", "render", "render_bytes"]