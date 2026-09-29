<!-- source: Blender Python API reference 5.2 / bpy.types.StripElement.html -->

<a id="stripelement-bpy-struct"></a>

# StripElement(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.StripElement"></a>

### class bpy.types.StripElement(bpy_struct)

Sequence strip data for a single frame

<a id="bpy.types.StripElement.filename"></a>

#### bpy.types.StripElement.filename

Name of the source file (default “”, never None)

**Type:**

str

<a id="bpy.types.StripElement.orig_fps"></a>

#### bpy.types.StripElement.orig_fps

Original frames per second (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.StripElement.orig_height"></a>

#### bpy.types.StripElement.orig_height

Original image height (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.StripElement.orig_width"></a>

#### bpy.types.StripElement.orig_width

Original image width (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.StripElement.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StripElement.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StripElement.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StripElement.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ImageStrip.elements`](bpy.types.ImageStrip.md#bpy.types.ImageStrip.elements "bpy.types.ImageStrip.elements") - [`MovieStrip.elements`](bpy.types.MovieStrip.md#bpy.types.MovieStrip.elements "bpy.types.MovieStrip.elements") | - [`Strip.strip_elem_from_frame`](bpy.types.Strip.md#bpy.types.Strip.strip_elem_from_frame "bpy.types.Strip.strip_elem_from_frame") - [`StripElements.append`](bpy.types.StripElements.md#bpy.types.StripElements.append "bpy.types.StripElements.append") |
