# Generator PPT-X

## Project Status

### Overall Progress
- [x] config.py
- [x] drawing/styles.py
- [x] drawing/canvas.py
- [x] drawing/primitives.py
- [x] drawing/shapes.py
- [x] drawing/arrows.py
- [x] drawing/labels.py
- [x] drawing/dimensions.py
- [x] drawing/transforms.py
- [x] drawing/geometry_utils.py
- [x] drawing/layout.py
- [ ] renderers/diagram_renderer.py
- [ ] diagrams/geometry.py
- [ ] diagrams/flowchart.py
- [ ] diagrams/tree.py
- [ ] renderers/graph_renderer.py
- [ ] diagrams/graph.py
- [ ] engine/ppt_generator.py
- [ ] engine/slide_dispatcher.py
- [ ] renderers/title_renderer.py
- [ ] renderers/theory_renderer.py
- [ ] renderers/question_renderer.py
- [ ] renderers/table_renderer.py
- [ ] engine/json_loader.py
- [ ] app.py

---

## Locked Files

### config.py ✅
**Status:** Locked

**Purpose**
- Stores all global constants.
- Centralizes slide dimensions.
- Centralizes fonts.
- Centralizes colors.
- Centralizes margins.
- Centralizes default image settings.
- Centralizes graph and diagram dimensions.
- Defines default background path.

**Dependencies**
- pptx.util
- pptx.dml.color

**Used By**
- Entire project.

### drawing/styles.py ✅
**Status:** Locked

**Purpose**
- Defines reusable drawing styles for the rendering engine.
- Keeps all styling separate from drawing logic.
- Provides a common style object shared by diagrams and graphs.
- Converts PowerPoint RGB colors into Matplotlib-compatible RGB values.

**Contains**
- rgb() helper
- DrawingStyle dataclass
- DEFAULT_STYLE
- PRIMARY_STYLE
- SECONDARY_STYLE
- ACCENT_STYLE
- LABEL_STYLE
- GRID_STYLE

**Dependencies**
- dataclasses
- config.py

**Used By**
- drawing/canvas.py
- drawing/primitives.py
- renderers/diagram_renderer.py
- renderers/graph_renderer.py
---

### drawing/primitives.py ✅
**Status:** Locked

**Purpose**
- Provides reusable low-level drawing primitives built on top of DrawingCanvas.
- Encapsulates all Matplotlib drawing operations behind a consistent API.
- Serves as the common drawing layer used by both diagram and graph renderers.
- Ensures renderers never interact with Matplotlib directly.

**Contains**

#### Canvas Helpers
- set_limits()
- set_equal_aspect()
- show_axes()
- hide_axes()
- show_grid()
- hide_grid()
- set_title()
- reset()
- get_xlim()
- get_ylim()

#### Line Primitives
- line()
- polyline()
- dashed_line()
- arrow()
- point()

#### Shape Primitives
- rectangle()
- rounded_rectangle()
- circle()
- ellipse()
- arc()
- polygon()

#### Advanced Drawing
- bezier()
- fill_polygon()
- fill_between()
- add_patch()
- image()

#### Text Utilities
- text()
- label()
- rotated_text()
- vertical_text()
- horizontal_text()
- centered_text()

#### Coordinate Utilities
- axes()
- coordinate_plane()
- number_line()
- ticks()
- set_xticks()
- set_yticks()

#### Utility Methods
- equal_aspect()
- auto_aspect()
- get_axis()
- get_canvas()

#### Internal Helpers
- _resolve_style()

**Dependencies**
- matplotlib.patches
- matplotlib.path
- matplotlib.offsetbox
- matplotlib.image
- drawing/styles.py
- drawing/canvas.py

**Used By**
- drawing/shapes.py
- drawing/arrows.py
- drawing/labels.py
- drawing/dimensions.py
- renderers/diagram_renderer.py
- renderers/graph_renderer.py

### drawing/shapes.py ✅
**Status:** Locked

**Purpose**
- Provides reusable high-level shapes built on top of DrawingPrimitives.
- Encapsulates common geometry, flowchart, UI, symbol, and annotation shapes.
- Ensures higher-level renderers never construct polygon geometry manually.
- Reuses common helpers for rotation, labels, and polygon generation.

**Contains**

#### Basic Shapes
- rectangle()
- rounded_rectangle()
- square()
- circle()
- ellipse()
- triangle()
- right_triangle()

#### Polygon Shapes
- diamond()
- parallelogram()
- trapezoid()
- regular_polygon()
- pentagon()
- hexagon()
- octagon()

