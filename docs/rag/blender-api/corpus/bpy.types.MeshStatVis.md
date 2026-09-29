<!-- source: Blender Python API reference 5.2 / bpy.types.MeshStatVis.html -->

<a id="meshstatvis-bpy-struct"></a>

# MeshStatVis(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MeshStatVis"></a>

### class bpy.types.MeshStatVis(bpy_struct)

<a id="bpy.types.MeshStatVis.distort_max"></a>

#### bpy.types.MeshStatVis.distort_max

Maximum angle to display (in [0, 3.14159], default 0.785398)

**Type:**

float

<a id="bpy.types.MeshStatVis.distort_min"></a>

#### bpy.types.MeshStatVis.distort_min

Minimum angle to display (in [0, 3.14159], default 0.0872665)

**Type:**

float

<a id="bpy.types.MeshStatVis.overhang_axis"></a>

#### bpy.types.MeshStatVis.overhang_axis

(default `'NEG_Z'`)

**Type:**

Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]

<a id="bpy.types.MeshStatVis.overhang_max"></a>

#### bpy.types.MeshStatVis.overhang_max

Maximum angle to display (in [0, 3.14159], default 0.785398)

**Type:**

float

<a id="bpy.types.MeshStatVis.overhang_min"></a>

#### bpy.types.MeshStatVis.overhang_min

Minimum angle to display (in [0, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.MeshStatVis.sharp_max"></a>

#### bpy.types.MeshStatVis.sharp_max

Maximum angle to display (in [-3.14159, 3.14159], default 3.14159)

**Type:**

float

<a id="bpy.types.MeshStatVis.sharp_min"></a>

#### bpy.types.MeshStatVis.sharp_min

Minimum angle to display (in [-3.14159, 3.14159], default 1.5708)

**Type:**

float

<a id="bpy.types.MeshStatVis.thickness_max"></a>

#### bpy.types.MeshStatVis.thickness_max

Maximum for measuring thickness (in [0, 1000], default 0.1)

**Type:**

float

<a id="bpy.types.MeshStatVis.thickness_min"></a>

#### bpy.types.MeshStatVis.thickness_min

Minimum for measuring thickness (in [0, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.MeshStatVis.thickness_samples"></a>

#### bpy.types.MeshStatVis.thickness_samples

Number of samples to test per face (in [1, 32], default 1)

**Type:**

int

<a id="bpy.types.MeshStatVis.type"></a>

#### bpy.types.MeshStatVis.type

Type of data to visualize/check (default `'OVERHANG'`)

**Type:**

Literal[‘OVERHANG’, ‘THICKNESS’, ‘INTERSECT’, ‘DISTORT’, ‘SHARP’]

<a id="bpy.types.MeshStatVis.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MeshStatVis.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MeshStatVis.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MeshStatVis.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.MeshStatVis.type "bpy.types.MeshStatVis.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.MeshStatVis.type "bpy.types.MeshStatVis.type")

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
| - [`ToolSettings.statvis`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.statvis "bpy.types.ToolSettings.statvis") |  |
