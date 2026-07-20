from dataclasses import dataclass

from config import (
    BLACK,
    WHITE,
    PRIMARY_COLOR,
    SECONDARY_COLOR,
    ACCENT_COLOR,
    TEXT_COLOR,
    SUBTEXT_COLOR,
)

# Helpers
def rgb(color):
    """Convert pptx RGBColor to matplotlib RGB tuple (0-1)."""
    return (
        color[0] / 255,
        color[1] / 255,
        color[2] / 255,
    )

# Base Style
@dataclass(frozen=True)
class DrawingStyle:

    line_color: tuple
    fill_color: tuple
    text_color: tuple

    line_width: float

    font_size: int
    font_weight: str

    alpha: float

# Standard Styles
DEFAULT_STYLE = DrawingStyle(
    line_color=rgb(BLACK),
    fill_color=rgb(WHITE),
    text_color=rgb(TEXT_COLOR),
    line_width=2.0,
    font_size=10,
    font_weight="normal",
    alpha=1.0,
)

PRIMARY_STYLE = DrawingStyle(
    line_color=rgb(PRIMARY_COLOR),
    fill_color=rgb(WHITE),
    text_color=rgb(TEXT_COLOR),
    line_width=2.0,
    font_size=10,
    font_weight="normal",
    alpha=1.0,
)

SECONDARY_STYLE = DrawingStyle(
    line_color=rgb(SECONDARY_COLOR),
    fill_color=rgb(WHITE),
    text_color=rgb(TEXT_COLOR),
    line_width=2.0,
    font_size=10,
    font_weight="normal",
    alpha=1.0,
)

ACCENT_STYLE = DrawingStyle(
    line_color=rgb(ACCENT_COLOR),
    fill_color=rgb(WHITE),
    text_color=rgb(TEXT_COLOR),
    line_width=2.0,
    font_size=10,
    font_weight="bold",
    alpha=1.0,
)

LABEL_STYLE = DrawingStyle(
    line_color=rgb(BLACK),
    fill_color=rgb(WHITE),
    text_color=rgb(SUBTEXT_COLOR),
    line_width=1.0,
    font_size=9,
    font_weight="normal",
    alpha=1.0,
)

GRID_STYLE = DrawingStyle(
    line_color=(0.85, 0.85, 0.85),
    fill_color=rgb(WHITE),
    text_color=rgb(TEXT_COLOR),
    line_width=0.8,
    font_size=8,
    font_weight="normal",
    alpha=0.7,
)