#### Flowchart Shapes
- process()
- decision()
- data()
- document()
- manual_input()
- database()
- stored_data()

#### UI & Diagram Shapes
- folder()
- file()
- note()
- cloud()
- speech_bubble()
- thought_bubble()
- banner()
- flag()

#### Symbols
- star()
- heart()
- gear()
- cross()
- plus()
- minus()
- check()
- x_mark()
- target()

#### Math Helpers
- brace()
- bracket()
- angle_marker()
- coordinate_marker()
- measurement_box()

#### Utility Methods
- rotate_shape()
- scale_shape()
- bounding_box()
- label_at_center()
- label_at()

#### Internal Helpers
- _resolve_style()
- _validate_dimension()
- _validate_point()
- _rectangle_points()
- _center()
- _rotate_point()
- _rotate_points()
- _draw_polygon()
- _draw_label()
- _regular_polygon()

**Dependencies**
- math
- drawing/primitives.py
- drawing/styles.py

**Used By**
- renderers/diagram_renderer.py
- diagrams/geometry.py
- diagrams/flowchart.py
- diagrams/tree.py
- diagrams/network.py
- diagrams/biology.py
- diagrams/chemistry.py
- diagrams/physics.py
- diagrams/computer.py

# drawing/arrows.py

## Status

**Status:** Locked ✅

---

## Purpose

Provides reusable arrow and connector drawing primitives for the rendering
engine.

This module is responsible only for drawing arrows and connectors.
It does not perform automatic routing, automatic layout, or diagram generation.

It serves as the common arrow layer for all higher-level diagram renderers.

---

## Responsibilities

- Draw straight arrows
- Draw curved arrows
- Draw decorative arrows
- Draw flowchart connectors
- Draw arrow labels
- Draw standalone arrowheads
- Calculate connection points
- Provide reusable geometry helper methods

---

## Public API

### Basic Arrows

- line_arrow()
- double_arrow()
- bidirectional_arrow()
- open_arrow()
- filled_arrow()
- thin_arrow()

---

### Curved Arrows

- curved_arrow()
- arc_arrow()
- circular_arrow()
- loop_arrow()
- self_loop()

---

### Flowchart Connectors

- orthogonal_connector()
- elbow_connector()
- step_connector()
- tree_connector()
- decision_connector()

---

### Decorative Arrows

- dashed_arrow()
- dotted_arrow()
- wavy_arrow()
- zigzag_arrow()
- lightning_arrow()

---

### Utility Methods

- arrow_label()
- arrowhead()
- arrow_midpoint()
- connection_point()

---

## Internal Helpers

These helpers are implementation details and are not considered part of the
public API.

- _resolve_style()
- _distance()
- _direction()
- _angle()
- _midpoint()
- _offset_point()
- _trim_line()
- _arrow_endpoints()
- _perpendicular()
- _scale_vector()
- _add_vectors()
- _subtract_vectors()

---

## Supported Connection Shapes

connection_point() currently supports:

- rectangle
- circle
- ellipse
- diamond

Additional shapes may be added without changing the public API.

---

## Supported Tree Orientations

tree_connector() currently supports:

- vertical
- horizontal

Future versions may introduce radial and freeform trees.

---

## Decorative Arrow Features

Decorative arrows support endpoint trimming using:

- start_padding
- end_padding

This keeps decorative arrows consistent with all other arrow types.

---

## Dependencies

Requires

- math
- matplotlib.patches
- drawing.styles

Uses

- DrawingStyle
- DEFAULT_STYLE

Requires

- DrawingCanvas.get_axis()

---

## Design Goals

- Lightweight
- Stateless
- Reusable
- Consistent styling
- Minimal dependencies
- Easy extension
- Shape-independent
- Renderer-independent

---

## Design Decisions

### Open Arrow

Open arrows are manually constructed using line segments instead of relying on
Matplotlib ArrowStyle.

Reason:

Matplotlib does not provide a consistent open-arrow implementation across
versions.

---

### Connection Points

Connection point calculation is centralized inside this module.

Higher-level diagram modules should never calculate shape edge positions
themselves.

---

### Arrowheads

Standalone arrowheads automatically scale using

- mutation_scale
- line width

instead of fixed coordinate distances.

---

### Endpoint Trimming

Whenever applicable, arrows trim both endpoints before rendering to avoid
drawing inside connected shapes.

---

## Known Limitations

Current implementation does **not** include:

