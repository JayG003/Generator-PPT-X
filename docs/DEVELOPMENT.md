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
- [ ] drawing/dimensions.py
- [ ] drawing/transforms.py
- [ ] drawing/geometry_utils.py
- [ ] drawing/layout.py
- [ ] renderers/diagram_renderer.py
- [ ] diagrams/geometry.py
- [ ] diagrams/flowchart.py
- [ ] diagrams/tree.py
- [ ] diagrams/network.py
- [ ] diagrams/biology.py
- [ ] diagrams/chemistry.py
- [ ] diagrams/physics.py
- [ ] diagrams/computer.py
- [ ] renderers/graph_renderer.py
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