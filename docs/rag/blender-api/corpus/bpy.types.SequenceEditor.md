<!-- source: Blender Python API reference 5.2 / bpy.types.SequenceEditor.html -->

<a id="sequenceeditor-bpy-struct"></a>

# SequenceEditor(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.SequenceEditor"></a>

### class bpy.types.SequenceEditor(bpy_struct)

Sequence editing data for a Scene data-block

<a id="bpy.types.SequenceEditor.active_strip"></a>

#### bpy.types.SequenceEditor.active_strip

Sequencer’s active strip

**Type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip") | None

<a id="bpy.types.SequenceEditor.cache_final_size"></a>

#### bpy.types.SequenceEditor.cache_final_size

Size of final rendered images cache in megabytes (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.SequenceEditor.cache_raw_size"></a>

#### bpy.types.SequenceEditor.cache_raw_size

Size of raw source images cache in megabytes (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.SequenceEditor.channels"></a>

#### bpy.types.SequenceEditor.channels

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`SequenceTimelineChannel`](bpy.types.SequenceTimelineChannel.md#bpy.types.SequenceTimelineChannel "bpy.types.SequenceTimelineChannel")]

<a id="bpy.types.SequenceEditor.meta_stack"></a>

#### bpy.types.SequenceEditor.meta_stack

Meta strip stack, last is currently edited meta strip (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")]

<a id="bpy.types.SequenceEditor.overlay_frame"></a>

#### bpy.types.SequenceEditor.overlay_frame

Number of frames to offset (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.SequenceEditor.proxy_dir"></a>

#### bpy.types.SequenceEditor.proxy_dir

(default “”, never None, blend relative `//` prefix supported)

**Type:**

str

<a id="bpy.types.SequenceEditor.proxy_storage"></a>

#### bpy.types.SequenceEditor.proxy_storage

How to store proxies for this project (default `'PER_STRIP'`)

- `PER_STRIP`
  Per Strip – Store proxies using per strip settings.
- `PROJECT`
  Project – Store proxies using project directory.

**Type:**

Literal[‘PER_STRIP’, ‘PROJECT’]

<a id="bpy.types.SequenceEditor.selected_retiming_keys"></a>

#### bpy.types.SequenceEditor.selected_retiming_keys

(default False, readonly)

**Type:**

bool

<a id="bpy.types.SequenceEditor.show_missing_media"></a>

#### bpy.types.SequenceEditor.show_missing_media

Render missing images/movies with a solid magenta color (default False)

**Type:**

bool

<a id="bpy.types.SequenceEditor.show_overlay_frame"></a>

#### bpy.types.SequenceEditor.show_overlay_frame

Partial overlay on top of the sequencer with a frame offset (default False)

**Type:**

bool

<a id="bpy.types.SequenceEditor.strips"></a>

#### bpy.types.SequenceEditor.strips

Top-level strips only (default None, readonly)

**Type:**

[`StripsTopLevel`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel "bpy.types.StripsTopLevel")[[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")]

<a id="bpy.types.SequenceEditor.strips_all"></a>

#### bpy.types.SequenceEditor.strips_all

All strips, recursively including those inside metastrips (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")]

<a id="bpy.types.SequenceEditor.use_cache_final"></a>

#### bpy.types.SequenceEditor.use_cache_final

Cache final image for each frame (default False)

**Type:**

bool

<a id="bpy.types.SequenceEditor.use_cache_raw"></a>

#### bpy.types.SequenceEditor.use_cache_raw

Cache raw images read from disk, for faster tweaking of strip parameters at the cost of memory usage (default False)

**Type:**

bool

<a id="bpy.types.SequenceEditor.use_overlay_frame_lock"></a>

#### bpy.types.SequenceEditor.use_overlay_frame_lock

(default False)

**Type:**

bool

<a id="bpy.types.SequenceEditor.use_prefetch"></a>

#### bpy.types.SequenceEditor.use_prefetch

Render frames ahead of current frame in the background for faster playback (default False)

**Type:**

bool

<a id="bpy.types.SequenceEditor.display_stack"></a>

#### bpy.types.SequenceEditor.display_stack(meta_sequence)

Display strips stack

**Parameters:**

**meta_sequence** ([`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip") | None) – Meta Strip, Meta to display its stack

<a id="bpy.types.SequenceEditor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SequenceEditor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SequenceEditor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SequenceEditor.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Scene.sequence_editor`](bpy.types.Scene.md#bpy.types.Scene.sequence_editor "bpy.types.Scene.sequence_editor") | - [`Scene.sequence_editor_create`](bpy.types.Scene.md#bpy.types.Scene.sequence_editor_create "bpy.types.Scene.sequence_editor_create") |