- Automatic path routing
- Obstacle avoidance
- Manhattan routing
- Orthogonal optimization
- Bezier connector routing
- Multi-segment smart routing
- Shape intersection detection
- Automatic connector attachment

These are intentionally left for higher-level routing modules.

---

## Future Enhancements

Potential future additions include:

- UML aggregation arrows
- UML composition arrows
- ER diagram arrows
- Crow's-foot notation
- Network routing
- Bezier connectors
- Smart obstacle avoidance
- Multi-arrow routing
- Dynamic arrowhead styles
- Animated arrows

---

## Used By

This module is intended to be reused by:

- renderers/diagram_renderer.py
- diagrams/flowchart.py
- diagrams/tree.py
- diagrams/network.py
- diagrams/biology.py
- diagrams/chemistry.py
- diagrams/physics.py
- diagrams/computer.py

---

## Notes

This module provides primitive arrow drawing only.

Diagram semantics, automatic layout, routing, collision detection, and graph
algorithms belong to higher-level diagram modules.

This file should remain focused on reusable drawing operations and simple
geometry.

---

# drawing/labels.py

## Status

**Status:** Locked ✅

---

## Purpose

Provides reusable text rendering, annotation, and label utilities for the
drawing engine.

This module is responsible only for drawing and positioning text.

It does not perform automatic diagram layout, routing, shape generation, or
rendering decisions.

It serves as the common text layer used by higher-level renderers and diagram
modules.

---

## Responsibilities

- Draw plain text
- Draw multiline text
- Draw rotated text
- Draw labels inside shapes
- Draw annotation labels
- Draw connector labels
- Draw boxed and highlighted labels
- Measure text dimensions
- Provide reusable text layout helpers

---

## Public API

### Basic Labels

- text()
- centered_text()
- left_text()
- right_text()
- top_text()
- bottom_text()
- rotated_text()
- vertical_text()
- multiline_text()

---

### Shape Labels

- rectangle_label()
- circle_label()
- ellipse_label()
- polygon_label()
- diamond_label()
- auto_center_label()
- padded_label()

---

### Annotation Labels

- callout()
- caption()
- note()
- tooltip()
- balloon_label()
- speech_annotation()
- leader_line_label()

---

### Connector Labels

- arrow_label()
- edge_label()
- curved_edge_label()
- midpoint_label()
- start_label()
- end_label()
- path_label()

---

### Background Labels

- boxed_text()
- rounded_box_label()
- highlight_label()
- filled_label()
- outline_label()
- badge()
- tag()

---

### Smart Layout

- auto_font_scale()
- wrap_text()
- clip_text()
- handle_overflow()
- bounding_box()
- avoid_collision()
- auto_center()

---

### Utility Methods

- rotation_radians()
- normalize_rotation()
- is_vertical_rotation()
- baseline_offset()
- text_baseline()
- apply_margin()
- inset_bounds()
- anchor_point()
- bounding_rectangle()

---

## Internal Helpers

These helpers are implementation details and are not considered part of the
public API.

- _resolve_style()
- _font_properties()
- _measure_text()
- _horizontal_alignment()
- _vertical_alignment()
- _anchor()
- _offset()
- _center_of_bounds()
- _inside_padding()
- _midpoint()

---

## Dependencies

Requires

- copy.replace
- functools.lru_cache
- textwrap
- matplotlib.textpath
- matplotlib.font_manager
- drawing.styles

Uses

- DrawingStyle
- DEFAULT_STYLE
- LABEL_STYLE

Requires

- DrawingCanvas.get_axis()
- DrawingCanvas.get_figure()

---

## Design Goals

- Lightweight
- Stateless
- Reusable
- Consistent styling
- Minimal dependencies
- Renderer-independent
- Shape-independent
- Easily extensible

---

## Design Decisions

### Text Measurement

Text size calculations are centralized using TextPath and cached with
LRU caching to reduce repeated font metric calculations.

---

### Style Resolution

All public drawing methods resolve styles through a common helper,
allowing temporary overrides without modifying immutable DrawingStyle
instances.

---

### Background Labels

Background label variants rely on Matplotlib's built-in bounding box
styles rather than custom patches to keep the implementation compact
and version compatible.

---

### Smart Layout

Wrapping, clipping, scaling and collision avoidance are intentionally
simple helper utilities.

Higher-level renderers remain responsible for full automatic layout.

---

## Known Limitations

Current implementation does **not** include:

