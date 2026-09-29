<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataImages.html -->

<a id="blenddataimages-bpy-prop-collection"></a>

# BlendDataImages(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.BlendDataImages"></a>

### class bpy.types.BlendDataImages(bpy_prop_collection)

Collection of images

<a id="bpy.types.BlendDataImages.new"></a>

#### bpy.types.BlendDataImages.new(name, width, height, *, alpha=False, float_buffer=False, stereo3d=False, is_data=False, tiled=False)

Add a new image to the main database

**Parameters:**

- **name** (str) – New name for the data-block (never None)
- **width** (int) – Width of the image (in [1, inf])
- **height** (int) – Height of the image (in [1, inf])
- **alpha** (bool) – Alpha, Use alpha channel (optional)
- **float_buffer** (bool) – Float Buffer, Create an image with floating-point color (optional)
- **stereo3d** (bool) – Stereo 3D, Create left and right views (optional)
- **is_data** (bool) – Is Data, Create image with non-color data color space (optional)
- **tiled** (bool) – Tiled, Create a tiled image (optional)

**Returns:**

New image data-block

**Return type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image")

<a id="bpy.types.BlendDataImages.load"></a>

#### bpy.types.BlendDataImages.load(filepath, *, check_existing=False)

Load a new image into the main database

**Parameters:**

- **filepath** (str) – Path of the file to load (never None, blend relative `//` prefix supported)
- **check_existing** (bool) – Using existing data-block if this file is already loaded (optional)

**Returns:**

New image data-block

**Return type:**

[`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image")

<a id="bpy.types.BlendDataImages.remove"></a>

#### bpy.types.BlendDataImages.remove(image, *, do_unlink=True, do_id_user=True, do_ui_user=True)

Remove an image from the current blendfile

**Parameters:**

- **image** ([`Image`](bpy.types.Image.md#bpy.types.Image "bpy.types.Image") | None) – Image to remove (never None)
- **do_unlink** (bool) – Unlink all usages of this image before deleting it (optional)
- **do_id_user** (bool) – Decrement user counter of all data-blocks used by this image (optional)
- **do_ui_user** (bool) – Make sure interface does not reference this image (optional)

<a id="bpy.types.BlendDataImages.tag"></a>

#### bpy.types.BlendDataImages.tag(value)

tag

**Parameters:**

**value** (bool) – Value

<a id="bpy.types.BlendDataImages.bl_rna_get_subclass"></a>

#### classmethod bpy.types.BlendDataImages.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.BlendDataImages.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.BlendDataImages.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`BlendData.images`](bpy.types.BlendData.md#bpy.types.BlendData.images "bpy.types.BlendData.images") |  |
