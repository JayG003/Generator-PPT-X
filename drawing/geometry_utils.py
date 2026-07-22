from __future__ import annotations

import math
from typing import Iterable, Sequence, Tuple, TypeAlias

# Constants
EPSILON: float = 1e-9

PI: float = math.pi
TAU: float = math.tau

DEG_TO_RAD: float = PI / 180.0
RAD_TO_DEG: float = 180.0 / PI

# Type Aliases
Point: TypeAlias = tuple[float, float]
Vector: TypeAlias = tuple[float, float]
Line: TypeAlias = tuple[Point, Point]
Segment: TypeAlias = tuple[Point, Point]

# Validation Helpers
def is_close(
    a: float,
    b: float,
    *,
    eps: float = EPSILON,
) -> bool:
    return abs(a - b) <= eps


def is_zero(
    value: float,
    *,
    eps: float = EPSILON,
) -> bool:
    return abs(value) <= eps


def validate_point(point: Sequence[float]) -> Point:
    if len(point) != 2:
        raise TypeError("Point must contain exactly two coordinates.")

    return (
        float(point[0]),
        float(point[1]),
    )


def validate_points(
    points: Iterable[Sequence[float]],
) -> list[Point]:
    return [
        validate_point(point)
        for point in points
    ]


# Basic Point Helpers
def point(
    x: float,
    y: float,
) -> Point:
    return (
        float(x),
        float(y),
    )


def x(point_: Point) -> float:
    return point_[0]


def y(point_: Point) -> float:
    return point_[1]


def midpoint(
    p1: Point,
    p2: Point,
) -> Point:
    return (
        (p1[0] + p2[0]) / 2.0,
        (p1[1] + p2[1]) / 2.0,
    )


def translate_point(
    point_: Point,
    dx: float,
    dy: float,
) -> Point:
    return (
        point_[0] + dx,
        point_[1] + dy,
    )


def scale_point(
    point_: Point,
    sx: float,
    sy: float | None = None,
) -> Point:
    if sy is None:
        sy = sx

    return (
        point_[0] * sx,
        point_[1] * sy,
    )


def points_equal(
    p1: Point,
    p2: Point,
    *,
    eps: float = EPSILON,
) -> bool:
    return (
        is_close(p1[0], p2[0], eps=eps)
        and
        is_close(p1[1], p2[1], eps=eps)
    )

# ============================================================================
# Vector Helpers
# ============================================================================

def vector(
    p1: Point,
    p2: Point,
) -> Vector:
    """
    Vector from p1 to p2.
    """

    return (
        p2[0] - p1[0],
        p2[1] - p1[1],
    )


def vector_from_xy(
    x: float,
    y: float,
) -> Vector:
    """
    Create a vector from x and y components.
    """

    return (
        float(x),
        float(y),
    )


def add_vectors(
    v1: Vector,
    v2: Vector,
) -> Vector:
    """
    Add two vectors.
    """

    return (
        v1[0] + v2[0],
        v1[1] + v2[1],
    )


def subtract_vectors(
    v1: Vector,
    v2: Vector,
) -> Vector:
    """
    Subtract two vectors.
    """

    return (
        v1[0] - v2[0],
        v1[1] - v2[1],
    )


def negate_vector(
    vector_: Vector,
) -> Vector:
    """
    Reverse vector direction.
    """

    return (
        -vector_[0],
        -vector_[1],
    )


def scale_vector(
    vector_: Vector,
    scalar: float,
) -> Vector:
    """
    Scale a vector.
    """

    return (
        vector_[0] * scalar,
        vector_[1] * scalar,
    )


def dot(
    v1: Vector,
    v2: Vector,
) -> float:
    """
    Dot product.
    """

    return (
        v1[0] * v2[0]
        + v1[1] * v2[1]
    )


def cross(
    v1: Vector,
    v2: Vector,
) -> float:
    """
    2D cross product.
    """

    return (
        v1[0] * v2[1]
        - v1[1] * v2[0]
    )


def magnitude(
    vector_: Vector,
) -> float:
    """
    Vector length.
    """

    return math.hypot(
        vector_[0],
        vector_[1],
    )


def magnitude_squared(
    vector_: Vector,
) -> float:
    """
    Squared vector length.
    """

    return dot(vector_, vector_)


def normalize(
    vector_: Vector,
) -> Vector:
    """
    Unit vector.
    """

    length = magnitude(vector_)

    if is_zero(length):
        raise ValueError("Cannot normalize a zero-length vector.")

    return (
        vector_[0] / length,
        vector_[1] / length,
    )


