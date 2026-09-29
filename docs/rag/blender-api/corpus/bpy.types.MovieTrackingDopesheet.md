<!-- source: Blender Python API reference 5.2 / bpy.types.MovieTrackingDopesheet.html -->

<a id="movietrackingdopesheet-bpy-struct"></a>

# MovieTrackingDopesheet(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MovieTrackingDopesheet"></a>

### class bpy.types.MovieTrackingDopesheet(bpy_struct)

Match-moving dopesheet data

<a id="bpy.types.MovieTrackingDopesheet.show_hidden"></a>

#### bpy.types.MovieTrackingDopesheet.show_hidden

Include channels from objects/bone that are not visible (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingDopesheet.show_only_selected"></a>

#### bpy.types.MovieTrackingDopesheet.show_only_selected

Only include channels relating to selected objects and data (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingDopesheet.sort_method"></a>

#### bpy.types.MovieTrackingDopesheet.sort_method

Method to be used to sort channels in dopesheet view (default `'NAME'`)

- `NAME`
  Name – Sort channels by their names.
- `LONGEST`
  Longest – Sort channels by longest tracked segment.
- `TOTAL`
  Total – Sort channels by overall amount of tracked segments.
- `AVERAGE_ERROR`
  Average Error – Sort channels by average reprojection error of tracks after solve.
- `START`
  Start Frame – Sort channels by first frame number.
- `END`
  End Frame – Sort channels by last frame number.

**Type:**

Literal[‘NAME’, ‘LONGEST’, ‘TOTAL’, ‘AVERAGE_ERROR’, ‘START’, ‘END’]

<a id="bpy.types.MovieTrackingDopesheet.use_invert_sort"></a>

#### bpy.types.MovieTrackingDopesheet.use_invert_sort

Invert sort order of dopesheet channels (default False)

**Type:**

bool

<a id="bpy.types.MovieTrackingDopesheet.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MovieTrackingDopesheet.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MovieTrackingDopesheet.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MovieTrackingDopesheet.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MovieTracking.dopesheet`](bpy.types.MovieTracking.md#bpy.types.MovieTracking.dopesheet "bpy.types.MovieTracking.dopesheet") |  |
