<!-- source: Blender Python API reference 5.2 / bpy.types.WorkSpaceTool.html -->

<a id="workspacetool-bpy-struct"></a>

# WorkSpaceTool(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.WorkSpaceTool"></a>

### class bpy.types.WorkSpaceTool(bpy_struct)

<a id="bpy.types.WorkSpaceTool.brush_type"></a>

#### bpy.types.WorkSpaceTool.brush_type

If the tool uses brushes and is limited to a specific brush type, the identifier of the brush type (default `'DEFAULT'`, readonly)

**Type:**

Literal[‘DEFAULT’]

<a id="bpy.types.WorkSpaceTool.has_datablock"></a>

#### bpy.types.WorkSpaceTool.has_datablock

(default False, readonly)

**Type:**

bool

<a id="bpy.types.WorkSpaceTool.idname"></a>

#### bpy.types.WorkSpaceTool.idname

(default “”, never None)

**Type:**

str

<a id="bpy.types.WorkSpaceTool.idname_fallback"></a>

#### bpy.types.WorkSpaceTool.idname_fallback

(default “”, never None)

**Type:**

str

<a id="bpy.types.WorkSpaceTool.index"></a>

#### bpy.types.WorkSpaceTool.index

(in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.WorkSpaceTool.mode"></a>

#### bpy.types.WorkSpaceTool.mode

(default `'DEFAULT'`, readonly)

**Type:**

Literal[‘DEFAULT’]

<a id="bpy.types.WorkSpaceTool.space_type"></a>

#### bpy.types.WorkSpaceTool.space_type

(default `'EMPTY'`, readonly)

**Type:**

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]

<a id="bpy.types.WorkSpaceTool.use_brushes"></a>

#### bpy.types.WorkSpaceTool.use_brushes

(default False, readonly)

**Type:**

bool

<a id="bpy.types.WorkSpaceTool.use_paint_canvas"></a>

#### bpy.types.WorkSpaceTool.use_paint_canvas

Does this tool use a painting canvas (default False, readonly)

**Type:**

bool

<a id="bpy.types.WorkSpaceTool.widget"></a>

#### bpy.types.WorkSpaceTool.widget

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.WorkSpaceTool.setup"></a>

#### bpy.types.WorkSpaceTool.setup(idname, *, cursor='DEFAULT', keymap='', gizmo_group='', brush_type='', data_block='', operator='', index=0, options=set(), idname_fallback='', keymap_fallback='')

Set the tool settings

**Parameters:**

- **idname** (str) – Identifier, (never None)
- **cursor** (Literal[[Window Cursor Items](bpy_types_enum_items/window_cursor_items.md#rna-enum-window-cursor-items)]) – cursor, (optional)
- **keymap** (str) – Key Map, (optional, never None)
- **gizmo_group** (str) – Gizmo Group, (optional, never None)
- **brush_type** (str) – Brush Type, Limit this tool to a specific type of brush (optional)
- **data_block** (str) – Data Block, (optional, never None)
- **operator** (str) – Operator, (optional, never None)
- **index** (int) – Index, (in [-inf, inf], optional)
- **options** (set[Literal['KEYMAP_FALLBACK', 'USE_BRUSHES']]) –

  Tool Options, (optional)

  - `KEYMAP_FALLBACK`
    Fallback.
  - `USE_BRUSHES`
    Uses Brushes – Allow this tool to use brushes via the asset system.
- **idname_fallback** (str) – Fallback Identifier, (optional, never None)
- **keymap_fallback** (str) – Fallback Key Map, (optional, never None)

<a id="bpy.types.WorkSpaceTool.operator_properties"></a>

#### bpy.types.WorkSpaceTool.operator_properties(operator)

operator_properties

**Parameters:**

**operator** (str) – (never None)

**Returns:**

(never None)

**Return type:**

[`OperatorProperties`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties "bpy.types.OperatorProperties")

<a id="bpy.types.WorkSpaceTool.gizmo_group_properties"></a>

#### bpy.types.WorkSpaceTool.gizmo_group_properties(group)

gizmo_group_properties

**Parameters:**

**group** (str) – (never None)

**Returns:**

(never None)

**Return type:**

[`GizmoGroupProperties`](bpy.types.GizmoGroupProperties.md#bpy.types.GizmoGroupProperties "bpy.types.GizmoGroupProperties")

<a id="bpy.types.WorkSpaceTool.refresh_from_context"></a>

#### bpy.types.WorkSpaceTool.refresh_from_context()

refresh_from_context

<a id="bpy.types.WorkSpaceTool.bl_rna_get_subclass"></a>

#### classmethod bpy.types.WorkSpaceTool.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.WorkSpaceTool.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.WorkSpaceTool.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - [`WorkSpace.tools`](bpy.types.WorkSpace.md#bpy.types.WorkSpace.tools "bpy.types.WorkSpace.tools") - [`wmTools.from_space_image_mode`](bpy.types.wmTools.md#bpy.types.wmTools.from_space_image_mode "bpy.types.wmTools.from_space_image_mode") - [`wmTools.from_space_node`](bpy.types.wmTools.md#bpy.types.wmTools.from_space_node "bpy.types.wmTools.from_space_node") | - [`wmTools.from_space_sequencer`](bpy.types.wmTools.md#bpy.types.wmTools.from_space_sequencer "bpy.types.wmTools.from_space_sequencer") - [`wmTools.from_space_view3d_mode`](bpy.types.wmTools.md#bpy.types.wmTools.from_space_view3d_mode "bpy.types.wmTools.from_space_view3d_mode") |