# ============================================================================
# Distance Helpers
# ============================================================================

def distance(
    p1: Point,
    p2: Point,
) -> float:
    """
    Euclidean distance.
    """

    return math.hypot(
        p2[0] - p1[0],
        p2[1] - p1[1],
    )


def distance_squared(
    p1: Point,
    p2: Point,
) -> float:
    """
    Squared Euclidean distance.
    """

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    return dx * dx + dy * dy


def manhattan_distance(
    p1: Point,
    p2: Point,
) -> float:
    """
    Manhattan distance.
    """

    return (
        abs(p2[0] - p1[0])
        + abs(p2[1] - p1[1])
    )


# ============================================================================
# Angle Helpers
# ============================================================================

def angle_of_vector(
    vector_: Vector,
    *,
    degrees: bool = False,
) -> float:
    """
    Angle of a vector from +X axis.
    """

    angle = math.atan2(
        vector_[1],
        vector_[0],
    )

    return math.degrees(angle) if degrees else angle


def angle_between_vectors(
    v1: Vector,
    v2: Vector,
    *,
    degrees: bool = False,
) -> float:
    """
    Smallest angle between two vectors.
    """

    m1 = magnitude(v1)
    m2 = magnitude(v2)

    if is_zero(m1) or is_zero(m2):
        raise ValueError("Zero-length vector.")

    cosine = dot(v1, v2) / (m1 * m2)
    cosine = max(-1.0, min(1.0, cosine))

    angle = math.acos(cosine)

    return math.degrees(angle) if degrees else angle


def angle_between_points(
    p1: Point,
    p2: Point,
    *,
    degrees: bool = False,
) -> float:
    """
    Angle from p1 to p2.
    """

    return angle_of_vector(
        vector(p1, p2),
        degrees=degrees,
    )


# ============================================================================
# Direction Helpers
# ============================================================================

def direction(
    p1: Point,
    p2: Point,
) -> Vector:
    """
    Unit direction vector.
    """

    return normalize(vector(p1, p2))


def perpendicular_left(
    vector_: Vector,
) -> Vector:
    """
    90° CCW vector.
    """

    return (
        -vector_[1],
        vector_[0],
    )


def perpendicular_right(
    vector_: Vector,
) -> Vector:
    """
    90° CW vector.
    """

    return (
        vector_[1],
        -vector_[0],
    )


# ============================================================================
# Projection Helpers
# ============================================================================

def scalar_projection(
    source: Vector,
    onto: Vector,
) -> float:
    """
    Scalar projection of source onto onto.
    """

    length = magnitude(onto)

    if is_zero(length):
        raise ValueError("Cannot project onto a zero vector.")

    return dot(source, onto) / length


def vector_projection(
    source: Vector,
    onto: Vector,
) -> Vector:
    """
    Vector projection of source onto onto.
    """

    denominator = magnitude_squared(onto)

    if is_zero(denominator):
        raise ValueError("Cannot project onto a zero vector.")

    scale = dot(source, onto) / denominator

    return scale_vector(onto, scale)


def rejection(
    source: Vector,
    onto: Vector,
) -> Vector:
    """
    Vector component perpendicular to onto.
    """

    return subtract_vectors(
        source,
        vector_projection(source, onto),
    )

# ==========================================================
# BASIC LINE CONSTRUCTION
# ==========================================================

def line_from_points(p1: Point, p2: Point) -> Line:
    """
    Create an infinite line from two points.
    """
    return (p1, p2)


# ==========================================================
# LINE COEFFICIENTS
# ==========================================================

def line_coefficients(line: Line)-> tuple[float, float, float]:
    """
    Returns (A, B, C) for

        Ax + By + C = 0

    where

        A = y1 - y2
        B = x2 - x1
        C = x1*y2 - x2*y1
    """

    x1 = line[0][0]
    y1 = line[0][1]

    x2 = line[1][0]
    y2 = line[1][1]

    A = y1 - y2
    B = x2 - x1
    C = x1 * y2 - x2 * y1

    return A, B, C


# ==========================================================
# SLOPE
# ==========================================================

def line_slope(line: Line)-> float | None:
    """
    Returns the slope.

    Vertical line -> None
    """

    dx = line[1][0] - line[0][0]

    if is_zero(dx):
        return None

    dy = line[1][1] - line[0][1]

    return dy / dx


# ==========================================================
# DIRECTION VECTOR
# ==========================================================

def line_direction(line: Line):
    """
    Returns the direction vector.

    (dx, dy)
    """

    return (
        line[1][0] - line[0][0],
        line[1][1] - line[0][1],
    )


