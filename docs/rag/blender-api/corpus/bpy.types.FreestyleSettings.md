<!-- source: Blender Python API reference 5.2 / bpy.types.FreestyleSettings.html -->

<a id="freestylesettings-bpy-struct"></a>

# FreestyleSettings(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FreestyleSettings"></a>

### class bpy.types.FreestyleSettings(bpy_struct)

Freestyle settings for a ViewLayer data-block

<a id="bpy.types.FreestyleSettings.as_render_pass"></a>

#### bpy.types.FreestyleSettings.as_render_pass

Renders Freestyle output to a separate pass instead of overlaying it on the Combined pass (default False)

**Type:**

bool

<a id="bpy.types.FreestyleSettings.crease_angle"></a>

#### bpy.types.FreestyleSettings.crease_angle

Angular threshold for detecting crease edges (in [0, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.FreestyleSettings.kr_derivative_epsilon"></a>

#### bpy.types.FreestyleSettings.kr_derivative_epsilon

Kr derivative epsilon for computing suggestive contours (in [-1000, 1000], default 0.0)

**Type:**

float

<a id="bpy.types.FreestyleSettings.linesets"></a>

#### bpy.types.FreestyleSettings.linesets

(default None, readonly)

**Type:**

[`Linesets`](bpy.types.Linesets.md#bpy.types.Linesets "bpy.types.Linesets")[[`FreestyleLineSet`](bpy.types.FreestyleLineSet.md#bpy.types.FreestyleLineSet "bpy.types.FreestyleLineSet")]

<a id="bpy.types.FreestyleSettings.mode"></a>

#### bpy.types.FreestyleSettings.mode

Select the Freestyle control mode (default `'SCRIPT'`)

- `SCRIPT`
  Python Scripting – Advanced mode for using style modules written in Python.
- `EDITOR`
  Parameter Editor – Basic mode for interactive style parameter editing.

**Type:**

Literal[‘SCRIPT’, ‘EDITOR’]

<a id="bpy.types.FreestyleSettings.modules"></a>

#### bpy.types.FreestyleSettings.modules

A list of style modules (to be applied from top to bottom) (default None, readonly)

**Type:**

[`FreestyleModules`](bpy.types.FreestyleModules.md#bpy.types.FreestyleModules "bpy.types.FreestyleModules")[[`FreestyleModuleSettings`](bpy.types.FreestyleModuleSettings.md#bpy.types.FreestyleModuleSettings "bpy.types.FreestyleModuleSettings")]

<a id="bpy.types.FreestyleSettings.sphere_radius"></a>

#### bpy.types.FreestyleSettings.sphere_radius

Sphere radius for computing curvatures (in [0, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.FreestyleSettings.use_culling"></a>

#### bpy.types.FreestyleSettings.use_culling

If enabled, out-of-view edges are ignored (default False)

**Type:**

bool

<a id="bpy.types.FreestyleSettings.use_material_boundaries"></a>

#### bpy.types.FreestyleSettings.use_material_boundaries

Enable material boundaries (default False)

**Type:**

bool

<a id="bpy.types.FreestyleSettings.use_ridges_and_valleys"></a>

#### bpy.types.FreestyleSettings.use_ridges_and_valleys

Enable ridges and valleys (default False)

**Type:**

bool

<a id="bpy.types.FreestyleSettings.use_smoothness"></a>

#### bpy.types.FreestyleSettings.use_smoothness

Take face smoothness into account in view map calculation (default False)

**Type:**

bool

<a id="bpy.types.FreestyleSettings.use_suggestive_contours"></a>

#### bpy.types.FreestyleSettings.use_suggestive_contours

Enable suggestive contours (default False)

**Type:**

bool

<a id="bpy.types.FreestyleSettings.use_view_map_cache"></a>

#### bpy.types.FreestyleSettings.use_view_map_cache

Keep the computed view map and avoid recalculating it if mesh geometry is unchanged (default False)

**Type:**

bool

<a id="bpy.types.FreestyleSettings.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FreestyleSettings.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FreestyleSettings.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FreestyleSettings.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ViewLayer.freestyle_settings`](bpy.types.ViewLayer.md#bpy.types.ViewLayer.freestyle_settings "bpy.types.ViewLayer.freestyle_settings") |  |
