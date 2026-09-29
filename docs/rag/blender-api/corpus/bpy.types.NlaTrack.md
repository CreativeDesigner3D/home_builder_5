<!-- source: Blender Python API reference 5.2 / bpy.types.NlaTrack.html -->

<a id="nlatrack-bpy-struct"></a>

# NlaTrack(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.NlaTrack"></a>

### class bpy.types.NlaTrack(bpy_struct)

An animation layer containing Actions referenced as NLA strips

<a id="bpy.types.NlaTrack.active"></a>

#### bpy.types.NlaTrack.active

NLA Track is active (default False, readonly)

**Type:**

bool

<a id="bpy.types.NlaTrack.is_override_data"></a>

#### bpy.types.NlaTrack.is_override_data

In a local override data, whether this NLA track comes from the linked reference data, or is local to the override (default True, readonly)

**Type:**

bool

<a id="bpy.types.NlaTrack.is_solo"></a>

#### bpy.types.NlaTrack.is_solo

NLA Track is evaluated itself (i.e. active Action and all other NLA Tracks in the same AnimData block are disabled) (default False)

**Type:**

bool

<a id="bpy.types.NlaTrack.lock"></a>

#### bpy.types.NlaTrack.lock

NLA Track is locked (default False)

**Type:**

bool

<a id="bpy.types.NlaTrack.mute"></a>

#### bpy.types.NlaTrack.mute

Disable NLA Track evaluation (default False)

**Type:**

bool

<a id="bpy.types.NlaTrack.name"></a>

#### bpy.types.NlaTrack.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.NlaTrack.select"></a>

#### bpy.types.NlaTrack.select

NLA Track is selected (default False)

**Type:**

bool

<a id="bpy.types.NlaTrack.strips"></a>

#### bpy.types.NlaTrack.strips

NLA Strips on this NLA-track (default None, readonly)

**Type:**

[`NlaStrips`](bpy.types.NlaStrips.md#bpy.types.NlaStrips "bpy.types.NlaStrips")[[`NlaStrip`](bpy.types.NlaStrip.md#bpy.types.NlaStrip "bpy.types.NlaStrip")]

<a id="bpy.types.NlaTrack.bl_rna_get_subclass"></a>

#### classmethod bpy.types.NlaTrack.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.NlaTrack.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.NlaTrack.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.active_nla_track` - [`AnimData.nla_tracks`](bpy.types.AnimData.md#bpy.types.AnimData.nla_tracks "bpy.types.AnimData.nla_tracks") - [`NlaTracks.active`](bpy.types.NlaTracks.md#bpy.types.NlaTracks.active "bpy.types.NlaTracks.active") | - [`NlaTracks.new`](bpy.types.NlaTracks.md#bpy.types.NlaTracks.new "bpy.types.NlaTracks.new") - [`NlaTracks.new`](bpy.types.NlaTracks.md#bpy.types.NlaTracks.new "bpy.types.NlaTracks.new") - [`NlaTracks.remove`](bpy.types.NlaTracks.md#bpy.types.NlaTracks.remove "bpy.types.NlaTracks.remove") |