def normalized_direction(line: Line):
    """
    Returns unit direction vector.
    """

    dx, dy = line_direction(line)

    length = math.hypot(dx, dy)

    return (
        dx / length,
        dy / length,
    )


# ==========================================================
# LINE LENGTH
# ==========================================================

def line_length(line: Line):
    """
    Distance between the two defining points.
    """

    return math.hypot(
        line[1][0] - line[0][0],
        line[1][1] - line[0][1],
    )


# ==========================================================
# PARAMETRIC FORM
# ==========================================================

def point_at_parameter(line: Line, t: float) -> Point:
    """
    Parametric equation:

        P(t) = P1 + t(P2-P1)

    t=0 -> first point
    t=1 -> second point

    t<0 or t>1 lies outside the segment but still on the line.
    """

    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]

    x = line[0][0] + t * dx
    y = line[0][1] + t * dy

    return (
        x,
        y,
    )


# ==========================================================
# PARAMETER OF A POINT
# ==========================================================

def parameter_on_line(line: Line, point: Point):
    """
    Returns parameter t such that

        point = P1 + t(P2-P1)

    Returns None if the point is not on the line.
    """

    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]

    if abs(dx) >= abs(dy):

        if is_zero(dx):
            return None

        t = (point[0] - line[0][0]) / dx

    else:

        if is_close(dy, 0.0, eps=EPSILON):
            return None

        t = (point[1] - line[0][1]) / dy

    px = line[0][0] + t * dx
    py = line[0][1] + t * dy

    if (
        is_close(px, point[0], abs_tol=EPSILON) and
        is_close(py, point[1], abs_tol=EPSILON)
    ):
        return t

    return None

# ==========================================================
# LINE PROJECTIONS
# ==========================================================

def closest_point_on_line(line: Line, point: Point) -> Point:
    """
    Returns the closest point on the infinite line.

    Projection of point onto line.
    """

    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]

    length_sq = dx * dx + dy * dy

    if is_close(length_sq, 0.0, eps=EPSILON):
        return line[0]

    t = (
        (point[0] - line[0][0]) * dx +
        (point[1] - line[0][1]) * dy
    ) / length_sq

    x = line[0][0] + t * dx
    y = line[0][1] + t * dy

    return (
        x,
        y,
    )


# ==========================================================
# DISTANCE TO LINE
# ==========================================================

def distance_to_line(point: Point, line: Line) -> float:
    """
    Returns the shortest distance from a point
    to an infinite line.
    """

    projection = closest_point_on_line(line, point)

    return math.hypot(
        point[0] - projection[0],
        point[1] - projection[1],
    )


# ==========================================================
# PARALLEL HELPERS
# ==========================================================

def are_parallel(line1: Line, line2: Line) -> bool:
    """
    Returns True if two infinite lines are parallel.
    """

    dx1 = line1[1][0] - line1[0][0]
    dy1 = line1[1][1] - line1[0][1]

    dx2 = line2[1][0] - line2[0][0]
    dy2 = line2[1][1] - line2[0][1]

    return is_close(
        dx1 * dy2 - dy1 * dx2,
        0.0,
        eps=EPSILON,
    )


def parallel_line(line: Line, through: Point) -> Line:
    """
    Creates a line parallel to the given line
    passing through 'through'.
    """

    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]

    return (
        through,
        (
            through[0] + dx,
            through[1] + dy,
        ),
    )


# ==========================================================
# PERPENDICULAR HELPERS
# ==========================================================

def are_perpendicular(line1: Line, line2: Line) -> bool:
    """
    Returns True if two lines are perpendicular.
    """

    dx1 = line1[1][0] - line1[0][0]
    dy1 = line1[1][1] - line1[0][1]

    dx2 = line2[1][0] - line2[0][0]
    dy2 = line2[1][1] - line2[0][1]

    return is_close(
        dx1 * dx2 + dy1 * dy2,
        0.0,
        eps=EPSILON,
    )


def perpendicular_line(line: Line, through: Point) -> Line:
    """
    Creates a line perpendicular to the given line
    passing through the specified point.
    """

    dx = line[1][0] - line[0][0]
    dy = line[1][1] - line[0][1]

    return (
        through,
        (
            through[0] - dy,
            through[1] + dx,
        ),
    )


# ==========================================================
# COLLINEARITY
# ==========================================================

