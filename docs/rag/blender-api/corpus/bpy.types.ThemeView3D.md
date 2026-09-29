<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeView3D.html -->

<a id="themeview3d-bpy-struct"></a>

# ThemeView3D(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeView3D"></a>

### class bpy.types.ThemeView3D(bpy_struct)

Theme settings for the 3D viewport

<a id="bpy.types.ThemeView3D.after_current_frame"></a>

#### bpy.types.ThemeView3D.after_current_frame

The color for things after the current frame (for onion skinning, motion paths, etc.) (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.before_current_frame"></a>

#### bpy.types.ThemeView3D.before_current_frame

The color for things before the current frame (for onion skinning, motion paths, etc.) (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.bevel"></a>

#### bpy.types.ThemeView3D.bevel

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.bone_locked_weight"></a>

#### bpy.types.ThemeView3D.bone_locked_weight

Shade for bones corresponding to a locked weight group during painting (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.bone_pose"></a>

#### bpy.types.ThemeView3D.bone_pose

Outline color of selected pose bones (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.bone_pose_active"></a>

#### bpy.types.ThemeView3D.bone_pose_active

Outline color of active pose bones (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.bone_solid"></a>

#### bpy.types.ThemeView3D.bone_solid

Default color of the solid shapes of bones (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.bundle_solid"></a>

#### bpy.types.ThemeView3D.bundle_solid

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.camera"></a>

#### bpy.types.ThemeView3D.camera

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.camera_passepartout"></a>

#### bpy.types.ThemeView3D.camera_passepartout

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.camera_path"></a>

#### bpy.types.ThemeView3D.camera_path

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.clipping_border_3d"></a>

#### bpy.types.ThemeView3D.clipping_border_3d

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.crease"></a>

#### bpy.types.ThemeView3D.crease

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.edge_mode_select"></a>

#### bpy.types.ThemeView3D.edge_mode_select

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.edge_select"></a>

#### bpy.types.ThemeView3D.edge_select

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.edge_width"></a>

#### bpy.types.ThemeView3D.edge_width

(in [1, 32], default 0)

**Type:**

int

<a id="bpy.types.ThemeView3D.editmesh_active"></a>

#### bpy.types.ThemeView3D.editmesh_active

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.empty"></a>

#### bpy.types.ThemeView3D.empty

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.extra_edge_angle"></a>

#### bpy.types.ThemeView3D.extra_edge_angle

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.extra_edge_len"></a>

#### bpy.types.ThemeView3D.extra_edge_len

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.extra_face_angle"></a>

#### bpy.types.ThemeView3D.extra_face_angle

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.extra_face_area"></a>

#### bpy.types.ThemeView3D.extra_face_area

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.face"></a>

#### bpy.types.ThemeView3D.face

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.face_back"></a>

#### bpy.types.ThemeView3D.face_back

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.face_front"></a>

#### bpy.types.ThemeView3D.face_front

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.face_mode_select"></a>

#### bpy.types.ThemeView3D.face_mode_select

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.face_retopology"></a>

#### bpy.types.ThemeView3D.face_retopology

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.face_select"></a>

#### bpy.types.ThemeView3D.face_select

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.facedot_size"></a>

#### bpy.types.ThemeView3D.facedot_size

(in [1, 10], default 0)

**Type:**

int

<a id="bpy.types.ThemeView3D.freestyle"></a>

#### bpy.types.ThemeView3D.freestyle

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.gp_vertex"></a>

#### bpy.types.ThemeView3D.gp_vertex

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.gp_vertex_select"></a>

#### bpy.types.ThemeView3D.gp_vertex_select

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.gp_vertex_size"></a>

#### bpy.types.ThemeView3D.gp_vertex_size

(in [1, 10], default 0)

**Type:**

int

<a id="bpy.types.ThemeView3D.gp_wire_edit"></a>

#### bpy.types.ThemeView3D.gp_wire_edit

Grease Pencil wireframe color when in edit mode (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.grid"></a>

#### bpy.types.ThemeView3D.grid

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.grid_axis_brightness"></a>

#### bpy.types.ThemeView3D.grid_axis_brightness

Brightness of the grid axis lines (in [0, 1], default 0.46)

**Type:**

float

<a id="bpy.types.ThemeView3D.grid_major"></a>

#### bpy.types.ThemeView3D.grid_major

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.light"></a>

#### bpy.types.ThemeView3D.light

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeView3D.normal"></a>

#### bpy.types.ThemeView3D.normal

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.nurb_sel_uline"></a>

#### bpy.types.ThemeView3D.nurb_sel_uline

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.nurb_sel_vline"></a>

#### bpy.types.ThemeView3D.nurb_sel_vline

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.nurb_uline"></a>

#### bpy.types.ThemeView3D.nurb_uline

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.nurb_vline"></a>

#### bpy.types.ThemeView3D.nurb_vline

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.object_active"></a>

#### bpy.types.ThemeView3D.object_active

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.object_origin_size"></a>

#### bpy.types.ThemeView3D.object_origin_size

Diameter in pixels for object/light origin display (in [4, 10], default 0)

**Type:**

int

<a id="bpy.types.ThemeView3D.object_selected"></a>

#### bpy.types.ThemeView3D.object_selected

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.outline_width"></a>

#### bpy.types.ThemeView3D.outline_width

(in [1, 5], default 0)

**Type:**

int

<a id="bpy.types.ThemeView3D.seam"></a>

#### bpy.types.ThemeView3D.seam

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.sharp"></a>

#### bpy.types.ThemeView3D.sharp

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.skin_root"></a>

#### bpy.types.ThemeView3D.skin_root

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.space"></a>

#### bpy.types.ThemeView3D.space

Settings for space (readonly, never None)

**Type:**

[`ThemeSpaceGradient`](bpy.types.ThemeSpaceGradient.md#bpy.types.ThemeSpaceGradient "bpy.types.ThemeSpaceGradient")

<a id="bpy.types.ThemeView3D.speaker"></a>

#### bpy.types.ThemeView3D.speaker

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.split_normal"></a>

#### bpy.types.ThemeView3D.split_normal

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.text_grease_pencil"></a>

#### bpy.types.ThemeView3D.text_grease_pencil

Color for indicating Grease Pencil keyframes (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.transform"></a>

#### bpy.types.ThemeView3D.transform

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.vertex"></a>

#### bpy.types.ThemeView3D.vertex

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.vertex_normal"></a>

#### bpy.types.ThemeView3D.vertex_normal

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.vertex_select"></a>

#### bpy.types.ThemeView3D.vertex_select

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.vertex_size"></a>

#### bpy.types.ThemeView3D.vertex_size

(in [1, 32], default 0)

**Type:**

int

<a id="bpy.types.ThemeView3D.vertex_unreferenced"></a>

#### bpy.types.ThemeView3D.vertex_unreferenced

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.view_overlay"></a>

#### bpy.types.ThemeView3D.view_overlay

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.wire"></a>

#### bpy.types.ThemeView3D.wire

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.wire_edit"></a>

#### bpy.types.ThemeView3D.wire_edit

Color for wireframe when in edit mode, but edge selection is active (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeView3D.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeView3D.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeView3D.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeView3D.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Theme.view_3d`](bpy.types.Theme.md#bpy.types.Theme.view_3d "bpy.types.Theme.view_3d") |  |
