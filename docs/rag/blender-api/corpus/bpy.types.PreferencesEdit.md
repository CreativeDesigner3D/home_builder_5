<!-- source: Blender Python API reference 5.2 / bpy.types.PreferencesEdit.html -->

<a id="preferencesedit-bpy-struct"></a>

# PreferencesEdit(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.PreferencesEdit"></a>

### class bpy.types.PreferencesEdit(bpy_struct)

Settings for interacting with Blender data

<a id="bpy.types.PreferencesEdit.auto_keying_mode"></a>

#### bpy.types.PreferencesEdit.auto_keying_mode

Mode of automatic keyframe insertion for Objects and Bones (default setting used for new Scenes) (default `'ADD_REPLACE_KEYS'`)

**Type:**

Literal[‘ADD_REPLACE_KEYS’, ‘REPLACE_KEYS’]

<a id="bpy.types.PreferencesEdit.collection_instance_empty_size"></a>

#### bpy.types.PreferencesEdit.collection_instance_empty_size

Display size of the empty when new collection instances are created (in [0.001, inf], default 1.0)

**Type:**

float

<a id="bpy.types.PreferencesEdit.connect_strips_by_default"></a>

#### bpy.types.PreferencesEdit.connect_strips_by_default

Connect newly added movie strips by default if they have multiple channels (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.fcurve_new_auto_smoothing"></a>

#### bpy.types.PreferencesEdit.fcurve_new_auto_smoothing

Auto Handle Smoothing mode used for newly added F-Curves (default `'CONT_ACCEL'`)

**Type:**

Literal[[Fcurve Auto Smoothing Items](bpy_types_enum_items/fcurve_auto_smoothing_items.md#rna-enum-fcurve-auto-smoothing-items)]

<a id="bpy.types.PreferencesEdit.fcurve_unselected_alpha"></a>

#### bpy.types.PreferencesEdit.fcurve_unselected_alpha

The opacity of unselected F-Curves against the background of the Graph Editor (in [0.001, 1], default 0.25)

**Type:**

float

<a id="bpy.types.PreferencesEdit.grease_pencil_default_color"></a>

#### bpy.types.PreferencesEdit.grease_pencil_default_color

Color of new annotation layers (array of 4 items, in [0, inf], default (0.38, 0.61, 0.78, 0.9))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.PreferencesEdit.grease_pencil_eraser_radius"></a>

#### bpy.types.PreferencesEdit.grease_pencil_eraser_radius

Radius of eraser ‘brush’ (in [1, 500], default 25)

**Type:**

int

<a id="bpy.types.PreferencesEdit.grease_pencil_euclidean_distance"></a>

#### bpy.types.PreferencesEdit.grease_pencil_euclidean_distance

Distance moved by mouse when drawing stroke to include (in [0, 100], default 2)

**Type:**

int

<a id="bpy.types.PreferencesEdit.grease_pencil_manhattan_distance"></a>

#### bpy.types.PreferencesEdit.grease_pencil_manhattan_distance

Pixels moved by mouse per axis when drawing stroke (in [0, 100], default 1)

**Type:**

int

<a id="bpy.types.PreferencesEdit.key_insert_channels"></a>

#### bpy.types.PreferencesEdit.key_insert_channels

Which channels to insert keys at when no keying set is active (default {`'CUSTOM_PROPS'`, `'LOCATION'`, `'ROTATION'`, `'SCALE'`})

**Type:**

set[Literal[‘LOCATION’, ‘ROTATION’, ‘SCALE’, ‘ROTATE_MODE’, ‘CUSTOM_PROPS’]]

<a id="bpy.types.PreferencesEdit.keyframe_new_handle_type"></a>

#### bpy.types.PreferencesEdit.keyframe_new_handle_type

Handle type for handles of new keyframes (default `'FREE'`)

**Type:**

Literal[[Keyframe Handle Type Items](bpy_types_enum_items/keyframe_handle_type_items.md#rna-enum-keyframe-handle-type-items)]

<a id="bpy.types.PreferencesEdit.keyframe_new_interpolation_type"></a>

#### bpy.types.PreferencesEdit.keyframe_new_interpolation_type

Interpolation mode used for first keyframe on newly added F-Curves (subsequent keyframes take interpolation from preceding keyframe) (default `'BEZIER'`)

**Type:**

Literal[[Beztriple Interpolation Mode Items](bpy_types_enum_items/beztriple_interpolation_mode_items.md#rna-enum-beztriple-interpolation-mode-items)]

<a id="bpy.types.PreferencesEdit.material_link"></a>

#### bpy.types.PreferencesEdit.material_link

Toggle whether the material is linked to object data or the object block (default `'OBDATA'`)

- `OBDATA`
  Object Data – Toggle whether the material is linked to object data or the object block.
- `OBJECT`
  Object – Toggle whether the material is linked to object data or the object block.

**Type:**

Literal[‘OBDATA’, ‘OBJECT’]

<a id="bpy.types.PreferencesEdit.node_margin"></a>

#### bpy.types.PreferencesEdit.node_margin

Minimum distance between nodes for Auto-offsetting nodes (in [0, 255], default 40)

**Type:**

int

<a id="bpy.types.PreferencesEdit.node_preview_resolution"></a>

#### bpy.types.PreferencesEdit.node_preview_resolution

Resolution used for Shader node previews (should be changed for performance convenience) (in [50, 250], default 120)

**Type:**

int

<a id="bpy.types.PreferencesEdit.node_use_insert_offset"></a>

#### bpy.types.PreferencesEdit.node_use_insert_offset

Automatically offset the following or previous nodes in a chain when inserting a new node (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.object_align"></a>

#### bpy.types.PreferencesEdit.object_align

The default alignment for objects added from a 3D viewport menu (default `'WORLD'`)

- `WORLD`
  World – Align newly added objects to the world coordinate system.
- `VIEW`
  View – Align newly added objects to the active 3D view orientation.
- `CURSOR`
  3D Cursor – Align newly added objects to the 3D Cursor’s rotation.

**Type:**

Literal[‘WORLD’, ‘VIEW’, ‘CURSOR’]

<a id="bpy.types.PreferencesEdit.sculpt_paint_overlay_color"></a>

#### bpy.types.PreferencesEdit.sculpt_paint_overlay_color

Color of texture overlay (array of 3 items, in [0, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.PreferencesEdit.show_only_selected_curve_keyframes"></a>

#### bpy.types.PreferencesEdit.show_only_selected_curve_keyframes

Only keyframes of selected F-Curves are visible and editable (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.undo_memory_limit"></a>

#### bpy.types.PreferencesEdit.undo_memory_limit

Maximum memory usage in megabytes (0 means unlimited) (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.PreferencesEdit.undo_steps"></a>

#### bpy.types.PreferencesEdit.undo_steps

Number of undo steps available (smaller values conserve memory) (in [0, 256], default 32)

**Type:**

int

<a id="bpy.types.PreferencesEdit.use_anim_channel_group_colors"></a>

#### bpy.types.PreferencesEdit.use_anim_channel_group_colors

Use animation channel group colors; generally this is used to show bone group colors (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_auto_keyframe_insert_needed"></a>

#### bpy.types.PreferencesEdit.use_auto_keyframe_insert_needed

Auto-Keying will skip inserting keys that don’t affect the animation (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_auto_keying"></a>

#### bpy.types.PreferencesEdit.use_auto_keying

Automatic keyframe insertion for Objects and Bones (default setting used for new Scenes) (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_auto_keying_warning"></a>

#### bpy.types.PreferencesEdit.use_auto_keying_warning

Show warning indicators when transforming objects and bones if auto keying is enabled (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_cursor_lock_adjust"></a>

#### bpy.types.PreferencesEdit.use_cursor_lock_adjust

Place the cursor without ‘jumping’ to the new location (when lock-to-cursor is used) (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_action"></a>

#### bpy.types.PreferencesEdit.use_duplicate_action

Causes actions to be duplicated with the data-blocks (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_armature"></a>

#### bpy.types.PreferencesEdit.use_duplicate_armature

Causes armature data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_camera"></a>

#### bpy.types.PreferencesEdit.use_duplicate_camera

Causes camera data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_curve"></a>

#### bpy.types.PreferencesEdit.use_duplicate_curve

Causes curve data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_curves"></a>

#### bpy.types.PreferencesEdit.use_duplicate_curves

Causes curves data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_grease_pencil"></a>

#### bpy.types.PreferencesEdit.use_duplicate_grease_pencil

Causes Grease Pencil data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_lattice"></a>

#### bpy.types.PreferencesEdit.use_duplicate_lattice

Causes lattice data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_light"></a>

#### bpy.types.PreferencesEdit.use_duplicate_light

Causes light data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_lightprobe"></a>

#### bpy.types.PreferencesEdit.use_duplicate_lightprobe

Causes light probe data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_material"></a>

#### bpy.types.PreferencesEdit.use_duplicate_material

Causes material data to be duplicated with the object (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_mesh"></a>

#### bpy.types.PreferencesEdit.use_duplicate_mesh

Causes mesh data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_metaball"></a>

#### bpy.types.PreferencesEdit.use_duplicate_metaball

Causes metaball data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_node_tree"></a>

#### bpy.types.PreferencesEdit.use_duplicate_node_tree

Make copies of node groups when duplicating nodes in the node editor (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_particle"></a>

#### bpy.types.PreferencesEdit.use_duplicate_particle

Causes particle systems to be duplicated with the object (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_pointcloud"></a>

#### bpy.types.PreferencesEdit.use_duplicate_pointcloud

Causes point cloud data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_speaker"></a>

#### bpy.types.PreferencesEdit.use_duplicate_speaker

Causes speaker data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_surface"></a>

#### bpy.types.PreferencesEdit.use_duplicate_surface

Causes surface data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_text"></a>

#### bpy.types.PreferencesEdit.use_duplicate_text

Causes text data to be duplicated with the object (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_duplicate_volume"></a>

#### bpy.types.PreferencesEdit.use_duplicate_volume

Causes volume data to be duplicated with the object (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_enter_edit_mode"></a>

#### bpy.types.PreferencesEdit.use_enter_edit_mode

Enter edit mode automatically after adding a new object (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_fcurve_high_quality_drawing"></a>

#### bpy.types.PreferencesEdit.use_fcurve_high_quality_drawing

Draw F-Curves using Anti-Aliasing (disable for better performance) (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_global_undo"></a>

#### bpy.types.PreferencesEdit.use_global_undo

Global undo works by keeping a full copy of the file itself in memory, so takes extra memory (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_insertkey_xyz_to_rgb"></a>

#### bpy.types.PreferencesEdit.use_insertkey_xyz_to_rgb

Color for newly added transformation F-Curves (Location, Rotation, Scale) and also Color is based on the transform axis (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_keyframe_insert_available"></a>

#### bpy.types.PreferencesEdit.use_keyframe_insert_available

Insert Keyframes only for properties that are already animated (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_keyframe_insert_needed"></a>

#### bpy.types.PreferencesEdit.use_keyframe_insert_needed

When keying manually, skip inserting keys that don’t affect the animation (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_mouse_depth_cursor"></a>

#### bpy.types.PreferencesEdit.use_mouse_depth_cursor

Use the surface depth for cursor placement (default True)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_negative_frames"></a>

#### bpy.types.PreferencesEdit.use_negative_frames

Current frame number can be manually set to a negative value (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_text_edit_auto_close"></a>

#### bpy.types.PreferencesEdit.use_text_edit_auto_close

Automatically close relevant character pairs when typing in the text editor (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.use_visual_keying"></a>

#### bpy.types.PreferencesEdit.use_visual_keying

Use Visual keying automatically for constrained objects (default False)

**Type:**

bool

<a id="bpy.types.PreferencesEdit.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PreferencesEdit.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PreferencesEdit.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PreferencesEdit.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Preferences.edit`](bpy.types.Preferences.md#bpy.types.Preferences.edit "bpy.types.Preferences.edit") |  |
