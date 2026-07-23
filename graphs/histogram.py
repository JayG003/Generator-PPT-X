"""Histograms and frequency distributions.

Binning
-------
The bin count is the only decision a histogram really makes, and a fixed
default of ten is wrong often enough to mislead. When ``bins`` is not given
the module uses the Freedman-Diaconis rule, ``width = 2 * IQR / n^(1/3)``,
which adapts to spread and is resistant to outliers, falling back to Sturges'
rule for small or degenerate samples where the interquartile range collapses
to zero.

Options consumed here
---------------------
``bins``          integer fixed bin count, overriding automatic selection
``bin_width``     number  fixed bin width, overriding both
``range``         array   [minimum, maximum] to bin within
``density``       bool    normalise to a probability density
``cumulative``    bool    plot a cumulative distribution
``horizontal``    bool    draw bars along the x axis
``edge``          bool    outline each bar
``mean_line``     bool    mark the arithmetic mean
``median_line``   bool    mark the median
``curve``         bool    overlay a fitted normal curve
``frequency_labels`` bool label each bar with its count

The normal curve and the quantiles are computed here rather than pulled from
scipy or numpy, for the same reason as the regression in ``scatter``: a few
lines of arithmetic against a heavyweight dependency.
"""

from __future__ import annotations

import math
from typing import Final, Sequence

from drawing.canvas import DrawingCanvas
from engine.json_loader import GraphData
from graphs.base import (
    GraphError,
    GraphOptions,
    palette_colors,
    parse_options,
    render_to_bytes,
    require_values,
)

KIND: Final[str] = "histogram"

_MIN_BINS: Final[int] = 1
_MAX_BINS: Final[int] = 250
_DEFAULT_ALPHA: Final[float] = 0.9
_EDGE_COLOR: Final[str] = "#ffffff"
_EDGE_WIDTH: Final[float] = 0.9
_CURVE_POINTS: Final[int] = 200
_CURVE_WIDTH: Final[float] = 2.0
_MARKER_WIDTH: Final[float] = 1.8
_MEAN_COLOR: Final[str] = "#d32f2f"
_MEDIAN_COLOR: Final[str] = "#2e7d32"
_LABEL_FONT_SIZE: Final[int] = 9
_LABEL_PAD: Final[float] = 3.0
_TEXT_COLOR: Final[str] = "#282828"


def quantile(sorted_values: Sequence[float], fraction: float) -> float:
    """Linear-interpolation quantile of an already-sorted sample."""
    if not sorted_values:
        raise GraphError("cannot take a quantile of an empty sample")
    if len(sorted_values) == 1:
        return sorted_values[0]

    position = fraction * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[int(position)]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def freedman_diaconis_bins(values: Sequence[float]) -> int:
    """Bin count from the Freedman-Diaconis rule, with a Sturges fallback.

    FD is preferred because it responds to the spread of the middle half of
    the data rather than to extremes, so one stray outlier does not collapse
    every real feature into a single bar. When the interquartile range is zero
    -- a heavily tied sample -- FD is undefined and Sturges is used instead.
    """
    count = len(values)
    if count < 2:
        return _MIN_BINS

    ordered = sorted(values)
    spread = ordered[-1] - ordered[0]
    if spread <= 0:
        return _MIN_BINS

    iqr = quantile(ordered, 0.75) - quantile(ordered, 0.25)
    if iqr <= 0:
        bins = int(math.ceil(math.log2(count) + 1))
    else:
        width = 2.0 * iqr / (count ** (1.0 / 3.0))
        bins = int(math.ceil(spread / width)) if width > 0 else _MIN_BINS

    return max(_MIN_BINS, min(_MAX_BINS, bins))


def _mean(values: Sequence[float]) -> float:
    return sum(values) / len(values)


def _standard_deviation(values: Sequence[float]) -> float:
    """Sample standard deviation, Bessel-corrected."""
    count = len(values)
    if count < 2:
        return 0.0
    average = _mean(values)
    return math.sqrt(
        sum((value - average) ** 2 for value in values) / (count - 1)
    )


def _normal_curve(
    values: Sequence[float],
    low: float,
    high: float,
    scale: float,
) -> tuple[list[float], list[float]]:
    """Sample a normal density fitted to the data, scaled to the bar heights."""
    deviation = _standard_deviation(values)
    if deviation <= 0 or high <= low:
        return ([], [])

    average = _mean(values)
    step = (high - low) / (_CURVE_POINTS - 1)
    xs = [low + index * step for index in range(_CURVE_POINTS)]
    factor = 1.0 / (deviation * math.sqrt(2.0 * math.pi))
    ys = [
        scale * factor * math.exp(-0.5 * ((x - average) / deviation) ** 2)
        for x in xs
    ]
    return (xs, ys)


