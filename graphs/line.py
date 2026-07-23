"""Line graphs.

Accepts either ``points`` (explicit xy pairs) or ``values`` (an index axis is
synthesised), so a categorical trend and a continuous function use the same
slide type.

Options consumed here
---------------------
``markers``      bool    draw a marker at every data point
``marker``       string  matplotlib marker code
``marker_size``  number  marker size in points
``line_width``   number  stroke width
``line_style``   string  solid | dashed | dotted | dashdot
``fill``         bool    shade the area between the line and the baseline
``fill_alpha``   number  opacity of that shading
``baseline``     number  value the fill descends to
``step``         string  none | pre | post | mid
``smooth``       bool    subdivide with a Catmull-Rom spline

Smoothing is implemented locally rather than pulled from scipy: it is roughly
thirty lines of interpolation against a dependency that adds tens of megabytes
and a compiled extension, which fails the minimal-dependency rule.
"""

from __future__ import annotations

from typing import Final, Sequence

from drawing.canvas import DrawingCanvas
from engine.json_loader import GraphData
from graphs.base import (
    GraphOptions,
    category_labels,
    iter_series_with_color,
    parse_options,
    render_to_bytes,
    require_points,
    require_series,
)

KIND: Final[str] = "line"

LINE_STYLES: Final[dict[str, str]] = {
    "solid": "-",
    "dashed": "--",
    "dotted": ":",
    "dashdot": "-.",
}

STEP_MODES: Final[tuple[str, ...]] = ("none", "pre", "post", "mid")

_DEFAULT_LINE_WIDTH: Final[float] = 2.2
_DEFAULT_MARKER: Final[str] = "o"
_DEFAULT_MARKER_SIZE: Final[float] = 5.0
_DEFAULT_FILL_ALPHA: Final[float] = 0.18
_SMOOTH_SEGMENTS: Final[int] = 16
_MAX_SMOOTH_POINTS: Final[int] = 400
_LABEL_FONT_SIZE: Final[int] = 9
_LABEL_PAD: Final[float] = 6.0
_TEXT_COLOR: Final[str] = "#282828"


def _catmull_rom(
    points: Sequence[tuple[float, float]],
    segments: int = _SMOOTH_SEGMENTS,
) -> list[tuple[float, float]]:
    """Subdivide a polyline with a Catmull-Rom spline.

    Chosen over a Bezier fit because the curve passes *through* every input
    point: a chart whose line misses its own data points is wrong, however
    smooth it looks. Endpoints are duplicated to give the first and last
    segments the neighbours the basis needs.
    """
    if len(points) < 3:
        return list(points)

    padded = [points[0], *points, points[-1]]
    curve: list[tuple[float, float]] = []

    for index in range(len(padded) - 3):
        p0, p1, p2, p3 = padded[index : index + 4]
        for step in range(segments):
            t = step / segments
            t2 = t * t
            t3 = t2 * t
            curve.append(
                (
                    0.5
                    * (
                        2 * p1[0]
                        + (-p0[0] + p2[0]) * t
                        + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                        + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3
                    ),
                    0.5
                    * (
                        2 * p1[1]
                        + (-p0[1] + p2[1]) * t
                        + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                        + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3
                    ),
                )
            )

    curve.append(points[-1])
    return curve


def _uses_index_axis(data: GraphData) -> bool:
    """True when every series was given bare values rather than xy pairs."""
    return all(not item.points for item in data.series)


def render(
    data: GraphData,
    options: GraphOptions,
    canvas: DrawingCanvas,
) -> None:
    """Draw one polyline per series onto ``canvas``."""
    require_series(data, KIND)

    axis = canvas.get_axis()

    markers = options.get_bool("markers", True)
    marker = options.get_string("marker", _DEFAULT_MARKER)
    marker_size = options.get_number(
        "marker_size", _DEFAULT_MARKER_SIZE, minimum=0.0, maximum=40.0
    )
    line_width = options.get_number(
        "line_width", _DEFAULT_LINE_WIDTH, minimum=0.1, maximum=20.0
    )
    line_style = LINE_STYLES[
        options.get_enum("line_style", tuple(LINE_STYLES), "solid")
    ]
    fill = options.get_bool("fill")
    fill_alpha = options.get_number(
        "fill_alpha", _DEFAULT_FILL_ALPHA, minimum=0.0, maximum=1.0
    )
    baseline = options.get_number("baseline", 0.0)
    step = options.get_enum("step", STEP_MODES, "none")
    smooth = options.get_bool("smooth")

    longest = 0

    for index, series, color in iter_series_with_color(data, options):
        points = require_points(series, KIND, index)
        longest = max(longest, len(points))

        drawn = points
        if smooth and step == "none" and len(points) <= _MAX_SMOOTH_POINTS:
            drawn = _catmull_rom(points)

        xs = [point[0] for point in drawn]
        ys = [point[1] for point in drawn]

        if step != "none":
            axis.step(
                xs,
                ys,
                where=step,
                label=series.name or None,
                color=color,
                linewidth=line_width,
                linestyle=line_style,
            )
        else:
            axis.plot(
                xs,
                ys,
                label=series.name or None,
                color=color,
                linewidth=line_width,
                linestyle=line_style,
            )

        if markers and marker_size > 0:
            axis.plot(
                [point[0] for point in points],
                [point[1] for point in points],
                linestyle="none",
                marker=marker,
                markersize=marker_size,
                color=color,
                markeredgecolor="#ffffff",
                markeredgewidth=0.8,
            )

        if fill:
            axis.fill_between(
                xs, ys, baseline, color=color, alpha=fill_alpha, linewidth=0
            )

        if options.value_labels:
            for x, y in points:
                axis.annotate(
                    options.format_value(y),
                    (x, y),
                    xytext=(0, _LABEL_PAD),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=_LABEL_FONT_SIZE,
                    color=_TEXT_COLOR,
                )

    if data.labels and _uses_index_axis(data):
        slots = list(range(longest))
        axis.set_xticks(slots)
        axis.set_xticklabels(category_labels(data, longest))


def render_bytes(data: GraphData, options: dict | GraphOptions | None = None) -> bytes:
    """Convenience entry point for callers holding a raw options mapping."""
    resolved = (
        options if isinstance(options, GraphOptions) else parse_options(options)
    )
    return render_to_bytes(render, data, resolved)


__all__ = ["KIND", "LINE_STYLES", "STEP_MODES", "render", "render_bytes"]