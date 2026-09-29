<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceConsole.html -->

<a id="spaceconsole-space"></a>

# SpaceConsole(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceConsole"></a>

### class bpy.types.SpaceConsole(Space)

Interactive Python console

<a id="bpy.types.SpaceConsole.font_size"></a>

#### bpy.types.SpaceConsole.font_size

Font size to use for displaying the text (in [1, 256], default 0)

**Type:**

int

<a id="bpy.types.SpaceConsole.history"></a>

#### bpy.types.SpaceConsole.history

Command history (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ConsoleLine`](bpy.types.ConsoleLine.md#bpy.types.ConsoleLine "bpy.types.ConsoleLine")]

<a id="bpy.types.SpaceConsole.language"></a>

#### bpy.types.SpaceConsole.language

Command line prompt language (default “”, never None)

**Type:**

str

<a id="bpy.types.SpaceConsole.prompt"></a>

#### bpy.types.SpaceConsole.prompt

Command line prompt (default “”, never None)

**Type:**

str

<a id="bpy.types.SpaceConsole.scrollback"></a>

#### bpy.types.SpaceConsole.scrollback

Command output (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ConsoleLine`](bpy.types.ConsoleLine.md#bpy.types.ConsoleLine "bpy.types.ConsoleLine")]

<a id="bpy.types.SpaceConsole.select_end"></a>

#### bpy.types.SpaceConsole.select_end

(in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.SpaceConsole.select_start"></a>

#### bpy.types.SpaceConsole.select_start

(in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.SpaceConsole.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceConsole.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceConsole.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceConsole.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceConsole.draw_handler_add"></a>

#### classmethod bpy.types.SpaceConsole.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.SpaceConsole.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceConsole.draw_handler_remove(handler, region_type)

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
