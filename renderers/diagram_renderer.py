"""
renderers/diagram_renderer.py

Central renderer for all supported diagram types.
"""

from pathlib import Path
import tempfile
import uuid

from drawing.canvas import DrawingCanvas
from drawing.primitives import DrawingPrimitives
from drawing.shapes import DrawingShapes

from diagrams import (
    geometry,
    flowchart,
    tree,
    venn,
)


class DiagramRenderer:
    """
    Universal renderer for supported diagrams.
    """

    DIAGRAM_RENDERERS = {
        "geometry": geometry,
        "flowchart": flowchart,
        "tree": tree,
        "venn": venn,
    }

    def __init__(self):
        """
        Initialize the rendering environment.
        """

        self.canvas = DrawingCanvas()

        self.primitives = DrawingPrimitives(
            self.canvas
        )

        self.shapes = DrawingShapes(
            self.canvas
        )

        # ==========================================
        # Drawing Components
        # ==========================================

        from drawing.arrows import DrawingArrows
        from drawing.labels import DrawingLabels
        from drawing.layout import DrawingLayout

        self.arrows = DrawingArrows(
            self.canvas
        )

        self.labels = DrawingLabels(
            self.canvas
        )

        self.layout = DrawingLayout()

        # ==========================================
        # Connector Registry
        # ==========================================

        self.connector_types = {

            "line":
                self.arrows.line_arrow,

            "arrow":
                self.arrows.line_arrow,

            "double_arrow":
                self.arrows.double_arrow,

            "bidirectional":
                self.arrows.bidirectional_arrow,

            "open_arrow":
                self.arrows.open_arrow,

            "filled_arrow":
                self.arrows.filled_arrow,

            "thin_arrow":
                self.arrows.thin_arrow,

            "curved":
                self.arrows.curved_arrow,

            "arc":
                self.arrows.arc_arrow,

            "loop":
                self.arrows.loop_arrow,

            "self_loop":
                self.arrows.self_loop,

            "orthogonal":
                self.arrows.orthogonal_connector,

            "elbow":
                self.arrows.elbow_connector,

            "step":
                self.arrows.step_connector,

            "tree":
                self.arrows.tree_connector,

            "decision":
                self.arrows.decision_connector,

            "dashed":
                self.arrows.dashed_arrow,

            "dotted":
                self.arrows.dotted_arrow,

            "wavy":
                self.arrows.wavy_arrow,

            "zigzag":
                self.arrows.zigzag_arrow,

            "lightning":
                self.arrows.lightning_arrow,
        }

        # ==========================================
        # Arrow Style Registry
        # ==========================================

        self.arrow_styles = {

            "default": "arrow",

            "straight": "line",

            "double": "double_arrow",

            "bidirectional": "bidirectional",

            "open": "open_arrow",

            "filled": "filled_arrow",

            "thin": "thin_arrow",

            "curved": "curved",

            "arc": "arc",

            "loop": "loop",

            "orthogonal": "orthogonal",

            "elbow": "elbow",

            "step": "step",

            "tree": "tree",

            "decision": "decision",

            "dashed": "dashed",

            "dotted": "dotted",

            "wavy": "wavy",

            "zigzag": "zigzag",

            "lightning": "lightning",
        }

        # ==========================================
        # Label Registry
        # ==========================================

        self.label_types = {

            "text":
                self.labels.text,

            "center":
                self.labels.centered_text,

            "left":
                self.labels.left_text,

            "right":
                self.labels.right_text,

            "top":
                self.labels.top_text,

            "bottom":
                self.labels.bottom_text,

            "multiline":
                self.labels.multiline_text,

            "boxed":
                self.labels.boxed_text,

            "rounded":
                self.labels.rounded_box_label,

            "highlight":
                self.labels.highlight_label,

            "badge":
                self.labels.badge,

            "tag":
                self.labels.tag,

            "callout":
                self.labels.callout,

            "caption":
                self.labels.caption,

            "tooltip":
                self.labels.tooltip,

            "speech":
                self.labels.speech_annotation,

            "leader":
                self.labels.leader_label,

            "edge":
                self.labels.edge_label,

            "midpoint":
                self.labels.midpoint_label,

            "start":
                self.labels.start_label,

            "end":
                self.labels.end_label,
        }

        self.figure = self.canvas.get_figure()

        self.axis = self.canvas.get_axis()

        # ==========================================
        # Shape Registry
        # ==========================================

        self.node_shapes = {

            # Basic Shapes

            "rectangle":
                self.shapes.rectangle,

            "rounded_rectangle":
                self.shapes.rounded_rectangle,

            "square":
                self.shapes.square,

            "circle":
                self.shapes.circle,

            "ellipse":
                self.shapes.ellipse,

            "triangle":
                self.shapes.triangle,

            "right_triangle":
                self.shapes.right_triangle,

            "diamond":
                self.shapes.diamond,

            "parallelogram":
                self.shapes.parallelogram,

            "trapezoid":
                self.shapes.trapezoid,

            "pentagon":
                self.shapes.pentagon,

            "hexagon":
                self.shapes.hexagon,

            "octagon":
                self.shapes.octagon,

            # Documents

            "folder":
                self.shapes.folder,

            "file":
                self.shapes.file,

            "note":
                self.shapes.note,

            # Diagram Shapes

            "cloud":
                self.shapes.cloud,

            "speech_bubble":
                self.shapes.speech_bubble,

            "thought_bubble":
                self.shapes.thought_bubble,

            "banner":
                self.shapes.banner,

            "flag":
                self.shapes.flag,

            # Symbols

            "star":
                self.shapes.star,

            "heart":
                self.shapes.heart,

            "gear":
                self.shapes.gear,

            "cross":
                self.shapes.cross,

            "plus":
                self.shapes.plus,

            "minus":
                self.shapes.minus,

            "check":
                self.shapes.check,

            "x_mark":
                self.shapes.x_mark,

            "target":
                self.shapes.target,
        }

    # ==================================================
    # Validation
    # ==================================================

    def validate(
        self,
        diagram_data,
    ):
        """
        Validate a diagram definition.

        Parameters
        ----------
        diagram_data : dict

        Returns
        -------
        str
            Validated diagram type.
        """

        if not isinstance(
            diagram_data,
            dict,
        ):
            raise TypeError(
                "Diagram data must be a dictionary."
            )

        diagram_type = diagram_data.get(
            "diagram_type"
        )

        if diagram_type is None:
            raise ValueError(
                "Missing required field 'diagram_type'."
            )

        if not isinstance(
            diagram_type,
            str,
        ):
            raise TypeError(
                "'diagram_type' must be a string."
            )

        diagram_type = (
            diagram_type
            .strip()
            .lower()
        )

        if not diagram_type:
            raise ValueError(
                "'diagram_type' cannot be empty."
            )

        if diagram_type not in self.DIAGRAM_RENDERERS:

            supported = ", ".join(
                sorted(
                    self.DIAGRAM_RENDERERS.keys()
                )
            )

            raise ValueError(
                f"Unsupported diagram type "
                f"'{diagram_type}'. "
                f"Supported types: {supported}"
            )

        return diagram_type

    # ==================================================
    # Core Helpers
    # ==================================================

    def get_renderer(
        self,
        diagram_type,
    ):
        """
        Return the renderer module for a diagram type.
        """

        return self.DIAGRAM_RENDERERS[
            diagram_type
        ]

    def clear(self):
        """
        Clear the drawing canvas.
        """

        self.canvas.clear()

    def reset(self):
        """
        Reset the renderer before drawing a new diagram.
        """

        self.clear()

    def save(
        self,
        output_path,
    ):
        """
        Save the rendered image.
        """

        self.canvas.save(
            output_path
        )

    def close(self):
        """
        Release rendering resources.
        """

        self.canvas.close()

    def create_temp_output(
        self,
        suffix=".png",
    ):
        """
        Create a unique temporary output path.
        """

        filename = (
            f"{uuid.uuid4().hex}"
            f"{suffix}"
        )

        return (
            Path(
                tempfile.gettempdir()
            )
            / filename
        )

    # ==================================================
    # Style Helpers
    # ==================================================

    def resolve_style(
        self,
        style=None,
    ):
        """
        Resolve a drawing style.

        Parameters
        ----------
        style : DrawingStyle | None

        Returns
        -------
        DrawingStyle
        """

        if style is None:
            return None

        return self.shapes._resolve_style(
            style
        )

    def validate_node(
        self,
        node,
    ):
        """
        Validate a node definition.

        Parameters
        ----------
        node : dict

        Returns
        -------
        dict
        """

        if not isinstance(
            node,
            dict,
        ):
            raise TypeError(
                "Node must be a dictionary."
            )

        shape = node.get(
            "shape"
        )

        if shape is None:
            raise ValueError(
                "Node is missing 'shape'."
            )

        if not isinstance(
            shape,
            str,
        ):
            raise TypeError(
                "'shape' must be a string."
            )

        shape = (
            shape
            .strip()
            .lower()
        )

        if shape not in self.node_shapes:

            supported = ", ".join(
                sorted(
                    self.node_shapes.keys()
                )
            )

            raise ValueError(
                f"Unsupported shape '{shape}'. "
                f"Supported shapes: {supported}"
            )

        return node

    def get_node_renderer(
        self,
        shape,
    ):
        """
        Return the renderer associated
        with a node shape.
        """

        if not isinstance(
            shape,
            str,
        ):
            raise TypeError(
                "Shape must be a string."
            )

        shape = (
            shape
            .strip()
            .lower()
        )

        try:
            return self.node_shapes[
                shape
            ]

        except KeyError:

            supported = ", ".join(
                sorted(
                    self.node_shapes.keys()
                )
            )

            raise ValueError(
                f"Unsupported shape '{shape}'. "
                f"Supported shapes: {supported}"
            )

    def has_node_shape(
        self,
        shape,
    ):
        """
        Check whether a shape exists.
        """

        if not isinstance(
            shape,
            str,
        ):
            return False

        return (
            shape
            .strip()
            .lower()
            in self.node_shapes
        )

    # ==================================================
    # Generic Node Rendering
    # ==================================================

    def render_node(
        self,
        node,
    ):
        """
        Render a single diagram node.

        Parameters
        ----------
        node : dict

        Returns
        -------
        object
            Whatever the underlying shape renderer returns.
        """

        if not isinstance(
            node,
            dict,
        ):
            raise TypeError(
                "Node must be a dictionary."
            )

        shape = node.get(
            "shape",
            "rectangle",
        )

        renderer = self.get_node_renderer(
            shape,
        )

        style = self.resolve_style(
            node.get(
                "style",
            )
        )

        kwargs = {
            key: value
            for key, value in node.items()
            if key not in (
                "shape",
                "style",
            )
        }

        kwargs["style"] = style

        return renderer(
            **kwargs
        )

    def render_nodes(
        self,
        nodes,
    ):
        """
        Render multiple nodes.

        Parameters
        ----------
        nodes : list[dict]
        """

        if not isinstance(
            nodes,
            list,
        ):
            raise TypeError(
                "'nodes' must be a list."
            )

        rendered = []

        for node in nodes:
            rendered.append(
                self.render_node(
                    node
                )
            )

        return rendered

    # ==================================================
    # Rendering Dispatcher
    # ==================================================

    def render(
        self,
        diagram_data,
        output_path=None,
    ):
        """
        Render a diagram.

        Parameters
        ----------
        diagram_data : dict
            Diagram definition.

        output_path : str | Path | None
            Output image path.

        Returns
        -------
        pathlib.Path
            Path of the rendered image.
        """

        diagram_type = self.validate(
            diagram_data
        )

        renderer = self.get_renderer(
            diagram_type
        )

        if output_path is None:
            output_path = self.create_temp_output()

        output_path = Path(
            output_path
        )

        self.reset()

        try:

            renderer.render(
                diagram_data=diagram_data,
                canvas=self.canvas,
                primitives=self.primitives,
                shapes=self.shapes,
            )

            self.save(
                output_path
            )

            return output_path

        finally:

            self.close()

    def render_to_temp(
        self,
        diagram_data,
    ):
        """
        Render a diagram to a temporary file.

        Parameters
        ----------
        diagram_data : dict

        Returns
        -------
        pathlib.Path
        """

        return self.render(
            diagram_data=diagram_data,
            output_path=self.create_temp_output(),
        )

    def render_to_file(
        self,
        diagram_data,
        output_path,
    ):
        """
        Render a diagram to a specified file.

        Parameters
        ----------
        diagram_data : dict

        output_path : str | Path

        Returns
        -------
        pathlib.Path
        """

        return self.render(
            diagram_data=diagram_data,
            output_path=output_path,
        )

    # ==================================================
    # Generic Connector Rendering
    # ==================================================

    def render_connector(
        self,
        connector,
    ):
        """
        Render a single connector.
        """

        if not isinstance(
            connector,
            dict,
        ):
            raise TypeError(
                "Connector must be a dictionary."
            )

        connector_type = (
            connector.get(
                "type",
                "arrow",
            )
            .strip()
            .lower()
        )

        renderer = self.connector_types.get(
            connector_type
        )

        if renderer is None:

            supported = ", ".join(
                sorted(
                    self.connector_types.keys()
                )
            )

            raise ValueError(
                f"Unsupported connector "
                f"'{connector_type}'. "
                f"Supported connectors: "
                f"{supported}"
            )

        kwargs = {
            key: value
            for key, value in connector.items()
            if key != "type"
        }

        return renderer(
            **kwargs
        )

    def render_connectors(
        self,
        connectors,
    ):
        """
        Render multiple connectors.
        """

        if connectors is None:
            return []

        if not isinstance(
            connectors,
            list,
        ):
            raise TypeError(
                "'connectors' must be a list."
            )

        rendered = []

        for connector in connectors:

            rendered.append(
                self.render_connector(
                    connector
                )
            )

        return rendered

    # ==================================================
    # Generic Label Rendering
    # ==================================================

    def render_label(
        self,
        label,
    ):
        """
        Render a single label.
        """

        if not isinstance(
            label,
            dict,
        ):
            raise TypeError(
                "Label must be a dictionary."
            )

        label_type = (
            label.get(
                "type",
                "text",
            )
            .strip()
            .lower()
        )

        renderer = self.label_types.get(
            label_type
        )

        if renderer is None:

            supported = ", ".join(
                sorted(
                    self.label_types.keys()
                )
            )

            raise ValueError(
                f"Unsupported label "
                f"'{label_type}'. "
                f"Supported labels: "
                f"{supported}"
            )

        kwargs = {
            key: value
            for key, value in label.items()
            if key != "type"
        }

        return renderer(
            **kwargs
        )

    def render_labels(
        self,
        labels,
    ):
        """
        Render multiple labels.
        """

        if labels is None:
            return []

        if not isinstance(
            labels,
            list,
        ):
            raise TypeError(
                "'labels' must be a list."
            )

        rendered = []

        for label in labels:

            rendered.append(
                self.render_label(
                    label
                )
            )

        return rendered

    # ==================================================
    # Layout Helpers
    # ==================================================

    def compute_bounds(
        self,
        points,
    ):
        """
        Compute the bounding box of points.
        """

        return self.layout.bounding_box(
            points
        )


    def expand_bounds(
        self,
        bounds,
        padding=None,
    ):
        """
        Expand a bounding box.
        """

        return self.layout.expand_bounding_box(
            bounds,
            padding=padding,
        )


    def fit_canvas(
        self,
        bounds,
        padding=None,
    ):
        """
        Fit the canvas around a bounding box.
        """

        xmin, ymin, xmax, ymax = (
            self.expand_bounds(
                bounds,
                padding,
            )
        )

        self.axis.set_xlim(
            xmin,
            xmax,
        )

        self.axis.set_ylim(
            ymin,
            ymax,
        )

        self.axis.set_aspect(
            "equal",
            adjustable="box",
        )


    def center_canvas(
        self,
        points,
    ):
        """
        Center the canvas on a collection of points.
        """

        bounds = self.compute_bounds(
            points
        )

        self.fit_canvas(
            bounds,
        )


    def auto_scale(
        self,
        points,
        padding=None,
    ):
        """
        Automatically compute bounds and fit
        the drawing canvas.
        """

        bounds = self.compute_bounds(
            points
        )

        self.fit_canvas(
            bounds,
            padding,
        )

        return bounds