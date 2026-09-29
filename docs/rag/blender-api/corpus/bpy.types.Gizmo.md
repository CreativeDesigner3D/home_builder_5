<!-- source: Blender Python API reference 5.2 / bpy.types.Gizmo.html -->

<a id="gizmo-bpy-struct"></a>

# Gizmo(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Gizmo"></a>

### class bpy.types.Gizmo(bpy_struct)

Collection of gizmos

<a id="bpy.types.Gizmo.alpha"></a>

#### bpy.types.Gizmo.alpha

(in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Gizmo.alpha_highlight"></a>

#### bpy.types.Gizmo.alpha_highlight

(in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Gizmo.bl_idname"></a>

#### bpy.types.Gizmo.bl_idname

(default “”, never None)

**Type:**

str

<a id="bpy.types.Gizmo.color"></a>

#### bpy.types.Gizmo.color

(array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.Gizmo.color_highlight"></a>

#### bpy.types.Gizmo.color_highlight

(array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.Gizmo.group"></a>

#### bpy.types.Gizmo.group

Gizmo group this gizmo is a member of (readonly)

**Type:**

[`GizmoGroup`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup "bpy.types.GizmoGroup") | None

<a id="bpy.types.Gizmo.hide"></a>

#### bpy.types.Gizmo.hide

(default False)

**Type:**

bool

<a id="bpy.types.Gizmo.hide_keymap"></a>

#### bpy.types.Gizmo.hide_keymap

Ignore the key-map for this gizmo (default False)

**Type:**

bool

<a id="bpy.types.Gizmo.hide_select"></a>

#### bpy.types.Gizmo.hide_select

(default False)

**Type:**

bool

<a id="bpy.types.Gizmo.is_highlight"></a>

#### bpy.types.Gizmo.is_highlight

(default False, readonly)

**Type:**

bool

<a id="bpy.types.Gizmo.is_modal"></a>

#### bpy.types.Gizmo.is_modal

(default False, readonly)

**Type:**

bool

<a id="bpy.types.Gizmo.line_width"></a>

#### bpy.types.Gizmo.line_width

(in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Gizmo.matrix_basis"></a>

#### bpy.types.Gizmo.matrix_basis

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Gizmo.matrix_offset"></a>

#### bpy.types.Gizmo.matrix_offset

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Gizmo.matrix_space"></a>

#### bpy.types.Gizmo.matrix_space

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Gizmo.matrix_world"></a>

#### bpy.types.Gizmo.matrix_world

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), readonly)

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Gizmo.properties"></a>

#### bpy.types.Gizmo.properties

(readonly, never None)

**Type:**

[`GizmoProperties`](bpy.types.GizmoProperties.md#bpy.types.GizmoProperties "bpy.types.GizmoProperties")

<a id="bpy.types.Gizmo.scale_basis"></a>

#### bpy.types.Gizmo.scale_basis

(in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Gizmo.select"></a>

#### bpy.types.Gizmo.select

(default False)

**Type:**

bool

<a id="bpy.types.Gizmo.select_bias"></a>

#### bpy.types.Gizmo.select_bias

Depth bias used for selection (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Gizmo.use_draw_hover"></a>

#### bpy.types.Gizmo.use_draw_hover

(default False)

**Type:**

bool

<a id="bpy.types.Gizmo.use_draw_modal"></a>

#### bpy.types.Gizmo.use_draw_modal

Show while dragging (default False)

**Type:**

bool

<a id="bpy.types.Gizmo.use_draw_offset_scale"></a>

#### bpy.types.Gizmo.use_draw_offset_scale

Scale the offset matrix (use to apply screen-space offset) (default False)

**Type:**

bool

<a id="bpy.types.Gizmo.use_draw_scale"></a>

#### bpy.types.Gizmo.use_draw_scale

Use scale when calculating the matrix (default True)

**Type:**

bool

<a id="bpy.types.Gizmo.use_draw_value"></a>

#### bpy.types.Gizmo.use_draw_value

Show an indicator for the current value while dragging (default False)

**Type:**

bool

<a id="bpy.types.Gizmo.use_event_handle_all"></a>

#### bpy.types.Gizmo.use_event_handle_all

When highlighted, do not pass events through to be handled by other keymaps (default False)

**Type:**

bool

<a id="bpy.types.Gizmo.use_grab_cursor"></a>

#### bpy.types.Gizmo.use_grab_cursor

(default False)

**Type:**

bool

<a id="bpy.types.Gizmo.use_operator_tool_properties"></a>

#### bpy.types.Gizmo.use_operator_tool_properties

Merge active tool properties on activation (does not overwrite existing) (default False)

**Type:**

bool

<a id="bpy.types.Gizmo.use_select_background"></a>

#### bpy.types.Gizmo.use_select_background

Don’t write into the depth buffer (default False)

**Type:**

bool

<a id="bpy.types.Gizmo.use_tooltip"></a>

#### bpy.types.Gizmo.use_tooltip

Use tooltips when hovering over this gizmo (default True)

**Type:**

bool

<a id="bpy.types.Gizmo.use_undo"></a>

#### bpy.types.Gizmo.use_undo

Push an undo step after each use of the gizmo (default False)

**Type:**

bool

<a id="bpy.types.Gizmo.draw"></a>

#### bpy.types.Gizmo.draw(context)

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.Gizmo.draw_select"></a>

#### bpy.types.Gizmo.draw_select(context, *, select_id=0)

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **select_id** (int) – (in [0, inf], optional)

<a id="bpy.types.Gizmo.test_select"></a>

#### bpy.types.Gizmo.test_select(context, location)

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **location** (Sequence[int]) – Location, Region coordinates (array of 2 items, in [-inf, inf], never None)

**Returns:**

Use -1 to skip this gizmo (in [-1, inf])

**Return type:**

int

<a id="bpy.types.Gizmo.modal"></a>

#### bpy.types.Gizmo.modal(context, event, tweak)

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **event** ([`Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event") | None) – (never None)
- **tweak** (set[Literal['PRECISE', 'SNAP']]) – Tweak

**Returns:**

result

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.types.Gizmo.setup"></a>

#### bpy.types.Gizmo.setup()

<a id="bpy.types.Gizmo.invoke"></a>

#### bpy.types.Gizmo.invoke(context, event)

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **event** ([`Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event") | None) – (never None)

**Returns:**

result

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.types.Gizmo.exit"></a>

#### bpy.types.Gizmo.exit(context, cancel)

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **cancel** (bool) – Cancel, otherwise confirm

<a id="bpy.types.Gizmo.select_refresh"></a>

#### bpy.types.Gizmo.select_refresh()

<a id="bpy.types.Gizmo.draw_preset_box"></a>

#### bpy.types.Gizmo.draw_preset_box(matrix, *, select_id=-1)

Draw a box

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The matrix to transform (multi-dimensional array of 4 * 4 items, in [-inf, inf])
- **select_id** (int) – ID to use when gizmo is selectable. Use -1 when not selecting., (in [-1, inf], optional)

<a id="bpy.types.Gizmo.draw_preset_arrow"></a>

#### bpy.types.Gizmo.draw_preset_arrow(matrix, *, axis='POS_Z', select_id=-1)

Draw a box

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The matrix to transform (multi-dimensional array of 4 * 4 items, in [-inf, inf])
- **axis** (Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]) – Arrow Orientation (optional)
- **select_id** (int) – ID to use when gizmo is selectable. Use -1 when not selecting., (in [-1, inf], optional)

<a id="bpy.types.Gizmo.draw_preset_circle"></a>

#### bpy.types.Gizmo.draw_preset_circle(matrix, *, axis='POS_Z', select_id=-1)

Draw a box

**Parameters:**

- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The matrix to transform (multi-dimensional array of 4 * 4 items, in [-inf, inf])
- **axis** (Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]) – Arrow Orientation (optional)
- **select_id** (int) – ID to use when gizmo is selectable. Use -1 when not selecting., (in [-1, inf], optional)

<a id="bpy.types.Gizmo.target_set_prop"></a>

#### bpy.types.Gizmo.target_set_prop(target, data, property, *, index=-1)

**Parameters:**

- **target** (str) – Target property (never None)
- **data** ([`AnyType`](bpy.types.AnyType.md#bpy.types.AnyType "bpy.types.AnyType") | None) – Data from which to take property (never None)
- **property** (str) – Identifier of property in data (never None)
- **index** (int) – (in [-1, inf], optional)

<a id="bpy.types.Gizmo.target_set_operator"></a>

#### bpy.types.Gizmo.target_set_operator(operator, *, index=0)

Operator to run when activating the gizmo (overrides property targets)

**Parameters:**

- **operator** (str) – Target operator (never None)
- **index** (int) – Part index, (in [0, 255], optional)

**Returns:**

Operator properties to fill in

**Return type:**

[`OperatorProperties`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties "bpy.types.OperatorProperties")

<a id="bpy.types.Gizmo.target_is_valid"></a>

#### bpy.types.Gizmo.target_is_valid(property)

**Parameters:**

**property** (str) – Property identifier (never None)

**Return type:**

bool

<a id="bpy.types.Gizmo.draw_custom_shape"></a>

#### bpy.types.Gizmo.draw_custom_shape(shape, *, matrix=None, select_id=None)

Draw a shape created form [`Gizmo.draw_custom_shape`](#bpy.types.Gizmo.draw_custom_shape "bpy.types.Gizmo.draw_custom_shape").

**Parameters:**

- **shape** (Any) – The cached shape to draw.
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | None) – 4x4 matrix, when not given [`Gizmo.matrix_world`](#bpy.types.Gizmo.matrix_world "bpy.types.Gizmo.matrix_world") is used.
- **select_id** (int | None) – The selection id.
  Only use when drawing within [`Gizmo.draw_select`](#bpy.types.Gizmo.draw_select "bpy.types.Gizmo.draw_select").

<a id="bpy.types.Gizmo.new_custom_shape"></a>

#### static bpy.types.Gizmo.new_custom_shape(type, verts)

Create a new shape that can be passed to [`Gizmo.draw_custom_shape`](#bpy.types.Gizmo.draw_custom_shape "bpy.types.Gizmo.draw_custom_shape").

**Parameters:**

- **type** (Literal['POINTS', 'LINES', 'TRIS', 'LINE_STRIP']) – The type of shape to create.
- **verts** (Sequence[Sequence[float]]) – Sequence of 2D or 3D coordinates.

**Returns:**

The newly created shape (the return type make change).

**Return type:**

Any

<a id="bpy.types.Gizmo.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Gizmo.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Gizmo.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Gizmo.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.Gizmo.target_get_range"></a>

#### bpy.types.Gizmo.target_get_range(target)

Get the range for this target property.

**Parameters:**

**target** (str) – Target property name.

**Returns:**

The range of this property (min, max).

**Return type:**

tuple[float, float]

<a id="bpy.types.Gizmo.target_get_value"></a>

#### bpy.types.Gizmo.target_get_value(target)

Get the value of this target property.

**Parameters:**

**target** (str) – Target property name.

**Returns:**

The value of the target property as a value or array based on the target type.

**Return type:**

float | tuple[float, …]

<a id="bpy.types.Gizmo.target_set_handler"></a>

#### bpy.types.Gizmo.target_set_handler(target, get, set, range=None)

Assigns callbacks to a gizmos property.

**Parameters:**

- **target** (str) – Target property name.
- **get** (Callable[[], float | Sequence[float]]) – Function that returns the value for this property (single value or sequence).
- **set** (Callable[[tuple[float, ...]], Any]) – Function that takes a single value argument and applies it.
- **range** (Callable[[], tuple[float, float]] | None) – Function that returns a (min, max) tuple for gizmos that use a range. The returned value is not used.

<a id="bpy.types.Gizmo.target_set_value"></a>

#### bpy.types.Gizmo.target_set_value(target)

Set the value of this target property.

**Parameters:**

**target** (str) – Target property name.

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - [`GizmoGroup.gizmos`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.gizmos "bpy.types.GizmoGroup.gizmos") - [`GizmoGroup.invoke_prepare`](bpy.types.GizmoGroup.md#bpy.types.GizmoGroup.invoke_prepare "bpy.types.GizmoGroup.invoke_prepare") | - [`Gizmos.new`](bpy.types.Gizmos.md#bpy.types.Gizmos.new "bpy.types.Gizmos.new") - [`Gizmos.remove`](bpy.types.Gizmos.md#bpy.types.Gizmos.remove "bpy.types.Gizmos.remove") |
