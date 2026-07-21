from matplotlib.path import Path
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
import matplotlib.image as mpimg

from matplotlib.patches import (
    Arc,
    Circle,
    Ellipse,
    FancyBboxPatch,
    FancyArrowPatch,
    Polygon,
    Rectangle,
    PathPatch,
)

from drawing.styles import (
    DEFAULT_STYLE,
    DrawingStyle,
)


class DrawingPrimitives:
    """
    Low-level drawing primitives.

    Every diagram and graph renderer should build on this class
    instead of calling matplotlib directly.
    """

    # Constructor
    def __init__(self, canvas):

        self.canvas = canvas
        self.axis = canvas.get_axis()

    # ------------------- Internal Helpers --------------------------

    # Resolve Style
    def _resolve_style(
        self,
        style,
    ):

        if style is None:
            return DEFAULT_STYLE

        if isinstance(style, DrawingStyle):
            return style

        raise TypeError(
            "style must be a DrawingStyle or None"
        )

    # -------------- Canvas Helpers -------------------------

    # Set Drawing Limits
    def set_limits(
        self,
        xmin,
        xmax,
        ymin,
        ymax,
    ):

        self.canvas.set_limits(
            xmin,
            xmax,
            ymin,
            ymax,
        )

    # Set Aspect Ratio
    def set_equal_aspect(
        self,
        enabled=True,
    ):

        self.canvas.set_equal_aspect(enabled)

    # Show Axes
    def show_axes(self):

        self.canvas.show_axes()

    # Hide Axes
    def hide_axes(self):

        self.canvas.hide_axes()

    # Show Grid
    def show_grid(
        self,
        major=True,
        minor=False,
    ):

        self.canvas.show_grid(
            major,
            minor,
        )

    # Hide Grid
    def hide_grid(self):

        self.canvas.hide_grid()

    # Set Title
    def set_title(
        self,
        title,
    ):

        self.canvas.set_title(title)

    # Reset Canvas
    def reset(self):

        self.canvas.reset()

    # Get X Limits
    def get_xlim(self):

        return self.canvas.get_xlim()

    # Get Y Limits
    def get_ylim(self):

        return self.canvas.get_ylim()
    
    # Draw Line
    def line(
        self,
        x1,
        y1,
        x2,
        y2,
        style=None,
    ):

        style = self._resolve_style(style)

        self.axis.plot(
            [x1, x2],
            [y1, y2],
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
        )

    # Draw Polyline
    def polyline(
        self,
        points,
        style=None,
    ):

        style = self._resolve_style(style)

        xs = [point[0] for point in points]
        ys = [point[1] for point in points]

        self.axis.plot(
            xs,
            ys,
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
        )

    # Draw Dashed Line
    def dashed_line(
        self,
        x1,
        y1,
        x2,
        y2,
        style=None,
        dash_pattern=(6, 3),
    ):

        style = self._resolve_style(style)

        self.axis.plot(
            [x1, x2],
            [y1, y2],
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
            dashes=dash_pattern,
        )

    # Draw Arrow
    def arrow(
        self,
        start,
        end,
        style=None,
        arrow_style="->",
        mutation_scale=15,
    ):

        style = self._resolve_style(style)

        self.axis.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle=arrow_style,
                mutation_scale=mutation_scale,
                linewidth=style.line_width,
                color=style.line_color,
                alpha=style.alpha,
            )
        )

    # Draw Point
    def point(
        self,
        x,
        y,
        size=25,
        style=None,
    ):

        style = self._resolve_style(style)

        self.axis.scatter(
            [x],
            [y],
            s=size,
            color=[style.fill_color],
            edgecolors=[style.line_color],
            linewidths=style.line_width,
            alpha=style.alpha,
        )

    # Draw Rectangle
    def rectangle(
        self,
        x,
        y,
        width,
        height,
        style=None,
    ):

        style = self._resolve_style(style)

        self.axis.add_patch(
            Rectangle(
                (x, y),
                width,
                height,
                edgecolor=style.line_color,
                facecolor=style.fill_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )
        )

    # Draw Rounded Rectangle
    def rounded_rectangle(
        self,
        x,
        y,
        width,
        height,
        radius=0.2,
        style=None,
    ):

        style = self._resolve_style(style)

        self.axis.add_patch(
            FancyBboxPatch(
                (x, y),
                width,
                height,
                boxstyle=f"round,pad=0,rounding_size={radius}",
                edgecolor=style.line_color,
                facecolor=style.fill_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )
        )

    # Draw Circle
    def circle(
        self,
        x,
        y,
        radius,
        style=None,
    ):

        style = self._resolve_style(style)

        self.axis.add_patch(
            Circle(
                (x, y),
                radius,
                edgecolor=style.line_color,
                facecolor=style.fill_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )
        )

    # Draw Ellipse
    def ellipse(
        self,
        x,
        y,
        width,
        height,
        angle=0,
        style=None,
    ):

        style = self._resolve_style(style)

        self.axis.add_patch(
            Ellipse(
                (x, y),
                width,
                height,
                angle=angle,
                edgecolor=style.line_color,
                facecolor=style.fill_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )
        )

    # Draw Arc
    def arc(
        self,
        x,
        y,
        width,
        height,
        theta1,
        theta2,
        angle=0,
        style=None,
    ):

        style = self._resolve_style(style)

        self.axis.add_patch(
            Arc(
                (x, y),
                width,
                height,
                angle=angle,
                theta1=theta1,
                theta2=theta2,
                edgecolor=style.line_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )
        )

    # Draw Polygon
    def polygon(
        self,
        points,
        style=None,
        closed=True,
    ):

        style = self._resolve_style(style)

        self.axis.add_patch(
            Polygon(
                points,
                closed=closed,
                edgecolor=style.line_color,
                facecolor=style.fill_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )
        )

    # Draw Bezier Curve
    def bezier(
        self,
        start,
        control1,
        control2,
        end,
        style=None,
    ):

        style = self._resolve_style(style)

        path = Path(
            [
                start,
                control1,
                control2,
                end,
            ],
            [
                Path.MOVETO,
                Path.CURVE4,
                Path.CURVE4,
                Path.CURVE4,
            ],
        )

        self.axis.add_patch(
            PathPatch(
                path,
                fill=False,
                edgecolor=style.line_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )
        )

    # Fill Polygon
    def fill_polygon(
        self,
        points,
        color,
        alpha=1.0,
    ):

        self.axis.fill(
            [p[0] for p in points],
            [p[1] for p in points],
            color=color,
            alpha=alpha,
        )

    # Fill Between Curves
    def fill_between(
        self,
        x,
        y1,
        y2=0,
        color="lightgray",
        alpha=0.5,
    ):

        self.axis.fill_between(
            x,
            y1,
            y2,
            color=color,
            alpha=alpha,
        )

    # Add Generic Patch
    def add_patch(
        self,
        patch,
    ):

        self.axis.add_patch(patch)

    # Draw Image
    def image(
        self,
        image_path,
        x,
        y,
        zoom=1.0,
    ):

        image = mpimg.imread(image_path)

        image_box = OffsetImage(
            image,
            zoom=zoom,
        )

        annotation = AnnotationBbox(
            image_box,
            (x, y),
            frameon=False,
        )

        self.axis.add_artist(annotation)

    # Draw Text
    def text(
        self,
        x,
        y,
        value,
        style=None,
        ha="center",
        va="center",
        rotation=0,
    ):

        style = self._resolve_style(style)

        self.axis.text(
            x,
            y,
            value,
            ha=ha,
            va=va,
            rotation=rotation,
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            alpha=style.alpha,
        )

    # Draw Label
    def label(
        self,
        x,
        y,
        text,
        offset=(0, 0),
        style=None,
        ha="center",
        va="center",
    ):

        self.text(
            x + offset[0],
            y + offset[1],
            text,
            style=style,
            ha=ha,
            va=va,
        )

    # Draw Rotated Text
    def rotated_text(
        self,
        x,
        y,
        value,
        angle,
        style=None,
        ha="center",
        va="center",
    ):

        self.text(
            x,
            y,
            value,
            style=style,
            ha=ha,
            va=va,
            rotation=angle,
        )

    # Draw Vertical Text
    def vertical_text(
        self,
        x,
        y,
        value,
        style=None,
        ha="center",
        va="center",
    ):

        self.rotated_text(
            x,
            y,
            value,
            angle=90,
            style=style,
            ha=ha,
            va=va,
        )

    # Draw Horizontal Text
    def horizontal_text(
        self,
        x,
        y,
        value,
        style=None,
        ha="center",
        va="center",
    ):

        self.text(
            x,
            y,
            value,
            style=style,
            ha=ha,
            va=va,
            rotation=0,
        )

    # Draw Centered Text
    def centered_text(
        self,
        x,
        y,
        value,
        style=None,
    ):

        self.text(
            x,
            y,
            value,
            style=style,
            ha="center",
            va="center",
        )

    # Draw Coordinate Axes
    def axes(
        self,
        style=None,
    ):

        style = self._resolve_style(style)

        x_min, x_max = self.canvas.get_xlim()
        y_min, y_max = self.canvas.get_ylim()

        self.line(
            x_min,
            0,
            x_max,
            0,
            style=style,
        )

        self.line(
            0,
            y_min,
            0,
            y_max,
            style=style,
        )

    # Draw Coordinate Plane
    def coordinate_plane(
        self,
        major_grid=True,
        minor_grid=False,
        style=None,
    ):

        self.show_axes()

        if major_grid or minor_grid:
            self.show_grid(
                major=major_grid,
                minor=minor_grid,
            )

        self.axes(style=style)

    # Draw Number Line
    def number_line(
        self,
        start,
        end,
        y=0,
        style=None,
    ):

        self.line(
            start,
            y,
            end,
            y,
            style=style,
        )

    # Draw Tick Marks
    def ticks(
        self,
        positions,
        axis="x",
        size=0.2,
        style=None,
    ):

        style = self._resolve_style(style)

        for value in positions:

            if axis.lower() == "x":

                self.line(
                    value,
                    -size,
                    value,
                    size,
                    style=style,
                )

            else:

                self.line(
                    -size,
                    value,
                    size,
                    value,
                    style=style,
                )

    # Set X Ticks
    def set_xticks(
        self,
        ticks,
        labels=None,
    ):

        self.axis.set_xticks(ticks)

        if labels is not None:
            self.axis.set_xticklabels(labels)

    # Set Y Ticks
    def set_yticks(
        self,
        ticks,
        labels=None,
    ):

        self.axis.set_yticks(ticks)

        if labels is not None:
            self.axis.set_yticklabels(labels)

    # Equal Aspect
    def equal_aspect(self):

        self.canvas.set_equal_aspect(True)

    # Auto Aspect
    def auto_aspect(self):

        self.canvas.set_equal_aspect(False)

    # Get Axis
    def get_axis(self):

        return self.axis

    # Get Canvas
    def get_canvas(self):

        return self.canvas


__all__ = [
    "DrawingPrimitives",
]