"""Numeric helpers for data-driven slides.

Scope is deliberately narrow. Points, vectors, lines, angles and polygons
already live in :mod:`drawing.geometry_utils`; this module must not duplicate
them. What lives here is the arithmetic that *graphs* need and geometry does
not: axis tick selection, range padding, histogram binning and aggregation
that stays well-defined on empty or degenerate input.
"""

from __future__ import annotations

import math
from typing import Iterable, Sequence

EPSILON = 1e-12

_NICE_MANTISSAS = (1.0, 2.0, 2.5, 5.0, 10.0)

DEFAULT_TICK_COUNT = 6
MAX_TICK_COUNT = 20
DEFAULT_RANGE_PADDING = 0.05


class MathError(ValueError):
    """Raised when numeric input cannot yield a meaningful result."""


# ----------------------------------------------------------------------
# Scalars
# ----------------------------------------------------------------------


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Constrain ``value`` to ``[minimum, maximum]``."""
    if minimum > maximum:
        raise MathError(f"minimum {minimum} exceeds maximum {maximum}")
    return max(minimum, min(maximum, value))


def is_finite(value: float) -> bool:
    """True when ``value`` is a real number that can be plotted."""
    return isinstance(value, (int, float)) and math.isfinite(value)


def safe_divide(
    numerator: float,
    denominator: float,
    default: float = 0.0,
) -> float:
    """Divide, returning ``default`` instead of raising on a zero divisor."""
    if abs(denominator) < EPSILON:
        return default
    return numerator / denominator


def percentage(part: float, whole: float) -> float:
    """``part`` as a percentage of ``whole``; 0.0 when ``whole`` is zero."""
    return safe_divide(part, whole, 0.0) * 100.0


def round_to(value: float, step: float) -> float:
    """Round ``value`` to the nearest multiple of ``step``."""
    if abs(step) < EPSILON:
        return value
    return round(value / step) * step


def lerp(start: float, end: float, fraction: float) -> float:
    """Linear interpolation between ``start`` and ``end``."""
    return start + (end - start) * fraction


# ----------------------------------------------------------------------
# Aggregation
# ----------------------------------------------------------------------


def finite_values(values: Iterable[float]) -> list[float]:
    """Drop ``None``, ``NaN`` and infinities so downstream maths is total."""
    return [float(item) for item in values if is_finite(item)]


def minimum(values: Sequence[float], default: float = 0.0) -> float:
    finite = finite_values(values)
    return min(finite) if finite else default


def maximum(values: Sequence[float], default: float = 0.0) -> float:
    finite = finite_values(values)
    return max(finite) if finite else default


def total(values: Sequence[float]) -> float:
    return math.fsum(finite_values(values))


def mean(values: Sequence[float], default: float = 0.0) -> float:
    finite = finite_values(values)
    if not finite:
        return default
    return math.fsum(finite) / len(finite)


def median(values: Sequence[float], default: float = 0.0) -> float:
    finite = sorted(finite_values(values))
    count = len(finite)
    if not count:
        return default
    middle = count // 2
    if count % 2:
        return finite[middle]
    return (finite[middle - 1] + finite[middle]) / 2.0


def standard_deviation(values: Sequence[float], default: float = 0.0) -> float:
    """Population standard deviation."""
    finite = finite_values(values)
    if len(finite) < 2:
        return default
    average = math.fsum(finite) / len(finite)
    variance = math.fsum((item - average) ** 2 for item in finite) / len(finite)
    return math.sqrt(variance)


def value_range(values: Sequence[float]) -> tuple[float, float]:
    """``(min, max)`` of the finite values, or ``(0.0, 0.0)`` if none."""
    finite = finite_values(values)
    if not finite:
        return (0.0, 0.0)
    return (min(finite), max(finite))


def normalize(values: Sequence[float]) -> list[float]:
    """Scale values to ``[0, 1]``; a flat series becomes all zeros."""
    low, high = value_range(values)
    span = high - low
    if abs(span) < EPSILON:
        return [0.0] * len(values)
    return [
        clamp((float(item) - low) / span, 0.0, 1.0) if is_finite(item) else 0.0
        for item in values
    ]


def proportions(values: Sequence[float]) -> list[float]:
    """Non-negative values as fractions summing to 1.0."""
    positive = [max(0.0, float(item)) for item in values if is_finite(item)]
    grand_total = math.fsum(positive)
    if grand_total < EPSILON:
        count = len(positive)
        return [1.0 / count] * count if count else []
    return [item / grand_total for item in positive]


def cumulative(values: Sequence[float]) -> list[float]:
    """Running total, used for stacked bars and ogives."""
    running = 0.0
    output: list[float] = []
    for item in values:
        running += float(item) if is_finite(item) else 0.0
        output.append(running)
    return output


# ----------------------------------------------------------------------
# Axis scaling
# ----------------------------------------------------------------------


def nice_number(value: float, *, round_result: bool = True) -> float:
    """Snap ``value`` to 1, 2, 2.5, 5 or 10 times a power of ten.

    The classic Heckbert algorithm. Axis ticks land on numbers a human reads
    without effort (0, 25, 50, 75) instead of on the raw data range
    (0, 23.7, 47.4).
    """
    if abs(value) < EPSILON:
        return 0.0

    exponent = math.floor(math.log10(abs(value)))
    fraction = abs(value) / (10.0**exponent)

    if round_result:
        if fraction < 1.5:
            nice = 1.0
        elif fraction < 3.0:
            nice = 2.0
        elif fraction < 7.0:
            nice = 5.0
        else:
            nice = 10.0
    else:
        nice = next(
            (item for item in _NICE_MANTISSAS if fraction <= item), 10.0
        )

    return math.copysign(nice * (10.0**exponent), value)


def nice_range(
    low: float,
    high: float,
    tick_count: int = DEFAULT_TICK_COUNT,
) -> tuple[float, float, float]:
    """Return ``(axis_min, axis_max, step)`` bounding ``[low, high]``.

    Both bounds are multiples of ``step``, so no tick label carries spurious
    decimals and the data never touches the frame.
    """
    if tick_count < 2:
        raise MathError(f"tick_count must be at least 2, got {tick_count}")
    if not (is_finite(low) and is_finite(high)):
        raise MathError("nice_range requires finite bounds")

    if low > high:
        low, high = high, low

    if abs(high - low) < EPSILON:
        if abs(high) < EPSILON:
            return (0.0, 1.0, 0.5)
        magnitude = abs(high) * 0.5
        low, high = low - magnitude, high + magnitude

    step = nice_number((high - low) / (tick_count - 1), round_result=True)
    if step < EPSILON:
        return (low, high, max((high - low) / (tick_count - 1), EPSILON))

    axis_min = math.floor(low / step) * step
    axis_max = math.ceil(high / step) * step
    return (axis_min, axis_max, step)


def tick_values(
    low: float,
    high: float,
    tick_count: int = DEFAULT_TICK_COUNT,
) -> list[float]:
    """Evenly spaced, human-readable tick positions covering the range."""
    axis_min, axis_max, step = nice_range(low, high, tick_count)
    if step < EPSILON:
        return [axis_min, axis_max]

    ticks: list[float] = []
    count = int(round((axis_max - axis_min) / step)) + 1
    for index in range(min(count, MAX_TICK_COUNT + 1)):
        tick = axis_min + index * step
        ticks.append(0.0 if abs(tick) < EPSILON else tick)
    return ticks


def pad_range(
    low: float,
    high: float,
    fraction: float = DEFAULT_RANGE_PADDING,
) -> tuple[float, float]:
    """Widen a range by ``fraction`` on each side so markers are not clipped."""
    if low > high:
        low, high = high, low
    span = high - low
    if abs(span) < EPSILON:
        margin = abs(high) * fraction if abs(high) > EPSILON else 1.0
        return (low - margin, high + margin)
    margin = span * fraction
    return (low - margin, high + margin)


def include_zero(low: float, high: float) -> tuple[float, float]:
    """Extend a range to the origin.

    Bar charts must be zero-based; a truncated baseline exaggerates
    differences and is the single most common way a chart misleads.
    """
    return (min(0.0, low), max(0.0, high))


def decimal_places(step: float, *, maximum_places: int = 6) -> int:
    """Digits needed to label ticks of size ``step`` without repetition."""
    if abs(step) < EPSILON or step != step:
        return 0
    exponent = math.floor(math.log10(abs(step)))
    return int(clamp(-exponent, 0, maximum_places)) if exponent < 0 else 0


def format_number(value: float, places: int | None = None) -> str:
    """Render a tick or data label without trailing noise."""
    if not is_finite(value):
        return ""
    if places is None:
        places = 0 if abs(value - round(value)) < EPSILON else 2
    text = f"{value:.{places}f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


# ----------------------------------------------------------------------
# Binning
# ----------------------------------------------------------------------


def sturges_bin_count(sample_size: int) -> int:
    """Sturges' rule; a sane default bin count for histograms."""
    if sample_size <= 1:
        return 1
    return int(clamp(math.ceil(math.log2(sample_size) + 1), 1, MAX_TICK_COUNT))