def _resolve_bins(
    values: Sequence[float], options: GraphOptions
) -> int | list[float]:
    """Decide the binning: explicit width, explicit count, then automatic."""
    width = options.get_number("bin_width", 0.0, minimum=0.0)
    if width > 0:
        low, high = min(values), max(values)
        if high <= low:
            return _MIN_BINS
        count = int(math.ceil((high - low) / width))
        if count > _MAX_BINS:
            raise GraphError(
                f"'bin_width' of {width:g} produces {count} bins, above the "
                f"limit of {_MAX_BINS}; widen it"
            )
        return [low + index * width for index in range(count + 1)]

    explicit = options.get_int("bins", 0, minimum=0, maximum=_MAX_BINS)
    if explicit > 0:
        return explicit

    return freedman_diaconis_bins(values)


def _resolve_range(options: GraphOptions) -> tuple[float, float] | None:
    bounds = options.get_number_list("range")
    if not bounds:
        return None
    if len(bounds) != 2 or bounds[0] >= bounds[1]:
        raise GraphError(
            "'range' must be [minimum, maximum] with minimum below maximum"
        )
    return (bounds[0], bounds[1])


def render(
    data: GraphData,
    options: GraphOptions,
    canvas: DrawingCanvas,
) -> None:
    """Draw a frequency distribution onto ``canvas``."""
    values = require_values(data, KIND)
    if len(values) < 2:
        raise GraphError(
            f"a '{KIND}' graph needs at least two values, got {len(values)}"
        )

    axis = canvas.get_axis()

    density = options.get_bool("density")
    cumulative = options.get_bool("cumulative")
    horizontal = options.get_bool("horizontal")
    edge = options.get_bool("edge", True)
    color = palette_colors(1, options)[0]

    counts, edges, patches = axis.hist(
        values,
        bins=_resolve_bins(values, options),
        range=_resolve_range(options),
        density=density,
        cumulative=cumulative,
        color=color,
        alpha=_DEFAULT_ALPHA,
        orientation="horizontal" if horizontal else "vertical",
        edgecolor=_EDGE_COLOR if edge else "none",
        linewidth=_EDGE_WIDTH if edge else 0.0,
        label=data.series[0].name if data.series else None,
        zorder=2,
    )

    if options.get_bool("curve") and not cumulative:
        widths = [edges[index + 1] - edges[index] for index in range(len(edges) - 1)]
        scale = 1.0 if density else len(values) * (
            sum(widths) / len(widths) if widths else 1.0
        )
        xs, ys = _normal_curve(values, edges[0], edges[-1], scale)
        if xs:
            if horizontal:
                axis.plot(ys, xs, color=_MEAN_COLOR, linewidth=_CURVE_WIDTH,
                          label="normal fit", zorder=4)
            else:
                axis.plot(xs, ys, color=_MEAN_COLOR, linewidth=_CURVE_WIDTH,
                          label="normal fit", zorder=4)

    marker = axis.axhline if horizontal else axis.axvline

    if options.get_bool("mean_line"):
        average = _mean(values)
        marker(average, color=_MEAN_COLOR, linestyle="--",
               linewidth=_MARKER_WIDTH, zorder=5,
               label=f"mean {options.format_value(average)}")

    if options.get_bool("median_line"):
        middle = quantile(sorted(values), 0.5)
        marker(middle, color=_MEDIAN_COLOR, linestyle=":",
               linewidth=_MARKER_WIDTH, zorder=5,
               label=f"median {options.format_value(middle)}")

    if options.get_bool("frequency_labels") or options.value_labels:
        for count, patch in zip(counts, patches):
            if count <= 0:
                continue
            text = options.format_value(count)
            if horizontal:
                axis.annotate(
                    text,
                    (patch.get_width(), patch.get_y() + patch.get_height() / 2),
                    xytext=(_LABEL_PAD, 0),
                    textcoords="offset points",
                    ha="left", va="center",
                    fontsize=_LABEL_FONT_SIZE, color=_TEXT_COLOR,
                )
            else:
                axis.annotate(
                    text,
                    (patch.get_x() + patch.get_width() / 2, patch.get_height()),
                    xytext=(0, _LABEL_PAD),
                    textcoords="offset points",
                    ha="center", va="bottom",
                    fontsize=_LABEL_FONT_SIZE, color=_TEXT_COLOR,
                )

    if not options.y_label and not horizontal:
        axis.set_ylabel(
            "Density" if density else "Frequency", fontsize=12, color=_TEXT_COLOR
        )


def render_bytes(data: GraphData, options: dict | GraphOptions | None = None) -> bytes:
    """Convenience entry point for callers holding a raw options mapping."""
    resolved = (
        options if isinstance(options, GraphOptions) else parse_options(options)
    )
    return render_to_bytes(render, data, resolved)


__all__ = [
    "KIND",
    "quantile",
    "freedman_diaconis_bins",
    "render",
    "render_bytes",
]