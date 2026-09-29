<!-- source: Blender Python API reference 5.2 / bpy.types.MovieClipProxy.html -->

<a id="movieclipproxy-bpy-struct"></a>

# MovieClipProxy(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieClipProxy"></a>

### class bpy.types.MovieClipProxy(bpy_struct)

Proxy parameters for a movie clip

<a id="bpy.types.MovieClipProxy.build_100"></a>

#### bpy.types.MovieClipProxy.build_100

Build proxy resolution 100% of the original footage dimension (default False)

**Type:**

bool

<a id="bpy.types.MovieClipProxy.build_25"></a>

#### bpy.types.MovieClipProxy.build_25

Build proxy resolution 25% of the original footage dimension (default True)

**Type:**

bool

<a id="bpy.types.MovieClipProxy.build_50"></a>

#### bpy.types.MovieClipProxy.build_50

Build proxy resolution 50% of the original footage dimension (default False)

**Type:**

bool

<a id="bpy.types.MovieClipProxy.build_75"></a>

#### bpy.types.MovieClipProxy.build_75

Build proxy resolution 75% of the original footage dimension (default False)

**Type:**

bool

<a id="bpy.types.MovieClipProxy.build_undistorted_100"></a>

#### bpy.types.MovieClipProxy.build_undistorted_100

Build proxy resolution 100% of the original undistorted footage dimension (default False)

**Type:**

bool

<a id="bpy.types.MovieClipProxy.build_undistorted_25"></a>

#### bpy.types.MovieClipProxy.build_undistorted_25

Build proxy resolution 25% of the original undistorted footage dimension (default False)

**Type:**

bool

<a id="bpy.types.MovieClipProxy.build_undistorted_50"></a>

#### bpy.types.MovieClipProxy.build_undistorted_50

Build proxy resolution 50% of the original undistorted footage dimension (default False)

**Type:**

bool

<a id="bpy.types.MovieClipProxy.build_undistorted_75"></a>

#### bpy.types.MovieClipProxy.build_undistorted_75

Build proxy resolution 75% of the original undistorted footage dimension (default False)

**Type:**

bool

<a id="bpy.types.MovieClipProxy.directory"></a>

#### bpy.types.MovieClipProxy.directory

Location to store the proxy files (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.MovieClipProxy.quality"></a>

#### bpy.types.MovieClipProxy.quality

JPEG quality of proxy images (in [0, 32767], default 50)

**Type:**

int

<a id="bpy.types.MovieClipProxy.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieClipProxy.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieClipProxy.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieClipProxy.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieClip.proxy`](bpy.types.MovieClip.md#bpy.types.MovieClip.proxy "bpy.types.MovieClip.proxy") |  |
