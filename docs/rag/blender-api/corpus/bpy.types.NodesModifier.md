<!-- source: Blender Python API reference 5.2 / bpy.types.NodesModifier.html -->

<a id="nodesmodifier-modifier"></a>

# NodesModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.NodesModifier"></a>

### class bpy.types.NodesModifier(Modifier)

<a id="bpy.types.NodesModifier.bake_directory"></a>

#### bpy.types.NodesModifier.bake_directory

Location on disk where the bake data is stored (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.NodesModifier.bake_target"></a>

#### bpy.types.NodesModifier.bake_target

Where to store the baked data (default `'PACKED'`)

- `PACKED`
  Packed – Pack the baked data into the .blend file.
- `DISK`
  Disk – Store the baked data in a directory on disk.

**Type:**

Literal[‘PACKED’, ‘DISK’]

<a id="bpy.types.NodesModifier.bakes"></a>

#### bpy.types.NodesModifier.bakes

All potential bakes, as defined by the assigned Geometry Nodes (default None, readonly)

**Type:**

[`NodesModifierBakes`](bpy.types.NodesModifierBakes.md#bpy.types.NodesModifierBakes "bpy.types.NodesModifierBakes")[[`NodesModifierBake`](bpy.types.NodesModifierBake.md#bpy.types.NodesModifierBake "bpy.types.NodesModifierBake")]

<a id="bpy.types.NodesModifier.node_group"></a>

#### bpy.types.NodesModifier.node_group

Node group that controls what this modifier does

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.NodesModifier.node_warnings"></a>

#### bpy.types.NodesModifier.node_warnings

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`NodesModifierWarning`](bpy.types.NodesModifierWarning.md#bpy.types.NodesModifierWarning "bpy.types.NodesModifierWarning")]

<a id="bpy.types.NodesModifier.open_bake_data_blocks_panel"></a>

#### bpy.types.NodesModifier.open_bake_data_blocks_panel

(default False)

**Type:**

bool

<a id="bpy.types.NodesModifier.open_bake_panel"></a>

#### bpy.types.NodesModifier.open_bake_panel

(default False)

**Type:**

bool

<a id="bpy.types.NodesModifier.open_manage_panel"></a>

#### bpy.types.NodesModifier.open_manage_panel

(default False)

**Type:**

bool

<a id="bpy.types.NodesModifier.open_named_attributes_panel"></a>

#### bpy.types.NodesModifier.open_named_attributes_panel

(default False)

**Type:**

bool

<a id="bpy.types.NodesModifier.open_output_attributes_panel"></a>

#### bpy.types.NodesModifier.open_output_attributes_panel

(default False)

**Type:**

bool

<a id="bpy.types.NodesModifier.open_warnings_panel"></a>

#### bpy.types.NodesModifier.open_warnings_panel

(default False)

**Type:**

bool

<a id="bpy.types.NodesModifier.panels"></a>

#### bpy.types.NodesModifier.panels

(default None, readonly)

**Type:**

[`NodesModifierPanels`](bpy.types.NodesModifierPanels.md#bpy.types.NodesModifierPanels "bpy.types.NodesModifierPanels")[[`NodesModifierPanel`](bpy.types.NodesModifierPanel.md#bpy.types.NodesModifierPanel "bpy.types.NodesModifierPanel")]

<a id="bpy.types.NodesModifier.properties"></a>

#### bpy.types.NodesModifier.properties

(readonly)

**Type:**

[`NodesModifierProperties`](bpy.types.NodesModifierProperties.md#bpy.types.NodesModifierProperties "bpy.types.NodesModifierProperties") | None

<a id="bpy.types.NodesModifier.show_group_selector"></a>

#### bpy.types.NodesModifier.show_group_selector

(default False)

**Type:**

bool

<a id="bpy.types.NodesModifier.show_manage_panel"></a>

#### bpy.types.NodesModifier.show_manage_panel

(default False)

**Type:**

bool

<a id="bpy.types.NodesModifier.is_input_visible"></a>

#### bpy.types.NodesModifier.is_input_visible(identifier)

Check whether an input is currently visible based on modifier settings.

**Parameters:**

**identifier** (str) – The identifier of the input (never None)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.NodesModifier.is_input_used"></a>

#### bpy.types.NodesModifier.is_input_used(identifier)

Check whether an input is currently used based on modifier settings.

**Parameters:**

**identifier** (str) – The identifier of the input (never None)

**Returns:**

Result

**Return type:**

bool

<a id="bpy.types.NodesModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NodesModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NodesModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NodesModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Modifier.name, Modifier.type, Modifier.show_viewport, Modifier.show_render, Modifier.show_in_editmode, Modifier.show_on_cage, Modifier.show_expanded, Modifier.is_active, Modifier.use_pin_to_last, Modifier.is_override_data, Modifier.use_apply_on_spline, Modifier.execution_time, Modifier.persistent_uid

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Modifier.bl_rna_get_subclass, Modifier.bl_rna_get_subclass_py