- Automatic text routing
- Polygon-aware text fitting
- True font metric rendering
- Rich text formatting
- HTML or Markdown rendering
- Automatic paragraph layout
- Shape-aware clipping
- Global collision resolution
- RTL text support
- Text justification

These responsibilities belong to future renderer or layout modules.

---

## Future Enhancements

Potential future additions include:

- Rich text rendering
- Markdown support
- HTML labels
- Curved text
- Path-following text
- Shape-aware wrapping
- Polygon clipping
- Automatic label placement
- Force-directed collision resolution
- Multi-language typography

---

## Used By

This module is intended to be reused by:

- renderers/diagram_renderer.py
- renderers/graph_renderer.py
- diagrams/geometry.py
- diagrams/flowchart.py
- diagrams/tree.py
- diagrams/network.py
- diagrams/biology.py
- diagrams/chemistry.py
- diagrams/physics.py
- diagrams/computer.py

---

## Notes

This module provides reusable text drawing utilities only.

Diagram semantics, automatic layout, routing decisions, collision
resolution across diagrams, and typography policies belong to
higher-level renderer modules.

This file should remain focused on reusable text rendering and helper
utilities.

---

## Future Checkpoints

### Checkpoint 1
- Foundation complete.

### Checkpoint 2
- Text rendering complete.

### Checkpoint 3
- Diagram engine complete.

### Checkpoint 4
- Graph engine complete.

### Checkpoint 5
- PPT engine complete.

### Checkpoint 6
- GUI complete.

---

## Notes

- Text measurement uses cached font metrics for improved performance.
- Public APIs remain renderer-independent.
- Style overrides preserve immutable DrawingStyle instances.
- Compatible with DrawingCanvas, DrawingShapes and DrawingArrows.

---

# drawing/dimensions.py

## Status

**Status:** Locked ✅

---

## Purpose

Provides reusable engineering dimensioning, measurement, and annotation
utilities for the drawing engine.

This module is responsible for creating CAD-style dimensions using the
lower-level drawing modules.

It does not perform automatic layout, collision detection, or diagram
generation.

It serves as the common dimension layer used by higher-level renderers and
diagram modules.

---

## Responsibilities

- Draw linear dimensions
- Draw aligned dimensions
- Draw angular dimensions
- Draw radial dimensions
- Draw leader annotations
- Draw engineering helper lines
- Calculate reusable geometry
- Format measurement values

---

## Public API

### Linear Dimensions

- horizontal_dimension()
- vertical_dimension()
- aligned_dimension()
- linear_measurement()

---

### Parallel Dimensions

- baseline_dimension()
- continuous_dimension()

---

### Angular Dimensions

- angle_dimension()
- arc_dimension()
- radius_dimension()
- diameter_dimension()
- chord_dimension()
- sector_dimension()

---

### Leader Dimensions

- leader_line()
- multi_leader()
- coordinate_dimension()
- elevation_marker()
- datum_marker()
- reference_dimension()

---

### Engineering Helpers

- extension_line()
- witness_line()
- tick_mark()
- terminator()
- center_mark()
- center_line()
- hidden_dimension_line()
- construction_line()

---

### Utility Methods

- auto_text_placement()
- format_units()
- format_precision()
- distance()
- midpoint()
- offset_point()
- offset_line()
- arrow_direction()

---

## Internal Helpers

These helpers are implementation details and are not considered part of the
public API.

### Style Helpers

- _resolve_style()
- _resolve_label_style()
- _copy_style()
- _copy_label_style()
- _dimension_style()
- _label_style()

### Geometry Helpers

- _distance()
- _direction()
- _perpendicular()
- _angle()
- _midpoint()
- _line_length()
- _normalize()
- _point_along()
- _rotate_vector()
- _project_point()

### Offset Helpers

- _offset_point()
- _offset_line()
- _extend_line()
- _trim_line()

### Arrow Helpers

- _arrow_endpoints()
- _inside_dimension()
- _arrow_direction()
- _extension_line()

### Label Helpers

- _label_position()
- _label_rotation()
- _label_anchor()
- _text_offset()
- _dimension_text_position()
- _draw_dimension_text()

### Dimension Helpers

- _dimension_line()
- _offset_dimension_lines()

### Arc Helpers

- _arc_angles()
- _arc_midpoint()
- _draw_arc()
- _draw_arc_arrows()

### Leader Helpers

- _leader_path()
- _leader_label_position()

---

## Dependencies

Requires

- math
- copy.replace

Uses

- DrawingPrimitives
- DrawingArrows
- DrawingLabels
- DrawingShapes

