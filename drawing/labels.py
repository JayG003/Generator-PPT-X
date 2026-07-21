from copy import replace
from functools import lru_cache
import textwrap

from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

from drawing.styles import (
    DEFAULT_STYLE,
    LABEL_STYLE,
)

class DrawingLabels:

    def __init__(self, canvas):

        self.canvas = canvas
        self.axis = canvas.get_axis()
        self.figure = canvas.get_figure()

    # STYLE HELPERS
    def _resolve_style(
        self,
        style=None,
        **overrides,
    ):

        if style is None:
            style = LABEL_STYLE

        if not overrides:
            return style

        return replace(style, **overrides)

    # FONT HELPERS
    @lru_cache(maxsize=128)
    def _font_properties(
        self,
        size,
        weight,
    ):

        return FontProperties(
            size=size,
            weight=weight,
        )

    # TEXT MEASUREMENT
    @lru_cache(maxsize=512)
    def _measure_text(
        self,
        text,
        font_size,
        font_weight,
    ):
        if not text:
            return (0.0, 0.0)

        fp = self._font_properties(
            font_size,
            font_weight,
        )

        path = TextPath(
            (0, 0),
            text,
            prop=fp,
        )

        bbox = path.get_extents()

        return (
            bbox.width,
            bbox.height,
        )

    def text_size(
        self,
        text,
        style=DEFAULT_STYLE,
        font_size=None,
        font_weight=None,
    ):
        if font_size is None:
            font_size = style.font_size

        if font_weight is None:
            font_weight = style.font_weight

        return self._measure_text(
            str(text),
            font_size,
            font_weight,
        )

    def multiline_size(
        self,
        text,
        style=DEFAULT_STYLE,
        line_spacing=1.20,
    ):
        lines = str(text).splitlines()

        if not lines:
            return (0.0, 0.0)

        widths = []
        heights = []

        for line in lines:

            w, h = self.text_size(
                line,
                style,
            )

            widths.append(w)
            heights.append(h)

        width = max(widths)

        height = (
            sum(heights)
            + (len(lines) - 1)
            * style.font_size
            * line_spacing
        )

        return (
            width,
            height,
        )

    # ALIGNMENT HELPERS
    def _horizontal_alignment(self, alignment):

        mapping = {
            "left": "left",
            "center": "center",
            "right": "right",
        }

        return mapping.get(
            alignment,
            "center",
        )

    def _vertical_alignment(self, alignment):

        mapping = {
            "top": "top",
            "center": "center",
            "bottom": "bottom",
            "baseline": "baseline",
        }

        return mapping.get(
            alignment,
            "center",
        )

    def _anchor(
        self,
        horizontal="center",
        vertical="center",
    ):
        return (
            self._horizontal_alignment(horizontal),
            self._vertical_alignment(vertical),
        )

    # POSITION HELPERS
    def _offset(
        self,
        x,
        y,
        dx=0,
        dy=0,
    ):

        return (
            x + dx,
            y + dy,
        )

    def _center_of_bounds(
        self,
        x,
        y,
        width,
        height,
    ):

        return (
            x + width / 2,
            y + height / 2,
        )

    def _inside_padding(
        self,
        x,
        y,
        padding,
    ):

        return (
            x + padding,
            y + padding,
        )

    # BASIC LABELS
    def text(
        self,
        x,
        y,
        value,
        style=None,
        horizontal="center",
        vertical="center",
        rotation=0,
        **style_overrides,
    ):
        style = self._resolve_style(
            style,
            **style_overrides,
        )

        ha, va = self._anchor(
            horizontal,
            vertical,
        )

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            alpha=style.alpha,
            ha=ha,
            va=va,
            rotation=rotation,
        )

    def centered_text(
        self,
        x,
        y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.text(
            x,
            y,
            value,
            style=style,
            horizontal="center",
            vertical="center",
            **style_overrides,
        )

    def left_text(
        self,
        x,
        y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.text(
            x,
            y,
            value,
            style=style,
            horizontal="left",
            vertical="center",
            **style_overrides,
        )

    def right_text(
        self,
        x,
        y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.text(
            x,
            y,
            value,
            style=style,
            horizontal="right",
            vertical="center",
            **style_overrides,
        )

    def top_text(
        self,
        x,
        y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.text(
            x,
            y,
            value,
            style=style,
            horizontal="center",
            vertical="top",
            **style_overrides,
        )

    def bottom_text(
        self,
        x,
        y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.text(
            x,
            y,
            value,
            style=style,
            horizontal="center",
            vertical="bottom",
            **style_overrides,
        )

    def rotated_text(
        self,
        x,
        y,
        value,
        angle,
        style=None,
        horizontal="center",
        vertical="center",
        **style_overrides,
    ):
        return self.text(
            x,
            y,
            value,
            style=style,
            horizontal=horizontal,
            vertical=vertical,
            rotation=angle,
            **style_overrides,
        )

    def vertical_text(
        self,
        x,
        y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.rotated_text(
            x,
            y,
            value,
            angle=90,
            style=style,
            **style_overrides,
        )

    def multiline_text(
        self,
        x,
        y,
        value,
        style=None,
        horizontal="center",
        vertical="center",
        line_spacing=1.2,
        rotation=0,
        **style_overrides,
    ):
        style = self._resolve_style(
            style,
            **style_overrides,
        )

        ha, va = self._anchor(
            horizontal,
            vertical,
        )

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            alpha=style.alpha,
            ha=ha,
            va=va,
            rotation=rotation,
            linespacing=line_spacing,
            multialignment=ha,
        )
    
    # SHAPE LABELS
    def rectangle_label(
        self,
        x,
        y,
        width,
        height,
        value,
        style=None,
        **style_overrides,
    ):
        cx, cy = self._center_of_bounds(
            x,
            y,
            width,
            height,
        )

        return self.centered_text(
            cx,
            cy,
            value,
            style=style,
            **style_overrides,
        )

    def circle_label(
        self,
        center_x,
        center_y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.centered_text(
            center_x,
            center_y,
            value,
            style=style,
            **style_overrides,
        )

    def ellipse_label(
        self,
        center_x,
        center_y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.centered_text(
            center_x,
            center_y,
            value,
            style=style,
            **style_overrides,
        )
    
    def polygon_label(
        self,
        points,
        value,
        style=None,
        **style_overrides,
    ):
        if not points:
            return None

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        cx = sum(xs) / len(xs)
        cy = sum(ys) / len(ys)

        return self.centered_text(
            cx,
            cy,
            value,
            style=style,
            **style_overrides,
        )

    def diamond_label(
        self,
        center_x,
        center_y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.centered_text(
            center_x,
            center_y,
            value,
            style=style,
            **style_overrides,
        )

    def auto_center_label(
        self,
        points,
        value,
        style=None,
        **style_overrides,
    ):
        if not points:
            return None

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        cx = (min(xs) + max(xs)) / 2
        cy = (min(ys) + max(ys)) / 2

        return self.centered_text(
            cx,
            cy,
            value,
            style=style,
            **style_overrides,
        )

    def padded_label(
        self,
        x,
        y,
        value,
        padding=0.15,
        style=None,
        horizontal="left",
        vertical="top",
        **style_overrides,
    ):
        px, py = self._offset(
            x,
            y,
            dx=padding,
            dy=-padding,
        )

        return self.text(
            px,
            py,
            value,
            style=style,
            horizontal=horizontal,
            vertical=vertical,
            **style_overrides,
        )

    # ANNOTATION LABELS
    def callout(
        self,
        x,
        y,
        target_x,
        target_y,
        value,
        style=None,
        arrow_style="->",
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        self.axis.annotate(
            str(value),
            xy=(target_x, target_y),
            xytext=(x, y),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            ha="center",
            va="center",
            arrowprops=dict(
                arrowstyle=arrow_style,
                color=style.text_color,
                linewidth=style.line_width,
            ),
        )

    def caption(
        self,
        x,
        y,
        value,
        style=None,
        **style_overrides,
    ):
        return self.text(
            x,
            y,
            value,
            style=style,
            horizontal="center",
            vertical="top",
            **style_overrides,
        )

    def note(
        self,
        x,
        y,
        value,
        style=None,
        padding=0.15,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            ha="left",
            va="top",
            bbox=dict(
                boxstyle=f"round,pad={padding}",
                facecolor="#FFF9C4",
                edgecolor="#BDB76B",
                linewidth=style.line_width,
                alpha=0.95,
            ),
        )

    def tooltip(
        self,
        x,
        y,
        value,
        style=None,
        padding=0.20,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color="white",
            ha="center",
            va="center",
            bbox=dict(
                boxstyle=f"round,pad={padding}",
                facecolor="#333333",
                edgecolor="#111111",
                linewidth=style.line_width,
            ),
        )

    def balloon_label(
        self,
        x,
        y,
        target_x,
        target_y,
        value,
        style=None,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        self.axis.annotate(
            str(value),
            xy=(target_x, target_y),
            xytext=(x, y),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round,pad=0.35",
                facecolor="white",
                edgecolor=style.text_color,
                linewidth=style.line_width,
            ),
            arrowprops=dict(
                arrowstyle="->",
                color=style.text_color,
                linewidth=style.line_width,
            ),
        )

    def speech_annotation(
        self,
        x,
        y,
        target_x,
        target_y,
        value,
        style=None,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        self.axis.annotate(
            str(value),
            xy=(target_x, target_y),
            xytext=(x, y),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="round4,pad=0.45",
                facecolor="white",
                edgecolor=style.text_color,
                linewidth=style.line_width,
            ),
            arrowprops=dict(
                arrowstyle="wedge,tail_width=0.6",
                color=style.text_color,
                linewidth=style.line_width,
            ),
        )


    def leader_line_label(
        self,
        x,
        y,
        target_x,
        target_y,
        value,
        style=None,
        horizontal="left",
        vertical="center",
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        self.axis.plot(
            [target_x, x],
            [target_y, y],
            color=style.text_color,
            linewidth=style.line_width,
        )

        self.text(
            x,
            y,
            value,
            style=style,
            horizontal=horizontal,
            vertical=vertical,
        )

    # CONNECTOR LABELS
    def _midpoint(
        self,
        x1,
        y1,
        x2,
        y2,
    ):
        return (
            (x1 + x2) / 2,
            (y1 + y2) / 2,
        )

    def arrow_label(
        self,
        x1,
        y1,
        x2,
        y2,
        value,
        style=None,
        offset_x=0,
        offset_y=0,
        **style_overrides,
    ):
        mx, my = self._midpoint(
            x1,
            y1,
            x2,
            y2,
        )

        return self.centered_text(
            mx + offset_x,
            my + offset_y,
            value,
            style=style,
            **style_overrides,
        )

    def edge_label(
        self,
        x1,
        y1,
        x2,
        y2,
        value,
        style=None,
        offset_x=0,
        offset_y=0,
        **style_overrides,
    ):
        return self.arrow_label(
            x1,
            y1,
            x2,
            y2,
            value,
            style=style,
            offset_x=offset_x,
            offset_y=offset_y,
            **style_overrides,
        )

    def curved_edge_label(
        self,
        x1,
        y1,
        x2,
        y2,
        value,
        curvature=0.20,
        style=None,
        **style_overrides,
    ):
        mx, my = self._midpoint(
            x1,
            y1,
            x2,
            y2,
        )

        dx = x2 - x1
        dy = y2 - y1

        px = -dy
        py = dx

        length = (px ** 2 + py ** 2) ** 0.5

        if length != 0:
            px /= length
            py /= length

        mx += px * curvature
        my += py * curvature

        return self.centered_text(
            mx,
            my,
            value,
            style=style,
            **style_overrides,
        )

    def midpoint_label(
        self,
        x1,
        y1,
        x2,
        y2,
        value,
        style=None,
        **style_overrides,
    ):
        mx, my = self._midpoint(
            x1,
            y1,
            x2,
            y2,
        )

        return self.centered_text(
            mx,
            my,
            value,
            style=style,
            **style_overrides,
        )

    def start_label(
        self,
        x1,
        y1,
        value,
        style=None,
        offset_x=0,
        offset_y=0,
        **style_overrides,
    ):
        return self.text(
            x1 + offset_x,
            y1 + offset_y,
            value,
            style=style,
            horizontal="right",
            vertical="center",
            **style_overrides,
        )

    def end_label(
        self,
        x2,
        y2,
        value,
        style=None,
        offset_x=0,
        offset_y=0,
        **style_overrides,
    ):
        return self.text(
            x2 + offset_x,
            y2 + offset_y,
            value,
            style=style,
            horizontal="left",
            vertical="center",
            **style_overrides,
        )

    def path_label(
        self,
        points,
        value,
        style=None,
        **style_overrides,
    ):
        if not points:
            return None

        if len(points) == 1:
            return self.centered_text(
                points[0][0],
                points[0][1],
                value,
                style=style,
                **style_overrides,
            )

        middle = (len(points) - 1) // 2

        x1, y1 = points[middle]
        x2, y2 = points[middle + 1]

        mx, my = self._midpoint(
            x1,
            y1,
            x2,
            y2,
        )

        return self.centered_text(
            mx,
            my,
            value,
            style=style,
            **style_overrides,
        )
    
    # BACKGROUND LABELS
    def boxed_text(
        self,
        x,
        y,
        value,
        style=None,
        padding=0.25,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle=f"square,pad={padding}",
                facecolor="white",
                edgecolor=style.text_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            ),
        )

    def rounded_box_label(
        self,
        x,
        y,
        value,
        style=None,
        padding=0.30,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle=f"round,pad={padding}",
                facecolor="white",
                edgecolor=style.text_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            ),
        )

    def highlight_label(
        self,
        x,
        y,
        value,
        style=None,
        highlight_color="#FFF59D",
        padding=0.20,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle=f"square,pad={padding}",
                facecolor=highlight_color,
                edgecolor="none",
                alpha=0.90,
            ),
        )

    def filled_label(
        self,
        x,
        y,
        value,
        style=None,
        fill_color="#1976D2",
        text_color="white",
        padding=0.25,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=text_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle=f"round,pad={padding}",
                facecolor=fill_color,
                edgecolor=fill_color,
                linewidth=style.line_width,
            ),
        )

    def outline_label(
        self,
        x,
        y,
        value,
        style=None,
        outline_color=None,
        padding=0.25,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        if outline_color is None:
            outline_color = style.text_color

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=outline_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle=f"round,pad={padding}",
                facecolor="none",
                edgecolor=outline_color,
                linewidth=style.line_width,
            ),
        )

    def badge(
        self,
        x,
        y,
        value,
        style=None,
        badge_color="#D32F2F",
        text_color="white",
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight="bold",
            color=text_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle="circle,pad=0.35",
                facecolor=badge_color,
                edgecolor=badge_color,
                linewidth=style.line_width,
            ),
        )

    def tag(
        self,
        x,
        y,
        value,
        style=None,
        fill_color="#ECEFF1",
        edge_color="#90A4AE",
        padding=0.28,
        **style_overrides,
    ):
        style = self._resolve_style(style, **style_overrides)

        return self.axis.text(
            x,
            y,
            str(value),
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            ha="center",
            va="center",
            bbox=dict(
                boxstyle=f"round4,pad={padding}",
                facecolor=fill_color,
                edgecolor=edge_color,
                linewidth=style.line_width,
            ),
        )

    # SMART LAYOUT
    import textwrap

    def auto_font_scale(
        self,
        text,
        max_width,
        max_height,
        style=None,
        min_size=6,
        max_size=None,
    ):
        style = self._resolve_style(style)

        if max_size is None:
            max_size = style.font_size

        for size in range(int(max_size), int(min_size) - 1, -1):

            width, height = self.text_size(
                text,
                font_size=size,
            )

            if width <= max_width and height <= max_height:
                return size

        return min_size

    def wrap_text(
        self,
        text,
        max_width,
        style=None,
    ):
        style = self._resolve_style(style)

        char_width = max(style.font_size * 0.60, 1)

        max_chars = max(
            1,
            int(max_width / char_width),
        )

        return textwrap.fill(
            str(text),
            width=max_chars,
        )

    def clip_text(
        self,
        text,
        max_width,
        style=None,
        suffix="...",
    ):
        style = self._resolve_style(style)

        text = str(text)

        while text:

            width, _ = self.text_size(
                text + suffix,
                font_size=style.font_size,
            )

            if width <= max_width:
                return text + suffix

            text = text[:-1]

        return suffix

    def handle_overflow(
        self,
        text,
        max_width,
        max_height,
        style=None,
    ):
        style = self._resolve_style(style)

        wrapped = self.wrap_text(
            text,
            max_width,
            style,
        )

        font = self.auto_font_scale(
            wrapped,
            max_width,
            max_height,
            style,
        )

        width, height = self.text_size(
            wrapped,
            font_size=font,
        )

        if width <= max_width and height <= max_height:
            return wrapped, font

        clipped = self.clip_text(
            text,
            max_width,
            style,
        )

        return clipped, font

    def bounding_box(
        self,
        text,
        style=None,
    ):
        return self.text_size(
            text,
            style=style,
        )

    def avoid_collision(
        self,
        x,
        y,
        existing_boxes,
        width,
        height,
        spacing=0.20,
    ):

        while True:

            collision = False

            for bx, by, bw, bh in existing_boxes:

                if (
                    x < bx + bw + spacing
                    and x + width + spacing > bx
                    and y < by + bh + spacing
                    and y + height + spacing > by
                ):
                    y += bh + spacing
                    collision = True
                    break

            if not collision:
                break

        return x, y

    def auto_center(
        self,
        points,
    ):
        if not points:
            return None

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        return (
            (min(xs) + max(xs)) / 2,
            (min(ys) + max(ys)) / 2,
        )

    # UTILITIES
    def rotation_radians(
        self,
        angle,
    ):
        from math import radians

        return radians(angle)

    def normalize_rotation(
        self,
        angle,
    ):
        return angle % 360

    def is_vertical_rotation(
        self,
        angle,
    ):
        angle = self.normalize_rotation(angle)

        return angle in (90, 270)

    def baseline_offset(
        self,
        font_size,
        factor=0.80,
    ):
        return font_size * factor

    def text_baseline(
        self,
        y,
        font_size,
    ):
        return y - self.baseline_offset(font_size)

    def apply_margin(
        self,
        x,
        y,
        left=0,
        right=0,
        top=0,
        bottom=0,
    ):
        return (
            x + left - right,
            y + bottom - top,
        )

    def inset_bounds(
        self,
        x,
        y,
        width,
        height,
        margin,
    ):
        return (
            x + margin,
            y + margin,
            width - (2 * margin),
            height - (2 * margin),
        )

    def anchor_point(
        self,
        x,
        y,
        width,
        height,
        horizontal="center",
        vertical="center",
    ):
        ax = {
            "left": x,
            "center": x + width / 2,
            "right": x + width,
        }.get(horizontal, x + width / 2)

        ay = {
            "bottom": y,
            "center": y + height / 2,
            "top": y + height,
        }.get(vertical, y + height / 2)

        return ax, ay

    def bounding_rectangle(
        self,
        text,
        style=None,
        padding=0,
    ):
        width, height = self.bounding_box(
            text,
            style=style,
        )

        return (
            0,
            0,
            width + (padding * 2),
            height + (padding * 2),
        )


__all__ = [
    "DrawingLabels",
]