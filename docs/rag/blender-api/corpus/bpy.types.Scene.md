<!-- source: Blender Python API reference 5.2 / bpy.types.Scene.html -->

<a id="scene-id"></a>

# Scene(ID)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Scene"></a>

### class bpy.types.Scene(ID)

Scene data-block, consisting in objects and defining time and render related settings

<a id="bpy.types.Scene.active_clip"></a>

#### bpy.types.Scene.active_clip

Active Movie Clip that can be used by motion tracking constraints or as a camera’s background image

**Type:**

[`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip") | None

<a id="bpy.types.Scene.allow_preroll"></a>

#### bpy.types.Scene.allow_preroll

Allows playing back frames before the playback start frame (default False)

**Type:**

bool

<a id="bpy.types.Scene.animation_data"></a>

#### bpy.types.Scene.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Scene.annotation"></a>

#### bpy.types.Scene.annotation

Data-block used for annotations in the 3D view

**Type:**

[`Annotation`](bpy.types.Annotation.md#bpy.types.Annotation "bpy.types.Annotation") | None

<a id="bpy.types.Scene.audio_distance_model"></a>

#### bpy.types.Scene.audio_distance_model

Distance model for distance attenuation calculation (default `'INVERSE_CLAMPED'`)

- `NONE`
  None – No distance attenuation.
- `INVERSE`
  Inverse – Inverse distance model.
- `INVERSE_CLAMPED`
  Inverse Clamped – Inverse distance model with clamping.
- `LINEAR`
  Linear – Linear distance model.
- `LINEAR_CLAMPED`
  Linear Clamped – Linear distance model with clamping.
- `EXPONENT`
  Exponential – Exponential distance model.
- `EXPONENT_CLAMPED`
  Exponential Clamped – Exponential distance model with clamping.

**Type:**

Literal[‘NONE’, ‘INVERSE’, ‘INVERSE_CLAMPED’, ‘LINEAR’, ‘LINEAR_CLAMPED’, ‘EXPONENT’, ‘EXPONENT_CLAMPED’]

<a id="bpy.types.Scene.audio_doppler_factor"></a>

#### bpy.types.Scene.audio_doppler_factor

Pitch factor for Doppler effect calculation (in [0, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Scene.audio_doppler_speed"></a>

#### bpy.types.Scene.audio_doppler_speed

Speed of sound for Doppler effect calculation (in [0.01, inf], default 343.3)

**Type:**

float

<a id="bpy.types.Scene.audio_volume"></a>

#### bpy.types.Scene.audio_volume

Audio volume (in [0, 100], default 1.0)

**Type:**

float

<a id="bpy.types.Scene.background_set"></a>

#### bpy.types.Scene.background_set

Background set scene

**Type:**

[`Scene`](#bpy.types.Scene "bpy.types.Scene") | None

<a id="bpy.types.Scene.camera"></a>

#### bpy.types.Scene.camera

Active camera, used for rendering the scene

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.Scene.collection"></a>

#### bpy.types.Scene.collection

Scene root collection that owns all the objects and other collections instantiated in the scene (readonly, never None)

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection")

<a id="bpy.types.Scene.compositing_node_group"></a>

#### bpy.types.Scene.compositing_node_group

Compositor Nodes

**Type:**

[`NodeTree`](bpy.types.NodeTree.md#bpy.types.NodeTree "bpy.types.NodeTree") | None

<a id="bpy.types.Scene.cursor"></a>

#### bpy.types.Scene.cursor

(readonly, never None)

**Type:**

[`View3DCursor`](bpy.types.View3DCursor.md#bpy.types.View3DCursor "bpy.types.View3DCursor")

<a id="bpy.types.Scene.cycles"></a>

#### bpy.types.Scene.cycles

Cycles render settings (readonly)

**Type:**

`CyclesRenderSettings` | None

<a id="bpy.types.Scene.cycles_curves"></a>

#### bpy.types.Scene.cycles_curves

Cycles curves rendering settings (readonly)

**Type:**

`CyclesCurveRenderSettings` | None

<a id="bpy.types.Scene.display"></a>

#### bpy.types.Scene.display

Scene display settings for 3D viewport (readonly)

**Type:**

[`SceneDisplay`](bpy.types.SceneDisplay.md#bpy.types.SceneDisplay "bpy.types.SceneDisplay") | None

<a id="bpy.types.Scene.display_settings"></a>

#### bpy.types.Scene.display_settings

Settings of device saved image would be displayed on (readonly)

**Type:**

[`ColorManagedDisplaySettings`](bpy.types.ColorManagedDisplaySettings.md#bpy.types.ColorManagedDisplaySettings "bpy.types.ColorManagedDisplaySettings") | None

<a id="bpy.types.Scene.eevee"></a>

#### bpy.types.Scene.eevee

EEVEE settings for the scene (readonly)

**Type:**

[`SceneEEVEE`](bpy.types.SceneEEVEE.md#bpy.types.SceneEEVEE "bpy.types.SceneEEVEE") | None

<a id="bpy.types.Scene.frame_current"></a>

#### bpy.types.Scene.frame_current

Current frame, to update animation data from Python frame_set() instead (in [-1048574, 1048574], default 1)

**Type:**

int

<a id="bpy.types.Scene.frame_current_final"></a>

#### bpy.types.Scene.frame_current_final

Current frame with subframe and time remapping applied (in [-1.04857e+06, 1.04857e+06], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.Scene.frame_end"></a>

#### bpy.types.Scene.frame_end

Final frame of the playback/rendering range (in [0, 1048574], default 250)

**Type:**

int

<a id="bpy.types.Scene.frame_float"></a>

#### bpy.types.Scene.frame_float

(in [-1.04857e+06, 1.04857e+06], default 0.0)

**Type:**

float

<a id="bpy.types.Scene.frame_preview_end"></a>

#### bpy.types.Scene.frame_preview_end

Alternative end frame for UI playback (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Scene.frame_preview_start"></a>

#### bpy.types.Scene.frame_preview_start

Alternative start frame for UI playback (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Scene.frame_start"></a>

#### bpy.types.Scene.frame_start

First frame of the playback/rendering range (in [0, 1048574], default 1)

**Type:**

int

<a id="bpy.types.Scene.frame_step"></a>

#### bpy.types.Scene.frame_step

Number of frames to skip forward while rendering/playing back each frame (in [0, 1048574], default 1)

**Type:**

int

<a id="bpy.types.Scene.frame_subframe"></a>

#### bpy.types.Scene.frame_subframe

(in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.Scene.gravity"></a>

#### bpy.types.Scene.gravity

Constant acceleration in a given direction (array of 3 items, in [-inf, inf], default (0.0, 0.0, -9.81))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Scene.grease_pencil_settings"></a>

#### bpy.types.Scene.grease_pencil_settings

Grease Pencil settings for the scene (readonly)

**Type:**

[`SceneGpencil`](bpy.types.SceneGpencil.md#bpy.types.SceneGpencil "bpy.types.SceneGpencil") | None

<a id="bpy.types.Scene.hydra"></a>

#### bpy.types.Scene.hydra

Hydra settings for the scene (readonly)

**Type:**

[`SceneHydra`](bpy.types.SceneHydra.md#bpy.types.SceneHydra "bpy.types.SceneHydra") | None

<a id="bpy.types.Scene.is_nla_tweakmode"></a>

#### bpy.types.Scene.is_nla_tweakmode

Whether there is any action referenced by NLA being edited (strictly read-only) (default False, readonly)

**Type:**

bool

<a id="bpy.types.Scene.keying_sets"></a>

#### bpy.types.Scene.keying_sets

Absolute Keying Sets for this Scene (default None, readonly)

**Type:**

[`KeyingSets`](bpy.types.KeyingSets.md#bpy.types.KeyingSets "bpy.types.KeyingSets")[[`KeyingSet`](bpy.types.KeyingSet.md#bpy.types.KeyingSet "bpy.types.KeyingSet")]

<a id="bpy.types.Scene.keying_sets_all"></a>

#### bpy.types.Scene.keying_sets_all

All Keying Sets available for use (Builtins and Absolute Keying Sets for this Scene) (default None, readonly)

**Type:**

[`KeyingSetsAll`](bpy.types.KeyingSetsAll.md#bpy.types.KeyingSetsAll "bpy.types.KeyingSetsAll")[[`KeyingSet`](bpy.types.KeyingSet.md#bpy.types.KeyingSet "bpy.types.KeyingSet")]

<a id="bpy.types.Scene.lock_frame_selection_to_range"></a>

#### bpy.types.Scene.lock_frame_selection_to_range

Don’t allow frame to be selected with mouse outside of frame range (default False)

**Type:**

bool

<a id="bpy.types.Scene.objects"></a>

#### bpy.types.Scene.objects

(default None, readonly)

**Type:**

[`SceneObjects`](bpy.types.SceneObjects.md#bpy.types.SceneObjects "bpy.types.SceneObjects")[[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]

<a id="bpy.types.Scene.playback_loop_mode"></a>

#### bpy.types.Scene.playback_loop_mode

What to do when playback reaches the last frame (default `'INFINITE'`)

- `INFINITE`
  Infinite – After the last frame, jump back to the first and keep playing, infinitely.
- `STOP_END_FRAME`
  Stop at End Frame – Stop playback at the last frame, without looping.
- `STOP_START_FRAME`
  Stop at Start Frame – After the last frame, jump back to the first and stop playback.
- `RESTORE`
  Restore Frame – After the last frame, stop at the frame the playback started from.
- `BOUNCE`
  Bounce – At the last frame, reverse playback.

**Type:**

Literal[‘INFINITE’, ‘STOP_END_FRAME’, ‘STOP_START_FRAME’, ‘RESTORE’, ‘BOUNCE’]

<a id="bpy.types.Scene.render"></a>

#### bpy.types.Scene.render

(readonly, never None)

**Type:**

[`RenderSettings`](bpy.types.RenderSettings.md#bpy.types.RenderSettings "bpy.types.RenderSettings")

<a id="bpy.types.Scene.rigidbody_world"></a>

#### bpy.types.Scene.rigidbody_world

(readonly)

**Type:**

[`RigidBodyWorld`](bpy.types.RigidBodyWorld.md#bpy.types.RigidBodyWorld "bpy.types.RigidBodyWorld") | None

<a id="bpy.types.Scene.safe_areas"></a>

#### bpy.types.Scene.safe_areas

(readonly, never None)

**Type:**

[`DisplaySafeAreas`](bpy.types.DisplaySafeAreas.md#bpy.types.DisplaySafeAreas "bpy.types.DisplaySafeAreas")

<a id="bpy.types.Scene.sequence_editor"></a>

#### bpy.types.Scene.sequence_editor

(readonly)

**Type:**

[`SequenceEditor`](bpy.types.SequenceEditor.md#bpy.types.SequenceEditor "bpy.types.SequenceEditor") | None

<a id="bpy.types.Scene.sequencer_colorspace_settings"></a>

#### bpy.types.Scene.sequencer_colorspace_settings

Settings of color space sequencer is working in (readonly)

**Type:**

[`ColorManagedSequencerColorspaceSettings`](bpy.types.ColorManagedSequencerColorspaceSettings.md#bpy.types.ColorManagedSequencerColorspaceSettings "bpy.types.ColorManagedSequencerColorspaceSettings") | None

<a id="bpy.types.Scene.show_keys_from_selected_only"></a>

#### bpy.types.Scene.show_keys_from_selected_only

Only include channels relating to selected objects and data (default True)

**Type:**

bool

<a id="bpy.types.Scene.show_subframe"></a>

#### bpy.types.Scene.show_subframe

Display and allow setting fractional frame values for the current frame (default False)

**Type:**

bool

<a id="bpy.types.Scene.simulation_frame_end"></a>

#### bpy.types.Scene.simulation_frame_end

Frame at which simulations end (in [-inf, inf], default 250)

**Type:**

int

<a id="bpy.types.Scene.simulation_frame_start"></a>

#### bpy.types.Scene.simulation_frame_start

Frame at which simulations start (in [-inf, inf], default 1)

**Type:**

int

<a id="bpy.types.Scene.sync_mode"></a>

#### bpy.types.Scene.sync_mode

How to sync playback (default `'AUDIO_SYNC'`)

- `NONE`
  Play Every Frame – Do not sync, play every frame.
- `FRAME_DROP`
  Frame Dropping – Drop frames if playback is too slow.
- `AUDIO_SYNC`
  Sync to Audio – Sync to audio playback, dropping frames.

**Type:**

Literal[‘NONE’, ‘FRAME_DROP’, ‘AUDIO_SYNC’]

<a id="bpy.types.Scene.time_jump_delta"></a>

#### bpy.types.Scene.time_jump_delta

Number of frames or seconds to jump forward or backward (in [0.1, inf], default 1.0)

**Type:**

float

<a id="bpy.types.Scene.time_jump_unit"></a>

#### bpy.types.Scene.time_jump_unit

Which unit to use for time jumps in the timeline (default `'SECOND'`)

- `FRAME`
  Frame – Jump by frames.
- `SECOND`
  Second – Jump by seconds.

**Type:**

Literal[‘FRAME’, ‘SECOND’]

<a id="bpy.types.Scene.timeline_markers"></a>

#### bpy.types.Scene.timeline_markers

Markers used in all timelines for the current scene (default None, readonly)

**Type:**

[`TimelineMarkers`](bpy.types.TimelineMarkers.md#bpy.types.TimelineMarkers "bpy.types.TimelineMarkers")[[`TimelineMarker`](bpy.types.TimelineMarker.md#bpy.types.TimelineMarker "bpy.types.TimelineMarker")]

<a id="bpy.types.Scene.tool_settings"></a>

#### bpy.types.Scene.tool_settings

(readonly, never None)

**Type:**

[`ToolSettings`](bpy.types.ToolSettings.md#bpy.types.ToolSettings "bpy.types.ToolSettings")

<a id="bpy.types.Scene.transform_orientation_slots"></a>

#### bpy.types.Scene.transform_orientation_slots

(default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`TransformOrientationSlot`](bpy.types.TransformOrientationSlot.md#bpy.types.TransformOrientationSlot "bpy.types.TransformOrientationSlot")]

<a id="bpy.types.Scene.unit_settings"></a>

#### bpy.types.Scene.unit_settings

Unit editing settings (readonly, never None)

**Type:**

[`UnitSettings`](bpy.types.UnitSettings.md#bpy.types.UnitSettings "bpy.types.UnitSettings")

<a id="bpy.types.Scene.use_audio"></a>

#### bpy.types.Scene.use_audio

Play back of audio from Sequence Editor, otherwise mute audio (default False)

**Type:**

bool

<a id="bpy.types.Scene.use_audio_scrub"></a>

#### bpy.types.Scene.use_audio_scrub

Play audio from Sequence Editor while scrubbing (default False)

**Type:**

bool

<a id="bpy.types.Scene.use_custom_simulation_range"></a>

#### bpy.types.Scene.use_custom_simulation_range

Use a simulation range that is different from the scene range for simulation nodes that don’t override the frame range themselves (default False)

**Type:**

bool

<a id="bpy.types.Scene.use_gravity"></a>

#### bpy.types.Scene.use_gravity

Use global gravity for all dynamics (default True)

**Type:**

bool

<a id="bpy.types.Scene.use_nodes"></a>

#### bpy.types.Scene.use_nodes

Enable the compositing node group. (default False)

Deprecated since version 5.0: removal planned in version 6.0

Unused but kept for compatibility reasons. Setting the property has no effect, and getting it always returns True. Use #scene.render.use_compositing to turn compositing to enable or disable compositing.

**Type:**

bool

<a id="bpy.types.Scene.use_preview_range"></a>

#### bpy.types.Scene.use_preview_range

Use an alternative start/end frame range for animation playback and view renders (default False)

**Type:**

bool

<a id="bpy.types.Scene.use_stamp_note"></a>

#### bpy.types.Scene.use_stamp_note

User defined note for the render stamping (default “”, never None)

**Type:**

str

<a id="bpy.types.Scene.view_layers"></a>

#### bpy.types.Scene.view_layers

(default None, readonly)

**Type:**

[`ViewLayers`](bpy.types.ViewLayers.md#bpy.types.ViewLayers "bpy.types.ViewLayers")[[`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer")]

<a id="bpy.types.Scene.view_settings"></a>

#### bpy.types.Scene.view_settings

Color management settings applied on image before saving (readonly)

**Type:**

[`ColorManagedViewSettings`](bpy.types.ColorManagedViewSettings.md#bpy.types.ColorManagedViewSettings "bpy.types.ColorManagedViewSettings") | None

<a id="bpy.types.Scene.world"></a>

#### bpy.types.Scene.world

World used for rendering the scene

**Type:**

[`World`](bpy.types.World.md#bpy.types.World "bpy.types.World") | None

<a id="bpy.types.Scene.update_render_engine"></a>

#### classmethod bpy.types.Scene.update_render_engine()

Trigger a render engine update

<a id="bpy.types.Scene.statistics"></a>

#### bpy.types.Scene.statistics(view_layer)

statistics

**Parameters:**

**view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – View Layer, (never None)

**Returns:**

Statistics, (never None)

**Return type:**

str

<a id="bpy.types.Scene.frame_set"></a>

#### bpy.types.Scene.frame_set(frame, *, subframe=0.0)

Set scene frame updating all objects and view layers immediately

**Parameters:**

- **frame** (int) – Frame number to set (in [-1048574, 1048574])
- **subframe** (float) – Subframe time, between 0.0 and 1.0 (in [0, 1], optional)

<a id="bpy.types.Scene.uvedit_aspect"></a>

#### bpy.types.Scene.uvedit_aspect(object)

Get uv aspect for current object

**Parameters:**

**object** ([`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None) – Object (never None)

**Returns:**

aspect (array of 2 items, in [0, inf])

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Scene.ray_cast"></a>

#### bpy.types.Scene.ray_cast(depsgraph, origin, direction, *, distance=1.70141e+38)

Cast a ray onto evaluated geometry in world-space

**Parameters:**

- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – The current dependency graph (never None)
- **origin** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – (array of 3 items, in [-inf, inf])
- **direction** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – (array of 3 items, in [-inf, inf])
- **distance** (float) – Maximum distance (in [0, inf], optional)

**Returns:**

`result`, bool

`location`, The hit location of this ray cast, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`normal`, The face normal at the ray cast hit location, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`index`, The face index, -1 when original data isn’t available, int

`object`, The original (un-evaluated) object that was hit. Note that `location`, `normal`, and `index` correspond to the evaluated object’s mesh., [`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")

`matrix`, Matrix, [`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

**Return type:**

tuple[bool, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), int, [`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object"), [`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")]

<a id="bpy.types.Scene.sequence_editor_create"></a>

#### bpy.types.Scene.sequence_editor_create()

Ensure sequence editor is valid in this scene

**Returns:**

New sequence editor data or None

**Return type:**

[`SequenceEditor`](bpy.types.SequenceEditor.md#bpy.types.SequenceEditor "bpy.types.SequenceEditor")

<a id="bpy.types.Scene.sequence_editor_clear"></a>

#### bpy.types.Scene.sequence_editor_clear()

Clear sequence editor in this scene

<a id="bpy.types.Scene.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Scene.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Scene.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Scene.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

## References

|  |  |
| --- | --- |
| - `bpy.context.scene` - `bpy.context.sequencer_scene` - [`BlendData.scenes`](bpy.types.BlendData.md#bpy.types.BlendData.scenes "bpy.types.BlendData.scenes") - [`BlendDataScenes.new`](bpy.types.BlendDataScenes.md#bpy.types.BlendDataScenes.new "bpy.types.BlendDataScenes.new") - [`BlendDataScenes.remove`](bpy.types.BlendDataScenes.md#bpy.types.BlendDataScenes.remove "bpy.types.BlendDataScenes.remove") - [`Camera.view_frame`](bpy.types.Camera.md#bpy.types.Camera.view_frame "bpy.types.Camera.view_frame") - [`CompositorNodeCryptomatteV2.scene`](bpy.types.CompositorNodeCryptomatteV2.md#bpy.types.CompositorNodeCryptomatteV2.scene "bpy.types.CompositorNodeCryptomatteV2.scene") - [`CompositorNodeDefocus.scene`](bpy.types.CompositorNodeDefocus.md#bpy.types.CompositorNodeDefocus.scene "bpy.types.CompositorNodeDefocus.scene") - [`CompositorNodeRLayers.scene`](bpy.types.CompositorNodeRLayers.md#bpy.types.CompositorNodeRLayers.scene "bpy.types.CompositorNodeRLayers.scene") - [`Context.scene`](bpy.types.Context.md#bpy.types.Context.scene "bpy.types.Context.scene") - [`Depsgraph.scene`](bpy.types.Depsgraph.md#bpy.types.Depsgraph.scene "bpy.types.Depsgraph.scene") - [`Depsgraph.scene_eval`](bpy.types.Depsgraph.md#bpy.types.Depsgraph.scene_eval "bpy.types.Depsgraph.scene_eval") - [`ID.override_hierarchy_create`](bpy.types.ID.md#bpy.types.ID.override_hierarchy_create "bpy.types.ID.override_hierarchy_create") - [`IDOverrideLibrary.resync`](bpy.types.IDOverrideLibrary.md#bpy.types.IDOverrideLibrary.resync "bpy.types.IDOverrideLibrary.resync") - [`Image.save_render`](bpy.types.Image.md#bpy.types.Image.save_render "bpy.types.Image.save_render") - [`NodeSocketScene.default_value`](bpy.types.NodeSocketScene.md#bpy.types.NodeSocketScene.default_value "bpy.types.NodeSocketScene.default_value") | - [`NodeTreeInterfaceSocketScene.default_value`](bpy.types.NodeTreeInterfaceSocketScene.md#bpy.types.NodeTreeInterfaceSocketScene.default_value "bpy.types.NodeTreeInterfaceSocketScene.default_value") - [`Object.crazyspace_eval`](bpy.types.Object.md#bpy.types.Object.crazyspace_eval "bpy.types.Object.crazyspace_eval") - [`Object.is_deform_modified`](bpy.types.Object.md#bpy.types.Object.is_deform_modified "bpy.types.Object.is_deform_modified") - [`Object.is_modified`](bpy.types.Object.md#bpy.types.Object.is_modified "bpy.types.Object.is_modified") - [`RenderEngine.bind_display_space_shader`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.bind_display_space_shader "bpy.types.RenderEngine.bind_display_space_shader") - [`RenderEngine.get_preview_pixel_size`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.get_preview_pixel_size "bpy.types.RenderEngine.get_preview_pixel_size") - [`RenderEngine.register_pass`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.register_pass "bpy.types.RenderEngine.register_pass") - [`RenderEngine.support_display_space_shader`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.support_display_space_shader "bpy.types.RenderEngine.support_display_space_shader") - [`RenderEngine.update_render_passes`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.update_render_passes "bpy.types.RenderEngine.update_render_passes") - [`Scene.background_set`](#bpy.types.Scene.background_set "bpy.types.Scene.background_set") - [`SceneStrip.scene`](bpy.types.SceneStrip.md#bpy.types.SceneStrip.scene "bpy.types.SceneStrip.scene") - [`StripsMeta.new_scene`](bpy.types.StripsMeta.md#bpy.types.StripsMeta.new_scene "bpy.types.StripsMeta.new_scene") - [`StripsTopLevel.new_scene`](bpy.types.StripsTopLevel.md#bpy.types.StripsTopLevel.new_scene "bpy.types.StripsTopLevel.new_scene") - [`Window.find_playing_scene`](bpy.types.Window.md#bpy.types.Window.find_playing_scene "bpy.types.Window.find_playing_scene") - [`Window.scene`](bpy.types.Window.md#bpy.types.Window.scene "bpy.types.Window.scene") - [`WorkSpace.sequencer_scene`](bpy.types.WorkSpace.md#bpy.types.WorkSpace.sequencer_scene "bpy.types.WorkSpace.sequencer_scene") |