def are_collinear(
    p1: Point,
    p2: Point,
    p3: Point,
    tolerance: float = EPSILON,
) -> bool:
    """
    Returns True if three points are collinear.
    """

    area2 = (
        (p2[0] - p1[0]) * (p3[1] - p1[1])
        -
        (p2[1] - p1[1]) * (p3[0] - p1[0])
    )

    return abs(area2) <= tolerance


def point_on_line(
    point: Point,
    line: Line,
    tolerance: float = EPSILON,
) -> bool:
    """
    Returns True if the point lies on the
    infinite line.
    """

    return are_collinear(
        line[0],
        line[1],
        point,
        tolerance,
    )


def point_on_segment(
    point: Point,
    line: Line,
    tolerance: float = EPSILON,
) -> bool:
    """
    Returns True if the point lies on the
    finite line segment.
    """

    if not point_on_line(point, line, tolerance):
        return False

    min_x = min(line[0][0], line[1][0]) - tolerance
    max_x = max(line[0][0], line[1][0]) + tolerance

    min_y = min(line[0][1], line[1][1]) - tolerance
    max_y = max(line[0][1], line[1][1]) + tolerance

    return (
        min_x <= point[0] <= max_x
        and
        min_y <= point[1] <= max_y
    )

# ==========================================================
# LINE-LINE RELATIONSHIPS
# ==========================================================

from enum import Enum


class LineRelationship(Enum):
    """
    Relationship between two infinite lines.
    """

    INTERSECTING = "intersecting"
    PARALLEL = "parallel"
    COINCIDENT = "coincident"


# ==========================================================
# INFINITE LINE INTERSECTION
# ==========================================================

def line_intersection(
    line1: Line,
    line2: Line,
) -> Point | None:
    """
    Computes the intersection point of two infinite lines.

    Returns
    -------
    Point
        Intersection point.

    None
        If the lines are parallel or coincident.
    """

    x1, y1 = line1[0][0], line1[0][1]
    x2, y2 = line1[1][0], line1[1][1]

    x3, y3 = line2[0][0], line2[0][1]
    x4, y4 = line2[1][0], line2[1][1]

    denominator = (
        (x1 - x2) * (y3 - y4)
        -
        (y1 - y2) * (x3 - x4)
    )

    if is_close(denominator, 0.0, eps=EPSILON):
        return None

    determinant1 = x1 * y2 - y1 * x2
    determinant2 = x3 * y4 - y3 * x4

    px = (
        determinant1 * (x3 - x4)
        -
        (x1 - x2) * determinant2
    ) / denominator

    py = (
        determinant1 * (y3 - y4)
        -
        (y1 - y2) * determinant2
    ) / denominator

    return (
        px,
        py,
    )


# ==========================================================
# LINE RELATIONSHIP
# ==========================================================

def line_relationship(
    line1: Line,
    line2: Line,
) -> LineRelationship:
    """
    Determines the relationship between two infinite lines.
    """

    if not are_parallel(line1, line2):
        return LineRelationship.INTERSECTING

    if point_on_line(line1[0], line2):
        return LineRelationship.COINCIDENT

    return LineRelationship.PARALLEL


def lines_intersect(
    line1: Line,
    line2: Line,
) -> bool:
    """
    Returns True if two infinite lines intersect.
    Coincident lines also count as intersecting.
    """

    return (
        line_relationship(line1, line2)
        != LineRelationship.PARALLEL
    )


def intersection_exists(
    line1: Line,
    line2: Line,
) -> bool:
    """
    Alias for readability.
    """

    return lines_intersect(line1, line2)


# ==========================================================
# HORIZONTAL / VERTICAL TESTS
# ==========================================================

def is_horizontal(
    line: Line,
    tolerance: float = EPSILON,
) -> bool:
    """
    Returns True if the line is horizontal.
    """

    return is_close(
        line[0][1],
        line[1][1],
        abs_tol=tolerance,
    )


def is_vertical(
    line: Line,
    tolerance: float = EPSILON,
) -> bool:
    """
    Returns True if the line is vertical.
    """

    return is_close(
        line[0][0],
        line[1][0],
        abs_tol=tolerance,
    )

# ==========================================================
# SEGMENT UTILITIES
# ==========================================================

def segment_length(segment: Segment) -> float:
    """
    Length of a line segment.
    """
    return distance(segment[0], segment[1])


def segment_midpoint(segment: Segment) -> Point:
    """
    Midpoint of a line segment.
    """
    return midpoint(segment[0], segment[1])


