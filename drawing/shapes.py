from math import cos
from math import pi
from math import sin
from math import sqrt

from drawing.primitives import DrawingPrimitives
from drawing.styles import DEFAULT_STYLE
from drawing.styles import DrawingStyle

class DrawingShapes:
    """
    High-level reusable shapes.

    This class combines low-level drawing primitives into
    commonly used shapes such as rectangles, diamonds,
    hexagons, flowchart symbols, clouds, stars, etc.

    Every method should delegate the actual drawing to
    DrawingPrimitives.
    """

    # Constructor
    def __init__(self, canvas):

        self.canvas = canvas

        self.primitives = DrawingPrimitives(canvas)

    # Internal Helpers
    def _resolve_style(
        self,
        style,
    ):
        """
        Resolve the supplied drawing style.

        Parameters
        ----------
        style : DrawingStyle | None

        Returns
        -------
        DrawingStyle
        """

        if style is None:
            return DEFAULT_STYLE

        if isinstance(style, DrawingStyle):
            return style

        raise TypeError(
            "style must be a DrawingStyle or None"
        )

    def _validate_dimension(
        self,
        value,
        name,
    ):
        """
        Ensure a dimension is positive.
        """

        if value <= 0:
            raise ValueError(
                f"{name} must be greater than zero."
            )

    def _validate_point(
        self,
        point,
        name="point",
    ):
        """
        Validate a coordinate pair.
        """

        if len(point) != 2:
            raise ValueError(
                f"{name} must contain exactly two values."
            )

    def _rectangle_points(
        self,
        x,
        y,
        width,
        height,
    ):
        """
        Return rectangle corner coordinates.
        """

        return [
            (x, y),
            (x + width, y),
            (x + width, y + height),
            (x, y + height),
        ]

    def _center(
        self,
        x,
        y,
        width,
        height,
    ):
        """
        Calculate the center of a rectangle.
        """

        return (
            x + width / 2,
            y + height / 2,
        )

    def _rotate_point(
        self,
        point,
        center,
        angle,
    ):
        """
        Rotate a point around a center.

        Angle is measured in degrees.
        """

        if angle == 0:
            return point

        radians = angle * pi / 180.0

        px, py = point
        cx, cy = center

        dx = px - cx
        dy = py - cy

        rx = (
            dx * cos(radians)
            - dy * sin(radians)
        )

        ry = (
            dx * sin(radians)
            + dy * cos(radians)
        )

        return (
            cx + rx,
            cy + ry,
        )

    def _rotate_points(
        self,
        points,
        center,
        angle,
    ):
        """
        Rotate multiple points around a center.
        """

        if angle == 0:
            return points

        return [
            self._rotate_point(
                point,
                center,
                angle,
            )
            for point in points
        ]

    def _draw_polygon(
        self,
        points,
        style,
        rotation=0,
    ):
        """
        Draw a polygon with optional rotation.
        """

        style = self._resolve_style(style)

        if rotation != 0:

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            center = (
                sum(xs) / len(xs),
                sum(ys) / len(ys),
            )

            points = self._rotate_points(
                points,
                center,
                rotation,
            )

        self.primitives.polygon(
            points,
            style=style,
        )

    def _draw_label(
        self,
        x,
        y,
        width,
        height,
        label,
        style,
        rotation=0,
    ):
        """
        Draw centered text inside a shape.
        """

        if label is None:
            return

        cx, cy = self._center(
            x,
            y,
            width,
            height,
        )

        self.primitives.text(
            cx,
            cy,
            label,
            style=style,
            rotation=rotation,
        )

    def _regular_polygon(
        self,
        center_x,
        center_y,
        radius,
        sides,
        rotation=0,
    ):
        """
        Generate vertices for a regular polygon.
        """

        self._validate_dimension(
            radius,
            "radius",
        )

        if sides < 3:
            raise ValueError(
                "A polygon must have at least 3 sides."
            )

        angle_step = (
            2 * pi
        ) / sides

        start_angle = (
            -pi / 2
        ) + (
            rotation * pi / 180
        )

        vertices = []

        for i in range(sides):

            angle = (
                start_angle
                + i * angle_step
            )

            px = (
                center_x
                + radius * cos(angle)
            )

            py = (
                center_y
                + radius * sin(angle)
            )

            vertices.append(
                (
                    px,
                    py,
                )
            )

        return vertices
    
    # Rectangle
    def rectangle(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a rectangle.
        """

        style = self._resolve_style(style)

        self._validate_dimension(width, "width")
        self._validate_dimension(height, "height")

        if rotation == 0:

            self.primitives.rectangle(
                x,
                y,
                width,
                height,
                style=style,
            )

        else:

            points = self._rectangle_points(
                x,
                y,
                width,
                height,
            )

            self._draw_polygon(
                points,
                style,
                rotation=rotation,
            )

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Rounded Rectangle
    def rounded_rectangle(
        self,
        x,
        y,
        width,
        height,
        radius=0.2,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a rounded rectangle.
        """

        style = self._resolve_style(style)

        self._validate_dimension(width, "width")
        self._validate_dimension(height, "height")

        if rotation == 0:

            self.primitives.rounded_rectangle(
                x,
                y,
                width,
                height,
                radius=radius,
                style=style,
            )

        else:

            points = self._rectangle_points(
                x,
                y,
                width,
                height,
            )

            self._draw_polygon(
                points,
                style,
                rotation=rotation,
            )

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Square
    def square(
        self,
        x,
        y,
        size,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a square.
        """

        self.rectangle(
            x=x,
            y=y,
            width=size,
            height=size,
            label=label,
            style=style,
            rotation=rotation,
        )

    # Circle
    def circle(
        self,
        x,
        y,
        radius,
        label=None,
        style=None,
    ):
        """
        Draw a circle.
        """

        style = self._resolve_style(style)

        self._validate_dimension(
            radius,
            "radius",
        )

        self.primitives.circle(
            x,
            y,
            radius,
            style=style,
        )

        if label is not None:

            self.primitives.text(
                x,
                y,
                label,
                style=style,
            )

    # Ellipse
    def ellipse(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw an ellipse.
        """

        style = self._resolve_style(style)

        self._validate_dimension(width, "width")
        self._validate_dimension(height, "height")

        self.primitives.ellipse(
            x,
            y,
            width,
            height,
            angle=rotation,
            style=style,
        )

        if label is not None:

            self.primitives.text(
                x,
                y,
                label,
                style=style,
                rotation=rotation,
            )

    # Triangle
    def triangle(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw an isosceles triangle.
        """

        style = self._resolve_style(style)

        self._validate_dimension(width, "width")
        self._validate_dimension(height, "height")

        points = [

            (
                x + width / 2,
                y + height,
            ),

            (
                x,
                y,
            ),

            (
                x + width,
                y,
            ),

        ]

        self._draw_polygon(
            points,
            style,
            rotation=rotation,
        )

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Right Triangle
    def right_triangle(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a right triangle.
        """

        style = self._resolve_style(style)

        self._validate_dimension(width, "width")
        self._validate_dimension(height, "height")

        points = [

            (
                x,
                y,
            ),

            (
                x,
                y + height,
            ),

            (
                x + width,
                y,
            ),

        ]

        self._draw_polygon(
            points,
            style,
            rotation=rotation,
        )

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Diamond
    def diamond(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a diamond (rhombus).
        """

        style = self._resolve_style(style)

        self._validate_dimension(width, "width")
        self._validate_dimension(height, "height")

        points = [
            (x + width / 2, y + height),
            (x + width, y + height / 2),
            (x + width / 2, y),
            (x, y + height / 2),
        ]

        self._draw_polygon(points, style, rotation)

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Parallelogram
    def parallelogram(
        self,
        x,
        y,
        width,
        height,
        offset=None,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a parallelogram.
        """

        style = self._resolve_style(style)

        self._validate_dimension(width, "width")
        self._validate_dimension(height, "height")

        if offset is None:
            offset = width * 0.20

        points = [
            (x + offset, y + height),
            (x + width, y + height),
            (x + width - offset, y),
            (x, y),
        ]

        self._draw_polygon(points, style, rotation)

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Trapezoid
    def trapezoid(
        self,
        x,
        y,
        width,
        height,
        top_width_ratio=0.60,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw an isosceles trapezoid.
        """

        style = self._resolve_style(style)

        self._validate_dimension(width, "width")
        self._validate_dimension(height, "height")

        top_width = width * top_width_ratio
        inset = (width - top_width) / 2

        points = [
            (x + inset, y + height),
            (x + inset + top_width, y + height),
            (x + width, y),
            (x, y),
        ]

        self._draw_polygon(points, style, rotation)

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Regular Polygon
    def regular_polygon(
        self,
        x,
        y,
        radius,
        sides,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a regular polygon.
        """

        style = self._resolve_style(style)

        vertices = self._regular_polygon(
            x,
            y,
            radius,
            sides,
            rotation,
        )

        self.primitives.polygon(
            vertices,
            style=style,
        )

        if label is not None:

            self.primitives.text(
                x,
                y,
                label,
                style=style,
                rotation=rotation,
            )

    # Pentagon
    def pentagon(
        self,
        x,
        y,
        radius,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a regular pentagon.
        """

        self.regular_polygon(
            x=x,
            y=y,
            radius=radius,
            sides=5,
            label=label,
            style=style,
            rotation=rotation,
        )

    # Hexagon
    def hexagon(
        self,
        x,
        y,
        radius,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a regular hexagon.
        """

        self.regular_polygon(
            x=x,
            y=y,
            radius=radius,
            sides=6,
            label=label,
            style=style,
            rotation=rotation,
        )

    # Octagon
    def octagon(
        self,
        x,
        y,
        radius,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a regular octagon.
        """

        self.regular_polygon(
            x=x,
            y=y,
            radius=radius,
            sides=8,
            label=label,
            style=style,
            rotation=rotation,
        )

    # Folder
    def folder(
        self,
        x,
        y,
        width,
        height,
        tab_width=None,
        tab_height=None,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a folder.
        """

        style = self._resolve_style(style)

        if tab_width is None:
            tab_width = width * 0.35

        if tab_height is None:
            tab_height = height * 0.25

        points = [
            (x, y),
            (x + tab_width, y),
            (x + tab_width + tab_width * 0.25, y + tab_height),
            (x + width, y + tab_height),
            (x + width, y + height),
            (x, y + height),
        ]

        self._draw_polygon(points, style, rotation)

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # File
    def file(
        self,
        x,
        y,
        width,
        height,
        fold_size=None,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a file/page.
        """

        style = self._resolve_style(style)

        if fold_size is None:
            fold_size = min(width, height) * 0.20

        points = [
            (x, y),
            (x + width - fold_size, y),
            (x + width, y + fold_size),
            (x + width, y + height),
            (x, y + height),
        ]

        self._draw_polygon(points, style, rotation)

        self.primitives.line(
            x + width - fold_size,
            y,
            x + width - fold_size,
            y + fold_size,
            style=style,
        )

        self.primitives.line(
            x + width - fold_size,
            y + fold_size,
            x + width,
            y + fold_size,
            style=style,
        )

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Note
    def note(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Sticky note.
        """

        self.file(
            x=x,
            y=y,
            width=width,
            height=height,
            fold_size=min(width, height) * 0.18,
            label=label,
            style=style,
            rotation=rotation,
        )

    # Cloud
    def cloud(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
    ):
        """
        Cloud symbol.
        """

        style = self._resolve_style(style)

        r = min(width, height) * 0.18

        circles = [

            (x + width * 0.18, y + height * 0.52),

            (x + width * 0.35, y + height * 0.78),

            (x + width * 0.58, y + height * 0.82),

            (x + width * 0.80, y + height * 0.60),

            (x + width * 0.66, y + height * 0.34),

            (x + width * 0.40, y + height * 0.28),

        ]

        for cx, cy in circles:

            self.primitives.circle(
                cx,
                cy,
                r,
                style=style,
            )

        if label is not None:

            self.primitives.text(
                x + width / 2,
                y + height / 2,
                label,
                style=style,
            )

    # Speech Bubble
    def speech_bubble(
        self,
        x,
        y,
        width,
        height,
        tail_size=None,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Speech bubble.
        """

        style = self._resolve_style(style)

        if tail_size is None:
            tail_size = min(width, height) * 0.18

        self.rounded_rectangle(
            x,
            y + tail_size,
            width,
            height - tail_size,
            radius=0.18,
            style=style,
            rotation=rotation,
        )

        tail = [

            (
                x + width * 0.30,
                y + tail_size,
            ),

            (
                x + width * 0.40,
                y,
            ),

            (
                x + width * 0.48,
                y + tail_size,
            ),

        ]

        self._draw_polygon(
            tail,
            style,
            rotation,
        )

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Thought Bubble
    def thought_bubble(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
    ):
        """
        Thought bubble.
        """

        style = self._resolve_style(style)

        self.cloud(
            x,
            y,
            width,
            height,
            label=label,
            style=style,
        )

        r = min(width, height) * 0.06

        self.primitives.circle(
            x + width * 0.18,
            y - r * 2.5,
            r,
            style=style,
        )

        self.primitives.circle(
            x + width * 0.08,
            y - r * 5,
            r * 0.70,
            style=style,
        )

    # Banner
    def banner(
        self,
        x,
        y,
        width,
        height,
        notch=None,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Ribbon banner.
        """

        style = self._resolve_style(style)

        if notch is None:
            notch = width * 0.10

        points = [

            (x, y + height / 2),

            (x + notch, y + height),

            (x + width - notch, y + height),

            (x + width, y + height / 2),

            (x + width - notch, y),

            (x + notch, y),

        ]

        self._draw_polygon(
            points,
            style,
            rotation,
        )

        self._draw_label(
            x,
            y,
            width,
            height,
            label,
            style,
            rotation,
        )

    # Flag
    def flag(
        self,
        x,
        y,
        width,
        height,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Flag symbol.
        """

        style = self._resolve_style(style)

        self.primitives.line(
            x,
            y,
            x,
            y + height,
            style=style,
        )

        points = [

            (x, y + height),

            (x + width, y + height * 0.80),

            (x + width * 0.72, y + height * 0.45),

            (x + width, y),

            (x, y),

        ]

        self._draw_polygon(
            points,
            style,
            rotation,
        )

        if label is not None:

            self.primitives.text(
                x + width * 0.50,
                y + height * 0.52,
                label,
                style=style,
                rotation=rotation,
            )

    # Star
    def star(
        self,
        x,
        y,
        outer_radius,
        inner_radius=None,
        points=5,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a star.
        """

        style = self._resolve_style(style)

        if inner_radius is None:
            inner_radius = outer_radius * 0.45

        vertices = []

        start = -pi / 2 + rotation * pi / 180

        for i in range(points * 2):

            angle = start + i * pi / points

            radius = (
                outer_radius
                if i % 2 == 0
                else inner_radius
            )

            vertices.append(
                (
                    x + radius * cos(angle),
                    y + radius * sin(angle),
                )
            )

        self.primitives.polygon(
            vertices,
            style=style,
        )

        if label is not None:

            self.primitives.text(
                x,
                y,
                label,
                style=style,
            )

    # Heart
    def heart(
        self,
        x,
        y,
        size,
        label=None,
        style=None,
    ):
        """
        Draw a heart.
        """

        style = self._resolve_style(style)

        r = size * 0.25

        self.primitives.circle(
            x - r,
            y + r,
            r,
            style=style,
        )

        self.primitives.circle(
            x + r,
            y + r,
            r,
            style=style,
        )

        points = [
            (x - size * 0.50, y + r),
            (x, y - size * 0.50),
            (x + size * 0.50, y + r),
        ]

        self.primitives.polygon(
            points,
            style=style,
        )

        if label is not None:

            self.primitives.text(
                x,
                y,
                label,
                style=style,
            )

    # Gear
    def gear(
        self,
        x,
        y,
        radius,
        teeth=8,
        label=None,
        style=None,
        rotation=0,
    ):
        """
        Draw a simple gear.
        """

        style = self._resolve_style(style)

        outer = radius
        inner = radius * 0.75

        vertices = []

        start = rotation * pi / 180

        for i in range(teeth * 2):

            angle = start + i * pi / teeth

            r = outer if i % 2 == 0 else inner

            vertices.append(
                (
                    x + r * cos(angle),
                    y + r * sin(angle),
                )
            )

        self.primitives.polygon(
            vertices,
            style=style,
        )

        self.primitives.circle(
            x,
            y,
            radius * 0.35,
            style=style,
        )

        if label is not None:

            self.primitives.text(
                x,
                y,
                label,
                style=style,
            )

    # Cross
    def cross(
        self,
        x,
        y,
        size,
        thickness=None,
        style=None,
    ):
        """
        Draw a medical cross.
        """

        style = self._resolve_style(style)

        if thickness is None:
            thickness = size * 0.30

        self.primitives.rectangle(
            x - thickness / 2,
            y - size / 2,
            thickness,
            size,
            style=style,
        )

        self.primitives.rectangle(
            x - size / 2,
            y - thickness / 2,
            size,
            thickness,
            style=style,
        )

    # Plus
    def plus(
        self,
        x,
        y,
        size,
        style=None,
    ):
        """
        Draw a plus sign.
        """

        style = self._resolve_style(style)

        h = size / 2

        self.primitives.line(
            x - h,
            y,
            x + h,
            y,
            style=style,
        )

        self.primitives.line(
            x,
            y - h,
            x,
            y + h,
            style=style,
        )

    # Minus
    def minus(
        self,
        x,
        y,
        size,
        style=None,
    ):
        """
        Draw a minus sign.
        """

        style = self._resolve_style(style)

        h = size / 2

        self.primitives.line(
            x - h,
            y,
            x + h,
            y,
            style=style,
        )

    # Check Mark
    def check(
        self,
        x,
        y,
        size,
        style=None,
    ):
        """
        Draw a check mark.
        """

        style = self._resolve_style(style)

        self.primitives.line(
            x - size * 0.40,
            y,
            x - size * 0.10,
            y - size * 0.30,
            style=style,
        )

        self.primitives.line(
            x - size * 0.10,
            y - size * 0.30,
            x + size * 0.45,
            y + size * 0.35,
            style=style,
        )

    # X Mark
    def x_mark(
        self,
        x,
        y,
        size,
        style=None,
    ):
        """
        Draw an X mark.
        """

        style = self._resolve_style(style)

        h = size / 2

        self.primitives.line(
            x - h,
            y - h,
            x + h,
            y + h,
            style=style,
        )

        self.primitives.line(
            x - h,
            y + h,
            x + h,
            y - h,
            style=style,
        )

    # Target
    def target(
        self,
        x,
        y,
        radius,
        rings=3,
        style=None,
    ):
        """
        Draw a target.
        """

        style = self._resolve_style(style)

        for i in range(rings, 0, -1):

            self.primitives.circle(
                x,
                y,
                radius * i / rings,
                style=style,
            )

        self.primitives.line(
            x - radius,
            y,
            x + radius,
            y,
            style=style,
        )

        self.primitives.line(
            x,
            y - radius,
            x,
            y + radius,
            style=style,
        )

    # Brace
    def brace(
        self,
        x1,
        y1,
        x2,
        y2,
        size=0.20,
        style=None,
    ):
        """
        Draw a simple brace between two points.
        """

        style = self._resolve_style(style)

        dx = x2 - x1
        dy = y2 - y1

        length = sqrt(dx * dx + dy * dy)

        if length == 0:
            return

        nx = -dy / length
        ny = dx / length

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        offset = length * size * 0.15

        points = [

            (x1, y1),

            (
                x1 + dx * 0.25 + nx * offset,
                y1 + dy * 0.25 + ny * offset,
            ),

            (
                mx,
                my,
            ),

            (
                x1 + dx * 0.75 + nx * offset,
                y1 + dy * 0.75 + ny * offset,
            ),

            (
                x2,
                y2,
            ),

        ]

        for p1, p2 in zip(points[:-1], points[1:]):

            self.primitives.line(
                p1[0],
                p1[1],
                p2[0],
                p2[1],
                style=style,
            )

    # Bracket
    def bracket(
        self,
        x1,
        y1,
        x2,
        y2,
        size=0.15,
        style=None,
    ):
        """
        Draw a square bracket.
        """

        style = self._resolve_style(style)

        dx = x2 - x1
        dy = y2 - y1

        length = sqrt(dx * dx + dy * dy)

        if length == 0:
            return

        nx = -dy / length
        ny = dx / length

        offset = length * size

        p1 = (
            x1 + nx * offset,
            y1 + ny * offset,
        )

        p2 = (
            x2 + nx * offset,
            y2 + ny * offset,
        )

        self.primitives.line(
            x1,
            y1,
            x2,
            y2,
            style=style,
        )

        self.primitives.line(
            x1,
            y1,
            p1[0],
            p1[1],
            style=style,
        )

        self.primitives.line(
            x2,
            y2,
            p2[0],
            p2[1],
            style=style,
        )

    # Angle Marker
    def angle_marker(
        self,
        center_x,
        center_y,
        radius,
        start_angle,
        end_angle,
        label=None,
        style=None,
    ):
        """
        Draw an angle marker.
        """

        style = self._resolve_style(style)

        self.primitives.arc(
            center_x,
            center_y,
            radius * 2,
            radius * 2,
            theta1=start_angle,
            theta2=end_angle,
            style=style,
        )

        if label is not None:

            mid = (start_angle + end_angle) / 2

            px = center_x + radius * 1.35 * cos(
                mid * pi / 180
            )

            py = center_y + radius * 1.35 * sin(
                mid * pi / 180
            )

            self.primitives.text(
                px,
                py,
                label,
                style=style,
            )

    # Coordinate Marker
    def coordinate_marker(
        self,
        x,
        y,
        size=0.15,
        label=None,
        style=None,
    ):
        """
        Draw a coordinate point marker.
        """

        style = self._resolve_style(style)

        self.primitives.circle(
            x,
            y,
            size,
            style=style,
        )

        self.primitives.line(
            x - size * 2,
            y,
            x + size * 2,
            y,
            style=style,
        )

        self.primitives.line(
            x,
            y - size * 2,
            x,
            y + size * 2,
            style=style,
        )

        if label is not None:

            self.primitives.text(
                x + size * 3,
                y + size * 3,
                label,
                style=style,
            )

    # Measurement Box
    def measurement_box(
        self,
        x1,
        y1,
        x2,
        y2,
        text,
        box_height=0.35,
        style=None,
    ):
        """
        Draw a measurement annotation.
        """

        style = self._resolve_style(style)

        self.primitives.line(
            x1,
            y1,
            x2,
            y2,
            style=style,
        )

        tick = box_height * 0.50

        self.primitives.line(
            x1,
            y1 - tick,
            x1,
            y1 + tick,
            style=style,
        )

        self.primitives.line(
            x2,
            y2 - tick,
            x2,
            y2 + tick,
            style=style,
        )

        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        width = max(
            0.70,
            len(str(text)) * 0.18,
        )

        self.primitives.rectangle(
            mx - width / 2,
            my - box_height / 2,
            width,
            box_height,
            style=style,
        )

        self.primitives.text(
            mx,
            my,
            str(text),
            style=style,
        )

    # Shape Rotation
    def rotate_shape(
        self,
        points,
        angle,
        center=None,
    ):
        """
        Rotate a sequence of points.
        """

        if center is None:

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            center = (
                sum(xs) / len(xs),
                sum(ys) / len(ys),
            )

        return self._rotate_points(
            points,
            center,
            angle,
        )

    # Shape Scaling
    def scale_shape(
        self,
        points,
        scale_x=1.0,
        scale_y=None,
        center=None,
    ):
        """
        Scale a sequence of points.
        """

        if scale_y is None:
            scale_y = scale_x

        if center is None:

            xs = [p[0] for p in points]
            ys = [p[1] for p in points]

            center = (
                sum(xs) / len(xs),
                sum(ys) / len(ys),
            )

        cx, cy = center

        scaled = []

        for px, py in points:

            scaled.append(
                (
                    cx + (px - cx) * scale_x,
                    cy + (py - cy) * scale_y,
                )
            )

        return scaled

    # Bounding Box
    def bounding_box(
        self,
        points,
    ):
        """
        Return the bounding box of points.

        Returns:
            (min_x, min_y, width, height)
        """

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        min_x = min(xs)
        max_x = max(xs)

        min_y = min(ys)
        max_y = max(ys)

        return (
            min_x,
            min_y,
            max_x - min_x,
            max_y - min_y,
        )

    # Label Helpers
    def label_at_center(
        self,
        points,
        text,
        style=None,
        rotation=0,
    ):
        """
        Place a label at the center of a polygon.
        """

        style = self._resolve_style(style)

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]

        self.primitives.text(
            sum(xs) / len(xs),
            sum(ys) / len(ys),
            text,
            style=style,
            rotation=rotation,
        )

    def label_at(
        self,
        x,
        y,
        text,
        style=None,
        rotation=0,
    ):
        """
        Draw a label at an arbitrary position.
        """

        style = self._resolve_style(style)

        self.primitives.text(
            x,
            y,
            text,
            style=style,
            rotation=rotation,
        )

# Public Exports

__all__ = [ "DrawingShapes", ]