def freedman_diaconis_bins(values: Sequence[float]) -> int:
    """Bin count from the interquartile range; robust to outliers.

    Falls back to Sturges when the IQR collapses, which happens whenever more
    than half the sample shares a single value.
    """
    finite = sorted(finite_values(values))
    count = len(finite)
    if count < 2:
        return 1

    lower = finite[count // 4]
    upper = finite[(3 * count) // 4]
    iqr = upper - lower
    if iqr < EPSILON:
        return sturges_bin_count(count)

    width = 2.0 * iqr / (count ** (1.0 / 3.0))
    span = finite[-1] - finite[0]
    if width < EPSILON or span < EPSILON:
        return sturges_bin_count(count)
    return int(clamp(math.ceil(span / width), 1, MAX_TICK_COUNT * 2))


def bin_edges(
    values: Sequence[float],
    bin_count: int | None = None,
) -> list[float]:
    """Edges for ``bin_count`` equal-width bins covering ``values``."""
    finite = finite_values(values)
    if not finite:
        return [0.0, 1.0]

    if bin_count is None:
        bin_count = freedman_diaconis_bins(finite)
    if bin_count < 1:
        raise MathError(f"bin_count must be positive, got {bin_count}")

    low, high = min(finite), max(finite)
    if abs(high - low) < EPSILON:
        low, high = low - 0.5, high + 0.5

    width = (high - low) / bin_count
    return [low + index * width for index in range(bin_count + 1)]


def histogram(
    values: Sequence[float],
    bin_count: int | None = None,
) -> tuple[list[float], list[int]]:
    """Return ``(edges, counts)``; the final bin includes its right edge."""
    edges = bin_edges(values, bin_count)
    counts = [0] * (len(edges) - 1)
    low, high = edges[0], edges[-1]
    width = safe_divide(high - low, len(counts), 1.0)

    for item in finite_values(values):
        if item < low or item > high:
            continue
        index = int((item - low) / width) if width > EPSILON else 0
        counts[min(index, len(counts) - 1)] += 1

    return edges, counts


def bin_centers(edges: Sequence[float]) -> list[float]:
    """Midpoint of each bin, used to position histogram bars and labels."""
    return [
        (edges[index] + edges[index + 1]) / 2.0
        for index in range(len(edges) - 1)
    ]


# ----------------------------------------------------------------------
# Layout arithmetic
# ----------------------------------------------------------------------


def inverse_lerp(start: float, end: float, value: float) -> float:
    """Fraction of the way ``value`` lies between ``start`` and ``end``."""
    return safe_divide(value - start, end - start)


def remap(
    value: float,
    from_low: float,
    from_high: float,
    to_low: float,
    to_high: float,
) -> float:
    """Map a value from one range onto another."""
    return lerp(to_low, to_high, inverse_lerp(from_low, from_high, value))


def aspect_ratio(width: float, height: float) -> float:
    """Width divided by height, falling back to 1 on a degenerate box."""
    return safe_divide(width, height, default=1.0)


def scale_to_fit(
    width: float,
    height: float,
    max_width: float,
    max_height: float,
) -> float:
    """Largest uniform factor keeping a box inside bounds, never enlarging.

    Capped at 1.0 deliberately: upscaling an already-rendered PNG to fill a
    placeholder produces visible softening, so a diagram smaller than its
    frame stays sharp and is centred instead.
    """
    if width <= 0 or height <= 0:
        raise MathError(f"box size must be positive, got {width}x{height}")
    if max_width <= 0 or max_height <= 0:
        raise MathError(
            f"bounds must be positive, got {max_width}x{max_height}"
        )
    return min(1.0, max_width / width, max_height / height)


def fit_box(
    width: float,
    height: float,
    max_width: float,
    max_height: float,
) -> tuple[float, float]:
    """Box dimensions after applying :func:`scale_to_fit`."""
    factor = scale_to_fit(width, height, max_width, max_height)
    return (width * factor, height * factor)


def center_offset(inner: float, outer: float) -> float:
    """Offset that centres a span of ``inner`` inside a span of ``outer``."""
    return (outer - inner) / 2.0


def center_box(
    width: float,
    height: float,
    outer_width: float,
    outer_height: float,
) -> tuple[float, float]:
    """Top-left corner that centres a box inside an outer box."""
    return (
        center_offset(width, outer_width),
        center_offset(height, outer_height),
    )


def distribute(count: int, extent: float, gap: float = 0.0) -> list[float]:
    """Sizes of ``count`` equal slots filling ``extent`` with ``gap`` between."""
    if count < 1:
        raise MathError(f"count must be at least 1, got {count}")
    available = extent - gap * (count - 1)
    if available <= 0:
        raise MathError(
            f"a gap of {gap:g} leaves no room for {count} slot(s) "
            f"in an extent of {extent:g}"
        )
    return [available / count] * count


def slot_positions(
    start: float,
    extent: float,
    count: int,
    gap: float = 0.0,
) -> list[float]:
    """Leading edges of ``count`` equal slots laid out from ``start``."""
    size = distribute(count, extent, gap)[0]
    return [start + index * (size + gap) for index in range(count)]


def grid_shape(count: int, columns: int | None = None) -> tuple[int, int]:
    """Rows and columns for ``count`` items; defaults to a near-square grid."""
    if count < 1:
        raise MathError(f"count must be at least 1, got {count}")
    if columns is None:
        columns = max(1, int(math.ceil(math.sqrt(count))))
    if columns < 1:
        raise MathError(f"columns must be at least 1, got {columns}")
    return (int(math.ceil(count / columns)), columns)


# ----------------------------------------------------------------------
# Text fitting
# ----------------------------------------------------------------------


def estimate_lines(text: str, characters_per_line: int) -> int:
    """Lines a block of text wraps to at a given width.

    Word-aware rather than a plain character count, because where the wrap
    actually falls is what decides whether a bullet overflows its placeholder.
    An estimate only: the renderer still measures the result before committing
    to a font size.
    """
    if characters_per_line < 1:
        raise MathError(
            f"characters_per_line must be at least 1, "
            f"got {characters_per_line}"
        )
    if not text.strip():
        return 1

    lines = 0
    for paragraph in text.splitlines() or [text]:
        words = paragraph.split()
        if not words:
            lines += 1
            continue
        length = 0
        paragraph_lines = 1
        for word in words:
            addition = len(word) + (1 if length else 0)
            if length and length + addition > characters_per_line:
                paragraph_lines += 1
                length = len(word)
            else:
                length += addition
        lines += paragraph_lines
    return lines


def fit_font_size(
    text_length: int,
    available_area: float,
    base_size: float,
    *,
    minimum_size: float = 10.0,
    density: float = 0.6,
) -> float:
    """Starting font size for a body of text in a box of a given area.

    Area consumed per character scales with the square of the font size, so
    the correction is a square root rather than a linear ratio. ``density``
    is the empirical ratio of glyph area to font size squared for the project
    font.
    """
    if text_length <= 0:
        return base_size
    if available_area <= 0:
        raise MathError(
            f"available_area must be positive, got {available_area}"
        )
    if base_size <= 0:
        raise MathError(f"base_size must be positive, got {base_size}")

    per_character = available_area / text_length
    reference = base_size * base_size * density
    if per_character >= reference:
        return base_size
    return max(minimum_size, base_size * math.sqrt(per_character / reference))


def format_compact(value: float) -> str:
    """Abbreviate large magnitudes for axis labels: 12000 becomes 12K."""
    magnitude = abs(value)
    for threshold, suffix in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if magnitude >= threshold:
            return f"{value / threshold:g}{suffix}"
    return f"{value:g}"


__all__ = [
    "MathError",
    "EPSILON",
    "clamp",
    "is_finite",
    "safe_divide",
    "percentage",
    "round_to",
    "lerp",
    "finite_values",
    "minimum",
    "maximum",
    "total",
    "mean",
    "median",
    "standard_deviation",
    "value_range",
    "normalize",
    "proportions",
    "cumulative",
    "nice_number",
    "nice_range",
    "tick_values",
    "pad_range",
    "include_zero",
    "decimal_places",
    "format_number",
    "sturges_bin_count",
    "freedman_diaconis_bins",
    "bin_edges",
    "histogram",
    "bin_centers",
    "inverse_lerp",
    "remap",
    "aspect_ratio",
    "scale_to_fit",
    "fit_box",
    "center_offset",
    "center_box",
    "distribute",
    "slot_positions",
    "grid_shape",
    "estimate_lines",
    "fit_font_size",
    "format_compact",
]