import matplotlib.pyplot as plt

from config import (
    IMAGE_DPI,
    DIAGRAM_WIDTH,
    DIAGRAM_HEIGHT,
)


class DrawingCanvas:
    """
    Wrapper around a matplotlib figure and axis.

    Responsible only for:
    - Creating the drawing area
    - Configuring the axes
    - Saving the image
    """

    def __init__(
        self,
        width=DIAGRAM_WIDTH.inches,
        height=DIAGRAM_HEIGHT.inches,
        dpi=IMAGE_DPI,
    ):

        self.figure, self.axis = plt.subplots(
            figsize=(width, height),
            dpi=dpi,
        )

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

    # Save Canvas
    def save(self, output_path):

        self.figure.savefig(
            output_path,
            dpi=self.figure.dpi,
            bbox_inches="tight",
            transparent=True,
        )

    # Close Canvas
    def close(self):

        plt.close(self.figure)

    # Get Axis
    def get_axis(self):

        return self.axis

    # Get Figure
    def get_figure(self):

        return self.figure