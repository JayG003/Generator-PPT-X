import io
import os

import matplotlib

matplotlib.use("Agg", force=False)

import matplotlib.pyplot as plt

from config import (
    DIAGRAM_HEIGHT,
    DIAGRAM_WIDTH,
    EXPORT_FORMAT,
    FIGURE_BBOX,
    FIGURE_PAD_INCHES,
    IMAGE_DPI,
    TRANSPARENT_BACKGROUND,
)


class DrawingCanvas:
    """
    Wrapper around a matplotlib figure and axis.

    Responsible only for:
    - Creating the drawing area
    - Configuring the axes
    - Saving the image

    The figure is a heavyweight resource. Every caller must either use the
    canvas as a context manager or call close() in a finally block; an
    unclosed figure stays registered with pyplot and is never collected.
    """

    def __init__(
        self,
        width=DIAGRAM_WIDTH.inches,
        height=DIAGRAM_HEIGHT.inches,
        dpi=IMAGE_DPI,
    ):

        if width <= 0 or height <= 0:
            raise ValueError(
                f"canvas size must be positive, got {width}x{height} inches"
            )

        if dpi <= 0:
            raise ValueError(f"dpi must be positive, got {dpi}")

        self.figure, self.axis = plt.subplots(
            figsize=(width, height),
            dpi=dpi,
        )

        self._closed = False

        self._configure()

    # Configure Canvas
    def _configure(self):

        self.axis.set_aspect("equal")

        self.axis.axis("off")

    # Clear Canvas
    def clear(self):

        self.axis.cla()

        self._configure()

    # Set Drawing Limits
    def set_limits(
        self,
        xmin,
        xmax,
        ymin,
        ymax,
    ):

        self.axis.set_xlim(xmin, xmax)
        self.axis.set_ylim(ymin, ymax)

    # Set Aspect Ratio
    def set_equal_aspect(
        self,
        enabled=True,
    ):

        if enabled:
            self.axis.set_aspect("equal")
        else:
            self.axis.set_aspect("auto")

    # Show Axes
    def show_axes(self):

        self.axis.set_axis_on()

    # Hide Axes
    def hide_axes(self):

        self.axis.set_axis_off()

    # Show Grid
    def show_grid(
        self,
        major=True,
        minor=False,
    ):

        self.axis.grid(
            visible=major,
            which="major",
        )

        if minor:
            self.axis.minorticks_on()

            self.axis.grid(
                visible=True,
                which="minor",
            )

    # Hide Grid
    def hide_grid(self):

        self.axis.grid(False)

        self.axis.minorticks_off()

    # Set Title
    def set_title(
        self,
        title,
    ):

        self.axis.set_title(title)

    # Reset Canvas
    def reset(self):

        self.axis.cla()

        self._configure()

    # Get X Limits
    def get_xlim(self):

        return self.axis.get_xlim()

    # Get Y Limits
    def get_ylim(self):

        return self.axis.get_ylim()

    # Fit Limits To Content
    def autoscale(self, margin=0.05):

        self.axis.relim()
        self.axis.autoscale_view()

        if margin:
            self.axis.margins(margin)

    # Save Canvas
    def save(self, output_path):

        self._require_open()

        directory = os.path.dirname(os.fspath(output_path))

        if directory:
            os.makedirs(directory, exist_ok=True)

        self.figure.savefig(
            output_path,
            dpi=self.figure.dpi,
            bbox_inches=FIGURE_BBOX,
            pad_inches=FIGURE_PAD_INCHES,
            transparent=TRANSPARENT_BACKGROUND,
            format=EXPORT_FORMAT,
        )

        return output_path

    # Save Canvas To Bytes
    def save_to_bytes(self, image_format=EXPORT_FORMAT):
        """
        Encode the figure and return the raw image bytes.

        Used by the caching layer, which is content-addressed and therefore
        needs the encoded image before it knows where it will live on disk.
        """

        self._require_open()

        buffer = io.BytesIO()

        self.figure.savefig(
            buffer,
            dpi=self.figure.dpi,
            bbox_inches=FIGURE_BBOX,
            pad_inches=FIGURE_PAD_INCHES,
            transparent=TRANSPARENT_BACKGROUND,
            format=image_format,
        )

        return buffer.getvalue()

    # Close Canvas
    def close(self):

        if not self._closed:
            plt.close(self.figure)
            self._closed = True

    # Is Closed
    def is_closed(self):

        return self._closed

    # Guard
    def _require_open(self):

        if self._closed:
            raise RuntimeError(
                "canvas has been closed; create a new DrawingCanvas"
            )

    # Context Manager
    def __enter__(self):

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.close()

        return False

    # Get Axis
    def get_axis(self):

        return self.axis

    # Get Figure
    def get_figure(self):

        return self.figure


__all__ = [
    "DrawingCanvas",
]