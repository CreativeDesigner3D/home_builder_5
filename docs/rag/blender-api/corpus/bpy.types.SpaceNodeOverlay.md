<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceNodeOverlay.html -->

<a id="spacenodeoverlay-bpy-struct"></a>

# SpaceNodeOverlay(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SpaceNodeOverlay"></a>

### class bpy.types.SpaceNodeOverlay(bpy_struct)

Settings for display of overlays in the Node Editor

<a id="bpy.types.SpaceNodeOverlay.passepartout_alpha"></a>

#### bpy.types.SpaceNodeOverlay.passepartout_alpha

Opacity of the darkened overlay outside the render region (in [0, 1], default 0.5)

**Type:**

float

<a id="bpy.types.SpaceNodeOverlay.preview_shape"></a>

#### bpy.types.SpaceNodeOverlay.preview_shape

Preview shape used by the node previews (default `'FLAT'`)

- `FLAT`
  Flat – Use the default flat previews.
- `3D`
  3D – Use the material preview scene for the node previews.

**Type:**

Literal[‘FLAT’, ‘3D’]

<a id="bpy.types.SpaceNodeOverlay.show_context_path"></a>

#### bpy.types.SpaceNodeOverlay.show_context_path

Display breadcrumbs for the editor’s context (default True)

**Type:**

bool

<a id="bpy.types.SpaceNodeOverlay.show_named_attributes"></a>

#### bpy.types.SpaceNodeOverlay.show_named_attributes

Show when nodes are using named attributes (default True)

**Type:**

bool

<a id="bpy.types.SpaceNodeOverlay.show_overlays"></a>

#### bpy.types.SpaceNodeOverlay.show_overlays

Display overlays like colored or dashed wires (default True)

**Type:**

bool

<a id="bpy.types.SpaceNodeOverlay.show_previews"></a>

#### bpy.types.SpaceNodeOverlay.show_previews

Display each node’s preview if node is toggled (default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeOverlay.show_render_size"></a>

#### bpy.types.SpaceNodeOverlay.show_render_size

Display the region of the final render (default True)

**Type:**

bool

<a id="bpy.types.SpaceNodeOverlay.show_reroute_auto_labels"></a>

#### bpy.types.SpaceNodeOverlay.show_reroute_auto_labels

Label reroute nodes based on the label of connected reroute nodes (default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeOverlay.show_timing"></a>

#### bpy.types.SpaceNodeOverlay.show_timing

Display each node’s last execution time (default False)

**Type:**

bool

<a id="bpy.types.SpaceNodeOverlay.show_wire_color"></a>

#### bpy.types.SpaceNodeOverlay.show_wire_color

Color node links based on their connected sockets (default True)

**Type:**

bool

<a id="bpy.types.SpaceNodeOverlay.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceNodeOverlay.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceNodeOverlay.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceNodeOverlay.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`SpaceNodeEditor.overlay`](bpy.types.SpaceNodeEditor.md#bpy.types.SpaceNodeEditor.overlay "bpy.types.SpaceNodeEditor.overlay") |  |
