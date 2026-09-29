<!-- source: Blender Python API reference 5.2 / bpy.types.ObjectLineArt.html -->

<a id="objectlineart-bpy-struct"></a>

# ObjectLineArt(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ObjectLineArt"></a>

### class bpy.types.ObjectLineArt(bpy_struct)

Object Line Art settings

<a id="bpy.types.ObjectLineArt.crease_threshold"></a>

#### bpy.types.ObjectLineArt.crease_threshold

Angles smaller than this will be treated as creases (in [0, 3.14159], default 2.44346)

**Type:**

float

<a id="bpy.types.ObjectLineArt.intersection_priority"></a>

#### bpy.types.ObjectLineArt.intersection_priority

The intersection line will be included into the object with the higher intersection priority value (in [0, 255], default 0)

**Type:**

int

<a id="bpy.types.ObjectLineArt.usage"></a>

#### bpy.types.ObjectLineArt.usage

How to use this object in Line Art calculation (default `'INHERIT'`)

- `INHERIT`
  Inherit – Use settings from the parent collection.
- `INCLUDE`
  Include – Generate feature lines for this object’s data.
- `OCCLUSION_ONLY`
  Occlusion Only – Only use the object data to produce occlusion.
- `EXCLUDE`
  Exclude – Don’t use this object for Line Art rendering.
- `INTERSECTION_ONLY`
  Intersection Only – Only generate intersection lines for this collection.
- `NO_INTERSECTION`
  No Intersection – Include this object but do not generate intersection lines.
- `FORCE_INTERSECTION`
  Force Intersection – Generate intersection lines even with objects that disabled intersection.

**Type:**

Literal[‘INHERIT’, ‘INCLUDE’, ‘OCCLUSION_ONLY’, ‘EXCLUDE’, ‘INTERSECTION_ONLY’, ‘NO_INTERSECTION’, ‘FORCE_INTERSECTION’]

<a id="bpy.types.ObjectLineArt.use_crease_override"></a>

#### bpy.types.ObjectLineArt.use_crease_override

Use this object’s crease setting to overwrite scene global (default False)

**Type:**

bool

<a id="bpy.types.ObjectLineArt.use_intersection_priority_override"></a>

#### bpy.types.ObjectLineArt.use_intersection_priority_override

Use this object’s intersection priority to override collection setting (default False)

**Type:**

bool

<a id="bpy.types.ObjectLineArt.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ObjectLineArt.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ObjectLineArt.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ObjectLineArt.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Object.lineart`](bpy.types.Object.md#bpy.types.Object.lineart "bpy.types.Object.lineart") |  |
