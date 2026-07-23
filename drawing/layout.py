from math import inf
import math
import random

class DrawingLayout:
    """
    Computes layouts for diagrams.

    Responsibilities
    ----------------
    • Validate layout inputs
    • Compute spacing
    • Compute alignment
    • Compute bounding boxes
    • Provide helper methods for higher-level layouts

    Drawing is handled elsewhere.
    """

    # ---------------------------------------------------------
    # Constructor
    # ---------------------------------------------------------

    def __init__(
        self,
        horizontal_spacing=1.0,
        vertical_spacing=1.0,
        padding=0.25,
    ):

        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing
        self.padding = padding

    # =========================================================
    # Validation Helpers
    # =========================================================

    def _validate_points(
        self,
        points,
    ):

        if not isinstance(points, (list, tuple)):
            raise TypeError("points must be a sequence")

        if len(points) == 0:
            raise ValueError("points cannot be empty")

        for point in points:

            if (
                not isinstance(point, (list, tuple))
                or len(point) != 2
            ):
                raise ValueError(
                    "each point must be (x, y)"
                )

    def _validate_sizes(
        self,
        sizes,
    ):

        if not isinstance(sizes, (list, tuple)):
            raise TypeError("sizes must be a sequence")

        if len(sizes) == 0:
            raise ValueError("sizes cannot be empty")

        for width, height in sizes:

            if width <= 0 or height <= 0:
                raise ValueError(
                    "width and height must be positive"
                )

    def _validate_spacing(
        self,
        spacing,
    ):

        if spacing < 0:
            raise ValueError(
                "spacing cannot be negative"
            )

    # =========================================================
    # Spacing Helpers
    # =========================================================

    def horizontal_gap(
        self,
        spacing=None,
    ):

        return (
            self.horizontal_spacing
            if spacing is None
            else spacing
        )

    def vertical_gap(
        self,
        spacing=None,
    ):

        return (
            self.vertical_spacing
            if spacing is None
            else spacing
        )

    def total_horizontal_spacing(
        self,
        item_count,
        spacing=None,
    ):

        spacing = self.horizontal_gap(spacing)

        return max(
            0,
            item_count - 1,
        ) * spacing

    def total_vertical_spacing(
        self,
        item_count,
        spacing=None,
    ):

        spacing = self.vertical_gap(spacing)

        return max(
            0,
            item_count - 1,
        ) * spacing

    # =========================================================
    # Alignment Helpers
    # =========================================================

    def align_left(
        self,
        x,
    ):

        return x

    def align_right(
        self,
        x,
        width,
    ):

        return x - width

    def align_top(
        self,
        y,
    ):

        return y

    def align_bottom(
        self,
        y,
        height,
    ):

        return y - height

    def align_center_x(
        self,
        x,
        width,
    ):

        return x - width / 2

    def align_center_y(
        self,
        y,
        height,
    ):

        return y - height / 2

    def align_center(
        self,
        x,
        y,
        width,
        height,
    ):

        return (
            self.align_center_x(x, width),
            self.align_center_y(y, height),
        )

    # =========================================================
    # Bounding Box Helpers
    # =========================================================

    def bounding_box(
        self,
        points,
    ):

        self._validate_points(points)

        xmin = inf
        ymin = inf

        xmax = -inf
        ymax = -inf

        for x, y in points:

            xmin = min(xmin, x)
            xmax = max(xmax, x)

            ymin = min(ymin, y)
            ymax = max(ymax, y)

        return (
            xmin,
            ymin,
            xmax,
            ymax,
        )

    def bounding_size(
        self,
        points,
    ):

        xmin, ymin, xmax, ymax = self.bounding_box(points)

        return (
            xmax - xmin,
            ymax - ymin,
        )

    def bounding_center(
        self,
        points,
    ):

        xmin, ymin, xmax, ymax = self.bounding_box(points)

        return (
            (xmin + xmax) / 2,
            (ymin + ymax) / 2,
        )

    def expand_bounding_box(
        self,
        bbox,
        padding=None,
    ):

        if padding is None:
            padding = self.padding

        xmin, ymin, xmax, ymax = bbox

        return (
            xmin - padding,
            ymin - padding,
            xmax + padding,
            ymax + padding,
        )
    
    # =========================================================
    # Linear Layouts
    # =========================================================

    def horizontal_layout(
        self,
        sizes,
        start=(0.0, 0.0),
        spacing=None,
    ):
        """
        Arrange items horizontally.

        Returns
        -------
        [(x, y), ...]
        """

        self._validate_sizes(sizes)

        spacing = self.horizontal_gap(spacing)

        x, y = start
        positions = []

        for width, height in sizes:
            positions.append((x, y))
            x += width + spacing

        return positions

    def vertical_layout(
        self,
        sizes,
        start=(0.0, 0.0),
        spacing=None,
    ):
        """
        Arrange items vertically.
        """

        self._validate_sizes(sizes)

        spacing = self.vertical_gap(spacing)

        x, y = start
        positions = []

        for width, height in sizes:
            positions.append((x, y))
            y -= height + spacing

        return positions

    def row_layout(
        self,
        sizes,
        start=(0.0, 0.0),
        spacing=None,
    ):
        """
        Alias of horizontal layout.
        """

        return self.horizontal_layout(
            sizes=sizes,
            start=start,
            spacing=spacing,
        )

    def column_layout(
        self,
        sizes,
        start=(0.0, 0.0),
        spacing=None,
    ):
        """
        Alias of vertical layout.
        """

        return self.vertical_layout(
            sizes=sizes,
            start=start,
            spacing=spacing,
        )

    # ---------------------------------------------------------
    # Even Spacing
    # ---------------------------------------------------------

    def even_spacing(
        self,
        item_count,
        start,
        end,
    ):
        """
        Returns evenly spaced coordinates.

        Example
        -------
        even_spacing(5,0,100)
        -> [0,25,50,75,100]
        """

        if item_count <= 0:
            return []

        if item_count == 1:
            return [(start + end) / 2]

        step = (end - start) / (item_count - 1)

        return [
            start + i * step
            for i in range(item_count)
        ]

    # ---------------------------------------------------------
    # Packed Spacing
    # ---------------------------------------------------------

    def packed_spacing(
        self,
        sizes,
        spacing=None,
    ):
        """
        Minimal spacing using configured gap.
        """

        self._validate_sizes(sizes)

        spacing = self.horizontal_gap(spacing)

        positions = []
        cursor = 0.0

        for width, _ in sizes:
            positions.append(cursor)
            cursor += width + spacing

        return positions

    # ---------------------------------------------------------
    # Distributed Spacing
    # ---------------------------------------------------------

    def distributed_spacing(
        self,
        sizes,
        total_width,
    ):
        """
        Distributes items across a fixed width.

        Returns x positions.
        """

        self._validate_sizes(sizes)

        widths = [w for w, _ in sizes]
        used = sum(widths)

        count = len(widths)

        if count == 1:
            return [
                (total_width - widths[0]) / 2
            ]

        free_space = max(
            0.0,
            total_width - used,
        )

        gap = free_space / (count - 1)

        positions = []

        cursor = 0.0

        for width in widths:
            positions.append(cursor)
            cursor += width + gap

        return positions
    
    # =========================================================
    # Grid Layouts
    # =========================================================

    def grid_layout(
        self,
        sizes,
        rows,
        cols,
        start=(0.0, 0.0),
        h_spacing=None,
        v_spacing=None,
    ):
        """
        Arrange items in a fixed grid.

        Returns
        -------
        [(x, y), ...]
        """

        self._validate_sizes(sizes)

        if rows <= 0 or cols <= 0:
            raise ValueError("rows and cols must be positive")

        h_spacing = self.horizontal_gap(h_spacing)
        v_spacing = self.vertical_gap(v_spacing)

        max_width = max(width for width, _ in sizes)
        max_height = max(height for _, height in sizes)

        start_x, start_y = start

        positions = []

        for index in range(min(len(sizes), rows * cols)):

            row = index // cols
            col = index % cols

            x = start_x + col * (max_width + h_spacing)
            y = start_y - row * (max_height + v_spacing)

            positions.append((x, y))

        return positions

    # ---------------------------------------------------------
    # Matrix Layout
    # ---------------------------------------------------------

    def matrix_layout(
        self,
        sizes,
        rows,
        cols,
        start=(0.0, 0.0),
        h_spacing=None,
        v_spacing=None,
    ):
        """
        Alias for grid layout.
        """

        return self.grid_layout(
            sizes=sizes,
            rows=rows,
            cols=cols,
            start=start,
            h_spacing=h_spacing,
            v_spacing=v_spacing,
        )

    # ---------------------------------------------------------
    # Fixed Columns
    # ---------------------------------------------------------

    def fixed_columns(
        self,
        sizes,
        columns,
        start=(0.0, 0.0),
        h_spacing=None,
        v_spacing=None,
    ):
        """
        Grid with a fixed number of columns.
        """

        if columns <= 0:
            raise ValueError("columns must be positive")

        rows = (len(sizes) + columns - 1) // columns

        return self.grid_layout(
            sizes=sizes,
            rows=rows,
            cols=columns,
            start=start,
            h_spacing=h_spacing,
            v_spacing=v_spacing,
        )

    # ---------------------------------------------------------
    # Fixed Rows
    # ---------------------------------------------------------

    def fixed_rows(
        self,
        sizes,
        rows,
        start=(0.0, 0.0),
        h_spacing=None,
        v_spacing=None,
    ):
        """
        Grid with a fixed number of rows.
        """

        if rows <= 0:
            raise ValueError("rows must be positive")

        cols = (len(sizes) + rows - 1) // rows

        return self.grid_layout(
            sizes=sizes,
            rows=rows,
            cols=cols,
            start=start,
            h_spacing=h_spacing,
            v_spacing=v_spacing,
        )

    # ---------------------------------------------------------
    # Auto Grid
    # ---------------------------------------------------------

    def auto_grid(
        self,
        sizes,
        start=(0.0, 0.0),
        h_spacing=None,
        v_spacing=None,
    ):
        """
        Automatically chooses a nearly square grid.
        """

        count = len(sizes)

        if count == 0:
            return []

        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)

        return self.grid_layout(
            sizes=sizes,
            rows=rows,
            cols=cols,
            start=start,
            h_spacing=h_spacing,
            v_spacing=v_spacing,
        )

    # ---------------------------------------------------------
    # Cell Position
    # ---------------------------------------------------------

    def cell_position(
        self,
        row,
        col,
        cell_width,
        cell_height,
        start=(0.0, 0.0),
        h_spacing=None,
        v_spacing=None,
    ):
        """
        Returns the top-left coordinate of a grid cell.
        """

        if row < 0 or col < 0:
            raise ValueError("row and col must be >= 0")

        h_spacing = self.horizontal_gap(h_spacing)
        v_spacing = self.vertical_gap(v_spacing)

        start_x, start_y = start

        x = start_x + col * (cell_width + h_spacing)
        y = start_y - row * (cell_height + v_spacing)

        return (x, y)
    
    # =========================================================
    # Circular Layouts
    # =========================================================

    def circle_layout(
        self,
        item_count,
        radius,
        center=(0.0, 0.0),
        start_angle=0.0,
    ):
        """
        Places items evenly around a circle.

        Returns
        -------
        [(x, y), ...]
        """

        if item_count <= 0:
            return []

        cx, cy = center

        step = (2 * math.pi) / item_count

        positions = []

        for i in range(item_count):

            angle = start_angle + i * step

            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            positions.append((x, y))

        return positions

    # ---------------------------------------------------------
    # Radial Layout
    # ---------------------------------------------------------

    def radial_layout(
        self,
        item_count,
        radius,
        center=(0.0, 0.0),
        start_angle=0.0,
    ):
        """
        Alias for circle layout.

        Primarily used for mind maps.
        """

        return self.circle_layout(
            item_count=item_count,
            radius=radius,
            center=center,
            start_angle=start_angle,
        )

    # ---------------------------------------------------------
    # Ring Layout
    # ---------------------------------------------------------

    def ring_layout(
        self,
        item_count,
        inner_radius,
        outer_radius,
        center=(0.0, 0.0),
        start_angle=0.0,
    ):
        """
        Places items on the middle of a ring.

        Useful for concentric diagrams.
        """

        radius = (inner_radius + outer_radius) / 2

        return self.circle_layout(
            item_count=item_count,
            radius=radius,
            center=center,
            start_angle=start_angle,
        )

    # ---------------------------------------------------------
    # Spiral Layout
    # ---------------------------------------------------------

    def spiral_layout(
        self,
        item_count,
        start_radius=0.0,
        radius_step=20.0,
        angle_step=math.pi / 4,
        center=(0.0, 0.0),
    ):
        """
        Places items along an Archimedean spiral.
        """

        if item_count <= 0:
            return []

        cx, cy = center

        positions = []

        radius = start_radius
        angle = 0.0

        for _ in range(item_count):

            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            positions.append((x, y))

            radius += radius_step
            angle += angle_step

        return positions

    # ---------------------------------------------------------
    # Arc Layout
    # ---------------------------------------------------------

    def arc_layout(
        self,
        item_count,
        radius,
        start_angle,
        end_angle,
        center=(0.0, 0.0),
    ):
        """
        Places items along an arc.

        Angles are in radians.
        """

        if item_count <= 0:
            return []

        cx, cy = center

        if item_count == 1:

            angles = [
                (start_angle + end_angle) / 2
            ]

        else:

            step = (
                end_angle - start_angle
            ) / (item_count - 1)

            angles = [
                start_angle + i * step
                for i in range(item_count)
            ]

        positions = []

        for angle in angles:

            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)

            positions.append((x, y))

        return positions

    # =========================================================
    # Tree Layouts
    # =========================================================

    def vertical_tree(
        self,
        levels,
        root=(0.0, 0.0),
        level_spacing=100.0,
        sibling_spacing=80.0,
    ):
        """
        Layout a tree vertically.

        Parameters
        ----------
        levels : list[int]
            Number of nodes at each level.

        Example
        -------
        [1,2,4,3]

        Returns
        -------
        [[(x,y),...], ...]
        """

        if not levels:
            return []

        rx, ry = root
        layout = []

        for level, count in enumerate(levels):

            width = (count - 1) * sibling_spacing
            start_x = rx - width / 2

            y = ry - level * level_spacing

            nodes = []

            for i in range(count):

                x = start_x + i * sibling_spacing
                nodes.append((x, y))

            layout.append(nodes)

        return layout

    # ---------------------------------------------------------
    # Horizontal Tree
    # ---------------------------------------------------------

    def horizontal_tree(
        self,
        levels,
        root=(0.0, 0.0),
        level_spacing=120.0,
        sibling_spacing=80.0,
    ):
        """
        Layout a tree horizontally.
        """

        if not levels:
            return []

        rx, ry = root
        layout = []

        for level, count in enumerate(levels):

            height = (count - 1) * sibling_spacing
            start_y = ry + height / 2

            x = rx + level * level_spacing

            nodes = []

            for i in range(count):

                y = start_y - i * sibling_spacing
                nodes.append((x, y))

            layout.append(nodes)

        return layout

    # ---------------------------------------------------------
    # Balanced Tree
    # ---------------------------------------------------------

    def balanced_tree(
        self,
        depth,
        root=(0.0, 0.0),
        level_spacing=120.0,
        sibling_spacing=80.0,
    ):
        r"""
        Generates a perfect balanced binary tree.

        Example
        -------
        depth=3

               O
             /   \
            O     O
           / \   / \
        """

        if depth <= 0:
            return []

        levels = [
            2 ** i
            for i in range(depth)
        ]

        return self.vertical_tree(
            levels,
            root=root,
            level_spacing=level_spacing,
            sibling_spacing=sibling_spacing,
        )

    # ---------------------------------------------------------
    # Binary Tree Helper
    # ---------------------------------------------------------

    def binary_tree_positions(
        self,
        depth,
        root=(0.0, 0.0),
        horizontal_spacing=160.0,
        vertical_spacing=120.0,
    ):
        """
        Computes binary tree node positions.

        Returns
        -------
        dict

        node_index -> (x,y)
        """

        if depth <= 0:
            return {}

        rx, ry = root

        positions = {}

        for level in range(depth):

            nodes = 2 ** level

            offset = (
                horizontal_spacing
                * (2 ** (depth - level - 1))
            )

            start_x = rx - (
                offset * (nodes - 1) / 2
            )

            y = ry - level * vertical_spacing

            for i in range(nodes):

                node = (2 ** level - 1) + i

                x = start_x + i * offset

                positions[node] = (x, y)

        return positions

    # ---------------------------------------------------------
    # Mind Map Layout
    # ---------------------------------------------------------

    def mind_map_layout(
        self,
        branches,
        radius=180.0,
        center=(0.0, 0.0),
        branch_spacing=80.0,
    ):
        """
        Radial layout for mind maps.

        Parameters
        ----------
        branches : list[int]

        Example
        -------
        [3,4,2,5]

        Each number represents
        subtopics for one branch.

        Returns
        -------
        {
            "center":(...),
            "branches":[
                [(...),(...)]
            ]
        }
        """

        if not branches:
            return {
                "center": center,
                "branches": [],
            }

        cx, cy = center

        total = len(branches)

        angle_step = (
            2 * math.pi
        ) / total

        output = []

        for branch_index, children in enumerate(branches):

            angle = branch_index * angle_step

            root_x = cx + radius * math.cos(angle)
            root_y = cy + radius * math.sin(angle)

            branch_nodes = [
                (root_x, root_y)
            ]

            for child in range(children):

                child_radius = (
                    radius
                    + (child + 1)
                    * branch_spacing
                )

                x = (
                    cx
                    + child_radius
                    * math.cos(angle)
                )

                y = (
                    cy
                    + child_radius
                    * math.sin(angle)
                )

                branch_nodes.append((x, y))

            output.append(branch_nodes)

        return {
            "center": center,
            "branches": output,
        }
    
    # =========================================================
    # Graph Layouts
    # =========================================================

    def random_layout(
        self,
        item_count,
        width,
        height,
        origin=(0.0, 0.0),
        seed=None,
    ):
        """
        Places nodes randomly inside a rectangle.

        Returns
        -------
        [(x, y), ...]
        """

        if seed is not None:
            random.seed(seed)

        ox, oy = origin

        positions = []

        for _ in range(item_count):

            x = ox + random.random() * width
            y = oy + random.random() * height

            positions.append((x, y))

        return positions

    # ---------------------------------------------------------
    # Force Directed Layout
    # ---------------------------------------------------------

    def force_directed_layout(
        self,
        positions,
        edges,
        iterations=50,
        attraction=0.01,
        repulsion=5000.0,
        max_step=10.0,
    ):
        """
        Basic Fruchterman-style force layout.

        Parameters
        ----------
        positions : list[(x,y)]

        edges : list[(u,v)]

        Returns
        -------
        Updated node positions.
        """

        positions = [
            [float(x), float(y)]
            for x, y in positions
        ]

        count = len(positions)

        for _ in range(iterations):

            forces = [
                [0.0, 0.0]
                for _ in range(count)
            ]

            # -------------------------
            # Repulsion
            # -------------------------

            for i in range(count):

                xi, yi = positions[i]

                for j in range(i + 1, count):

                    xj, yj = positions[j]

                    dx = xi - xj
                    dy = yi - yj

                    distance = math.sqrt(
                        dx * dx + dy * dy
                    ) + 0.01

                    force = repulsion / (
                        distance * distance
                    )

                    fx = force * dx / distance
                    fy = force * dy / distance

                    forces[i][0] += fx
                    forces[i][1] += fy

                    forces[j][0] -= fx
                    forces[j][1] -= fy

            # -------------------------
            # Attraction
            # -------------------------

            for u, v in edges:

                dx = (
                    positions[v][0]
                    - positions[u][0]
                )

                dy = (
                    positions[v][1]
                    - positions[u][1]
                )

                fx = dx * attraction
                fy = dy * attraction

                forces[u][0] += fx
                forces[u][1] += fy

                forces[v][0] -= fx
                forces[v][1] -= fy

            # -------------------------
            # Apply
            # -------------------------

            for i in range(count):

                dx = max(
                    -max_step,
                    min(max_step, forces[i][0])
                )

                dy = max(
                    -max_step,
                    min(max_step, forces[i][1])
                )

                positions[i][0] += dx
                positions[i][1] += dy

        return [
            tuple(node)
            for node in positions
        ]

    # ---------------------------------------------------------
    # Layered Layout
    # ---------------------------------------------------------

    def layered_layout(
        self,
        layers,
        origin=(0.0, 0.0),
        layer_spacing=180.0,
        node_spacing=80.0,
    ):
        """
        Layout nodes layer by layer.

        Example
        -------
        [2,3,4]
        """

        ox, oy = origin

        positions = []

        index = 0

        for layer, count in enumerate(layers):

            width = (
                count - 1
            ) * node_spacing

            start_x = ox - width / 2

            y = oy - layer * layer_spacing

            for i in range(count):

                x = (
                    start_x
                    + i * node_spacing
                )

                positions.append(
                    (index, (x, y))
                )

                index += 1

        return dict(positions)

    # ---------------------------------------------------------
    # Hierarchical Layout
    # ---------------------------------------------------------

    def hierarchical_layout(
        self,
        levels,
        origin=(0.0, 0.0),
        level_spacing=150.0,
        node_spacing=90.0,
    ):
        """
        Wrapper around layered layout.

        Used for organization charts
        and dependency graphs.
        """

        return self.layered_layout(
            layers=levels,
            origin=origin,
            layer_spacing=level_spacing,
            node_spacing=node_spacing,
        )

    # ---------------------------------------------------------
    # Network Layout
    # ---------------------------------------------------------

    def network_layout(
        self,
        node_count,
        edges,
        width=800.0,
        height=600.0,
        iterations=80,
        attraction=0.01,
        repulsion=5000.0,
        max_step=10.0,
        seed=None,
    ):
        """
        Convenience helper.

        1. Randomize nodes.
        2. Run force layout.
        """

        positions = self.random_layout(
            item_count=node_count,
            width=width,
            height=height,
            seed=seed,
        )

        return self.force_directed_layout(
            positions=positions,
            edges=edges,
            iterations=iterations,
            attraction=attraction,
            repulsion=repulsion,
            max_step=max_step,
        )
    
    # =========================================================
    # Utility Helpers
    # =========================================================

    # ---------------------------------------------------------
    # Auto Spacing
    # ---------------------------------------------------------

    def auto_spacing(
        self,
        total_size,
        item_sizes,
        minimum_spacing=0.0,
    ):
        """
        Computes spacing required to evenly distribute items
        inside a fixed width or height.

        Returns
        -------
        float
        """

    # ---------------------------------------------------------
    # Collision Detection
    # ---------------------------------------------------------

    def rectangles_overlap(
        self,
        rect1,
        rect2,
    ):
        """
        Checks whether two rectangles overlap.

        Rectangle format
        ----------------
        (x, y, width, height)

        Returns
        -------
        bool
        """

    # ---------------------------------------------------------
    # Center Existing Layout
    # ---------------------------------------------------------

    def center_positions(
        self,
        positions,
        center=(0.0, 0.0),
    ):
        """
        Moves an existing layout so that its bounding center
        becomes the specified center.

        Returns
        -------
        [(x, y), ...]
        """

    # ---------------------------------------------------------
    # Scale To Fit
    # ---------------------------------------------------------

    def scale_to_fit(
        self,
        points,
        width,
        height,
        keep_aspect=True,
    ):
        """
        Scales points so they fit inside the specified
        width and height.

        Returns
        -------
        [(x, y), ...]
        """

    # ---------------------------------------------------------
    # Margin Helpers
    # ---------------------------------------------------------

    def apply_margin(
        self,
        bbox,
        left=0.0,
        right=0.0,
        top=0.0,
        bottom=0.0,
    ):
        """
        Applies margins to a bounding box.

        Bounding box format
        -------------------
        (xmin, ymin, xmax, ymax)

        Returns
        -------
        (xmin, ymin, xmax, ymax)
        """

    # ---------------------------------------------------------
    # Improve Existing Method (Instead of New Padding Helper)
    # ---------------------------------------------------------

    # def expand_bounding_box(
    #     self,
    #     bbox,
    #     padding=None,
    #     left=None,
    #     right=None,
    #     top=None,
    #     bottom=None,
    # ):
        """
        Expands a bounding box.

        If left/right/top/bottom are None,
        the uniform padding value is used.

        Returns
        -------
        (xmin, ymin, xmax, ymax)
        """

__all__ = [
    "DrawingLayout",
]