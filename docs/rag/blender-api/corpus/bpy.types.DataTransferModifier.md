<!-- source: Blender Python API reference 5.2 / bpy.types.DataTransferModifier.html -->

<a id="datatransfermodifier-modifier"></a>

# DataTransferModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.DataTransferModifier"></a>

### class bpy.types.DataTransferModifier(Modifier)

Modifier transferring some data from a source mesh

<a id="bpy.types.DataTransferModifier.data_types_edges"></a>

#### bpy.types.DataTransferModifier.data_types_edges

Which edge data layers to transfer (default set())

- `SHARP_EDGE`
  Sharp – Transfer sharp mark.
- `SEAM`
  UV Seam – Transfer UV seam mark.
- `CREASE`
  Crease – Transfer subdivision crease values.
- `BEVEL_WEIGHT_EDGE`
  Bevel Weight – Transfer bevel weights.
- `FREESTYLE_EDGE`
  Freestyle – Transfer Freestyle edge mark.

**Type:**

set[Literal[‘SHARP_EDGE’, ‘SEAM’, ‘CREASE’, ‘BEVEL_WEIGHT_EDGE’, ‘FREESTYLE_EDGE’]]

<a id="bpy.types.DataTransferModifier.data_types_loops"></a>

#### bpy.types.DataTransferModifier.data_types_loops

Which face corner data layers to transfer (default set())

- `CUSTOM_NORMAL`
  Custom Normals – Transfer custom normals.
- `COLOR_CORNER`
  Colors – Transfer color attributes.
- `UV`
  UVs – Transfer UV layers.

**Type:**

set[Literal[‘CUSTOM_NORMAL’, ‘COLOR_CORNER’, ‘UV’]]

<a id="bpy.types.DataTransferModifier.data_types_polys"></a>

#### bpy.types.DataTransferModifier.data_types_polys

Which face data layers to transfer (default set())

- `SMOOTH`
  Smooth – Transfer flat/smooth mark.
- `FREESTYLE_FACE`
  Freestyle Mark – Transfer Freestyle face mark.

**Type:**

set[Literal[‘SMOOTH’, ‘FREESTYLE_FACE’]]

<a id="bpy.types.DataTransferModifier.data_types_verts"></a>

#### bpy.types.DataTransferModifier.data_types_verts

Which vertex data layers to transfer (default set())

- `VGROUP_WEIGHTS`
  Vertex Groups – Transfer active or all vertex groups.
- `BEVEL_WEIGHT_VERT`
  Bevel Weight – Transfer bevel weights.
- `COLOR_VERTEX`
  Colors – Transfer color attributes.

**Type:**

set[Literal[‘VGROUP_WEIGHTS’, ‘BEVEL_WEIGHT_VERT’, ‘COLOR_VERTEX’]]

<a id="bpy.types.DataTransferModifier.edge_mapping"></a>

#### bpy.types.DataTransferModifier.edge_mapping

Method used to map source edges to destination ones (default `'NEAREST'`)

**Type:**

