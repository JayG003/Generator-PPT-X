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