"""Bar graphs: grouped, stacked and horizontal.

All three variants live in one module because they share one geometry
problem -- allocating a category slot between N series -- and splitting them
would duplicate that arithmetic three ways.

Options consumed here
---------------------
``stacked``      bool   stack series instead of grouping them
``horizontal``   bool   draw bars along the x axis
``bar_width``    number fraction of a category slot the bars occupy (0-1]
``bar_gap``      number fraction of the bar width left between grouped bars
``edge``         bool   outline each bar
``baseline``     number value the bars grow from

Everything else -- titles, legend, grid, value labels -- is handled by
``graphs.base`` and needs no code here.
"""

from __future__ import annotations

from typing import Final, Sequence

from drawing.canvas import DrawingCanvas
from engine.json_loader import GraphData
from graphs.base import (
    GraphError,
    GraphOptions,
    category_labels,
    iter_series_with_color,
    parse_options,
    render_to_bytes,
    require_series,
)

KIND: Final[str] = "bar"

_DEFAULT_BAR_WIDTH: Final[float] = 0.8
_DEFAULT_BAR_GAP: Final[float] = 0.0
_EDGE_COLOR: Final[str] = "#ffffff"
_EDGE_WIDTH: Final[float] = 0.8
_LABEL_FONT_SIZE: Final[int] = 10
_LABEL_PAD: Final[float] = 3.0
_TEXT_COLOR: Final[str] = "#282828"


def _category_count(data: GraphData) -> int:
    """Longest series decides how many category slots exist."""
    return max(len(item.values) for item in data.series)


def _validate(data: GraphData) -> None:
    require_series(data, KIND)
    for index, item in enumerate(data.series):
        if not item.values:
            raise GraphError(
                f"series {index} ('{item.name or 'unnamed'}') of a '{KIND}' "
                f"graph must supply 'values'"
            )


def _padded(values: Sequence[float], length: int) -> list[float]:
    """Pad a short series with zeros so stacking arithmetic stays aligned."""
    return list(values) + [0.0] * (length - len(values))


def _annotate(
    canvas: DrawingCanvas,
    options: GraphOptions,
    positions: Sequence[float],
    lengths: Sequence[float],
    bases: Sequence[float],
    *,
    horizontal: bool,
    stacked: bool,
) -> None:
    if not options.value_labels:
        return

    axis = canvas.get_axis()

    for position, length, base in zip(positions, lengths, bases):
        if stacked and length == 0:
            continue

        tip = base + length
        text = options.format_value(length)

        if horizontal:
            axis.annotate(
                text,
                (tip, position),
                xytext=(_LABEL_PAD if length >= 0 else -_LABEL_PAD, 0),
                textcoords="offset points",
                ha="left" if length >= 0 else "right",
                va="center",
                fontsize=_LABEL_FONT_SIZE,
                color=_TEXT_COLOR,
            )
        else:
            axis.annotate(
                text,
                (position, tip),
                xytext=(0, _LABEL_PAD if length >= 0 else -_LABEL_PAD),
                textcoords="offset points",
                ha="center",
                va="bottom" if length >= 0 else "top",
                fontsize=_LABEL_FONT_SIZE,
                color=_TEXT_COLOR,
            )


def render(
    data: GraphData,
    options: GraphOptions,
    canvas: DrawingCanvas,
) -> None:
    """Draw bars onto ``canvas``.

    Never creates, saves or closes a figure; ``graphs.base.render_to_bytes``
    owns that lifecycle.
    """
    _validate(data)

    axis = canvas.get_axis()

    stacked = options.get_bool("stacked")
    horizontal = options.get_bool("horizontal")
    edge = options.get_bool("edge", True)
    baseline = options.get_number("baseline", 0.0)
    total_width = options.get_number(
        "bar_width", _DEFAULT_BAR_WIDTH, minimum=0.05, maximum=1.0
    )
    gap = options.get_number(
        "bar_gap", _DEFAULT_BAR_GAP, minimum=0.0, maximum=0.9
    )

    count = _category_count(data)
    slots = list(range(count))
    series_count = len(data.series)

    if stacked:
        bar_width = total_width
        positive = [baseline] * count
        negative = [baseline] * count
    else:
        share = total_width / series_count
        bar_width = share * (1.0 - gap)

    edge_kwargs = (
        {"edgecolor": _EDGE_COLOR, "linewidth": _EDGE_WIDTH} if edge else {}
    )
    plot = axis.barh if horizontal else axis.bar
    length_key = "width" if horizontal else "height"
    thickness_key = "height" if horizontal else "width"
    base_key = "left" if horizontal else "bottom"

    for index, series, color in iter_series_with_color(data, options):
        lengths = _padded(series.values, count)

        if stacked:
            bases = [
                positive[slot] if lengths[slot] >= 0 else negative[slot]
                for slot in slots
            ]
            offsets = [float(slot) for slot in slots]
        else:
            bases = [baseline] * count
            centred = (index - (series_count - 1) / 2.0) * (
                total_width / series_count
            )
            offsets = [slot + centred for slot in slots]

        plot(
            offsets,
            **{
                length_key: lengths,
                thickness_key: bar_width,
                base_key: bases,
            },
            label=series.name or None,
            color=color,
            **edge_kwargs,
        )

        _annotate(
            canvas,
            options,
            offsets,
            lengths,
            bases,
            horizontal=horizontal,
            stacked=stacked,
        )

        if stacked:
            for slot in slots:
                if lengths[slot] >= 0:
                    positive[slot] += lengths[slot]
                else:
                    negative[slot] += lengths[slot]

    labels = category_labels(data, count)

    if horizontal:
        axis.set_yticks(slots)
        axis.set_yticklabels(labels)
        axis.invert_yaxis()
    else:
        axis.set_xticks(slots)
        axis.set_xticklabels(labels)


def render_bytes(data: GraphData, options: dict | GraphOptions | None = None) -> bytes:
    """Convenience entry point for callers holding a raw options mapping."""
    resolved = (
        options if isinstance(options, GraphOptions) else parse_options(options)
    )
    return render_to_bytes(render, data, resolved)


__all__ = ["KIND", "render", "render_bytes"]