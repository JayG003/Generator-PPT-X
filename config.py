"""Central configuration: paths, geometry, typography, palette, engine tuning.

This module is the single source of truth for every constant in the project.
It must never import from any other project module, so that every layer can
depend on it without creating cycles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

from pptx.dml.color import RGBColor
from pptx.util import Emu, Inches, Pt

# ----------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------

BASE_DIR: Final[Path] = Path(__file__).resolve().parent

ASSETS_DIR: Final[Path] = BASE_DIR / "assets"
BACKGROUNDS_DIR: Final[Path] = ASSETS_DIR / "backgrounds"
FONTS_DIR: Final[Path] = ASSETS_DIR / "fonts"
ICONS_DIR: Final[Path] = ASSETS_DIR / "icons"

TEMPLATES_DIR: Final[Path] = BASE_DIR / "templates"
OUTPUT_DIR: Final[Path] = BASE_DIR / "output"
CACHE_DIR: Final[Path] = OUTPUT_DIR / ".cache"

DEFAULT_BACKGROUND: Final[Path] = BACKGROUNDS_DIR / "slide.png"

# ----------------------------------------------------------------------
# Presentation geometry
# ----------------------------------------------------------------------

SLIDE_WIDTH: Final[Emu] = Inches(13.333)
SLIDE_HEIGHT: Final[Emu] = Inches(7.5)

BLANK_LAYOUT_INDEX: Final[int] = 6
DEFAULT_LAYOUT_INDEX: Final[int] = BLANK_LAYOUT_INDEX

LEFT_MARGIN: Final[Emu] = Inches(0.5)
RIGHT_MARGIN: Final[Emu] = Inches(0.5)
TOP_MARGIN: Final[Emu] = Inches(0.4)
BOTTOM_MARGIN: Final[Emu] = Inches(0.4)

CONTENT_WIDTH: Final[Emu] = Emu(SLIDE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN)
CONTENT_HEIGHT: Final[Emu] = Emu(SLIDE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN)

SLIDE_TITLE_HEIGHT: Final[Emu] = Inches(0.9)
SLIDE_FOOTER_HEIGHT: Final[Emu] = Inches(0.35)

# ----------------------------------------------------------------------
# Typography
# ----------------------------------------------------------------------

FONT_FAMILY: Final[str] = "Calibri"
MONO_FONT_FAMILY: Final[str] = "Consolas"

TITLE_FONT_SIZE: Final[Pt] = Pt(40)
SLIDE_TITLE_FONT_SIZE: Final[Pt] = Pt(28)
HEADING_FONT_SIZE: Final[Pt] = Pt(22)
SUBHEADING_FONT_SIZE: Final[Pt] = Pt(18)
BODY_FONT_SIZE: Final[Pt] = Pt(16)
SMALL_FONT_SIZE: Final[Pt] = Pt(13)
CAPTION_FONT_SIZE: Final[Pt] = Pt(11)

LINE_SPACING: Final[float] = 1.15
BULLET_INDENT: Final[Emu] = Inches(0.3)

MIN_AUTOFIT_FONT_SIZE: Final[Pt] = Pt(10)
AUTOFIT_STEP: Final[Pt] = Pt(1)

# ----------------------------------------------------------------------
# Palette
# ----------------------------------------------------------------------

BLACK: Final[RGBColor] = RGBColor(0, 0, 0)
WHITE: Final[RGBColor] = RGBColor(255, 255, 255)

TITLE_COLOR: Final[RGBColor] = RGBColor(33, 33, 33)
TEXT_COLOR: Final[RGBColor] = RGBColor(40, 40, 40)
SUBTEXT_COLOR: Final[RGBColor] = RGBColor(90, 90, 90)
MUTED_COLOR: Final[RGBColor] = RGBColor(140, 140, 140)

PRIMARY_COLOR: Final[RGBColor] = RGBColor(33, 150, 243)
SECONDARY_COLOR: Final[RGBColor] = RGBColor(76, 175, 80)
ACCENT_COLOR: Final[RGBColor] = RGBColor(255, 152, 0)

SUCCESS_COLOR: Final[RGBColor] = RGBColor(46, 125, 50)
WARNING_COLOR: Final[RGBColor] = RGBColor(255, 193, 7)
ERROR_COLOR: Final[RGBColor] = RGBColor(211, 47, 47)

SURFACE_COLOR: Final[RGBColor] = RGBColor(248, 249, 250)
BORDER_COLOR: Final[RGBColor] = RGBColor(220, 223, 228)
GRID_COLOR: Final[RGBColor] = RGBColor(217, 217, 217)

TABLE_HEADER_BG: Final[RGBColor] = PRIMARY_COLOR
TABLE_HEADER_FG: Final[RGBColor] = WHITE
TABLE_ROW_BG: Final[RGBColor] = WHITE
TABLE_ALT_ROW_BG: Final[RGBColor] = SURFACE_COLOR

SERIES_PALETTE: Final[tuple[RGBColor, ...]] = (
    RGBColor(33, 150, 243),
    RGBColor(255, 152, 0),
    RGBColor(76, 175, 80),
    RGBColor(233, 30, 99),
    RGBColor(156, 39, 176),
    RGBColor(0, 172, 193),
    RGBColor(255, 87, 34),
    RGBColor(121, 85, 72),
)

# ----------------------------------------------------------------------
# Rendering
# ----------------------------------------------------------------------

IMAGE_DPI: Final[int] = 200
EXPORT_FORMAT: Final[str] = "png"
TRANSPARENT_BACKGROUND: Final[bool] = True
FIGURE_BBOX: Final[str] = "tight"
FIGURE_PAD_INCHES: Final[float] = 0.05

GRAPH_WIDTH: Final[Emu] = Inches(11.3)
GRAPH_HEIGHT: Final[Emu] = Inches(5.6)

DIAGRAM_WIDTH: Final[Emu] = Inches(11.3)
DIAGRAM_HEIGHT: Final[Emu] = Inches(5.6)

TEXTBOX_WIDTH: Final[Emu] = Inches(12.333)
TEXTBOX_HEIGHT: Final[Emu] = Inches(5.6)

# ----------------------------------------------------------------------
# Engine tuning
# ----------------------------------------------------------------------

MATPLOTLIB_BACKEND: Final[str] = "Agg"

IMAGE_CACHE_ENABLED: Final[bool] = True
IMAGE_CACHE_MAX_ENTRIES: Final[int] = 512
IMAGE_CACHE_MAX_BYTES: Final[int] = 256 * 1024 * 1024

MAX_SLIDES_WARNING: Final[int] = 500
STRICT_VALIDATION: Final[bool] = True

SCHEMA_VERSION: Final[str] = "1.0"
SUPPORTED_SCHEMA_VERSIONS: Final[tuple[str, ...]] = ("1.0",)

DEFAULT_OUTPUT_NAME: Final[str] = "presentation.pptx"