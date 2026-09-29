<!-- source: Blender Python API reference 5.2 / bpy.types.Space.html -->

<a id="space-bpy-struct"></a>

# Space(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [SpaceClipEditor(Space)](bpy.types.SpaceClipEditor.md)
- [SpaceConsole(Space)](bpy.types.SpaceConsole.md)
- [SpaceDopeSheetEditor(Space)](bpy.types.SpaceDopeSheetEditor.md)
- [SpaceFileBrowser(Space)](bpy.types.SpaceFileBrowser.md)
- [SpaceGraphEditor(Space)](bpy.types.SpaceGraphEditor.md)
- [SpaceImageEditor(Space)](bpy.types.SpaceImageEditor.md)
- [SpaceInfo(Space)](bpy.types.SpaceInfo.md)
- [SpaceNLA(Space)](bpy.types.SpaceNLA.md)
- [SpaceNodeEditor(Space)](bpy.types.SpaceNodeEditor.md)
- [SpaceOutliner(Space)](bpy.types.SpaceOutliner.md)
- [SpacePreferences(Space)](bpy.types.SpacePreferences.md)
- [SpaceProperties(Space)](bpy.types.SpaceProperties.md)
- [SpaceSequenceEditor(Space)](bpy.types.SpaceSequenceEditor.md)
- [SpaceSpreadsheet(Space)](bpy.types.SpaceSpreadsheet.md)
- [SpaceTextEditor(Space)](bpy.types.SpaceTextEditor.md)
- [SpaceView3D(Space)](bpy.types.SpaceView3D.md)

<a id="bpy.types.Space"></a>

### class bpy.types.Space(bpy_struct)

Space data for a screen area

<a id="bpy.types.Space.show_locked_time"></a>

#### bpy.types.Space.show_locked_time

Synchronize the visible timeline range with other time-based editors (default False)

**Type:**

bool

<a id="bpy.types.Space.show_region_header"></a>

#### bpy.types.Space.show_region_header

(default False)

**Type:**

bool

<a id="bpy.types.Space.type"></a>

#### bpy.types.Space.type

Space data type (default `'EMPTY'`, readonly)

**Type:**

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]

<a id="bpy.types.Space.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Space.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Space.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Space.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Space.type "bpy.types.Space.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Space.type "bpy.types.Space.type")

<a id="bpy.types.Space.draw_handler_add"></a>

#### classmethod bpy.types.Space.draw_handler_add(callback, args, region_type, draw_type)

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

<a id="bpy.types.Space.draw_handler_remove"></a>

#### classmethod bpy.types.Space.draw_handler_remove(handler, region_type)

Remove a draw handler that was added previously.

**Parameters:**

- **handler** (object) – The draw handler that should be removed.
- **region_type** (str) – Region type the callback was added to.

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
| - [`Area.spaces`](bpy.types.Area.md#bpy.types.Area.spaces "bpy.types.Area.spaces") - [`AreaSpaces.active`](bpy.types.AreaSpaces.md#bpy.types.AreaSpaces.active "bpy.types.AreaSpaces.active") | - [`Context.space_data`](bpy.types.Context.md#bpy.types.Context.space_data "bpy.types.Context.space_data") |
