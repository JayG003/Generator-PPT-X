import math
from copy import replace

from drawing.arrows import DrawingArrows
from drawing.labels import DrawingLabels
from drawing.primitives import DrawingPrimitives
from drawing.shapes import DrawingShapes

from drawing.styles import (
    DEFAULT_STYLE,
    LABEL_STYLE,
    DrawingStyle,
)


class DrawingDimensions:

    # Constructor
    def __init__(
        self,
        canvas,
    ):

        self.canvas = canvas
        self.axis = canvas.get_axis()
        self.figure = canvas.get_figure()

        self.primitives = DrawingPrimitives(canvas)
        self.arrows = DrawingArrows(canvas)
        self.labels = DrawingLabels(canvas)
        self.shapes = DrawingShapes(canvas)

    # Style Helpers
    def _resolve_style(
        self,
        style=None,
        **overrides,
    ):

        if style is None:
            style = DEFAULT_STYLE

        if not isinstance(
            style,
            DrawingStyle,
        ):
            raise TypeError(
                "style must be a DrawingStyle or None"
            )

        if not overrides:
            return style

        return replace(
            style,
            **overrides,
        )

    def _resolve_label_style(
        self,
        style=None,
        **overrides,
    ):

        if style is None:
            style = LABEL_STYLE

        if not isinstance(
            style,
            DrawingStyle,
        ):
            raise TypeError(
                "style must be a DrawingStyle or None"
            )

        if not overrides:
            return style

        return replace(
            style,
            **overrides,
        )

    def _copy_style(
        self,
        style,
        **changes,
    ):

        style = self._resolve_style(style)

        if not changes:
            return style

        return replace(
            style,
            **changes,
        )

    def _copy_label_style(
        self,
        style,
        **changes,
    ):

        style = self._resolve_label_style(style)

        if not changes:
            return style

        return replace(
            style,
            **changes,
        )

    def _dimension_style(
        self,
        style=None,
        line_width=None,
        line_color=None,
        text_color=None,
        alpha=None,
        font_size=None,
        font_weight=None,
    ):

        overrides = {}

        if line_width is not None:
            overrides["line_width"] = line_width

        if line_color is not None:
            overrides["line_color"] = line_color

        if text_color is not None:
            overrides["text_color"] = text_color

        if alpha is not None:
            overrides["alpha"] = alpha

        if font_size is not None:
            overrides["font_size"] = font_size

        if font_weight is not None:
            overrides["font_weight"] = font_weight

        return self._resolve_style(
            style,
            **overrides,
        )

    def _label_style(
        self,
        style=None,
        font_size=None,
        font_weight=None,
        text_color=None,
        fill_color=None,
        alpha=None,
    ):

        overrides = {}

        if font_size is not None:
            overrides["font_size"] = font_size

        if font_weight is not None:
            overrides["font_weight"] = font_weight

        if text_color is not None:
            overrides["text_color"] = text_color

        if fill_color is not None:
            overrides["fill_color"] = fill_color

        if alpha is not None:
            overrides["alpha"] = alpha

        return self._resolve_label_style(
            style,
            **overrides,
        )
    
    # Geometry Helpers
    def _distance(
        self,
        start,
        end,
    ):

        return self.arrows._distance(
            start,
            end,
        )

    def _direction(
        self,
        start,
        end,
    ):

        return self.arrows._direction(
            start,
            end,
        )

    def _perpendicular(
        self,
        direction,
    ):

        return self.arrows._perpendicular(
            direction,
        )

    def _angle(
        self,
        start,
        end,
    ):

        return self.arrows._angle(
            start,
            end,
        )

    def _midpoint(
        self,
        start,
        end,
    ):

        return self.arrows._midpoint(
            start,
            end,
        )

    def _line_length(
        self,
        start,
        end,
    ):

        return self._distance(
            start,
            end,
        )

    def _normalize(
        self,
        vector,
    ):

        length = math.hypot(
            vector[0],
            vector[1],
        )

        if length == 0:
            return (
                0.0,
                0.0,
            )

        return (
            vector[0] / length,
            vector[1] / length,
        )

    def _point_along(
        self,
        start,
        end,
        distance,
    ):

        direction = self._direction(
            start,
            end,
        )

        return (
            start[0] + direction[0] * distance,
            start[1] + direction[1] * distance,
        )

    def _rotate_vector(
        self,
        vector,
        angle,
    ):

        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        return (
            vector[0] * cos_angle
            - vector[1] * sin_angle,
            vector[0] * sin_angle
            + vector[1] * cos_angle,
        )

    def _project_point(
        self,
        point,
        line_start,
        line_end,
    ):

        dx = line_end[0] - line_start[0]
        dy = line_end[1] - line_start[1]

        denominator = (
            dx * dx
            + dy * dy
        )

        if denominator == 0:
            return line_start

        t = (
            (
                (point[0] - line_start[0]) * dx
                + (point[1] - line_start[1]) * dy
            )
            / denominator
        )

        return (
            line_start[0] + t * dx,
            line_start[1] + t * dy,
        )
    
    # Offset Calculations
    def _offset_point(
        self,
        point,
        direction,
        distance,
    ):

        return self.arrows._offset_point(
            point,
            direction,
            distance,
        )


    def _offset_line(
        self,
        start,
        end,
        offset,
    ):

        direction = self._direction(
            start,
            end,
        )

        perpendicular = self._perpendicular(
            direction,
        )

        return (
            self._offset_point(
                start,
                perpendicular,
                offset,
            ),
            self._offset_point(
                end,
                perpendicular,
                offset,
            ),
        )


    def _extend_line(
        self,
        start,
        end,
        start_extension=0,
        end_extension=0,
    ):

        direction = self._direction(
            start,
            end,
        )

        new_start = (
            start[0] - direction[0] * start_extension,
            start[1] - direction[1] * start_extension,
        )

        new_end = (
            end[0] + direction[0] * end_extension,
            end[1] + direction[1] * end_extension,
        )

        return (
            new_start,
            new_end,
        )


    def _trim_line(
    self,
    start,
    end,
    start_trim=0,
    end_trim=0,
    ):
        return self.arrows._trim_line(
            start,
            end,
            start_trim,
            end_trim,
        )

    # Arrow Placement Helpers
    def _arrow_endpoints(
        self,
        start,
        end,
        start_padding=0,
        end_padding=0,
    ):

        return self.arrows._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

    def _inside_dimension(
        self,
        start,
        end,
        arrow_size,
        text_width=0,
    ):

        return (
            self._distance(start, end)
            >= (arrow_size * 2 + text_width)
        )

    def _arrow_direction(
        self,
        start,
        end,
    ):

        return self._direction(
            start,
            end,
        )
    
    def _extension_line(
        self,
        start,
        end,
        style,
    ):

        self.primitives.line(
            start[0],
            start[1],
            end[0],
            end[1],
            style=style,
        )

    # Label Placement Helpers
    def _label_position(
        self,
        start,
        end,
        offset=0,
    ):

        midpoint = self._midpoint(
            start,
            end,
        )

        if offset == 0:
            return midpoint

        direction = self._direction(
            start,
            end,
        )

        perpendicular = self._perpendicular(
            direction,
        )

        return (
            midpoint[0] + perpendicular[0] * offset,
            midpoint[1] + perpendicular[1] * offset,
        )

    def _label_rotation(
        self,
        start,
        end,
    ):

        angle = math.degrees(
            self._angle(
                start,
                end,
            )
        )

        if angle > 90:
            angle -= 180

        elif angle < -90:
            angle += 180

        return angle

    def _label_anchor(
        self,
        start,
        end,
        offset=0,
    ):

        x, y = self._label_position(
            start,
            end,
            offset,
        )

        return (
            x,
            y,
            "center",
            "center",
        )

    def _text_offset(
        self,
        position,
        dx=0,
        dy=0,
    ):

        return (
            position[0] + dx,
            position[1] + dy,
        )

    def _dimension_text_position(
        self,
        start,
        end,
        offset=0,
    ):
        return self._label_position(
            start,
            end,
            offset,
        )

    def _draw_dimension_text(
        self,
        start,
        end,
        text,
        style,
        offset=0,
        rotation=None,
    ):

        x, y = self._dimension_text_position(
            start,
            end,
            offset,
        )

        if rotation is None:

            rotation = self._label_rotation(
                start,
                end,
            )

        self.labels.rotated_text(
            x,
            y,
            str(text),
            rotation,
            style=style,
        )

    # Horizontal Dimension
    def horizontal_dimension(
        self,
        start,
        end,
        text=None,
        offset=0.75,
        extension=0.20,
        style=None,
        text_style=None,
        arrow_size=15,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        dimension_start = (
            start[0],
            start[1] + offset,
        )

        dimension_end = (
            end[0],
            end[1] + offset,
        )

        self._extension_line(
            start,
            (
                start[0],
                dimension_start[1],
            ),
            style,
        )

        self._extension_line(
            end,
            (
                end[0],
                dimension_end[1],
            ),
            style,
        )

        self.arrows.double_arrow(
            dimension_start,
            dimension_end,
            style=style,
            mutation_scale=arrow_size,
        )

        if extension > 0:

            self.primitives.line(
                dimension_start[0],
                dimension_start[1],
                dimension_start[0],
                dimension_start[1] + extension,
                style=style,
            )

            self.primitives.line(
                dimension_end[0],
                dimension_end[1],
                dimension_end[0],
                dimension_end[1] + extension,
                style=style,
            )

        if text is None:

            text = round(
                abs(
                    end[0]
                    - start[0]
                ),
                2,
            )

        self._draw_dimension_text(
            dimension_start,
            dimension_end,
            text,
            text_style,
            offset=0.15,
            rotation=0,
        )

    # Vertical Dimension
    def vertical_dimension(
        self,
        start,
        end,
        text=None,
        offset=0.75,
        extension=0.20,
        style=None,
        text_style=None,
        arrow_size=15,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        dimension_start = (
            start[0] + offset,
            start[1],
        )

        dimension_end = (
            end[0] + offset,
            end[1],
        )

        self._extension_line(
            start,
            (
                dimension_start[0],
                start[1],
            ),
            style,
        )

        self._extension_line(
            end,
            (
                dimension_end[0],
                end[1],
            ),
            style,
        )

        self.arrows.double_arrow(
            dimension_start,
            dimension_end,
            style=style,
            mutation_scale=arrow_size,
        )

        if extension > 0:

            self.primitives.line(
                dimension_start[0],
                dimension_start[1],
                dimension_start[0] + extension,
                dimension_start[1],
                style=style,
            )

            self.primitives.line(
                dimension_end[0],
                dimension_end[1],
                dimension_end[0] + extension,
                dimension_end[1],
                style=style,
            )

        if text is None:

            text = round(
                abs(
                    end[1]
                    - start[1]
                ),
                2,
            )

        self._draw_dimension_text(
            dimension_start,
            dimension_end,
            text,
            text_style,
            offset=0.15,
            rotation=90,
        )

    # Dimension Line Helper
    def _dimension_line(
        self,
        start,
        end,
        offset,
    ):
        direction = self._direction(
            start,
            end,
        )

        perpendicular = self._perpendicular(
            direction,
        )

        offset_vector = (
            perpendicular[0] * offset,
            perpendicular[1] * offset,
        )

        dimension_start = (
            start[0] + offset_vector[0],
            start[1] + offset_vector[1],
        )

        dimension_end = (
            end[0] + offset_vector[0],
            end[1] + offset_vector[1],
        )

        return (
            dimension_start,
            dimension_end,
        )
    
    # Aligned Dimension
    def aligned_dimension(
        self,
        start,
        end,
        text=None,
        offset=0.75,
        extension=0.20,
        style=None,
        text_style=None,
        arrow_size=15,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        dimension_start, dimension_end = (
            self._dimension_line(
                start,
                end,
                offset,
            )
        )

        self._extension_line(
            start,
            dimension_start,
            style,
        )

        self._extension_line(
            end,
            dimension_end,
            style,
        )

        self.arrows.double_arrow(
            dimension_start,
            dimension_end,
            style=style,
            mutation_scale=arrow_size,
        )

        if extension > 0:

            direction = self._direction(
                start,
                end,
            )

            self.primitives.line(
                dimension_start[0],
                dimension_start[1],
                dimension_start[0] + direction[0] * extension,
                dimension_start[1] + direction[1] * extension,
                style=style,
            )

            self.primitives.line(
                dimension_end[0],
                dimension_end[1],
                dimension_end[0] - direction[0] * extension,
                dimension_end[1] - direction[1] * extension,
                style=style,
            )

        if text is None:

            text = round(
                self._distance(
                    start,
                    end,
                ),
                2,
            )

        self._draw_dimension_text(
            dimension_start,
            dimension_end,
            text,
            text_style,
        )

    # Linear Measurement
    def linear_measurement(
        self,
        start,
        end,
        text=None,
        offset=0.75,
        extension=0.20,
        style=None,
        text_style=None,
        arrow_size=15,
    ):

        dx = abs(
            end[0] - start[0]
        )

        dy = abs(
            end[1] - start[1]
        )

        if dy <= 1e-9:

            return self.horizontal_dimension(
                start=start,
                end=end,
                text=text,
                offset=offset,
                extension=extension,
                style=style,
                text_style=text_style,
                arrow_size=arrow_size,
            )

        if dx <= 1e-9:

            return self.vertical_dimension(
                start=start,
                end=end,
                text=text,
                offset=offset,
                extension=extension,
                style=style,
                text_style=text_style,
                arrow_size=arrow_size,
            )

        return self.aligned_dimension(
            start=start,
            end=end,
            text=text,
            offset=offset,
            extension=extension,
            style=style,
            text_style=text_style,
            arrow_size=arrow_size,
        )
    
    # Offset Dimension Lines
    def _offset_dimension_lines(
        self,
        start,
        end,
        count,
        spacing,
    ):
        """
        Generate parallel dimension lines.
        """

        lines = []

        for index in range(count):

            lines.append(
                self._dimension_line(
                    start,
                    end,
                    spacing * (index + 1),
                )
            )

        return lines
    # Baseline Dimension
    def baseline_dimension(
        self,
        origin,
        points,
        spacing=0.75,
        extension=0.20,
        style=None,
        text_style=None,
        arrow_size=15,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        for index, point in enumerate(points):

            self.aligned_dimension(
                origin,
                point,
                offset=spacing * (index + 1),
                extension=extension,
                style=style,
                text_style=text_style,
                arrow_size=arrow_size,
            )

    # Continuous Dimension
    def continuous_dimension(
        self,
        points,
        offset=0.75,
        extension=0.20,
        style=None,
        text_style=None,
        arrow_size=15,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        if len(points) < 2:
            return

        for start, end in zip(
            points[:-1],
            points[1:],
        ):

            self.aligned_dimension(
                start,
                end,
                offset=offset,
                extension=extension,
                style=style,
                text_style=text_style,
                arrow_size=arrow_size,
            )

    def _arc_angles(
        self,
        center,
        start,
        end,
        clockwise=False,
    ):
        start_angle = math.degrees(
            self._angle(
                center,
                start,
            )
        )

        end_angle = math.degrees(
            self._angle(
                center,
                end,
            )
        )

        start_angle %= 360
        end_angle %= 360

        if clockwise:

            if start_angle < end_angle:
                start_angle += 360

        else:

            if end_angle < start_angle:
                end_angle += 360

        return (
            start_angle,
            end_angle,
        )
    
    def _arc_midpoint(
        self,
        center,
        radius,
        theta1,
        theta2,
    ):
        mid = (
            theta1 + theta2
        ) / 2

        radians = math.radians(mid)

        return (
            center[0]
            + radius * math.cos(radians),

            center[1]
            + radius * math.sin(radians),
        )
    
    def _draw_arc(
        self,
        center,
        radius,
        theta1,
        theta2,
        style=None,
    ):
        style = self._dimension_style(
            style,
        )

        self.primitives.arc(
            center[0],
            center[1],
            radius * 2,
            radius * 2,
            theta1,
            theta2,
            style=style,
        )

    def _draw_arc_arrows(
        self,
        center,
        radius,
        theta1,
        theta2,
        style=None,
        arrow_length=0.30,
        mutation_scale=12,
    ):
        """
        Draw arrowheads tangent to both ends
        of an arc.
        """

        style = self._dimension_style(
            style,
        )

        for angle, direction in (
            (theta1, 1),
            (theta2, -1),
        ):

            radians = math.radians(angle)

            point = (
                center[0]
                + radius * math.cos(radians),

                center[1]
                + radius * math.sin(radians),
            )

            tangent = (
                -math.sin(radians),
                math.cos(radians),
            )

            tangent = (
                tangent[0] * direction,
                tangent[1] * direction,
            )

            end = (
                point[0]
                + tangent[0] * arrow_length,

                point[1]
                + tangent[1] * arrow_length,
            )

            self.arrows.open_arrow(
                point,
                end,
                style=style,
                mutation_scale=mutation_scale,
            )

    # Angle Dimension
    def angle_dimension(
        self,
        center,
        start,
        end,
        text=None,
        radius=1.0,
        clockwise=False,
        style=None,
        text_style=None,
        arrow_size=12,
    ):
        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        theta1, theta2 = self._arc_angles(
            center,
            start,
            end,
            clockwise,
        )

        self._draw_arc(
            center,
            radius,
            theta1,
            theta2,
            style,
        )

        self._draw_arc_arrows(
            center,
            radius,
            theta1,
            theta2,
            style,
            mutation_scale=arrow_size,
        )

        if text is None:

            sweep = abs(theta2 - theta1)

            if sweep > 360:
                sweep %= 360

            text = f"{round(sweep, 1)}°"

        label = self._arc_midpoint(
            center,
            radius + 0.20,
            theta1,
            theta2,
        )

        self.labels.centered_text(
            label[0],
            label[1],
            text,
            style=text_style,
        )

    # Arc Dimension
    def arc_dimension(
        self,
        center,
        radius,
        start,
        end,
        text=None,
        clockwise=False,
        style=None,
        text_style=None,
        arrow_size=12,
    ):
        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        theta1, theta2 = self._arc_angles(
            center,
            start,
            end,
            clockwise,
        )

        self._draw_arc(
            center,
            radius,
            theta1,
            theta2,
            style,
        )

        self._draw_arc_arrows(
            center,
            radius,
            theta1,
            theta2,
            style,
            mutation_scale=arrow_size,
        )

        if text is None:

            sweep = abs(
                math.radians(
                    theta2 - theta1
                )
            )

            arc_length = radius * sweep

            text = round(
                arc_length,
                2,
            )

        label = self._arc_midpoint(
            center,
            radius + 0.20,
            theta1,
            theta2,
        )

        self.labels.centered_text(
            label[0],
            label[1],
            str(text),
            style=text_style,
        )

    # Radius Dimension
    def radius_dimension(
        self,
        center,
        point,
        text=None,
        style=None,
        text_style=None,
        arrow_size=12,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        self.arrows.open_arrow(
            center,
            point,
            style=style,
            mutation_scale=arrow_size,
        )

        radius = self._distance(
            center,
            point,
        )

        if text is None:
            text = f"R{round(radius, 2)}"

        label = self._midpoint(
            center,
            point,
        )

        self.labels.centered_text(
            label[0],
            label[1],
            text,
            style=text_style,
        )

    # Diameter Dimension
    def diameter_dimension(
        self,
        center,
        radius,
        angle=0,
        text=None,
        style=None,
        text_style=None,
        arrow_size=12,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        radians = math.radians(angle)

        start = (
            center[0] - radius * math.cos(radians),
            center[1] - radius * math.sin(radians),
        )

        end = (
            center[0] + radius * math.cos(radians),
            center[1] + radius * math.sin(radians),
        )

        self.arrows.double_arrow(
            start,
            end,
            style=style,
            mutation_scale=arrow_size,
        )

        if text is None:
            text = f"Ø{round(radius * 2, 2)}"

        self.labels.centered_text(
            center[0],
            center[1],
            text,
            style=text_style,
        )

    # Chord Dimension
    def chord_dimension(
        self,
        start,
        end,
        text=None,
        style=None,
        text_style=None,
        arrow_size=12,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        self.arrows.double_arrow(
            start,
            end,
            style=style,
            mutation_scale=arrow_size,
        )

        if text is None:

            text = round(
                self._distance(
                    start,
                    end,
                ),
                2,
            )

        midpoint = self._midpoint(
            start,
            end,
        )

        self.labels.centered_text(
            midpoint[0],
            midpoint[1],
            str(text),
            style=text_style,
        )

    # Sector Dimension
    def sector_dimension(
        self,
        center,
        start,
        end,
        radius,
        text=None,
        clockwise=False,
        style=None,
        text_style=None,
        arrow_size=12,
    ):

        style = self._dimension_style(style)
        text_style = self._label_style(text_style)

        self.primitives.line(
            center[0],
            center[1],
            start[0],
            start[1],
            style=style,
        )

        self.primitives.line(
            center[0],
            center[1],
            end[0],
            end[1],
            style=style,
        )

        self.arc_dimension(
            center=center,
            radius=radius,
            start=start,
            end=end,
            text=text,
            clockwise=clockwise,
            style=style,
            text_style=text_style,
            arrow_size=arrow_size,
        )

    def _leader_path(
        self,
        start,
        elbow=None,
        end=None,
    ):

        points = [start]

        if elbow is not None:
            points.append(elbow)

        if end is not None:
            points.append(end)

        return points


    def _leader_label_position(
        self,
        start,
        elbow,
        end,
        gap=0.15,
    ):
        if elbow is None:

            midpoint = self._midpoint(
                start,
                end,
            )

            direction = self._direction(
                start,
                end,
            )

            normal = self._perpendicular(
                direction,
            )

            return self._offset_point(
                midpoint,
                normal,
                gap,
            )

        direction = self._direction(
            elbow,
            end,
        )

        normal = self._perpendicular(
            direction,
        )

        midpoint = self._midpoint(
            elbow,
            end,
        )

        return self._offset_point(
            midpoint,
            normal,
            gap,
        )


    def leader_line(
        self,
        start,
        end,
        text=None,
        elbow=None,
        style=None,
        label_style=None,
        arrow="closed",
        mutation_scale=15,
        text_gap=0.15,
    ):
        style = self._resolve_style(style)

        label_style = self._resolve_label_style(
            label_style,
        )

        points = self._leader_path(
            start,
            elbow,
            end,
        )

        # Draw leader segments
        if len(points) > 2:

            self.primitives.polyline(
                points[:-1],
                style=style,
            )

            line_start = points[-2]

        else:

            line_start = points[0]

        # Draw arrow + landing
        if arrow == "closed":

            self.arrows.line_arrow(
                line_start,
                end,
                style=style,
                mutation_scale=mutation_scale,
            )

        elif arrow == "open":

            self.arrows.open_arrow(
                line_start,
                end,
                style=style,
                mutation_scale=mutation_scale,
            )

        else:

            self.primitives.line(
                line_start[0],
                line_start[1],
                end[0],
                end[1],
                style=style,
            )

        if text is None:
            return

        tx, ty = self._leader_label_position(
            start,
            elbow,
            end,
            text_gap,
        )

        self.labels.centered_text(
            tx,
            ty,
            text,
            style=label_style,
        )

    def multi_leader(
        self,
        starts,
        end,
        text=None,
        elbows=None,
        style=None,
        label_style=None,
        arrow="closed",
        mutation_scale=15,
        text_gap=0.15,
    ):
        """
        Draw multiple leaders sharing a common landing.

        Parameters
        ----------
        starts : iterable[tuple]
            Arrow tip locations.

        end : tuple
            Common landing end.

        elbows : iterable[tuple] | None
            Optional elbow for each leader.
        """

        if elbows is None:
            elbows = [None] * len(starts)

        starts = list(starts)
        elbows = list(elbows)

        if len(starts) != len(elbows):
            raise ValueError(
                "starts and elbows must have the same length."
            )

        style = self._resolve_style(style)

        label_style = self._resolve_label_style(
            label_style,
        )

        for start, elbow in zip(
            starts,
            elbows,
        ):

            self.leader_line(
                start=start,
                elbow=elbow,
                end=end,
                text=None,
                style=style,
                label_style=label_style,
                arrow=arrow,
                mutation_scale=mutation_scale,
            )

        if text is None:
            return

        reference_start = starts[0]

        reference_elbow = (
            elbows[0]
            if elbows
            else None
        )

        tx, ty = self._leader_label_position(
            reference_start,
            reference_elbow,
            end,
            text_gap,
        )

        self.labels.centered_text(
            tx,
            ty,
            text,
            style=label_style,
        )


    def reference_dimension(
        self,
        start,
        end,
        value,
        elbow=None,
        style=None,
        label_style=None,
        arrow="closed",
        mutation_scale=15,
        text_gap=0.15,
    ):
        """
        Draw a reference dimension.

        Displays the supplied value inside parentheses,
        following common engineering drafting practice.
        """

        self.leader_line(
            start=start,
            elbow=elbow,
            end=end,
            text=f"({value})",
            style=style,
            label_style=label_style,
            arrow=arrow,
            mutation_scale=mutation_scale,
            text_gap=text_gap,
        )


    def coordinate_dimension(
        self,
        point,
        end,
        axis="xy",
        elbow=None,
        style=None,
        label_style=None,
        arrow="closed",
        mutation_scale=15,
        precision=2,
        text_gap=0.15,
    ):
        """
        Draw a coordinate dimension.
        """

        axis = axis.lower()

        x = round(
            point[0],
            precision,
        )

        y = round(
            point[1],
            precision,
        )

        if axis == "x":

            text = f"X={x}"

        elif axis == "y":

            text = f"Y={y}"

        else:

            text = (
                f"X={x}\n"
                f"Y={y}"
            )

        self.leader_line(
            start=point,
            elbow=elbow,
            end=end,
            text=text,
            style=style,
            label_style=label_style,
            arrow=arrow,
            mutation_scale=mutation_scale,
            text_gap=text_gap,
        )


    def elevation_marker(
        self,
        point,
        elevation,
        end,
        elbow=None,
        style=None,
        label_style=None,
        marker_radius=0.08,
        arrow="closed",
        mutation_scale=15,
        text_gap=0.15,
    ):
        """
        Draw an elevation marker.
        """

        style = self._resolve_style(style)

        self.primitives.circle(
            point[0],
            point[1],
            marker_radius,
            style=style,
        )

        self.leader_line(
            start=point,
            elbow=elbow,
            end=end,
            text=f"EL {elevation}",
            style=style,
            label_style=label_style,
            arrow=arrow,
            mutation_scale=mutation_scale,
            text_gap=text_gap,
        )


    def datum_marker(
        self,
        point,
        datum,
        end,
        elbow=None,
        style=None,
        label_style=None,
        marker_radius=0.12,
        arrow="closed",
        mutation_scale=15,
        text_gap=0.15,
    ):
        """
        Draw a datum feature marker.
        """

        style = self._resolve_style(style)

        self.primitives.circle(
            point[0],
            point[1],
            marker_radius,
            style=style,
        )

        self.labels.centered_text(
            point[0],
            point[1],
            str(datum),
            style=label_style,
        )

        self.leader_line(
            start=point,
            elbow=elbow,
            end=end,
            text=None,
            style=style,
            label_style=label_style,
            arrow=arrow,
            mutation_scale=mutation_scale,
            text_gap=text_gap,
        )


    def extension_line(
        self,
        start,
        end,
        style=None,
    ):
        style = self._dimension_style(style)

        self.primitives.line(
            start[0],
            start[1],
            end[0],
            end[1],
            style=style,
        )

    def witness_line(
        self,
        start,
        end,
        style=None,
    ):
        style = self._dimension_style(style)

        self.primitives.line(
            start[0],
            start[1],
            end[0],
            end[1],
            style=style,
        )


    def tick_mark(
        self,
        point,
        angle=45,
        length=0.20,
        style=None,
    ):
        style = self._dimension_style(style)

        radians = math.radians(angle)

        dx = math.cos(radians) * length / 2
        dy = math.sin(radians) * length / 2

        self.primitives.line(
            point[0] - dx,
            point[1] - dy,
            point[0] + dx,
            point[1] + dy,
            style=style,
        )


    def terminator(
        self,
        point,
        direction,
        kind="arrow",
        size=15,
        style=None,
    ):
        style = self._dimension_style(style)

        end = (
            point[0] + direction[0] * 0.30,
            point[1] + direction[1] * 0.30,
        )

        if kind == "arrow":

            self.arrows.line_arrow(
                point,
                end,
                style=style,
                mutation_scale=size,
            )

        elif kind == "open":

            self.arrows.open_arrow(
                point,
                end,
                style=style,
                mutation_scale=size,
            )

        elif kind == "tick":

            self.tick_mark(
                point,
                style=style,
            )

        elif kind == "dot":

            self.primitives.circle(
                point[0],
                point[1],
                0.04,
                style=style,
            )


    def center_mark(
        self,
        center,
        size=0.25,
        style=None,
    ):
        style = self._dimension_style(style)

        x, y = center

        self.primitives.line(
            x - size,
            y,
            x + size,
            y,
            style=style,
        )

        self.primitives.line(
            x,
            y - size,
            x,
            y + size,
            style=style,
        )


    def center_line(
        self,
        start,
        end,
        style=None,
    ):
        style = self._dimension_style(style)

        dashed = self._copy_style(
            style,
            line_width=style.line_width,
        )

        self.primitives.dashed_line(
            start[0],
            start[1],
            end[0],
            end[1],
            style=dashed,
        )


    def hidden_dimension_line(
        self,
        start,
        end,
        style=None,
    ):
        style = self._dimension_style(style)

        hidden = self._copy_style(
            style,
            alpha=0.6,
        )

        self.primitives.dashed_line(
            start[0],
            start[1],
            end[0],
            end[1],
            style=hidden,
        )


    def construction_line(
        self,
        start,
        end,
        style=None,
    ):
        style = self._dimension_style(style)

        construction = self._copy_style(
            style,
            alpha=0.35,
            line_width=1.0,
        )

        self.primitives.dashed_line(
            start[0],
            start[1],
            end[0],
            end[1],
            style=construction,
        )


    def auto_text_placement(
        self,
        start,
        end,
        offset=0.15,
    ):
        return self._label_position(
            start,
            end,
            offset,
        )


    def format_units(
        self,
        value,
        unit="",
    ):
        value = self.format_precision(
            value,
        )

        if unit:
            return f"{value} {unit}"

        return str(value)


    def format_precision(
        self,
        value,
        precision=2,
    ):
        return round(
            value,
            precision,
        )


    def distance(
        self,
        start,
        end,
    ):
        return self._distance(
            start,
            end,
        )

    
    def midpoint(
        self,
        start,
        end,
    ):
        return self._midpoint(
            start,
            end,
        )
    

    def offset_point(
        self,
        point,
        direction,
        distance,
    ):
        return self._offset_point(
            point,
            direction,
            distance,
        )


    def offset_line(
        self,
        start,
        end,
        offset,
    ):
        return self._offset_line(
            start,
            end,
            offset,
        )


    def arrow_direction(
        self,
        start,
        end,
    ):
        return self._arrow_direction(
            start,
            end,
        )


__all__ = [
    "DrawingDimensions",
]