Uses

- DrawingStyle
- DEFAULT_STYLE
- LABEL_STYLE

Requires

- DrawingCanvas.get_axis()
- DrawingCanvas.get_figure()

---

## Design Goals

- Lightweight
- Stateless
- Reusable
- Consistent styling
- Geometry-driven
- Renderer-independent
- CAD-inspired
- Easily extensible

---

## Design Decisions

### Geometry Reuse

All geometric calculations are centralized into helper methods.

Higher-level dimension methods reuse these helpers instead of duplicating
geometry calculations.

---

### Style Resolution

Every public drawing method resolves styles through shared helper methods,
allowing temporary overrides while preserving immutable DrawingStyle
instances.

---

### Layered Design

Dimensions are composed using DrawingPrimitives, DrawingArrows and
DrawingLabels instead of interacting with Matplotlib directly.

---

### Public Utility Methods

Frequently used helper operations such as distance calculation, midpoint,
offsets and formatting are exposed through a small public utility API while
keeping implementation helpers private.

---

## Known Limitations

Current implementation does **not** include:

- Automatic dimension placement
- Collision avoidance
- Automatic witness line trimming
- Smart text repositioning
- Associative dimensions
- Parametric constraints
- GD&T annotations
- Welding symbols
- Surface finish symbols
- Automatic tolerance generation

These responsibilities belong to higher-level layout or CAD modules.

---

## Future Enhancements

Potential future additions include:

- Geometric Dimensioning & Tolerancing (GD&T)
- Weld symbols
- Surface finish symbols
- Fit and tolerance annotations
- Chain dimension optimization
- Automatic dimension spacing
- Collision-free dimension layout
- Smart leader routing
- Associative dimensions
- Parametric constraints

---

## Used By

This module is intended to be reused by:

- renderers/diagram_renderer.py
- diagrams/geometry.py
- diagrams/physics.py
- diagrams/computer.py
- diagrams/biology.py
- diagrams/chemistry.py
- diagrams/network.py
- diagrams/flowchart.py

---

## Notes

This module provides reusable engineering dimension drawing utilities only.

Diagram semantics, automatic layout, collision avoidance, constraint solving,
and CAD-specific intelligence belong to higher-level renderer or layout
modules.

This file should remain focused on reusable dimensioning operations and
geometry helpers.

---

# drawing/transforms.py ✅

**Status:** Locked

---

## Purpose

Provides reusable geometric transformation and geometry helper utilities for
the drawing engine.

This module is responsible for transforming points and collections of points.

It does not perform any drawing, rendering, diagram generation, or automatic
layout.

It serves as the common transformation layer used by higher-level drawing,
diagram and renderer modules.

---

## Responsibilities

- Translate points
- Rotate geometry
- Scale geometry
- Reflect geometry
- Shear geometry
- Apply affine transformations
- Perform matrix operations
- Compute bounding geometry
- Provide reusable geometry helper methods

---

## Public API

### Translation

- translate_point()
- translate_points()
- translate_x()
- translate_y()
- translate_about()

---

### Rotation

- rotate_point()
- rotate_points()

---

### Scaling

- scale_point()
- scale_points()

---

### Reflection

- reflect_point()
- reflect_points()

---

### Shearing

- shear_point()
- shear_points()

---

### Matrix Operations

- matrix_multiply()
- compose_matrices()
- identity_matrix()
- apply_matrix()
- apply_matrix_points()

---

### Bounding Helpers

- bounding_box()
- bounding_size()
- bounding_center()

---

### Geometry Utilities

- centroid()
- polygon_area()
- is_clockwise()

---

## Internal Helpers

These helpers are implementation details and are not considered part of the
public API.

### Validation Helpers

- _validate_point()
- _validate_points()
- _validate_center()

### Geometry Helpers

- _distance()
- _midpoint()
- _direction()
- _normalize()
- _angle()
- _copy_points()

---

## Dependencies

Requires

- math
- copy.deepcopy
- numbers.Real

Uses

- Standard Python geometry utilities

Requires

- No Matplotlib dependencies

---

## Design Goals

- Lightweight
- Stateless
- Reusable
- Geometry-driven
- Renderer-independent
- Drawing-independent
- Minimal dependencies
- Easily extensible

---

## Design Decisions

### Pure Geometry

Every transformation operates only on coordinates.

This module never performs drawing operations.

---

### Immutable Operations

Transformation methods return newly transformed coordinates.

Input points are never modified.

---

### Matrix-Based Transformations

