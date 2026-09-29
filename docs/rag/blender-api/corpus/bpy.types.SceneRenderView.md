<!-- source: Blender Python API reference 5.2 / bpy.types.SceneRenderView.html -->

<a id="scenerenderview-bpy-struct"></a>

# SceneRenderView(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SceneRenderView"></a>

### class bpy.types.SceneRenderView(bpy_struct)

Render viewpoint for 3D stereo and multiview rendering

<a id="bpy.types.SceneRenderView.camera_suffix"></a>

#### bpy.types.SceneRenderView.camera_suffix

Suffix to identify the cameras to use, and added to the render images for this view (default “”, never None)

**Type:**

str

<a id="bpy.types.SceneRenderView.file_suffix"></a>

#### bpy.types.SceneRenderView.file_suffix

Suffix added to the render images for this view (default “”, never None)

**Type:**

str

<a id="bpy.types.SceneRenderView.name"></a>

#### bpy.types.SceneRenderView.name

Render view name (default “”, never None)

**Type:**

str

<a id="bpy.types.SceneRenderView.use"></a>

#### bpy.types.SceneRenderView.use

Disable or enable the render view (default True)

**Type:**

bool

<a id="bpy.types.SceneRenderView.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SceneRenderView.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SceneRenderView.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SceneRenderView.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`RenderViews.active`](bpy.types.RenderViews.md#bpy.types.RenderViews.active "bpy.types.RenderViews.active") - [`RenderViews.new`](bpy.types.RenderViews.md#bpy.types.RenderViews.new "bpy.types.RenderViews.new") - [`RenderViews.remove`](bpy.types.RenderViews.md#bpy.types.RenderViews.remove "bpy.types.RenderViews.remove") | - [`RenderSettings.stereo_views`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.stereo_views "bpy.types.RenderSettings.stereo_views") - [`RenderSettings.views`](bpy.types.RenderSettings.md#bpy.types.RenderSettings.views "bpy.types.RenderSettings.views") |
