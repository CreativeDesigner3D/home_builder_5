<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilTimeModifierSegment.html -->

<a id="greasepenciltimemodifiersegment-bpy-struct"></a>

# GreasePencilTimeModifierSegment(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.GreasePencilTimeModifierSegment"></a>

### class bpy.types.GreasePencilTimeModifierSegment(bpy_struct)

Configuration for a single dash segment

<a id="bpy.types.GreasePencilTimeModifierSegment.name"></a>

#### bpy.types.GreasePencilTimeModifierSegment.name

Name of the dash segment (default “Segment”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilTimeModifierSegment.segment_end"></a>

#### bpy.types.GreasePencilTimeModifierSegment.segment_end

Last frame of the segment (in [0, 32767], default 2)

**Type:**

int

<a id="bpy.types.GreasePencilTimeModifierSegment.segment_mode"></a>

#### bpy.types.GreasePencilTimeModifierSegment.segment_mode

(default `'NORMAL'`)

- `NORMAL`
  Regular – Apply offset in usual animation direction.
- `REVERSE`
  Reverse – Apply offset in reverse animation direction.
- `PINGPONG`
  Ping Pong – Loop back and forth.

**Type:**

Literal[‘NORMAL’, ‘REVERSE’, ‘PINGPONG’]

<a id="bpy.types.GreasePencilTimeModifierSegment.segment_repeat"></a>

#### bpy.types.GreasePencilTimeModifierSegment.segment_repeat

Number of cycle repeats (in [1, 32767], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilTimeModifierSegment.segment_start"></a>

#### bpy.types.GreasePencilTimeModifierSegment.segment_start

First frame of the segment (in [0, 32767], default 1)

**Type:**

int

<a id="bpy.types.GreasePencilTimeModifierSegment.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilTimeModifierSegment.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilTimeModifierSegment.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilTimeModifierSegment.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GreasePencilTimeModifier.segments`](bpy.types.GreasePencilTimeModifier.md#bpy.types.GreasePencilTimeModifier.segments "bpy.types.GreasePencilTimeModifier.segments") |  |