def closest_point_on_segment(
    point: Point,
    segment: Segment,
) -> Point:
    """
    Returns the closest point on a finite segment.
    """

    a, b = segment

    ab = vector(a, b)
    ap = vector(a, point)

    length_sq = magnitude_squared(ab)

    if is_zero(length_sq):
        return a

    t = dot(ap, ab) / length_sq
    t = max(0.0, min(1.0, t))

    return (
        a[0] + ab[0] * t,
        a[1] + ab[1] * t,
    )


def distance_to_segment(
    point: Point,
    segment: Segment,
) -> float:
    """
    Distance from a point to a segment.
    """

    closest = closest_point_on_segment(point, segment)

    return distance(point, closest)

def _orientation(
    p: Point,
    q: Point,
    r: Point,
) -> int:

    value = cross(
        vector(p, q),
        vector(p, r),
    )

    if is_zero(value):
        return 0

    return 1 if value > 0 else -1


def segments_intersect(
    segment1: Segment,
    segment2: Segment,
) -> bool:
    """
    Returns True if two finite segments intersect.
    """

    p1, q1 = segment1
    p2, q2 = segment2

    o1 = _orientation(p1, q1, p2)
    o2 = _orientation(p1, q1, q2)
    o3 = _orientation(p2, q2, p1)
    o4 = _orientation(p2, q2, q1)

    if o1 != o2 and o3 != o4:
        return True

    if o1 == 0 and point_on_segment(p2, (p1, q1)):
        return True

    if o2 == 0 and point_on_segment(q2, (p1, q1)):
        return True

    if o3 == 0 and point_on_segment(p1, (p2, q2)):
        return True

    if o4 == 0 and point_on_segment(q1, (p2, q2)):
        return True

    return False


def segment_intersection(
    segment1: Segment,
    segment2: Segment,
) -> Point | None:
    """
    Returns the intersection point of two finite segments.
    """

    if not segments_intersect(segment1, segment2):
        return None

    line1 = (segment1[0], segment1[1])
    line2 = (segment2[0], segment2[1])

    return line_intersection(line1, line2)

def distance_between_segments(
    segment1: Segment,
    segment2: Segment,
) -> float:
    """
    Minimum distance between two finite segments.
    """

    if segments_intersect(segment1, segment2):
        return 0.0

    return min(
        distance_to_segment(segment1[0], segment2),
        distance_to_segment(segment1[1], segment2),
        distance_to_segment(segment2[0], segment1),
        distance_to_segment(segment2[1], segment1),
    )

# ============================================================================
# Circle Helpers
# ============================================================================

Circle: TypeAlias = tuple[Point, float]


def circle(
    center: Point,
    radius: float,
) -> Circle:
    """
    Create a circle.

    Raises
    ------
    ValueError
        If radius is negative.
    """

    if radius < 0:
        raise ValueError("Radius cannot be negative.")

    return (
        validate_point(center),
        float(radius),
    )


def circle_center(
    circle_: Circle,
) -> Point:
    """
    Return the center of a circle.
    """

    return circle_[0]


def circle_radius(
    circle_: Circle,
) -> float:
    """
    Return the radius.
    """

    return circle_[1]


def circle_diameter(
    circle_: Circle,
) -> float:
    """
    Circle diameter.
    """

    return circle_[1] * 2.0


def circle_circumference(
    circle_: Circle,
) -> float:
    """
    Circle circumference.
    """

    return TAU * circle_[1]


def circle_area(
    circle_: Circle,
) -> float:
    """
    Circle area.
    """

    radius = circle_[1]

    return PI * radius * radius


def point_in_circle(
    point_: Point,
    circle_: Circle,
    *,
    inclusive: bool = True,
) -> bool:
    """
    Check whether a point lies inside a circle.
    """

    d2 = distance_squared(
        point_,
        circle_[0],
    )

    r2 = circle_[1] ** 2

    if inclusive:
        return d2 <= r2 + EPSILON

    return d2 < r2


def point_on_circle(
    point_: Point,
    circle_: Circle,
    *,
    eps: float = EPSILON,
) -> bool:
    """
    Returns True if the point lies on the circumference.
    """

    return is_close(
        distance(
            point_,
            circle_[0],
        ),
        circle_[1],
        eps=eps,
    )


def circle_from_diameter(
    p1: Point,
    p2: Point,
) -> Circle:
    """
    Create a circle from a diameter.
    """

    center = midpoint(
        p1,
        p2,
    )

    radius = distance(
        p1,
        p2,
    ) / 2.0

    return (
        center,
        radius,
    )