Affine transformations are implemented using homogeneous 3×3 matrices.

This allows translation, rotation, scaling and shearing to be composed into
larger transformations.

---

### Geometry Reuse

Common geometric calculations are centralized into reusable helper methods.

Higher-level drawing modules should reuse these helpers instead of duplicating
geometry logic.

---

### Bounding Utilities

Bounding box calculations are intentionally lightweight and axis-aligned.

Rotated or oriented bounding boxes belong to higher-level geometry modules.

---

## Known Limitations

Current implementation does **not** include:

- 3D transformations
- Perspective transformations
- Projective transformations
- Matrix inversion
- Matrix determinant calculation
- Convex hull generation
- Polygon clipping
- Line intersection testing
- Bezier transformations
- Shape boolean operations

These responsibilities belong to future geometry utilities.

---

## Future Enhancements

Potential future additions include:

- Matrix inversion
- Transformation pipelines
- Transformation stacks
- Convex hull algorithms
- Polygon simplification
- Polygon clipping
- Line intersection helpers
- Oriented bounding boxes
- Minimum-area bounding rectangles
- 3D transformation support

---

## Used By

This module is intended to be reused by:

- drawing/shapes.py
- drawing/arrows.py
- drawing/dimensions.py
- drawing/geometry_utils.py
- renderers/diagram_renderer.py
- renderers/graph_renderer.py
- diagrams/geometry.py
- diagrams/flowchart.py
- diagrams/network.py
- diagrams/biology.py
- diagrams/chemistry.py
- diagrams/physics.py
- diagrams/computer.py

---

## Notes

This module provides reusable geometry and transformation utilities only.

Drawing operations, rendering decisions, automatic layout, collision detection,
routing and diagram semantics belong to higher-level drawing and renderer
modules.

This file should remain focused on reusable geometric transformations and
supporting helper utilities.

---

# drawing/geometry_utils.py

## Status

**Status:** Locked ✅

---

## Purpose

Provides reusable computational geometry and geometry helper utilities for the
drawing engine.

This module is responsible only for geometric calculations and geometric
relationships.

It performs no drawing, rendering, layout, or diagram generation.

It serves as the common geometry layer used by drawing modules, renderers,
graphs and diagram generators.

---

## Responsibilities

- Validate geometry objects
- Perform vector mathematics
- Compute distances and angles
- Work with infinite lines and finite segments
- Compute projections
- Handle circle geometry
- Perform polygon computations
- Compute centroids and areas
- Perform bounding-box operations
- Test geometric relationships
- Compute convex hulls
- Provide reusable geometry helper methods

---

## Public API

### Validation

- is_close()
- is_zero()
- validate_point()
- validate_points()

---

### Point Helpers

- point()
- x()
- y()
- midpoint()
- translate_point()
- scale_point()
- points_equal()

---

### Vector Helpers

- vector()
- vector_from_xy()
- add_vectors()
- subtract_vectors()
- negate_vector()
- scale_vector()
- dot()
- cross()
- magnitude()
- magnitude_squared()
- normalize()

---

### Distance Helpers

- distance()
- distance_squared()
- manhattan_distance()

---

### Angle Helpers

- angle_of_vector()
- angle_between_vectors()
- angle_between_points()

---

### Direction Helpers

- direction()
- perpendicular_left()
- perpendicular_right()

---

### Projection Helpers

- scalar_projection()
- vector_projection()
- rejection()

---

### Line Helpers

- line_from_points()
- line_coefficients()
- line_slope()
- line_direction()
- normalized_direction()
- line_length()
- point_at_parameter()
- parameter_on_line()
- closest_point_on_line()
- distance_to_line()
- are_parallel()
- parallel_line()
- are_perpendicular()
- perpendicular_line()
- are_collinear()
- point_on_line()
- point_on_segment()
- line_intersection()
- line_relationship()
- lines_intersect()
- intersection_exists()
- is_horizontal()
- is_vertical()

---

### Segment Helpers

- segment_length()
- segment_midpoint()
- closest_point_on_segment()
- distance_to_segment()
- segments_intersect()
- segment_intersection()
- distance_between_segments()

---

### Circle Helpers

- circle()
- circle_center()
- circle_radius()
- circle_diameter()
- circle_circumference()
- circle_area()
- point_in_circle()
- point_on_circle()
- circle_from_diameter()
- circle_bounding_box()

---

### Bounding Box Helpers

