import math

from drawing.styles import (
    DEFAULT_STYLE,
    DrawingStyle,
)


class DrawingArrows:

    # Constructor
    def __init__(self, canvas):

        self.canvas = canvas
        self.axis = canvas.get_axis()

    # Style Helpers
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

    # Vector Helpers
    def _distance(
        self,
        start,
        end,
    ):

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        return math.hypot(dx, dy)

    def _direction(
        self,
        start,
        end,
    ):

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        length = math.hypot(dx, dy)

        if length == 0:
            return (0.0, 0.0)

        return (
            dx / length,
            dy / length,
        )

    def _angle(
        self,
        start,
        end,
    ):

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        return math.atan2(
            dy,
            dx,
        )

    def _midpoint(
        self,
        start,
        end,
    ):

        return (
            (start[0] + end[0]) / 2,
            (start[1] + end[1]) / 2,
        )

    # Endpoint Helpers
    def _offset_point(
        self,
        point,
        direction,
        distance,
    ):

        return (
            point[0] + direction[0] * distance,
            point[1] + direction[1] * distance,
        )

    def _trim_line(
        self,
        start,
        end,
        start_offset=0,
        end_offset=0,
    ):
        direction = self._direction(
            start,
            end,
        )

        trimmed_start = self._offset_point(
            start,
            direction,
            start_offset,
        )

        trimmed_end = self._offset_point(
            end,
            (
                -direction[0],
                -direction[1],
            ),
            end_offset,
        )

        return (
            trimmed_start,
            trimmed_end,
        )

    def _arrow_endpoints(
        self,
        start,
        end,
        start_padding=0,
        end_padding=0,
    ):
        return self._trim_line(
            start,
            end,
            start_padding,
            end_padding,
        )

    # Utility Helpers
    def _perpendicular(
        self,
        direction,
    ):

        return (
            -direction[1],
            direction[0],
        )

    def _scale_vector(
        self,
        vector,
        scale,
    ):

        return (
            vector[0] * scale,
            vector[1] * scale,
        )

    def _add_vectors(
        self,
        a,
        b,
    ):

        return (
            a[0] + b[0],
            a[1] + b[1],
        )

    def _subtract_vectors(
        self,
        a,
        b,
    ):

        return (
            a[0] - b[0],
            a[1] - b[1],
        )
    
    # Line Arrow
    def line_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        self.axis.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="->",
                mutation_scale=mutation_scale,
                linewidth=style.line_width,
                color=style.line_color,
                alpha=style.alpha,
            )
        )


    # Double Arrow
    def double_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        self.axis.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="<->",
                mutation_scale=mutation_scale,
                linewidth=style.line_width,
                color=style.line_color,
                alpha=style.alpha,
            )
        )


    # Bidirectional Arrow
    def bidirectional_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=20,
    ):

        self.double_arrow(
            start,
            end,
            style=style,
            start_padding=start_padding,
            end_padding=end_padding,
            mutation_scale=mutation_scale,
        )


    # Open Arrow
    def open_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=18,
        head_length=0.25,
        head_angle=25,
    ):

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        # Draw shaft
        self.axis.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
        )

        direction = self._direction(start, end)

        if direction == (0.0, 0.0):
            return

        angle = math.radians(head_angle)

        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        dx, dy = direction

        # Rotate backwards
        left = (
            -(dx * cos_a - dy * sin_a),
            -(dx * sin_a + dy * cos_a),
        )

        right = (
            -(dx * cos_a + dy * sin_a),
            -(-dx * sin_a + dy * cos_a),
        )

        left_tip = (
            end[0] + left[0] * head_length,
            end[1] + left[1] * head_length,
        )

        right_tip = (
            end[0] + right[0] * head_length,
            end[1] + right[1] * head_length,
        )

        self.axis.plot(
            [left_tip[0], end[0]],
            [left_tip[1], end[1]],
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
        )

        self.axis.plot(
            [right_tip[0], end[0]],
            [right_tip[1], end[1]],
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
        )


    # Filled Arrow
    def filled_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=18,
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        self.axis.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=mutation_scale,
                linewidth=style.line_width,
                color=style.line_color,
                alpha=style.alpha,
            )
        )


    # Thin Arrow
    def thin_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=12,
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        self.axis.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="->",
                mutation_scale=mutation_scale,
                linewidth=max(1.0, style.line_width * 0.6),
                color=style.line_color,
                alpha=style.alpha,
            )
        )

    # Curved Arrow
    def curved_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        curvature=0.25,
        mutation_scale=15,
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        self.axis.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="->",
                connectionstyle=f"arc3,rad={curvature}",
                mutation_scale=mutation_scale,
                linewidth=style.line_width,
                color=style.line_color,
                alpha=style.alpha,
            )
        )


    # Arc Arrow
    def arc_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        radius=0.5,
        mutation_scale=15,
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        self.axis.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="->",
                connectionstyle=f"arc3,rad={radius}",
                mutation_scale=mutation_scale,
                linewidth=style.line_width,
                color=style.line_color,
                alpha=style.alpha,
            )
        )


    # Circular Arrow
    def circular_arrow(
        self,
        center,
        radius,
        start_angle=0,
        end_angle=300,
        style=None,
        mutation_scale=15,
    ):

        from matplotlib.patches import Arc

        style = self._resolve_style(style)

        arc = Arc(
            center,
            radius * 2,
            radius * 2,
            theta1=start_angle,
            theta2=end_angle,
            linewidth=style.line_width,
            color=style.line_color,
            alpha=style.alpha,
        )

        self.axis.add_patch(arc)

        angle = math.radians(end_angle)

        tip = (
            center[0] + radius * math.cos(angle),
            center[1] + radius * math.sin(angle),
        )

        tangent = (
            -math.sin(angle),
            math.cos(angle),
        )

        tail = (
            tip[0] - tangent[0] * radius * 0.25,
            tip[1] - tangent[1] * radius * 0.25,
        )

        self.line_arrow(
            tail,
            tip,
            style=style,
            mutation_scale=mutation_scale,
        )


    # Loop Arrow
    def loop_arrow(
        self,
        point,
        radius=0.4,
        style=None,
        mutation_scale=15,
    ):

        self.circular_arrow(
            center=point,
            radius=radius,
            start_angle=45,
            end_angle=330,
            style=style,
            mutation_scale=mutation_scale,
        )


    # Self Loop
    def self_loop(
        self,
        point,
        direction="right",
        radius=0.45,
        style=None,
        mutation_scale=15,
    ):

        offsets = {
            "right": (radius, 0),
            "left": (-radius, 0),
            "top": (0, radius),
            "bottom": (0, -radius),
        }

        dx, dy = offsets.get(direction, (radius, 0))

        center = (
            point[0] + dx,
            point[1] + dy,
        )

        angles = {
            "right": (90, 420),
            "left": (270, 600),
            "top": (180, 510),
            "bottom": (0, 330),
        }

        start_angle, end_angle = angles.get(direction, (90, 420))

        self.circular_arrow(
            center=center,
            radius=radius,
            start_angle=start_angle,
            end_angle=end_angle,
            style=style,
            mutation_scale=mutation_scale,
        )

    # Orthogonal Connector
    def orthogonal_connector(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        mid_x = (start[0] + end[0]) / 2

        points = [
            start,
            (mid_x, start[1]),
            (mid_x, end[1]),
            end,
        ]

        for p1, p2 in zip(points[:-2], points[1:-1]):
            self.axis.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                color=style.line_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )

        self.line_arrow(
            points[-2],
            points[-1],
            style=style,
            mutation_scale=mutation_scale,
        )


    # Elbow Connector
    def elbow_connector(
        self,
        start,
        end,
        style=None,
        horizontal_first=True,
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        if horizontal_first:
            corner = (
                end[0],
                start[1],
            )
        else:
            corner = (
                start[0],
                end[1],
            )

        self.axis.plot(
            [start[0], corner[0]],
            [start[1], corner[1]],
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
        )

        self.line_arrow(
            corner,
            end,
            style=style,
            mutation_scale=mutation_scale,
        )


    # Step Connector
    def step_connector(
        self,
        start,
        end,
        style=None,
        step_ratio=0.35,
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        dx = end[0] - start[0]

        step_x = start[0] + dx * step_ratio

        points = [
            start,
            (step_x, start[1]),
            (step_x, end[1]),
            end,
        ]

        for p1, p2 in zip(points[:-2], points[1:-1]):
            self.axis.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                color=style.line_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )

        self.line_arrow(
            points[-2],
            points[-1],
            style=style,
            mutation_scale=mutation_scale,
        )


    # Tree Connector
    def tree_connector(
        self,
        parent,
        child,
        style=None,
        branch_length=0.35,
        orientation="vertical",
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        style = self._resolve_style(style)

        parent, child = self._arrow_endpoints(
            parent,
            child,
            start_padding,
            end_padding,
        )

        if orientation == "vertical":

            branch_y = parent[1] - branch_length

            points = [
                parent,
                (parent[0], branch_y),
                (child[0], branch_y),
                child,
            ]

        elif orientation == "horizontal":

            branch_x = (
                parent[0] + branch_length
                if child[0] >= parent[0]
                else parent[0] - branch_length
            )

            points = [
                parent,
                (branch_x, parent[1]),
                (branch_x, child[1]),
                child,
            ]

        else:

            raise ValueError(
                "orientation must be 'vertical' or 'horizontal'"
            )

        for p1, p2 in zip(points[:-2], points[1:-1]):
            self.axis.plot(
                [p1[0], p2[0]],
                [p1[1], p2[1]],
                color=style.line_color,
                linewidth=style.line_width,
                alpha=style.alpha,
            )

        self.line_arrow(
            points[-2],
            points[-1],
            style=style,
            mutation_scale=mutation_scale,
        )


    # Decision Connector
    def decision_connector(
        self,
        start,
        end,
        style=None,
        label=None,
        label_offset=(0.0, 0.15),
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        self.orthogonal_connector(
            start,
            end,
            style=style,
            start_padding=start_padding,
            end_padding=end_padding,
            mutation_scale=mutation_scale,
        )

        if label is None:
            return

        style = self._resolve_style(style)

        midpoint = self._midpoint(
            start,
            end,
        )

        self.axis.text(
            midpoint[0] + label_offset[0],
            midpoint[1] + label_offset[1],
            str(label),
            ha="center",
            va="center",
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
        )

    # Dashed Arrow
    def dashed_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
        dash_pattern=(6, 4),
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        arrow = FancyArrowPatch(
            start,
            end,
            arrowstyle="->",
            mutation_scale=mutation_scale,
            linewidth=style.line_width,
            color=style.line_color,
            alpha=style.alpha,
        )

        arrow.set_linestyle((0, dash_pattern))

        self.axis.add_patch(arrow)


    # Dotted Arrow
    def dotted_arrow(
        self,
        start,
        end,
        style=None,
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        arrow = FancyArrowPatch(
            start,
            end,
            arrowstyle="->",
            mutation_scale=mutation_scale,
            linewidth=style.line_width,
            color=style.line_color,
            alpha=style.alpha,
        )

        arrow.set_linestyle(":")

        self.axis.add_patch(arrow)


    # Wavy Arrow
    def wavy_arrow(
        self,
        start,
        end,
        style=None,
        amplitude=0.15,
        waves=6,
        start_padding=0,
        end_padding=0,
        mutation_scale=15,
    ):

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        length = math.hypot(dx, dy)

        if length == 0:
            return

        ux = dx / length
        uy = dy / length

        px = -uy
        py = ux

        points = []

        samples = max(20, waves * 12)

        for i in range(samples + 1):

            t = i / samples

            x = start[0] + dx * t
            y = start[1] + dy * t

            offset = amplitude * math.sin(2 * math.pi * waves * t)

            points.append((
                x + px * offset,
                y + py * offset,
            ))

        xs = [p[0] for p in points[:-1]]
        ys = [p[1] for p in points[:-1]]

        self.axis.plot(
            xs,
            ys,
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
        )

        self.line_arrow(
            points[-2],
            points[-1],
            style=style,
            mutation_scale=mutation_scale,
        )


    # Zigzag Arrow
    def zigzag_arrow(
        self,
        start,
        end,
        style=None,
        amplitude=0.2,
        segments=12,
        start_padding=0,
        end_padding =0,
        mutation_scale=15,
    ):

        style = self._resolve_style(style)

        start, end = self._arrow_endpoints(
            start,
            end,
            start_padding,
            end_padding,
        )

        dx = end[0] - start[0]
        dy = end[1] - start[1]

        length = math.hypot(dx, dy)

        if length == 0:
            return

        ux = dx / length
        uy = dy / length

        px = -uy
        py = ux

        points = []

        for i in range(segments + 1):

            t = i / segments

            x = start[0] + dx * t
            y = start[1] + dy * t

            if i == 0 or i == segments:
                offset = 0
            else:
                offset = amplitude if i % 2 else -amplitude

            points.append((
                x + px * offset,
                y + py * offset,
            ))

        xs = [p[0] for p in points[:-1]]
        ys = [p[1] for p in points[:-1]]

        self.axis.plot(
            xs,
            ys,
            color=style.line_color,
            linewidth=style.line_width,
            alpha=style.alpha,
        )

        self.line_arrow(
            points[-2],
            points[-1],
            style=style,
            mutation_scale=mutation_scale,
        )


    # Lightning Arrow
    def lightning_arrow(
        self,
        start,
        end,
        style=None,
        amplitude=0.3,
        mutation_scale=18,
    ):

        self.zigzag_arrow(
            start,
            end,
            style=style,
            amplitude=amplitude,
            segments=8,
            mutation_scale=mutation_scale,
        )

    # Arrow Label
    def arrow_label(
        self,
        start,
        end,
        text,
        style=None,
        offset=(0.0, 0.15),
        **kwargs,
    ):

        style = self._resolve_style(style)

        x, y = self._midpoint(start, end)

        self.axis.text(
            x + offset[0],
            y + offset[1],
            str(text),
            ha="center",
            va="center",
            fontsize=style.font_size,
            fontweight=style.font_weight,
            color=style.text_color,
            alpha=style.alpha,
            **kwargs,
        )


    # Arrow Head Only
    def arrowhead(
        self,
        start,
        end,
        style=None,
        mutation_scale=15,
    ):

        from matplotlib.patches import FancyArrowPatch

        style = self._resolve_style(style)

        direction = self._direction(start, end)

        length = max(
            style.line_width * 2,
            mutation_scale * 0.015,
        )

        tail = (
            end[0] - direction[0] * length,
            end[1] - direction[1] * length,
        )

        self.axis.add_patch(
            FancyArrowPatch(
                tail,
                end,
                arrowstyle="->",
                mutation_scale=mutation_scale,
                linewidth=style.line_width,
                color=style.line_color,
                alpha=style.alpha,
            )
        )


    # Midpoint
    def arrow_midpoint(
        self,
        start,
        end,
    ):

        return self._midpoint(
            start,
            end,
        )

    # Shape Connection Point
    def connection_point(
        self,
        center,
        width,
        height,
        direction,
        shape="rectangle",
    ):
        x, y = center

        direction = direction.lower()

        shape = shape.lower()

        if shape == "circle":

            r = width / 2

            if direction == "left":
                return (x - r, y)

            if direction == "right":
                return (x + r, y)

            if direction == "top":
                return (x, y + r)

            if direction == "bottom":
                return (x, y - r)
            
        if shape == "ellipse":

            rx = width / 2
            ry = height / 2

            if direction == "left":
                return (x - rx, y)

            if direction == "right":
                return (x + rx, y)

            if direction == "top":
                return (x, y + ry)

            if direction == "bottom":
                return (x, y - ry)

        if shape == "diamond":

            if direction == "left":
                return (x - width / 2, y)

            if direction == "right":
                return (x + width / 2, y)

            if direction == "top":
                return (x, y + height / 2)

            if direction == "bottom":
                return (x, y - height / 2)

        if direction == "left":
            return (
                x - width / 2,
                y,
            )

        if direction == "right":
            return (
                x + width / 2,
                y,
            )

        if direction == "top":
            return (
                x,
                y + height / 2,
            )

        if direction == "bottom":
            return (
                x,
                y - height / 2,
            )

        valid_shapes = {
            "rectangle",
            "circle",
            "ellipse",
            "diamond",
        }

        if shape not in valid_shapes:
            raise ValueError(
                f"Unknown shape: {shape}"
            )

        raise ValueError(
            f"Unknown direction: {direction}"
        )


# Public Exports

__all__ = [
    "DrawingArrows",
]