def circle_bounding_box(
    circle_: Circle,
) -> tuple[Point, Point]:
    """
    Bounding box of a circle.

    Returns
    -------
    (
        (min_x, min_y),
        (max_x, max_y)
    )
    """

    center, radius = circle_

    return (
        (
            center[0] - radius,
            center[1] - radius,
        ),
        (
            center[0] + radius,
            center[1] + radius,
        ),
    )


# ============================================================================
# Bounding Box Helpers
# ============================================================================

BoundingBox: TypeAlias = tuple[Point, Point]


def bounding_box(
    points: Sequence[Point],
) -> BoundingBox:
    """
    Compute the axis-aligned bounding box
    for a collection of points.
    """

    if not points:
        raise ValueError("At least one point is required.")

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    return (
        (
            min(xs),
            min(ys),
        ),
        (
            max(xs),
            max(ys),
        ),
    )


def bounding_box_width(
    box: BoundingBox,
) -> float:
    """
    Width of a bounding box.
    """

    return box[1][0] - box[0][0]


def bounding_box_height(
    box: BoundingBox,
) -> float:
    """
    Height of a bounding box.
    """

    return box[1][1] - box[0][1]


def bounding_box_center(
    box: BoundingBox,
) -> Point:
    """
    Center of a bounding box.
    """

    return midpoint(
        box[0],
        box[1],
    )


def point_in_bounding_box(
    point_: Point,
    box: BoundingBox,
    *,
    inclusive: bool = True,
) -> bool:
    """
    Check whether a point lies inside
    a bounding box.
    """

    min_point, max_point = box

    if inclusive:
        return (
            min_point[0] <= point_[0] <= max_point[0]
            and
            min_point[1] <= point_[1] <= max_point[1]
        )

    return (
        min_point[0] < point_[0] < max_point[0]
        and
        min_point[1] < point_[1] < max_point[1]
    )


def boxes_intersect(
    box1: BoundingBox,
    box2: BoundingBox,
) -> bool:
    """
    Check whether two bounding boxes intersect.
    """

    return not (
        box1[1][0] < box2[0][0]
        or box2[1][0] < box1[0][0]
        or box1[1][1] < box2[0][1]
        or box2[1][1] < box1[0][1]
    )

def expand_bounding_box(box: BoundingBox, padding: float) -> BoundingBox:
    """
    Expand a bounding box by a given padding.
    """

    return (
        (
            box[0][0] - padding,
            box[0][1] - padding,
        ),
        (
            box[1][0] + padding,
            box[1][1] + padding,
        ),
    )

# ============================================================================
# Polygon Helpers
# ============================================================================

Polygon: TypeAlias = tuple[Point, ...]


def polygon(
    points: Sequence[Point],
) -> Polygon:
    """
    Create a polygon from a sequence of points.

    Raises
    ------
    ValueError
        If fewer than 3 vertices are supplied.
    """

    vertices = tuple(validate_points(points))

    if len(vertices) < 3:
        raise ValueError(
            "A polygon requires at least three vertices."
        )

    return vertices


def polygon_vertex_count(
    polygon_: Polygon,
) -> int:
    """
    Number of vertices.
    """

    return len(polygon_)


def polygon_edges(
    polygon_: Polygon,
) -> list[Segment]:
    """
    Returns all polygon edges.
    """

    count = len(polygon_)

    return [
        (
            polygon_[i],
            polygon_[(i + 1) % count],
        )
        for i in range(count)
    ]


def polygon_perimeter(
    polygon_: Polygon,
) -> float:
    """
    Polygon perimeter.
    """

    total = 0.0

    for edge in polygon_edges(polygon_):
        total += distance(
            edge[0],
            edge[1],
        )

    return total


# ============================================================================
# Polygon Area
# ============================================================================

def signed_polygon_area(
    polygon_: Polygon,
) -> float:
    """
    Signed polygon area using the shoelace formula.

    Counter-clockwise polygons have positive area.
    Clockwise polygons have negative area.
    """

    area = 0.0
    n = len(polygon_)

    for i in range(n):
        x1, y1 = polygon_[i]
        x2, y2 = polygon_[(i + 1) % n]

        area += (
            x1 * y2
            -
            x2 * y1
        )

    return area / 2.0


def polygon_area(
    polygon_: Polygon,
) -> float:
    """
    Absolute polygon area.
    """

    return abs(
        signed_polygon_area(
            polygon_,
        )
    )


def is_clockwise(
    polygon_: Polygon,
) -> bool:
    """
    Returns True if the polygon
    vertices are ordered clockwise.
    """

    return signed_polygon_area(
        polygon_
    ) < 0.0