- bounding_box()
- bounding_box_width()
- bounding_box_height()
- bounding_box_center()
- point_in_bounding_box()
- boxes_intersect()
- expand_bounding_box()

---

### Polygon Helpers

- polygon()
- polygon_vertex_count()
- polygon_edges()
- polygon_perimeter()
- signed_polygon_area()
- polygon_area()
- polygon_centroid()
- polygon_bounding_box()
- point_in_polygon()
- is_clockwise()
- is_counter_clockwise()
- is_convex_polygon()
- convex_hull()

---

### Polygon Transformations

- translate_polygon()
- scale_polygon()
- rotate_polygon()

---

### Miscellaneous Utilities

- lerp()
- clamp()
- almost_equal_points()

---

## Internal Helpers

These helpers are implementation details and are not considered part of the
public API.

- _orientation()

Additional private helpers may be added in future versions without changing
the public API.

---

## Dependencies

Requires

- math
- typing
- enum

Uses

- Standard Python geometry utilities only

Requires

- No Matplotlib dependencies
- No PowerPoint dependencies

---

## Design Goals

- Lightweight
- Stateless
- Reusable
- Pure geometry
- Renderer-independent
- Drawing-independent
- Minimal dependencies
- Numerically stable
- Easily extensible

---

## Design Decisions

### Pure Geometry

Every function operates only on geometric data.

No drawing, rendering or layout operations are performed.

---

### Immutable Operations

Geometry helpers never modify input objects.

Every transformation returns newly computed geometry.

---

### Consistent Precision

Floating-point comparisons use a shared EPSILON tolerance to improve numerical
stability.

---

### Layer Separation

Geometry calculations are centralized here so higher-level drawing modules
avoid duplicating mathematical logic.

---

### Shared Utilities

Frequently used operations such as distance, projections, intersections,
centroids and convex hull computation are implemented once and reused
throughout the rendering engine.

---

## Known Limitations

Current implementation does **not** include:

- Boolean polygon operations
- Polygon clipping
- Bezier curve intersections
- Spline geometry
- Voronoi diagrams
- Delaunay triangulation
- Oriented bounding boxes
- Spatial indexing
- 3D geometry
- Mesh processing

These responsibilities belong to future geometry or computational geometry
modules.

---

## Future Enhancements

Potential future additions include:

- Convex polygon intersection
- Polygon clipping algorithms
- Bezier utilities
- Arc intersection helpers
- Line-circle intersections
- Circle-circle intersections
- Polygon simplification
- Minimum-area bounding rectangles
- KD-tree spatial searches
- R-tree spatial indexing
- 3D geometry helpers

---

## Used By

This module is intended to be reused by:

- drawing/shapes.py
- drawing/arrows.py
- drawing/dimensions.py
- drawing/transforms.py
- drawing/layout.py
- renderers/diagram_renderer.py
- renderers/graph_renderer.py
- diagrams/geometry.py
- diagrams/flowchart.py
- diagrams/tree.py
- diagrams/network.py
- diagrams/biology.py
- diagrams/chemistry.py
- diagrams/physics.py
- diagrams/computer.py

---

## Notes

This module provides reusable computational geometry utilities only.

Rendering, styling, layout, collision resolution, routing and diagram
semantics belong to higher-level drawing and renderer modules.

This file should remain focused on reusable mathematical operations,
geometric relationships and computational geometry helpers.

---

## Future Checkpoints

### Checkpoint 1
- Core geometry helpers complete.

### Checkpoint 2
- Line and segment utilities complete.

### Checkpoint 3
- Circle and polygon utilities complete.

### Checkpoint 4
- Diagram engine integration complete.

### Checkpoint 5
- Graph engine integration complete.

### Checkpoint 6
- PPT engine complete.

---

## Notes

- Pure Python implementation with no rendering dependencies.
- Floating-point comparisons use shared EPSILON tolerance.
- Computational geometry algorithms remain renderer-independent.
- Compatible with DrawingShapes, DrawingArrows, DrawingDimensions and DrawingTransforms.

---

# drawing/layout.py ✅

**Status:** Locked

---

## Purpose

Provides reusable layout algorithms and positioning utilities for the drawing
engine.

This module is responsible for computing positions of objects for diagrams,
graphs, trees, grids and general layouts.

It performs no drawing or rendering.

It serves as the common layout engine used by higher-level renderers and
diagram generators.

---

## Responsibilities

- Validate layout inputs
- Compute spacing
- Compute alignment
- Compute bounding boxes
- Arrange objects into common layouts
- Position graph nodes
- Position tree structures
- Position circular diagrams
- Provide reusable layout utilities

