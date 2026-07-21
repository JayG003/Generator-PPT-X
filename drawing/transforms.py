from numbers import Real
import math
from copy import deepcopy

class DrawingTransforms:

    # Constructor
    def __init__(
        self,
        canvas=None,
    ):

        self.canvas = canvas

    # Validate Point
    def _validate_point(
        self,
        point,
        name="point",
    ):
        if not isinstance(
            point,
            (tuple, list),
        ):
            raise TypeError(
                f"{name} must be a tuple or list."
            )

        if len(point) != 2:
            raise ValueError(
                f"{name} must contain exactly two values."
            )

        x, y = point

        if not isinstance(
            x,
            Real,
        ):
            raise TypeError(
                f"{name}[0] must be numeric."
            )

        if not isinstance(
            y,
            Real,
        ):
            raise TypeError(
                f"{name}[1] must be numeric."
            )

    # Validate Points
    def _validate_points(
        self,
        points,
        name="points",
    ):

        if not isinstance(
            points,
            (list, tuple),
        ):
            raise TypeError(
                f"{name} must be a list or tuple."
            )

        if len(points) == 0:
            raise ValueError(
                f"{name} cannot be empty."
            )

        for index, point in enumerate(points):

            self._validate_point(
                point,
                name=f"{name}[{index}]",
            )

    # Validate Center
    def _validate_center(
        self,
        center,
    ):
        self._validate_point(
            center,
            name="center",
        )

    # Distance
    def _distance(
        self,
        point1,
        point2,
    ):

        self._validate_point(
            point1,
            "point1",
        )

        self._validate_point(
            point2,
            "point2",
        )

        x1, y1 = point1
        x2, y2 = point2

        return math.hypot(
            x2 - x1,
            y2 - y1,
        )

    # Midpoint
    def _midpoint(
        self,
        point1,
        point2,
    ):

        self._validate_point(
            point1,
            "point1",
        )

        self._validate_point(
            point2,
            "point2",
        )

        x1, y1 = point1
        x2, y2 = point2

        return (
            (x1 + x2) / 2,
            (y1 + y2) / 2,
        )

    # Direction
    def _direction(
        self,
        point1,
        point2,
    ):

        self._validate_point(
            point1,
            "point1",
        )

        self._validate_point(
            point2,
            "point2",
        )

        x1, y1 = point1
        x2, y2 = point2

        return (
            x2 - x1,
            y2 - y1,
        )

    # Normalize
    def _normalize(
        self,
        vector,
    ):

        self._validate_point(
            vector,
            "vector",
        )

        x, y = vector

        length = math.hypot(
            x,
            y,
        )

        if length == 0:
            raise ValueError(
                "Cannot normalize a zero-length vector."
            )

        return (
            x / length,
            y / length,
        )

    # Angle
    def _angle(
        self,
        point1,
        point2,
        degrees=True,
    ):

        self._validate_point(
            point1,
            "point1",
        )

        self._validate_point(
            point2,
            "point2",
        )

        x1, y1 = point1
        x2, y2 = point2

        angle = math.atan2(
            y2 - y1,
            x2 - x1,
        )

        if degrees:
            return math.degrees(
                angle,
            )

        return angle

    # Copy Points
    def _copy_points(
        self,
        points,
    ):

        self._validate_points(
            points,
        )

        return deepcopy(
            points,
        )

        # Translate Point
    def translate_point(
        self,
        point,
        dx=0,
        dy=0,
    ):

        self._validate_point(
            point,
        )

        if not isinstance(
            dx,
            Real,
        ):
            raise TypeError(
                "dx must be numeric."
            )

        if not isinstance(
            dy,
            Real,
        ):
            raise TypeError(
                "dy must be numeric."
            )

        return (
            point[0] + dx,
            point[1] + dy,
        )

    # Translate Points
    def translate_points(
        self,
        points,
        dx=0,
        dy=0,
    ):

        self._validate_points(
            points,
        )

        return [
            self.translate_point(
                point,
                dx=dx,
                dy=dy,
            )
            for point in points
        ]

    # Translate X
    def translate_x(
        self,
        point,
        distance,
    ):

        return self.translate_point(
            point,
            dx=distance,
            dy=0,
        )

    # Translate Y
    def translate_y(
        self,
        point,
        distance,
    ):

        return self.translate_point(
            point,
            dx=0,
            dy=distance,
        )

    # Translate About
    def translate_about(
        self,
        point,
        center,
        dx=0,
        dy=0,
    ):

        self._validate_point(
            point,
            "point",
        )

        self._validate_center(
            center,
        )

        translated = self.translate_point(
            point,
            dx=dx,
            dy=dy,
        )

        return (
            translated[0]
            + (center[0] - center[0]),
            translated[1]
            + (center[1] - center[1]),
        )
    
        # Rotate Point
    def rotate_point(
        self,
        point,
        angle,
        center=(0, 0),
        degrees=True,
    ):

        self._validate_point(
            point,
            "point",
        )

        self._validate_center(
            center,
        )

        if not isinstance(
            angle,
            Real,
        ):
            raise TypeError(
                "angle must be numeric."
            )

        if degrees:
            angle = math.radians(
                angle,
            )

        px = point[0] - center[0]
        py = point[1] - center[1]

        cos_angle = math.cos(
            angle,
        )

        sin_angle = math.sin(
            angle,
        )

        return (
            center[0]
            + px * cos_angle
            - py * sin_angle,

            center[1]
            + px * sin_angle
            + py * cos_angle,
        )

    # Rotate Points
    def rotate_points(
        self,
        points,
        angle,
        center=(0, 0),
        degrees=True,
    ):

        self._validate_points(
            points,
        )

        return [
            self.rotate_point(
                point,
                angle=angle,
                center=center,
                degrees=degrees,
            )
            for point in points
        ]

    # Scale Point
    def scale_point(
        self,
        point,
        scale_x=1.0,
        scale_y=None,
        center=(0, 0),
    ):

        self._validate_point(
            point,
            "point",
        )

        self._validate_center(
            center,
        )

        if scale_y is None:
            scale_y = scale_x

        if not isinstance(
            scale_x,
            Real,
        ):
            raise TypeError(
                "scale_x must be numeric."
            )

        if not isinstance(
            scale_y,
            Real,
        ):
            raise TypeError(
                "scale_y must be numeric."
            )

        return (
            center[0]
            + (point[0] - center[0])
            * scale_x,

            center[1]
            + (point[1] - center[1])
            * scale_y,
        )

    # Scale Points
    def scale_points(
        self,
        points,
        scale_x=1.0,
        scale_y=None,
        center=(0, 0),
    ):

        self._validate_points(
            points,
        )

        return [
            self.scale_point(
                point,
                scale_x=scale_x,
                scale_y=scale_y,
                center=center,
            )
            for point in points
        ]

    # Reflect Point
    def reflect_point(
        self,
        point,
        axis="x",
    ):

        self._validate_point(
            point,
            "point",
        )

        axis = axis.lower()

        if axis == "x":

            return (
                point[0],
                -point[1],
            )

        if axis == "y":

            return (
                -point[0],
                point[1],
            )

        if axis == "origin":

            return (
                -point[0],
                -point[1],
            )

        if axis == "y=x":

            return (
                point[1],
                point[0],
            )

        if axis == "y=-x":

            return (
                -point[1],
                -point[0],
            )

        raise ValueError(
            "axis must be 'x', 'y', 'origin', 'y=x' or 'y=-x'."
        )

    # Reflect Points
    def reflect_points(
        self,
        points,
        axis="x",
    ):

        self._validate_points(
            points,
        )

        return [
            self.reflect_point(
                point,
                axis=axis,
            )
            for point in points
        ]

    # Shear Point
    def shear_point(
        self,
        point,
        shear_x=0,
        shear_y=0,
        center=(0, 0),
    ):

        self._validate_point(
            point,
            "point",
        )

        self._validate_center(
            center,
        )

        if not isinstance(
            shear_x,
            Real,
        ):
            raise TypeError(
                "shear_x must be numeric."
            )

        if not isinstance(
            shear_y,
            Real,
        ):
            raise TypeError(
                "shear_y must be numeric."
            )

        x = point[0] - center[0]
        y = point[1] - center[1]

        return (
            center[0]
            + x
            + shear_x * y,

            center[1]
            + y
            + shear_y * x,
        )

    # Shear Points
    def shear_points(
        self,
        points,
        shear_x=0,
        shear_y=0,
        center=(0, 0),
    ):

        self._validate_points(
            points,
        )

        return [
            self.shear_point(
                point,
                shear_x=shear_x,
                shear_y=shear_y,
                center=center,
            )
            for point in points
        ]

    # Matrix Multiply
    def matrix_multiply(
        self,
        matrix1,
        matrix2,
    ):

        if len(matrix1[0]) != len(matrix2):
            raise ValueError(
                "Matrix dimensions are incompatible."
            )

        result = []

        for row in matrix1:

            result_row = []

            for column in zip(
                *matrix2,
            ):

                result_row.append(
                    sum(
                        a * b
                        for a, b in zip(
                            row,
                            column,
                        )
                    )
                )

            result.append(
                result_row,
            )

        return result

    # Apply Matrix
    def apply_matrix(
        self,
        point,
        matrix,
    ):

        self._validate_point(
            point,
            "point",
        )

        if (
            len(matrix) != 3
            or any(
                len(row) != 3
                for row in matrix
            )
        ):
            raise ValueError(
                "matrix must be a 3x3 matrix."
            )

        x = point[0]
        y = point[1]

        vector = [
            [x],
            [y],
            [1],
        ]

        result = self.matrix_multiply(
            matrix,
            vector,
        )

        return (
            result[0][0],
            result[1][0],
        )

    # Apply Matrix Points
    def apply_matrix_points(
        self,
        points,
        matrix,
    ):

        self._validate_points(
            points,
        )

        return [
            self.apply_matrix(
                point,
                matrix,
            )
            for point in points
        ]
    
        # Compose Matrices
    def compose_matrices(
        self,
        *matrices,
    ):

        if len(matrices) == 0:
            return self.identity_matrix()

        result = matrices[0]

        for matrix in matrices[1:]:

            result = self.matrix_multiply(
                result,
                matrix,
            )

        return result

    # Identity Matrix
    def identity_matrix(
        self,
    ):

        return [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
        ]

    # Bounding Box
    def bounding_box(
        self,
        points,
    ):

        self._validate_points(
            points,
        )

        xs = [
            point[0]
            for point in points
        ]

        ys = [
            point[1]
            for point in points
        ]

        return (
            min(xs),
            min(ys),
            max(xs),
            max(ys),
        )

    # Bounding Size
    def bounding_size(
        self,
        points,
    ):

        min_x, min_y, max_x, max_y = (
            self.bounding_box(
                points,
            )
        )

        return (
            max_x - min_x,
            max_y - min_y,
        )

    # Bounding Center
    def bounding_center(
        self,
        points,
    ):

        min_x, min_y, max_x, max_y = (
            self.bounding_box(
                points,
            )
        )

        return (
            (min_x + max_x) / 2,
            (min_y + max_y) / 2,
        )

    # Centroid
    def centroid(
        self,
        points,
    ):

        self._validate_points(
            points,
        )

        count = len(
            points,
        )

        return (
            sum(
                point[0]
                for point in points
            )
            / count,

            sum(
                point[1]
                for point in points
            )
            / count,
        )

    # Polygon Area
    def polygon_area(
        self,
        points,
    ):

        self._validate_points(
            points,
        )

        if len(points) < 3:
            raise ValueError(
                "At least three points are required."
            )

        area = 0

        count = len(
            points,
        )

        for index in range(
            count,
        ):

            x1, y1 = points[index]

            x2, y2 = points[
                (index + 1)
                % count
            ]

            area += (
                x1 * y2
                - x2 * y1
            )

        return abs(
            area,
        ) / 2

    # Is Clockwise
    def is_clockwise(
        self,
        points,
    ):

        self._validate_points(
            points,
        )

        if len(points) < 3:
            raise ValueError(
                "At least three points are required."
            )

        total = 0

        count = len(
            points,
        )

        for index in range(
            count,
        ):

            x1, y1 = points[index]

            x2, y2 = points[
                (index + 1)
                % count
            ]

            total += (
                x2 - x1
            ) * (
                y2 + y1
            )

        return total > 0


__all__ = [
    "DrawingTransforms",
]