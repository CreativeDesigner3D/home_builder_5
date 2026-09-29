<!-- source: Blender Python API reference 5.2 / bpy.types.SpacePreferences.html -->

<a id="spacepreferences-space"></a>

# SpacePreferences(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpacePreferences"></a>

### class bpy.types.SpacePreferences(Space)

Blender preferences space data

<a id="bpy.types.SpacePreferences.filter_text"></a>

#### bpy.types.SpacePreferences.filter_text

Search term for filtering in the UI (default “”, never None)

**Type:**

str

<a id="bpy.types.SpacePreferences.filter_type"></a>

#### bpy.types.SpacePreferences.filter_type

Filter method (default `'NAME'`)

- `NAME`
  Name – Filter based on the operator name.
- `KEY`
  Key-Binding – Filter based on key bindings.

**Type:**

Literal[‘NAME’, ‘KEY’]

<a id="bpy.types.SpacePreferences.search_filter"></a>

#### bpy.types.SpacePreferences.search_filter

Live search filtering string (default “”, never None)

**Type:**

str

<a id="bpy.types.SpacePreferences.show_region_ui"></a>

#### bpy.types.SpacePreferences.show_region_ui

(default False)

**Type:**

bool

<a id="bpy.types.SpacePreferences.tab_search_results"></a>

#### bpy.types.SpacePreferences.tab_search_results

Whether or not each visible tab has a search result (dynamic array, default False, readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.SpacePreferences.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpacePreferences.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpacePreferences.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpacePreferences.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpacePreferences.draw_handler_add"></a>

#### classmethod bpy.types.SpacePreferences.draw_handler_add(callback, args, region_type, draw_type)

Add a new draw handler to this space type.
It will be called every time the specified region in the space type will be drawn.
Note: All arguments are positional only for now.

**Parameters:**

- **callback** (Callable[..., Any]) – A function that will be called when the region is drawn.
  It gets the specified arguments as input, it’s return value is ignored.
- **args** (tuple[Any, ...]) – Arguments that will be passed to the callback.
- **region_type** (str) – The region type the callback draws in; usually `WINDOW`. ([`bpy.types.Region.type`](bpy.types.Region.md#bpy.types.Region.type "bpy.types.Region.type"))
- **draw_type** (str) – Usually `POST_PIXEL` for 2D drawing and `POST_VIEW` for 3D drawing. In some cases `PRE_VIEW` can be used. `BACKDROP` can be used for backdrops in the node editor.

**Returns:**

Handler that can be removed later on.

**Return type:**

object

<a id="bpy.types.SpacePreferences.draw_handler_remove"></a>

#### classmethod bpy.types.SpacePreferences.draw_handler_remove(handler, region_type)

Remove a draw handler that was added previously.

**Parameters:**

- **handler** (object) – The draw handler that should be removed.
- **region_type** (str) – Region type the callback was added to.

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Space.type, Space.show_locked_time, Space.show_region_header

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Space.bl_rna_get_subclass, Space.bl_rna_get_subclass_py, Space.draw_handler_add, Space.draw_handler_remove