Literal[[Dt Method Edge Items](bpy_types_enum_items/dt_method_edge_items.md#rna-enum-dt-method-edge-items)]

<a id="bpy.types.DataTransferModifier.invert_vertex_group"></a>

#### bpy.types.DataTransferModifier.invert_vertex_group

Invert vertex group influence (default False)

**Type:**

bool

<a id="bpy.types.DataTransferModifier.islands_precision"></a>

#### bpy.types.DataTransferModifier.islands_precision

Factor controlling precision of islands handling (typically, 0.1 should be enough, higher values can make things really slow) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DataTransferModifier.layers_uv_select_dst"></a>

#### bpy.types.DataTransferModifier.layers_uv_select_dst

How to match source and destination layers (default `'NAME'`)

**Type:**

Literal[[Dt Layers Select Dst Items](bpy_types_enum_items/dt_layers_select_dst_items.md#rna-enum-dt-layers-select-dst-items)]

<a id="bpy.types.DataTransferModifier.layers_uv_select_src"></a>

#### bpy.types.DataTransferModifier.layers_uv_select_src

Which layers to transfer, in case of multi-layers types (default `'ALL'`)

**Type:**

Literal[[Dt Layers Select Src Items](bpy_types_enum_items/dt_layers_select_src_items.md#rna-enum-dt-layers-select-src-items)]

<a id="bpy.types.DataTransferModifier.layers_vcol_loop_select_dst"></a>

#### bpy.types.DataTransferModifier.layers_vcol_loop_select_dst

How to match source and destination layers (default `'NAME'`)

**Type:**

Literal[[Dt Layers Select Dst Items](bpy_types_enum_items/dt_layers_select_dst_items.md#rna-enum-dt-layers-select-dst-items)]

<a id="bpy.types.DataTransferModifier.layers_vcol_loop_select_src"></a>

#### bpy.types.DataTransferModifier.layers_vcol_loop_select_src

Which layers to transfer, in case of multi-layers types (default `'ALL'`)

**Type:**

Literal[[Dt Layers Select Src Items](bpy_types_enum_items/dt_layers_select_src_items.md#rna-enum-dt-layers-select-src-items)]

<a id="bpy.types.DataTransferModifier.layers_vcol_vert_select_dst"></a>

#### bpy.types.DataTransferModifier.layers_vcol_vert_select_dst

How to match source and destination layers (default `'NAME'`)

**Type:**

Literal[[Dt Layers Select Dst Items](bpy_types_enum_items/dt_layers_select_dst_items.md#rna-enum-dt-layers-select-dst-items)]

<a id="bpy.types.DataTransferModifier.layers_vcol_vert_select_src"></a>

#### bpy.types.DataTransferModifier.layers_vcol_vert_select_src

Which layers to transfer, in case of multi-layers types (default `'ALL'`)

**Type:**

Literal[[Dt Layers Select Src Items](bpy_types_enum_items/dt_layers_select_src_items.md#rna-enum-dt-layers-select-src-items)]

<a id="bpy.types.DataTransferModifier.layers_vgroup_select_dst"></a>

#### bpy.types.DataTransferModifier.layers_vgroup_select_dst

How to match source and destination layers (default `'NAME'`)

**Type:**

Literal[[Dt Layers Select Dst Items](bpy_types_enum_items/dt_layers_select_dst_items.md#rna-enum-dt-layers-select-dst-items)]

<a id="bpy.types.DataTransferModifier.layers_vgroup_select_src"></a>

#### bpy.types.DataTransferModifier.layers_vgroup_select_src

Which layers to transfer, in case of multi-layers types (default `'ALL'`)

**Type:**

Literal[[Dt Layers Select Src Items](bpy_types_enum_items/dt_layers_select_src_items.md#rna-enum-dt-layers-select-src-items)]

<a id="bpy.types.DataTransferModifier.loop_mapping"></a>

#### bpy.types.DataTransferModifier.loop_mapping

Method used to map source faces’ corners to destination ones (default `'NEAREST_POLYNOR'`)

**Type:**

Literal[[Dt Method Loop Items](bpy_types_enum_items/dt_method_loop_items.md#rna-enum-dt-method-loop-items)]

<a id="bpy.types.DataTransferModifier.max_distance"></a>

#### bpy.types.DataTransferModifier.max_distance

Maximum allowed distance between source and destination element, for non-topology mappings (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.DataTransferModifier.mix_factor"></a>

#### bpy.types.DataTransferModifier.mix_factor

Factor to use when applying data to destination (exact behavior depends on mix mode, multiplied with weights from vertex group when defined) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.DataTransferModifier.mix_mode"></a>

#### bpy.types.DataTransferModifier.mix_mode

How to affect destination elements with source values (default `'REPLACE'`)

**Type:**

Literal[[Dt Mix Mode Items](bpy_types_enum_items/dt_mix_mode_items.md#rna-enum-dt-mix-mode-items)]

<a id="bpy.types.DataTransferModifier.object"></a>

#### bpy.types.DataTransferModifier.object

Object to transfer data from

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.DataTransferModifier.poly_mapping"></a>

#### bpy.types.DataTransferModifier.poly_mapping

Method used to map source faces to destination ones (default `'NEAREST'`)

**Type:**

Literal[[Dt Method Poly Items](bpy_types_enum_items/dt_method_poly_items.md#rna-enum-dt-method-poly-items)]

<a id="bpy.types.DataTransferModifier.ray_radius"></a>

#### bpy.types.DataTransferModifier.ray_radius

‘Width’ of rays (especially useful when raycasting against vertices or edges) (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.DataTransferModifier.use_edge_data"></a>

#### bpy.types.DataTransferModifier.use_edge_data

Enable edge data transfer (default False)

**Type:**

bool

<a id="bpy.types.DataTransferModifier.use_loop_data"></a>

#### bpy.types.DataTransferModifier.use_loop_data

Enable face corner data transfer (default False)

**Type:**

bool

<a id="bpy.types.DataTransferModifier.use_max_distance"></a>

#### bpy.types.DataTransferModifier.use_max_distance

Source elements must be closer than given distance from destination one (default False)

**Type:**

bool

<a id="bpy.types.DataTransferModifier.use_object_transform"></a>

#### bpy.types.DataTransferModifier.use_object_transform

Evaluate source and destination meshes in global space (default True)

**Type:**

bool

<a id="bpy.types.DataTransferModifier.use_poly_data"></a>

#### bpy.types.DataTransferModifier.use_poly_data

Enable face data transfer (default False)

**Type:**

bool

<a id="bpy.types.DataTransferModifier.use_vert_data"></a>

#### bpy.types.DataTransferModifier.use_vert_data

Enable vertex data transfer (default False)

**Type:**

bool

<a id="bpy.types.DataTransferModifier.vert_mapping"></a>

#### bpy.types.DataTransferModifier.vert_mapping

Method used to map source vertices to destination ones (default `'NEAREST'`)

**Type:**

Literal[[Dt Method Vertex Items](bpy_types_enum_items/dt_method_vertex_items.md#rna-enum-dt-method-vertex-items)]

<a id="bpy.types.DataTransferModifier.vertex_group"></a>

#### bpy.types.DataTransferModifier.vertex_group

Vertex group name for selecting the affected areas (default “”, never None)

**Type:**

str

<a id="bpy.types.DataTransferModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.DataTransferModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.DataTransferModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.DataTransferModifier.bl_rna_get_subclass_py(id, default=None, /)

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