def is_counter_clockwise(
    polygon_: Polygon,
) -> bool:
    """
    Returns True if the polygon
    vertices are ordered counter-clockwise.
    """

    return signed_polygon_area(
        polygon_
    ) > 0.0


# ============================================================================
# Polygon Centroid
# ============================================================================

def polygon_centroid(
    polygon_: Polygon,
) -> Point:
    """
    Area-weighted centroid.

    Raises
    ------
    ValueError
        If the polygon has zero area.
    """

    area = signed_polygon_area(
        polygon_,
    )

    if is_zero(area):
        raise ValueError(
            "Degenerate polygon."
        )

    factor = 1.0 / (6.0 * area)

    cx = 0.0
    cy = 0.0

    n = len(polygon_)

    for i in range(n):

        x1, y1 = polygon_[i]
        x2, y2 = polygon_[(i + 1) % n]

        cross_product = (
            x1 * y2
            -
            x2 * y1
        )

        cx += (
            x1 + x2
        ) * cross_product

        cy += (
            y1 + y2
        ) * cross_product

    return (
        cx * factor,
        cy * factor,
    )


# ============================================================================
# Polygon Bounding Box
# ============================================================================

def polygon_bounding_box(
    polygon_: Polygon,
) -> BoundingBox:
    """
    Axis-aligned bounding box.
    """

    return bounding_box(
        polygon_,
    )


# ============================================================================
# Point In Polygon
# ============================================================================

def point_in_polygon(
    point_: Point,
    polygon_: Polygon,
    *,
    inclusive: bool = True,
) -> bool:
    """
    Ray-casting point-in-polygon test.
    """

    x, y = point_

    inside = False

    n = len(polygon_)

    for i in range(n):

        x1, y1 = polygon_[i]
        x2, y2 = polygon_[(i + 1) % n]

        if point_on_segment(
            point_,
            (polygon_[i], polygon_[(i + 1) % n]),
        ):
            return inclusive

        intersects = (
            (y1 > y) != (y2 > y)
        )

        if intersects:

            intersection_x = (
                (x2 - x1)
                * (y - y1)
                / (y2 - y1)
                + x1
            )

            if x < intersection_x:
                inside = not inside

    return inside

# ============================================================================
# Convex Hull
# ============================================================================

def convex_hull(
    points: Sequence[Point],
) -> Polygon:
    """
    Computes the convex hull using Andrew's Monotonic Chain algorithm.

    Complexity
    ----------
    O(n log n)
    """

    pts = sorted(set(validate_points(points)))

    if len(pts) <= 1:
        return tuple(pts)

    def cross_product(
        o: Point,
        a: Point,
        b: Point,
    ) -> float:
        return cross(
            vector(o, a),
            vector(o, b),
        )

    lower: list[Point] = []

    for p in pts:
        while (
            len(lower) >= 2
            and cross_product(
                lower[-2],
                lower[-1],
                p,
            ) <= EPSILON
        ):
            lower.pop()

        lower.append(p)

    upper: list[Point] = []

    for p in reversed(pts):

        while (
            len(upper) >= 2
            and cross_product(
                upper[-2],
                upper[-1],
                p,
            ) <= EPSILON
        ):
            upper.pop()

        upper.append(p)

    return tuple(
        lower[:-1] + upper[:-1]
    )


# ============================================================================
# Polygon Validation
# ============================================================================

def is_convex_polygon(
    polygon_: Polygon,
) -> bool:
    """
    Returns True if the polygon is convex.
    """

    n = len(polygon_)

    if n < 3:
        return False

    sign = 0

    for i in range(n):

        p1 = polygon_[i]
        p2 = polygon_[(i + 1) % n]
        p3 = polygon_[(i + 2) % n]

        value = cross(
            vector(p1, p2),
            vector(p2, p3),
        )

        if is_zero(value):
            continue

        current = 1 if value > 0 else -1

        if sign == 0:
            sign = current
        elif sign != current:
            return False

    return True


# ============================================================================
# Polygon Transformations
# ============================================================================

def translate_polygon(
    polygon_: Polygon,
    dx: float,
    dy: float,
) -> Polygon:
    """
    Translate every vertex.
    """

    return tuple(
        translate_point(
            p,
            dx,
            dy,
        )
        for p in polygon_
    )


def scale_polygon(
    polygon_: Polygon,
    sx: float,
    sy: float | None = None,
    *,
    origin: Point = (0.0, 0.0),
) -> Polygon:
    """
    Scale polygon about an origin.
    """

    if sy is None:
        sy = sx

    ox, oy = origin

    return tuple(
        (
            ox + (p[0] - ox) * sx,
            oy + (p[1] - oy) * sy,
        )
        for p in polygon_
    )


