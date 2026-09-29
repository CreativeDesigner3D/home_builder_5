<!-- source: Blender Python API reference 5.2 / bpy.types.TimelineMarker.html -->

<a id="timelinemarker-bpy-struct"></a>

# TimelineMarker(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.TimelineMarker"></a>

### class bpy.types.TimelineMarker(bpy_struct)

Marker for noting points in the timeline

<a id="bpy.types.TimelineMarker.camera"></a>

#### bpy.types.TimelineMarker.camera

Camera that becomes active on this frame

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.TimelineMarker.frame"></a>

#### bpy.types.TimelineMarker.frame

The frame on which the timeline marker appears (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.TimelineMarker.name"></a>

#### bpy.types.TimelineMarker.name

(default “”, never None)

**Type:**

str

<a id="bpy.types.TimelineMarker.select"></a>

#### bpy.types.TimelineMarker.select

Marker selection state (default False)

**Type:**

bool

<a id="bpy.types.TimelineMarker.bl_system_properties_get"></a>

#### bpy.types.TimelineMarker.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.TimelineMarker.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TimelineMarker.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TimelineMarker.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TimelineMarker.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Action.pose_markers`](bpy.types.Action.md#bpy.types.Action.pose_markers "bpy.types.Action.pose_markers") - [`ActionPoseMarkers.active`](bpy.types.ActionPoseMarkers.md#bpy.types.ActionPoseMarkers.active "bpy.types.ActionPoseMarkers.active") - [`ActionPoseMarkers.new`](bpy.types.ActionPoseMarkers.md#bpy.types.ActionPoseMarkers.new "bpy.types.ActionPoseMarkers.new") - [`ActionPoseMarkers.remove`](bpy.types.ActionPoseMarkers.md#bpy.types.ActionPoseMarkers.remove "bpy.types.ActionPoseMarkers.remove") | - [`Scene.timeline_markers`](bpy.types.Scene.md#bpy.types.Scene.timeline_markers "bpy.types.Scene.timeline_markers") - [`TimelineMarkers.new`](bpy.types.TimelineMarkers.md#bpy.types.TimelineMarkers.new "bpy.types.TimelineMarkers.new") - [`TimelineMarkers.remove`](bpy.types.TimelineMarkers.md#bpy.types.TimelineMarkers.remove "bpy.types.TimelineMarkers.remove") |
