<!-- source: Blender Python API reference 5.2 / bpy.types.SpaceOutliner.html -->

<a id="spaceoutliner-space"></a>

# SpaceOutliner(Space)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")

<a id="bpy.types.SpaceOutliner"></a>

### class bpy.types.SpaceOutliner(Space)

Outliner space data

<a id="bpy.types.SpaceOutliner.display_mode"></a>

#### bpy.types.SpaceOutliner.display_mode

Type of information to display (default `'SCENES'`)

- `SCENES`
  Scenes – Display scenes and their view layers, collections and objects.
- `VIEW_LAYER`
  View Layer – Display collections and objects in the view layer.
- `SEQUENCE`
  Video Sequencer – Display data belonging to the Video Sequencer.
- `LIBRARIES`
  Blender File – Display data of current file and linked libraries.
- `DATA_API`
  Data API – Display low level Blender data and its properties.
- `LIBRARY_OVERRIDES`
  Library Overrides – Display data-blocks with library overrides and list their overridden properties.
- `ORPHAN_DATA`
  Unused Data – Display data that is unused and/or will be lost when the file is reloaded.

**Type:**

Literal[‘SCENES’, ‘VIEW_LAYER’, ‘SEQUENCE’, ‘LIBRARIES’, ‘DATA_API’, ‘LIBRARY_OVERRIDES’, ‘ORPHAN_DATA’]

<a id="bpy.types.SpaceOutliner.filter_id_type"></a>

#### bpy.types.SpaceOutliner.filter_id_type

Data-block type to show (default `'ACTION'`)

**Type:**

Literal[[Id Type Items](bpy_types_enum_items/id_type_items.md#rna-enum-id-type-items)]

<a id="bpy.types.SpaceOutliner.filter_invert"></a>

#### bpy.types.SpaceOutliner.filter_invert

Invert the object state filter (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.filter_state"></a>

#### bpy.types.SpaceOutliner.filter_state

(default `'ALL'`)

- `ALL`
  All – Show all objects in the view layer.
- `VISIBLE`
  Visible – Show visible objects.
- `SELECTED`
  Selected – Show selected objects.
- `ACTIVE`
  Active – Show only the active object.
- `SELECTABLE`
  Selectable – Show only selectable objects.

**Type:**

Literal[‘ALL’, ‘VISIBLE’, ‘SELECTED’, ‘ACTIVE’, ‘SELECTABLE’]

<a id="bpy.types.SpaceOutliner.filter_text"></a>

#### bpy.types.SpaceOutliner.filter_text

Live search filtering string (default “”, never None)

**Type:**

str

<a id="bpy.types.SpaceOutliner.lib_override_view_mode"></a>

#### bpy.types.SpaceOutliner.lib_override_view_mode

Choose different visualizations of library override data (default `'PROPERTIES'`)

- `PROPERTIES`
  Properties – Display all local override data-blocks with their overridden properties and buttons to edit them.
- `HIERARCHIES`
  Hierarchies – Display library override relationships.

**Type:**

Literal[‘PROPERTIES’, ‘HIERARCHIES’]

<a id="bpy.types.SpaceOutliner.scroll_to_active"></a>

#### bpy.types.SpaceOutliner.scroll_to_active

Scroll the active item into view when it changes outside of the Outliner (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.show_mode_column"></a>

#### bpy.types.SpaceOutliner.show_mode_column

Show the mode column for mode toggle and activation (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.show_restrict_column_enable"></a>

#### bpy.types.SpaceOutliner.show_restrict_column_enable

Exclude from view layer (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.show_restrict_column_hide"></a>

#### bpy.types.SpaceOutliner.show_restrict_column_hide

Temporarily hide in viewport (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.show_restrict_column_holdout"></a>

#### bpy.types.SpaceOutliner.show_restrict_column_holdout

Holdout (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.show_restrict_column_indirect_only"></a>

#### bpy.types.SpaceOutliner.show_restrict_column_indirect_only

Indirect only (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.show_restrict_column_render"></a>

#### bpy.types.SpaceOutliner.show_restrict_column_render

Globally disable in renders (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.show_restrict_column_select"></a>

#### bpy.types.SpaceOutliner.show_restrict_column_select

Selectable (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.show_restrict_column_viewport"></a>

#### bpy.types.SpaceOutliner.show_restrict_column_viewport

Globally disable in viewports (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_case_sensitive"></a>

#### bpy.types.SpaceOutliner.use_filter_case_sensitive

Only use case sensitive matches of search string (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_children"></a>

#### bpy.types.SpaceOutliner.use_filter_children

Show children (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_collection"></a>

#### bpy.types.SpaceOutliner.use_filter_collection

Show collections (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_complete"></a>

#### bpy.types.SpaceOutliner.use_filter_complete

Only use complete matches of search string (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_id_type"></a>

#### bpy.types.SpaceOutliner.use_filter_id_type

Show only data-blocks of one type (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_lib_override_system"></a>

#### bpy.types.SpaceOutliner.use_filter_lib_override_system

For libraries with overrides created, show the overridden values that are defined/controlled automatically (e.g. to make users of an overridden data-block point to the override data, not the original linked data) (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object"></a>

#### bpy.types.SpaceOutliner.use_filter_object

Show objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object_armature"></a>

#### bpy.types.SpaceOutliner.use_filter_object_armature

Show armature objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object_camera"></a>

#### bpy.types.SpaceOutliner.use_filter_object_camera

Show camera objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object_content"></a>

#### bpy.types.SpaceOutliner.use_filter_object_content

Show what is inside the objects elements (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object_empty"></a>

#### bpy.types.SpaceOutliner.use_filter_object_empty

Show empty objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object_grease_pencil"></a>

#### bpy.types.SpaceOutliner.use_filter_object_grease_pencil

Show Grease Pencil objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object_light"></a>

#### bpy.types.SpaceOutliner.use_filter_object_light

Show light objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object_mesh"></a>

#### bpy.types.SpaceOutliner.use_filter_object_mesh

Show mesh objects (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_object_others"></a>

#### bpy.types.SpaceOutliner.use_filter_object_others

Show curves, lattices, light probes, fonts, … (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_filter_view_layers"></a>

#### bpy.types.SpaceOutliner.use_filter_view_layers

Show all the view layers (default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_sort_alpha"></a>

#### bpy.types.SpaceOutliner.use_sort_alpha

(default True)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.use_sync_select"></a>

#### bpy.types.SpaceOutliner.use_sync_select

Sync outliner selection with other editors (default False)

**Type:**

bool

<a id="bpy.types.SpaceOutliner.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SpaceOutliner.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SpaceOutliner.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SpaceOutliner.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="bpy.types.SpaceOutliner.draw_handler_add"></a>

#### classmethod bpy.types.SpaceOutliner.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.SpaceOutliner.draw_handler_remove"></a>

#### classmethod bpy.types.SpaceOutliner.draw_handler_remove(handler, region_type)

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