def rotate_polygon(
    polygon_: Polygon,
    angle: float,
    *,
    origin: Point = (0.0, 0.0),
) -> Polygon:
    """
    Rotate polygon about an origin.

    Angle is in radians.
    """

    ox, oy = origin

    c = math.cos(angle)
    s = math.sin(angle)

    result = []

    for x, y in polygon_:

        x -= ox
        y -= oy

        result.append(
            (
                ox + x * c - y * s,
                oy + x * s + y * c,
            )
        )

    return tuple(result)


# ============================================================================
# Miscellaneous Utilities
# ============================================================================

def lerp(
    p1: Point,
    p2: Point,
    t: float,
) -> Point:
    """
    Linear interpolation.

    t=0 -> p1
    t=1 -> p2
    """

    return (
        p1[0] + (p2[0] - p1[0]) * t,
        p1[1] + (p2[1] - p1[1]) * t,
    )


def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Clamp a value.
    """

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def almost_equal_points(
    p1: Point,
    p2: Point,
    *,
    eps: float = EPSILON,
) -> bool:
    """
    Alias for points_equal().
    """

    return points_equal(
        p1,
        p2,
        eps=eps,
    )


# ============================================================================
# Extend __all__
# ============================================================================

__all__ = [
    # Constants
    "EPSILON",
    "PI",
    "TAU",
    "DEG_TO_RAD",
    "RAD_TO_DEG",

    # Types
    "Point",
    "Vector",
    "Line",
    "Segment",

    # Validation
    "is_close",
    "is_zero",
    "validate_point",
    "validate_points",

    # Point helpers
    "point",
    "x",
    "y",
    "midpoint",
    "translate_point",
    "scale_point",
    "points_equal",

    # Vector helpers
    "vector",
    "vector_from_xy",
    "add_vectors",
    "subtract_vectors",
    "negate_vector",
    "scale_vector",
    "dot",
    "cross",
    "magnitude",
    "magnitude_squared",
    "normalize",

    # Distance helpers
    "distance",
    "distance_squared",
    "manhattan_distance",

    # Angle helpers
    "angle_of_vector",
    "angle_between_vectors",
    "angle_between_points",

    # Direction helpers
    "direction",
    "perpendicular_left",
    "perpendicular_right",

    # Projection helpers
    "scalar_projection",
    "vector_projection",
    "rejection",

    # Line helpers
    "line_from_points",
    "line_coefficients",
    "line_slope",
    "line_direction",
    "normalized_direction",
    "line_length",
    "point_at_parameter",
    "parameter_on_line",
    "closest_point_on_line",
    "distance_to_line",
    "are_parallel",
    "parallel_line",
    "are_perpendicular",
    "perpendicular_line",
    "are_collinear",
    "point_on_line",
    "point_on_segment",

     # Enum
    "LineRelationship",

    # Intersection
    "line_intersection",
    "line_relationship",
    "lines_intersect",
    "intersection_exists",

    # Orientation
    "is_horizontal",
    "is_vertical",

    # Segment utilities
    "segment_length",
    "segment_midpoint",
    "closest_point_on_segment",
    "distance_to_segment",
    "segments_intersect",
    "segment_intersection",
    "distance_between_segments",

    # Circle
    "Circle",
    "circle",
    "circle_center",
    "circle_radius",
    "circle_diameter",
    "circle_circumference",
    "circle_area",
    "point_in_circle",
    "point_on_circle",
    "circle_from_diameter",
    "circle_bounding_box",

    # Bounding boxes
    "BoundingBox",
    "bounding_box",
    "bounding_box_width",
    "bounding_box_height",
    "bounding_box_center",
    "point_in_bounding_box",
    "boxes_intersect",
    "expand_bounding_box",

    # Polygon
    "Polygon",

    # Construction
    "polygon",

    # Information
    "polygon_vertex_count",
    "polygon_edges",
    "polygon_perimeter",

    # Area
    "signed_polygon_area",
    "polygon_area",

    # Orientation
    "is_clockwise",
    "is_counter_clockwise",

    # Geometry
    "polygon_centroid",
    "polygon_bounding_box",
    "point_in_polygon",

    # Convex hull
    "convex_hull",

    # Validation
    "is_convex_polygon",

    # Transformations
    "translate_polygon",
    "scale_polygon",
    "rotate_polygon",

    # Utilities
    "lerp",
    "clamp",
    "almost_equal_points",
]