<!-- source: Blender Python API reference 5.2 / bpy.types.Area.html -->

<a id="area-bpy-struct"></a>

# Area(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Area"></a>

### class bpy.types.Area(bpy_struct)

Area in a subdivided screen, containing an editor

<a id="bpy.types.Area.height"></a>

#### bpy.types.Area.height

Area height (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.Area.regions"></a>

#### bpy.types.Area.regions

Regions this area is subdivided in (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Region`](bpy.types.Region.md#bpy.types.Region "bpy.types.Region")]

<a id="bpy.types.Area.show_menus"></a>

#### bpy.types.Area.show_menus

Show menus in the header (default True)

**Type:**

bool

<a id="bpy.types.Area.spaces"></a>

#### bpy.types.Area.spaces

Spaces contained in this area, the first being the active space (NOTE: Useful for example to restore a previously used 3D view space in a certain area to get the old view orientation) (default None, readonly)

**Type:**

[`AreaSpaces`](bpy.types.AreaSpaces.md#bpy.types.AreaSpaces "bpy.types.AreaSpaces")[[`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")]

<a id="bpy.types.Area.type"></a>

#### bpy.types.Area.type

Current editor type for this area (default `'VIEW_3D'`)

**Type:**

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]

<a id="bpy.types.Area.ui_type"></a>

#### bpy.types.Area.ui_type

Current editor type for this area

**Type:**

str

<a id="bpy.types.Area.width"></a>

#### bpy.types.Area.width

Area width (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.Area.x"></a>

#### bpy.types.Area.x

The window relative vertical location of the area (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Area.y"></a>

#### bpy.types.Area.y

The window relative horizontal location of the area (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Area.tag_redraw"></a>

#### bpy.types.Area.tag_redraw()

tag_redraw

<a id="bpy.types.Area.header_text_set"></a>

#### bpy.types.Area.header_text_set(text)

Set the header status text

**Parameters:**

**text** (str) – Text, New string for the header, None clears the text

<a id="bpy.types.Area.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Area.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Area.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Area.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Area.type "bpy.types.Area.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Area.type "bpy.types.Area.type")

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
| - [`Context.area`](bpy.types.Context.md#bpy.types.Context.area "bpy.types.Context.area") | - [`Screen.areas`](bpy.types.Screen.md#bpy.types.Screen.areas "bpy.types.Screen.areas") |