---

## Public API

### Validation Helpers

- _validate_points()
- _validate_sizes()
- _validate_spacing()

---

### Spacing Helpers

- horizontal_gap()
- vertical_gap()
- total_horizontal_spacing()
- total_vertical_spacing()

---

### Alignment Helpers

- align_left()
- align_right()
- align_top()
- align_bottom()
- align_center_x()
- align_center_y()
- align_center()

---

### Bounding Box Helpers

- bounding_box()
- bounding_size()
- bounding_center()
- expand_bounding_box()

---

### Linear Layouts

- horizontal_layout()
- vertical_layout()
- row_layout()
- column_layout()
- even_spacing()
- packed_spacing()
- distributed_spacing()

---

### Grid Layouts

- grid_layout()
- matrix_layout()
- fixed_columns()
- fixed_rows()
- auto_grid()
- cell_position()

---

### Circular Layouts

- circle_layout()
- radial_layout()
- ring_layout()
- spiral_layout()
- arc_layout()

---

### Tree Layouts

- vertical_tree()
- horizontal_tree()
- balanced_tree()
- binary_tree_positions()
- mind_map_layout()

---

### Graph Layouts

- random_layout()
- force_directed_layout()
- layered_layout()
- hierarchical_layout()
- network_layout()

---

### Utility Helpers

- auto_spacing()
- rectangles_overlap()
- center_positions()
- scale_to_fit()
- apply_margin()

---

## Internal Helpers

Validation helpers are intentionally private.

- _validate_points()
- _validate_sizes()
- _validate_spacing()

Additional helper methods may be added in future versions without changing
the public API.

---

## Dependencies

Requires

- math
- random
- math.inf

Uses

- Standard Python geometry and layout calculations only.

Requires

- No Matplotlib dependencies
- No PowerPoint dependencies

---

## Design Goals

- Lightweight
- Stateless
- Reusable
- Renderer-independent
- Drawing-independent
- Minimal dependencies
- Easily extensible
- Deterministic layouts

---

## Design Decisions

### Layout Only

This module computes positions only.

It never draws shapes, connectors, labels or diagrams.

---

### Layer Separation

Layout algorithms are centralized here so renderers and diagram generators
never duplicate positioning logic.

---

### Generic Algorithms

Layouts operate on coordinates and sizes instead of specific diagram objects,
making them reusable across the entire rendering engine.

---

### Reusable Building Blocks

Complex layouts are composed from simpler algorithms whenever possible.
Examples include:

- row_layout() using horizontal_layout()
- column_layout() using vertical_layout()
- matrix_layout() using grid_layout()
- radial_layout() using circle_layout()
- ring_layout() using circle_layout()
- balanced_tree() using vertical_tree()
- hierarchical_layout() using layered_layout()
- network_layout() using random_layout() and force_directed_layout()

---

## Known Limitations

Current implementation does **not** include:

- DAG layout algorithms
- Sugiyama graph layout
- Orthogonal graph routing
- Edge crossing minimization
- Automatic connector routing
- Obstacle avoidance
- Constraint-based layouts
- Hypergraph layouts
- UML-specific layouts
- Animated layouts

These responsibilities belong to future diagram or routing modules.

---

## Future Enhancements

Potential future additions include:

- Sugiyama layered graphs
- Radial trees
- Treemap layouts
- Sankey layouts
- Timeline layouts
- Swimlane layouts
- UML layouts
- ER diagram layouts
- Smart collision resolution
- Automatic edge routing

---

## Used By

This module is intended to be reused by:

- renderers/diagram_renderer.py
- renderers/graph_renderer.py
- diagrams/geometry.py
- diagrams/flowchart.py
- diagrams/tree.py
- diagrams/network.py
- diagrams/biology.py
- diagrams/chemistry.py
- diagrams/physics.py
- diagrams/computer.py

---

## Notes

This module provides reusable layout algorithms only.

Rendering, styling, routing, collision resolution between rendered objects,
and diagram semantics belong to higher-level renderer and diagram modules.

This file should remain focused on reusable positioning algorithms and layout
utilities.

---

## Future Checkpoints

### Checkpoint 1
- Foundation complete.

### Checkpoint 2
- Drawing engine complete.

### Checkpoint 3
- Diagram engine complete.

### Checkpoint 4
- Graph engine complete.

### Checkpoint 5
- PPT engine complete.

### Checkpoint 6
- GUI complete.

---


## Notes