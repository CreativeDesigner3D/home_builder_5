<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilDashModifierSegment.html -->

<a id="greasepencildashmodifiersegment-bpy-struct"></a>

# GreasePencilDashModifierSegment(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.GreasePencilDashModifierSegment"></a>

### class bpy.types.GreasePencilDashModifierSegment(bpy_struct)

Configuration for a single dash segment

<a id="bpy.types.GreasePencilDashModifierSegment.dash"></a>

#### bpy.types.GreasePencilDashModifierSegment.dash

The number of consecutive points from the original stroke to include in this segment (in [1, 32767], default 2)

**Type:**

int

<a id="bpy.types.GreasePencilDashModifierSegment.gap"></a>

#### bpy.types.GreasePencilDashModifierSegment.gap

The number of points skipped after this segment (in [0, 32767], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilDashModifierSegment.material_index"></a>

#### bpy.types.GreasePencilDashModifierSegment.material_index

Use this index on generated segment. -1 means using the existing material. (in [-1, 32767], default -1)

**Type:**

int

<a id="bpy.types.GreasePencilDashModifierSegment.name"></a>

#### bpy.types.GreasePencilDashModifierSegment.name

Name of the dash segment (default “Segment”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilDashModifierSegment.opacity"></a>

#### bpy.types.GreasePencilDashModifierSegment.opacity

The factor to apply to the original point’s opacity for the new points (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilDashModifierSegment.radius"></a>

#### bpy.types.GreasePencilDashModifierSegment.radius

The factor to apply to the original point’s radius for the new points (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilDashModifierSegment.use_cyclic"></a>

#### bpy.types.GreasePencilDashModifierSegment.use_cyclic

Enable cyclic on individual stroke dashes (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilDashModifierSegment.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilDashModifierSegment.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilDashModifierSegment.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilDashModifierSegment.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GreasePencilDashModifierData.segments`](bpy.types.GreasePencilDashModifierData.md#bpy.types.GreasePencilDashModifierData.segments "bpy.types.GreasePencilDashModifierData.segments") |  |
