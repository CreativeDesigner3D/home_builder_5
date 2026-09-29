<!-- source: Blender Python API reference 5.2 / bpy.types.GizmoGroup.html -->

<a id="gizmogroup-bpy-struct"></a>

# GizmoGroup(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.GizmoGroup"></a>

### class bpy.types.GizmoGroup(bpy_struct)

Storage of an operator being executed, or registered after execution

<a id="bpy.types.GizmoGroup.bl_idname"></a>

#### bpy.types.GizmoGroup.bl_idname

(default “”, never None)

**Type:**

str

<a id="bpy.types.GizmoGroup.bl_label"></a>

#### bpy.types.GizmoGroup.bl_label

(default “”, never None)

**Type:**

str

<a id="bpy.types.GizmoGroup.bl_options"></a>

#### bpy.types.GizmoGroup.bl_options

Options for this operator type (default set())

- `3D`
  3D – Use in 3D viewport.
- `SCALE`
  Scale – Scale to respect zoom (otherwise zoom independent display size).
- `DEPTH_3D`
  Depth 3D – Supports culled depth by other objects in the view.
- `SELECT`
  Select – Supports selection.
- `PERSISTENT`
  Persistent.
- `SHOW_MODAL_ALL`
  Show Modal All – Show all while interacting, as well as this group when another is being interacted with.
- `EXCLUDE_MODAL`
  Exclude Modal – Show all except this group while interacting.
- `TOOL_INIT`
  Tool Init – Postpone running until tool operator run (when used with a tool).
- `TOOL_FALLBACK_KEYMAP`
  Use fallback tools keymap – Add fallback tools keymap to this gizmo type.
- `VR_REDRAWS`
  VR Redraws – The gizmos are made for use with virtual reality sessions and require special redraw management.

**Type:**

set[Literal[‘3D’, ‘SCALE’, ‘DEPTH_3D’, ‘SELECT’, ‘PERSISTENT’, ‘SHOW_MODAL_ALL’, ‘EXCLUDE_MODAL’, ‘TOOL_INIT’, ‘TOOL_FALLBACK_KEYMAP’, ‘VR_REDRAWS’]]

<a id="bpy.types.GizmoGroup.bl_owner_id"></a>

#### bpy.types.GizmoGroup.bl_owner_id

(default “”, never None)

**Type:**

str

<a id="bpy.types.GizmoGroup.bl_region_type"></a>

#### bpy.types.GizmoGroup.bl_region_type

The region where the panel is going to be used in (default `'WINDOW'`)

**Type:**

Literal[[Region Type Items](bpy_types_enum_items/region_type_items.md#rna-enum-region-type-items)]

<a id="bpy.types.GizmoGroup.bl_space_type"></a>

#### bpy.types.GizmoGroup.bl_space_type

The space where the panel is going to be used in (default `'EMPTY'`)

**Type:**

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]

<a id="bpy.types.GizmoGroup.gizmos"></a>

#### bpy.types.GizmoGroup.gizmos

List of gizmos in the Gizmo Map (default None, readonly)

**Type:**

[`Gizmos`](bpy.types.Gizmos.md#bpy.types.Gizmos "bpy.types.Gizmos")[[`Gizmo`](bpy.types.Gizmo.md#bpy.types.Gizmo "bpy.types.Gizmo")]

<a id="bpy.types.GizmoGroup.name"></a>

#### bpy.types.GizmoGroup.name

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.GizmoGroup.poll"></a>

#### classmethod bpy.types.GizmoGroup.poll(context)

Test if the gizmo group can be called or not

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

**Return type:**

bool

<a id="bpy.types.GizmoGroup.setup_keymap"></a>

#### classmethod bpy.types.GizmoGroup.setup_keymap(keyconfig)

Initialize keymaps for this gizmo group, use fallback keymap when not present

**Parameters:**

**keyconfig** ([`KeyConfig`](bpy.types.KeyConfig.md#bpy.types.KeyConfig "bpy.types.KeyConfig") | None) – (never None)

**Returns:**

(never None)

**Return type:**

[`KeyMap`](bpy.types.KeyMap.md#bpy.types.KeyMap "bpy.types.KeyMap")

<a id="bpy.types.GizmoGroup.setup"></a>

#### bpy.types.GizmoGroup.setup(context)

Create gizmos function for the gizmo group

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.GizmoGroup.refresh"></a>

#### bpy.types.GizmoGroup.refresh(context)

Refresh data (called on common state changes such as selection)

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.GizmoGroup.draw_prepare"></a>

#### bpy.types.GizmoGroup.draw_prepare(context)

Run before each redraw

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.GizmoGroup.invoke_prepare"></a>

#### bpy.types.GizmoGroup.invoke_prepare(context, gizmo)

Run before invoke

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)
- **gizmo** ([`Gizmo`](bpy.types.Gizmo.md#bpy.types.Gizmo "bpy.types.Gizmo") | None) – (never None)

<a id="bpy.types.GizmoGroup.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GizmoGroup.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GizmoGroup.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GizmoGroup.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Context.gizmo_group`](bpy.types.Context.md#bpy.types.Context.gizmo_group "bpy.types.Context.gizmo_group") | - [`Gizmo.group`](bpy.types.Gizmo.md#bpy.types.Gizmo.group "bpy.types.Gizmo.group") |
