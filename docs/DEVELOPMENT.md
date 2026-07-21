# Generator PPT-X

## Project Status

### Overall Progress
- [x] config.py
- [x] drawing/styles.py
- [x] drawing/canvas.py
- [x] drawing/primitives.py
- [ ] drawing/shapes.py
- [ ] drawing/arrows.py
- [ ] drawing/labels.py
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