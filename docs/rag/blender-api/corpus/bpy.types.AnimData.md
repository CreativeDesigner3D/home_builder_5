<!-- source: Blender Python API reference 5.2 / bpy.types.AnimData.html -->

<a id="animdata-bpy-struct"></a>

# AnimData(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.AnimData"></a>

### class bpy.types.AnimData(bpy_struct)

Animation data for data-block

<a id="bpy.types.AnimData.action"></a>

#### bpy.types.AnimData.action

Active Action for this data-block

**Type:**

[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None

<a id="bpy.types.AnimData.action_blend_type"></a>

#### bpy.types.AnimData.action_blend_type

Method used for combining Active Action’s result with result of NLA stack (default `'REPLACE'`)

- `REPLACE`
  Replace – The strip values replace the accumulated results by amount specified by influence.
- `COMBINE`
  Combine – The strip values are combined with accumulated results by appropriately using addition, multiplication, or quaternion math, based on channel type.
- `ADD`
  Add – Weighted result of strip is added to the accumulated results.
- `SUBTRACT`
  Subtract – Weighted result of strip is removed from the accumulated results.
- `MULTIPLY`
  Multiply – Weighted result of strip is multiplied with the accumulated results.

**Type:**

Literal[‘REPLACE’, ‘COMBINE’, ‘ADD’, ‘SUBTRACT’, ‘MULTIPLY’]

<a id="bpy.types.AnimData.action_extrapolation"></a>

#### bpy.types.AnimData.action_extrapolation

Action to take for gaps past the Active Action’s range (when evaluating with NLA) (default `'HOLD'`)

- `NOTHING`
  Nothing – Strip has no influence past its extents.
- `HOLD`
  Hold – Hold the first frame if no previous strips in track, and always hold last frame.
- `HOLD_FORWARD`
  Hold Forward – Only hold last frame.

**Type:**

Literal[‘NOTHING’, ‘HOLD’, ‘HOLD_FORWARD’]

<a id="bpy.types.AnimData.action_influence"></a>

#### bpy.types.AnimData.action_influence

Amount the Active Action contributes to the result of the NLA stack (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.AnimData.action_slot"></a>

#### bpy.types.AnimData.action_slot

The slot identifies which sub-set of the Action is considered to be for this data-block, and its name is used to find the right slot when assigning an Action

**Type:**

[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot") | None

<a id="bpy.types.AnimData.action_slot_handle"></a>

#### bpy.types.AnimData.action_slot_handle

A number that identifies which sub-set of the Action is considered to be for this data-block (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.AnimData.action_slot_handle_tweak_storage"></a>

#### bpy.types.AnimData.action_slot_handle_tweak_storage

Storage to temporarily hold the main action slot while in tweak mode (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.AnimData.action_suitable_slots"></a>

#### bpy.types.AnimData.action_suitable_slots

The list of slots in this animation data-block (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ActionSlot`](bpy.types.ActionSlot.md#bpy.types.ActionSlot "bpy.types.ActionSlot")]

<a id="bpy.types.AnimData.action_tweak_storage"></a>

#### bpy.types.AnimData.action_tweak_storage

Storage to temporarily hold the main action while in tweak mode

**Type:**

[`Action`](bpy.types.Action.md#bpy.types.Action "bpy.types.Action") | None

<a id="bpy.types.AnimData.drivers"></a>

#### bpy.types.AnimData.drivers

The Drivers/Expressions for this data-block (default None, readonly)

**Type:**

[`AnimDataDrivers`](bpy.types.AnimDataDrivers.md#bpy.types.AnimDataDrivers "bpy.types.AnimDataDrivers")[[`FCurve`](bpy.types.FCurve.md#bpy.types.FCurve "bpy.types.FCurve")]

<a id="bpy.types.AnimData.last_slot_identifier"></a>

#### bpy.types.AnimData.last_slot_identifier

The identifier of the most recently assigned action slot. The slot identifies which sub-set of the Action is considered to be for this data-block, and its identifier is used to find the right slot when assigning an Action. (default “”, never None)

**Type:**

str

<a id="bpy.types.AnimData.nla_tracks"></a>

#### bpy.types.AnimData.nla_tracks

NLA Tracks (i.e. Animation Layers) (default None, readonly)

**Type:**

[`NlaTracks`](bpy.types.NlaTracks.md#bpy.types.NlaTracks "bpy.types.NlaTracks")[[`NlaTrack`](bpy.types.NlaTrack.md#bpy.types.NlaTrack "bpy.types.NlaTrack")]

<a id="bpy.types.AnimData.use_nla"></a>

#### bpy.types.AnimData.use_nla

NLA stack is evaluated when evaluating this block (default True)

**Type:**

bool

<a id="bpy.types.AnimData.use_pin"></a>

#### bpy.types.AnimData.use_pin

(default False)

**Type:**

bool

<a id="bpy.types.AnimData.use_tweak_mode"></a>

#### bpy.types.AnimData.use_tweak_mode

Whether to enable or disable tweak mode in NLA (default False)

**Type:**

bool

<a id="bpy.types.AnimData.nla_tweak_strip_time_to_scene"></a>

#### bpy.types.AnimData.nla_tweak_strip_time_to_scene(frame, *, invert=False)

Convert a time value from the local time of the tweaked strip to scene time, exactly as done by built-in key editing tools. Returns the input time unchanged if not tweaking.

**Parameters:**

- **frame** (float) – Input time (in [-1.04857e+06, 1.04857e+06])
- **invert** (bool) – Invert, Convert scene time to action time (optional)

**Returns:**

Converted time (in [-1.04857e+06, 1.04857e+06])

**Return type:**

float

<a id="bpy.types.AnimData.fix_paths_rename_all"></a>

#### bpy.types.AnimData.fix_paths_rename_all(*, prefix='', old_name='', new_name='')

Rename the property paths in the animation system, since properties are animated via string paths, it’s needed to keep them valid after properties has been renamed

**Parameters:**

- **prefix** (str) – Prefix, Name prefix (optional, never None)
- **old_name** (str) – Old Name, Old name (optional, never None)
- **new_name** (str) – New Name, New name (optional, never None)

<a id="bpy.types.AnimData.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AnimData.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AnimData.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AnimData.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Annotation.animation_data`](bpy.types.Annotation.md#bpy.types.Annotation.animation_data "bpy.types.Annotation.animation_data") - [`Armature.animation_data`](bpy.types.Armature.md#bpy.types.Armature.animation_data "bpy.types.Armature.animation_data") - [`CacheFile.animation_data`](bpy.types.CacheFile.md#bpy.types.CacheFile.animation_data "bpy.types.CacheFile.animation_data") - [`Camera.animation_data`](bpy.types.Camera.md#bpy.types.Camera.animation_data "bpy.types.Camera.animation_data") - [`Curve.animation_data`](bpy.types.Curve.md#bpy.types.Curve.animation_data "bpy.types.Curve.animation_data") - [`Curves.animation_data`](bpy.types.Curves.md#bpy.types.Curves.animation_data "bpy.types.Curves.animation_data") - [`FreestyleLineStyle.animation_data`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle.animation_data "bpy.types.FreestyleLineStyle.animation_data") - [`GreasePencil.animation_data`](bpy.types.GreasePencil.md#bpy.types.GreasePencil.animation_data "bpy.types.GreasePencil.animation_data") - [`ID.animation_data_create`](bpy.types.ID.md#bpy.types.ID.animation_data_create "bpy.types.ID.animation_data_create") - [`Key.animation_data`](bpy.types.Key.md#bpy.types.Key.animation_data "bpy.types.Key.animation_data") - [`Lattice.animation_data`](bpy.types.Lattice.md#bpy.types.Lattice.animation_data "bpy.types.Lattice.animation_data") - [`Light.animation_data`](bpy.types.Light.md#bpy.types.Light.animation_data "bpy.types.Light.animation_data") - [`LightProbe.animation_data`](bpy.types.LightProbe.md#bpy.types.LightProbe.animation_data "bpy.types.LightProbe.animation_data") - [`Mask.animation_data`](bpy.types.Mask.md#bpy.types.Mask.animation_data "bpy.types.Mask.animation_data") | - [`Material.animation_data`](bpy.types.Material.md#bpy.types.Material.animation_data "bpy.types.Material.animation_data") - [`Mesh.animation_data`](bpy.types.Mesh.md#bpy.types.Mesh.animation_data "bpy.types.Mesh.animation_data") - [`MetaBall.animation_data`](bpy.types.MetaBall.md#bpy.types.MetaBall.animation_data "bpy.types.MetaBall.animation_data") - [`MovieClip.animation_data`](bpy.types.MovieClip.md#bpy.types.MovieClip.animation_data "bpy.types.MovieClip.animation_data") - [`NodeTree.animation_data`](bpy.types.NodeTree.md#bpy.types.NodeTree.animation_data "bpy.types.NodeTree.animation_data") - [`Object.animation_data`](bpy.types.Object.md#bpy.types.Object.animation_data "bpy.types.Object.animation_data") - [`ParticleSettings.animation_data`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.animation_data "bpy.types.ParticleSettings.animation_data") - [`PointCloud.animation_data`](bpy.types.PointCloud.md#bpy.types.PointCloud.animation_data "bpy.types.PointCloud.animation_data") - [`Scene.animation_data`](bpy.types.Scene.md#bpy.types.Scene.animation_data "bpy.types.Scene.animation_data") - [`Speaker.animation_data`](bpy.types.Speaker.md#bpy.types.Speaker.animation_data "bpy.types.Speaker.animation_data") - [`Texture.animation_data`](bpy.types.Texture.md#bpy.types.Texture.animation_data "bpy.types.Texture.animation_data") - [`Volume.animation_data`](bpy.types.Volume.md#bpy.types.Volume.animation_data "bpy.types.Volume.animation_data") - [`World.animation_data`](bpy.types.World.md#bpy.types.World.animation_data "bpy.types.World.animation_data") |
