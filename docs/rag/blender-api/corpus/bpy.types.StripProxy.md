<!-- source: Blender Python API reference 5.2 / bpy.types.StripProxy.html -->

<a id="stripproxy-bpy-struct"></a>

# StripProxy(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.StripProxy"></a>

### class bpy.types.StripProxy(bpy_struct)

Proxy parameters for a sequence strip

<a id="bpy.types.StripProxy.build_100"></a>

#### bpy.types.StripProxy.build_100

Build 100% proxy resolution (default False)

**Type:**

bool

<a id="bpy.types.StripProxy.build_25"></a>

#### bpy.types.StripProxy.build_25

Build 25% proxy resolution (default False)

**Type:**

bool

<a id="bpy.types.StripProxy.build_50"></a>

#### bpy.types.StripProxy.build_50

Build 50% proxy resolution (default False)

**Type:**

bool

<a id="bpy.types.StripProxy.build_75"></a>

#### bpy.types.StripProxy.build_75

Build 75% proxy resolution (default False)

**Type:**

bool

<a id="bpy.types.StripProxy.directory"></a>

#### bpy.types.StripProxy.directory

Location to store the proxy files (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.StripProxy.filepath"></a>

#### bpy.types.StripProxy.filepath

Location of custom proxy file (default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.StripProxy.quality"></a>

#### bpy.types.StripProxy.quality

Quality of proxies to build (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.StripProxy.use_overwrite"></a>

#### bpy.types.StripProxy.use_overwrite

Overwrite existing proxy files when building (default False)

**Type:**

bool

<a id="bpy.types.StripProxy.use_proxy_custom_directory"></a>

#### bpy.types.StripProxy.use_proxy_custom_directory

Use a custom directory to store data (default False)

**Type:**

bool

<a id="bpy.types.StripProxy.use_proxy_custom_file"></a>

#### bpy.types.StripProxy.use_proxy_custom_file

Use a custom file to read proxy data from (default False)

**Type:**

bool

<a id="bpy.types.StripProxy.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StripProxy.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StripProxy.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StripProxy.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`EffectStrip.proxy`](bpy.types.EffectStrip.md#bpy.types.EffectStrip.proxy "bpy.types.EffectStrip.proxy") - [`ImageStrip.proxy`](bpy.types.ImageStrip.md#bpy.types.ImageStrip.proxy "bpy.types.ImageStrip.proxy") - [`MetaStrip.proxy`](bpy.types.MetaStrip.md#bpy.types.MetaStrip.proxy "bpy.types.MetaStrip.proxy") | - [`MovieStrip.proxy`](bpy.types.MovieStrip.md#bpy.types.MovieStrip.proxy "bpy.types.MovieStrip.proxy") - [`SceneStrip.proxy`](bpy.types.SceneStrip.md#bpy.types.SceneStrip.proxy "bpy.types.SceneStrip.proxy") |
