<!-- source: Blender Python API reference 5.2 / bpy.types.Object.html -->

<a id="object-id"></a>

# Object(ID)

<a id="basic-object-operations-example"></a>

## Basic Object Operations Example

This script demonstrates basic operations on object like creating new
object, placing it into a view layer, selecting it and making it active.

```python
import bpy

view_layer = bpy.context.view_layer

# Create new light data-block.
light_data = bpy.data.lights.new(name="New Light", type='POINT')

# Create new object with our light data-block.
light_object = bpy.data.objects.new(name="New Light", object_data=light_data)

# Link light object to the active collection of current view layer,
# so that it'll appear in the current scene.
view_layer.active_layer_collection.collection.objects.link(light_object)

# Place light to a specified location.
light_object.location = (5.0, 5.0, 5.0)

# And finally select it and make it active.
light_object.select_set(True)
view_layer.objects.active = light_object
```

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")

<a id="bpy.types.Object"></a>

### class bpy.types.Object(ID)

Object data-block defining an object in a scene

<a id="bpy.types.Object.active_material"></a>

#### bpy.types.Object.active_material

Active material being displayed

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.Object.active_material_index"></a>

#### bpy.types.Object.active_material_index

Index of active material slot (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.Object.active_selection_set"></a>

#### bpy.types.Object.active_selection_set

Index of the currently active selection set (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Object.active_shape_key"></a>

#### bpy.types.Object.active_shape_key

Current shape key (readonly)

**Type:**

[`ShapeKey`](bpy.types.ShapeKey.md#bpy.types.ShapeKey "bpy.types.ShapeKey") | None

<a id="bpy.types.Object.active_shape_key_index"></a>

#### bpy.types.Object.active_shape_key_index

Current shape key index (in [-32768, 32767], default 0)

**Type:**

int

<a id="bpy.types.Object.add_rest_position_attribute"></a>

#### bpy.types.Object.add_rest_position_attribute

Add a “rest_position” attribute that is a copy of the position attribute before shape keys and modifiers are evaluated (default False)

**Type:**

bool

<a id="bpy.types.Object.animation_data"></a>

#### bpy.types.Object.animation_data

Animation data for this data-block (readonly)

**Type:**

[`AnimData`](bpy.types.AnimData.md#bpy.types.AnimData "bpy.types.AnimData") | None

<a id="bpy.types.Object.animation_visualization"></a>

#### bpy.types.Object.animation_visualization

Animation data for this data-block (readonly, never None)

**Type:**

[`AnimViz`](bpy.types.AnimViz.md#bpy.types.AnimViz "bpy.types.AnimViz")

<a id="bpy.types.Object.bound_box"></a>

#### bpy.types.Object.bound_box

Object’s bounding box in object-space coordinates, all values are -1.0 when not available (multi-dimensional array of 8 * 3 items, in [-inf, inf], default ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0)), readonly)

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]]

<a id="bpy.types.Object.collision"></a>

#### bpy.types.Object.collision

Settings for using the object as a collider in physics simulation (readonly)

**Type:**

[`CollisionSettings`](bpy.types.CollisionSettings.md#bpy.types.CollisionSettings "bpy.types.CollisionSettings") | None

<a id="bpy.types.Object.color"></a>

#### bpy.types.Object.color

Object color and alpha, used when the Object Color mode is enabled (array of 4 items, in [0, inf], default (1.0, 1.0, 1.0, 1.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Object.constraints"></a>

#### bpy.types.Object.constraints

Constraints affecting the transformation of the object (default None, readonly)

**Type:**

[`ObjectConstraints`](bpy.types.ObjectConstraints.md#bpy.types.ObjectConstraints "bpy.types.ObjectConstraints")[[`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")]

<a id="bpy.types.Object.cycles"></a>

#### bpy.types.Object.cycles

Cycles object settings (readonly)

**Type:**

`CyclesObjectSettings` | None

<a id="bpy.types.Object.data"></a>

#### bpy.types.Object.data

Object data

**Type:**

[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID") | None

<a id="bpy.types.Object.delta_location"></a>

#### bpy.types.Object.delta_location

Extra translation added to the location of the object (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Object.delta_rotation_euler"></a>

#### bpy.types.Object.delta_rotation_euler

Extra rotation added to the rotation of the object (when using Euler rotations) (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.Object.delta_rotation_quaternion"></a>

#### bpy.types.Object.delta_rotation_quaternion

Extra rotation added to the rotation of the object (when using Quaternion rotations) (array of 4 items, in [-inf, inf], default (1.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.Object.delta_scale"></a>

#### bpy.types.Object.delta_scale

Extra scaling added to the scale of the object (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Object.dimensions"></a>

#### bpy.types.Object.dimensions

Absolute bounding box dimensions of the object.
Warning: Assigning to it or its members multiple consecutive times will not work correctly, as this needs up-to-date evaluated data

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Object.display"></a>

#### bpy.types.Object.display

Object display settings for 3D viewport (readonly, never None)

**Type:**

[`ObjectDisplay`](bpy.types.ObjectDisplay.md#bpy.types.ObjectDisplay "bpy.types.ObjectDisplay")

<a id="bpy.types.Object.display_bounds_type"></a>

#### bpy.types.Object.display_bounds_type

Object boundary display type (default `'BOX'`)

- `BOX`
  Box – Display bounds as box.
- `SPHERE`
  Sphere – Display bounds as sphere.
- `CYLINDER`
  Cylinder – Display bounds as cylinder.
- `CONE`
  Cone – Display bounds as cone.
- `CAPSULE`
  Capsule – Display bounds as capsule.

**Type:**

Literal[‘BOX’, ‘SPHERE’, ‘CYLINDER’, ‘CONE’, ‘CAPSULE’]

<a id="bpy.types.Object.display_type"></a>

#### bpy.types.Object.display_type

How to display object in viewport (default `'TEXTURED'`)

- `BOUNDS`
  Bounds – Display the bounds of the object.
- `WIRE`
  Wire – Display the object as a wireframe.
- `SOLID`
  Solid – Display the object as a solid (if solid drawing is enabled in the viewport).
- `TEXTURED`
  Textured – Display the object with textures (if textures are enabled in the viewport).

**Type:**

Literal[‘BOUNDS’, ‘WIRE’, ‘SOLID’, ‘TEXTURED’]

<a id="bpy.types.Object.empty_display_size"></a>

#### bpy.types.Object.empty_display_size

Size of display for empties in the viewport (in [0.0001, 1000], default 1.0)

**Type:**

float

<a id="bpy.types.Object.empty_display_type"></a>

#### bpy.types.Object.empty_display_type

Viewport display style for empties (default `'PLAIN_AXES'`)

**Type:**

Literal[[Object Empty Drawtype Items](bpy_types_enum_items/object_empty_drawtype_items.md#rna-enum-object-empty-drawtype-items)]

<a id="bpy.types.Object.empty_image_depth"></a>

#### bpy.types.Object.empty_image_depth

Determine which other objects will occlude the image (default `'DEFAULT'`)

**Type:**

Literal[‘DEFAULT’, ‘FRONT’, ‘BACK’]

<a id="bpy.types.Object.empty_image_offset"></a>

#### bpy.types.Object.empty_image_offset

Origin offset distance (array of 2 items, in [-inf, inf], default (-0.5, -0.5))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Object.empty_image_side"></a>

#### bpy.types.Object.empty_image_side

Show front/back side (default `'DOUBLE_SIDED'`)

**Type:**

Literal[‘DOUBLE_SIDED’, ‘FRONT’, ‘BACK’]

<a id="bpy.types.Object.field"></a>

#### bpy.types.Object.field

Settings for using the object as a field in physics simulation (readonly)

**Type:**

[`FieldSettings`](bpy.types.FieldSettings.md#bpy.types.FieldSettings "bpy.types.FieldSettings") | None

<a id="bpy.types.Object.hide_probe_plane"></a>

#### bpy.types.Object.hide_probe_plane

Globally disable in planar light probes (default False)

**Type:**

bool

<a id="bpy.types.Object.hide_probe_sphere"></a>

#### bpy.types.Object.hide_probe_sphere

Globally disable in spherical light probes (default False)

**Type:**

bool

<a id="bpy.types.Object.hide_probe_volume"></a>

#### bpy.types.Object.hide_probe_volume

Globally disable in volume probes (default False)

**Type:**

bool

<a id="bpy.types.Object.hide_render"></a>

#### bpy.types.Object.hide_render

Globally disable in renders (default False)

**Type:**

bool

<a id="bpy.types.Object.hide_select"></a>

#### bpy.types.Object.hide_select

Disable selection in viewport (default False)

**Type:**

bool

<a id="bpy.types.Object.hide_surface_pick"></a>

#### bpy.types.Object.hide_surface_pick

Disable surface influence during selection, snapping and depth-picking operators. Usually used to avoid semi-transparent objects to affect scene navigation (default False)

**Type:**

bool

<a id="bpy.types.Object.hide_viewport"></a>

#### bpy.types.Object.hide_viewport

Globally disable in viewports (default False)

**Type:**

bool

<a id="bpy.types.Object.image_user"></a>

#### bpy.types.Object.image_user

Parameters defining which layer, pass and frame of the image is displayed (readonly, never None)

**Type:**

[`ImageUser`](bpy.types.ImageUser.md#bpy.types.ImageUser "bpy.types.ImageUser")

<a id="bpy.types.Object.instance_collection"></a>

#### bpy.types.Object.instance_collection

Instance an existing collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.Object.instance_faces_scale"></a>

#### bpy.types.Object.instance_faces_scale

Scale the face instance objects (in [0.001, 10000], default 1.0)

**Type:**

float

<a id="bpy.types.Object.instance_type"></a>

#### bpy.types.Object.instance_type

If not None, object instancing method to use (default `'NONE'`)

- `NONE`
  None.
- `VERTS`
  Vertices – Instantiate child objects on all vertices.
- `FACES`
  Faces – Instantiate child objects on all faces.
- `COLLECTION`
  Collection – Enable collection instancing.

**Type:**

Literal[‘NONE’, ‘VERTS’, ‘FACES’, ‘COLLECTION’]

<a id="bpy.types.Object.is_from_instancer"></a>

#### bpy.types.Object.is_from_instancer

Object comes from a instancer (default False, readonly)

**Type:**

bool

<a id="bpy.types.Object.is_from_set"></a>

#### bpy.types.Object.is_from_set

Object comes from a background set (default False, readonly)

**Type:**

bool

<a id="bpy.types.Object.is_holdout"></a>

#### bpy.types.Object.is_holdout

Render objects as a holdout or matte, creating a hole in the image with zero alpha, to fill out in compositing with real footage or another render (default False)

**Type:**

bool

<a id="bpy.types.Object.is_instancer"></a>

#### bpy.types.Object.is_instancer

(default False, readonly)

**Type:**

bool

<a id="bpy.types.Object.is_shadow_catcher"></a>

#### bpy.types.Object.is_shadow_catcher

Only render shadows and reflections on this object, for compositing renders into real footage. Objects with this setting are considered to already exist in the footage, objects without it are synthetic objects being composited into it. (default False)

**Type:**

bool

<a id="bpy.types.Object.light_linking"></a>

#### bpy.types.Object.light_linking

Light linking settings (readonly, never None)

**Type:**

[`ObjectLightLinking`](bpy.types.ObjectLightLinking.md#bpy.types.ObjectLightLinking "bpy.types.ObjectLightLinking")

<a id="bpy.types.Object.lightgroup"></a>

#### bpy.types.Object.lightgroup

Lightgroup that the object belongs to (default “”, never None)

**Type:**

str

<a id="bpy.types.Object.lineart"></a>

#### bpy.types.Object.lineart

Line Art settings for the object (readonly)

**Type:**

[`ObjectLineArt`](bpy.types.ObjectLineArt.md#bpy.types.ObjectLineArt "bpy.types.ObjectLineArt") | None

<a id="bpy.types.Object.location"></a>

#### bpy.types.Object.location

Location of the object (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Object.lock_location"></a>

#### bpy.types.Object.lock_location

Lock editing of location when transforming (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.Object.lock_rotation"></a>

#### bpy.types.Object.lock_rotation

Lock editing of rotation when transforming (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.Object.lock_rotation_w"></a>

#### bpy.types.Object.lock_rotation_w

Lock editing of ‘angle’ component of four-component rotations when transforming (default False)

**Type:**

bool

<a id="bpy.types.Object.lock_rotations_4d"></a>

#### bpy.types.Object.lock_rotations_4d

Lock editing of four component rotations by components (instead of as Eulers) (default True)

**Type:**

bool

<a id="bpy.types.Object.lock_scale"></a>

#### bpy.types.Object.lock_scale

Lock editing of scale when transforming (array of 3 items, default (False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.Object.material_slots"></a>

#### bpy.types.Object.material_slots

Material slots in the object (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`MaterialSlot`](bpy.types.MaterialSlot.md#bpy.types.MaterialSlot "bpy.types.MaterialSlot")]

<a id="bpy.types.Object.matrix_basis"></a>

#### bpy.types.Object.matrix_basis

Matrix access to location, rotation and scale (including deltas), before constraints and parenting are applied (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Object.matrix_local"></a>

#### bpy.types.Object.matrix_local

Parent relative transformation matrix.
Warning: Only takes into account object parenting, so e.g. in case of bone parenting you get a matrix relative to the Armature object, not to the actual parent bone

(multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Object.matrix_parent_inverse"></a>

#### bpy.types.Object.matrix_parent_inverse

Inverse of object’s parent matrix at time of parenting (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((1.0, 0.0, 0.0, 0.0), (0.0, 1.0, 0.0, 0.0), (0.0, 0.0, 1.0, 0.0), (0.0, 0.0, 0.0, 1.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Object.matrix_world"></a>

#### bpy.types.Object.matrix_world

Worldspace transformation matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Object.mode"></a>

#### bpy.types.Object.mode

Object interaction mode (default `'OBJECT'`, readonly)

**Type:**

Literal[[Object Mode Items](bpy_types_enum_items/object_mode_items.md#rna-enum-object-mode-items)]

<a id="bpy.types.Object.modifiers"></a>

#### bpy.types.Object.modifiers

Modifiers affecting the geometric data of the object (default None, readonly)

**Type:**

[`ObjectModifiers`](bpy.types.ObjectModifiers.md#bpy.types.ObjectModifiers "bpy.types.ObjectModifiers")[[`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")]

<a id="bpy.types.Object.motion_path"></a>

#### bpy.types.Object.motion_path

Motion Path for this element (readonly)

**Type:**

[`MotionPath`](bpy.types.MotionPath.md#bpy.types.MotionPath "bpy.types.MotionPath") | None

<a id="bpy.types.Object.parent"></a>

#### bpy.types.Object.parent

Parent object

**Type:**

[`Object`](#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.Object.parent_bone"></a>

#### bpy.types.Object.parent_bone

Name of parent bone in case of a bone parenting relation (default “”, never None)

**Type:**

str

<a id="bpy.types.Object.parent_bone_head_tail_factor"></a>

#### bpy.types.Object.parent_bone_head_tail_factor

Position along the length of bone (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.Object.parent_type"></a>

#### bpy.types.Object.parent_type

Type of parent relation (default `'OBJECT'`)

- `OBJECT`
  Object – The object is parented to an object.
- `ARMATURE`
  Armature.
- `LATTICE`
  Lattice – The object is parented to a lattice.
- `VERTEX`
  Vertex – The object is parented to a vertex.
- `VERTEX_3`
  3 Vertices.
- `BONE`
  Bone – The object is parented to a bone.

**Type:**

Literal[‘OBJECT’, ‘ARMATURE’, ‘LATTICE’, ‘VERTEX’, ‘VERTEX_3’, ‘BONE’]

<a id="bpy.types.Object.parent_vertices"></a>

#### bpy.types.Object.parent_vertices

Indices of vertices in case of a vertex parenting relation (array of 3 items, in [0, inf], default (0, 0, 0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[int]

<a id="bpy.types.Object.particle_systems"></a>

#### bpy.types.Object.particle_systems

Particle systems emitted from the object (default None, readonly)

**Type:**

[`ParticleSystems`](bpy.types.ParticleSystems.md#bpy.types.ParticleSystems "bpy.types.ParticleSystems")[[`ParticleSystem`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem "bpy.types.ParticleSystem")]

<a id="bpy.types.Object.pass_index"></a>

#### bpy.types.Object.pass_index

Index number for the “Object Index” render pass (in [0, 32767], default 0)

**Type:**

int

<a id="bpy.types.Object.pose"></a>

#### bpy.types.Object.pose

Current pose for armatures (readonly)

**Type:**

[`Pose`](bpy.types.Pose.md#bpy.types.Pose "bpy.types.Pose") | None

<a id="bpy.types.Object.rigid_body"></a>

#### bpy.types.Object.rigid_body

Settings for rigid body simulation (readonly)

**Type:**

[`RigidBodyObject`](bpy.types.RigidBodyObject.md#bpy.types.RigidBodyObject "bpy.types.RigidBodyObject") | None

<a id="bpy.types.Object.rigid_body_constraint"></a>

#### bpy.types.Object.rigid_body_constraint

Constraint constraining rigid bodies (readonly)

**Type:**

[`RigidBodyConstraint`](bpy.types.RigidBodyConstraint.md#bpy.types.RigidBodyConstraint "bpy.types.RigidBodyConstraint") | None

<a id="bpy.types.Object.rotation_axis_angle"></a>

#### bpy.types.Object.rotation_axis_angle

Angle of Rotation for Axis-Angle rotation representation (array of 4 items, in [-inf, inf], default (0.0, 0.0, 1.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.Object.rotation_euler"></a>

#### bpy.types.Object.rotation_euler

Rotation in Eulers (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.Object.rotation_mode"></a>

#### bpy.types.Object.rotation_mode

The kind of rotation to apply, values from other rotation modes are not used (default `'XYZ'`)

**Type:**

Literal[[Object Rotation Mode Items](bpy_types_enum_items/object_rotation_mode_items.md#rna-enum-object-rotation-mode-items)]

<a id="bpy.types.Object.rotation_quaternion"></a>

#### bpy.types.Object.rotation_quaternion

Rotation in Quaternions (array of 4 items, in [-inf, inf], default (1.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.Object.scale"></a>

#### bpy.types.Object.scale

Scaling of the object (array of 3 items, in [-inf, inf], default (1.0, 1.0, 1.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Object.selection_sets"></a>

#### bpy.types.Object.selection_sets

List of groups of bones for easy selection (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[`SelectionSet`]

<a id="bpy.types.Object.shader_effects"></a>

#### bpy.types.Object.shader_effects

Effects affecting display of object (default None, readonly)

**Type:**

[`ObjectShaderFx`](bpy.types.ObjectShaderFx.md#bpy.types.ObjectShaderFx "bpy.types.ObjectShaderFx")[[`ShaderFx`](bpy.types.ShaderFx.md#bpy.types.ShaderFx "bpy.types.ShaderFx")]

<a id="bpy.types.Object.shadow_terminator_geometry_offset"></a>

#### bpy.types.Object.shadow_terminator_geometry_offset

Offset rays from the surface to reduce shadow terminator artifact on low poly geometry. Only affects triangles at grazing angles to light (in [0, inf], default 0.1)

**Type:**

float

<a id="bpy.types.Object.shadow_terminator_normal_offset"></a>

#### bpy.types.Object.shadow_terminator_normal_offset

Offset rays from the surface to reduce shadow terminator artifact on low poly geometry. Only affect triangles that are affected by the geometry offset (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Object.shadow_terminator_shading_offset"></a>

#### bpy.types.Object.shadow_terminator_shading_offset

Push the shadow terminator towards the light to hide artifacts on low poly geometry (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.Object.show_all_edges"></a>

#### bpy.types.Object.show_all_edges

Display all edges for mesh objects (default False)

**Type:**

bool

<a id="bpy.types.Object.show_axis"></a>

#### bpy.types.Object.show_axis

Display the object’s origin and axes (default False)

**Type:**

bool

<a id="bpy.types.Object.show_bounds"></a>

#### bpy.types.Object.show_bounds

Display the object’s bounds (default False)

**Type:**

bool

<a id="bpy.types.Object.show_empty_image_only_axis_aligned"></a>

#### bpy.types.Object.show_empty_image_only_axis_aligned

Only display the image when it is aligned with the view axis (default False)

**Type:**

bool

<a id="bpy.types.Object.show_empty_image_orthographic"></a>

#### bpy.types.Object.show_empty_image_orthographic

Display image in orthographic mode (default True)

**Type:**

bool

<a id="bpy.types.Object.show_empty_image_perspective"></a>

#### bpy.types.Object.show_empty_image_perspective

Display image in perspective mode (default True)

**Type:**

bool

<a id="bpy.types.Object.show_in_front"></a>

#### bpy.types.Object.show_in_front

Make the object display in front of others (default False)

**Type:**

bool

<a id="bpy.types.Object.show_instancer_for_render"></a>

#### bpy.types.Object.show_instancer_for_render

Make instancer visible when rendering (default True)

**Type:**

bool

<a id="bpy.types.Object.show_instancer_for_viewport"></a>

#### bpy.types.Object.show_instancer_for_viewport

Make instancer visible in the viewport (default True)

**Type:**

bool

<a id="bpy.types.Object.show_name"></a>

#### bpy.types.Object.show_name

Display the object’s name (default False)

**Type:**

bool

<a id="bpy.types.Object.show_only_shape_key"></a>

#### bpy.types.Object.show_only_shape_key

Only show the active shape key at full value (default False)

**Type:**

bool

<a id="bpy.types.Object.show_texture_space"></a>

#### bpy.types.Object.show_texture_space

Display the object’s texture space (default False)

**Type:**

bool

<a id="bpy.types.Object.show_transparent"></a>

#### bpy.types.Object.show_transparent

Display material transparency in the object (default False)

**Type:**

bool

<a id="bpy.types.Object.show_wire"></a>

#### bpy.types.Object.show_wire

Display the object’s wireframe over solid shading (default False)

**Type:**

bool

<a id="bpy.types.Object.soft_body"></a>

#### bpy.types.Object.soft_body

Settings for soft body simulation (readonly)

**Type:**

[`SoftBodySettings`](bpy.types.SoftBodySettings.md#bpy.types.SoftBodySettings "bpy.types.SoftBodySettings") | None

<a id="bpy.types.Object.track_axis"></a>

#### bpy.types.Object.track_axis

Axis that points in the ‘forward’ direction (applies to Instance Vertices when Align to Vertex Normal is enabled) (default `'POS_X'`)

**Type:**

Literal[[Object Axis Items](bpy_types_enum_items/object_axis_items.md#rna-enum-object-axis-items)]

<a id="bpy.types.Object.type"></a>

#### bpy.types.Object.type

Type of object (default `'EMPTY'`, readonly)

**Type:**

Literal[[Object Type Items](bpy_types_enum_items/object_type_items.md#rna-enum-object-type-items)]

<a id="bpy.types.Object.up_axis"></a>

#### bpy.types.Object.up_axis

Axis that points in the upward direction (applies to Instance Vertices when Align to Vertex Normal is enabled) (default `'Y'`)

**Type:**

Literal[‘X’, ‘Y’, ‘Z’]

<a id="bpy.types.Object.use_camera_lock_parent"></a>

#### bpy.types.Object.use_camera_lock_parent

View Lock 3D viewport camera transformation affects the object’s parent instead (default False)

**Type:**

bool

<a id="bpy.types.Object.use_dynamic_topology_sculpting"></a>

#### bpy.types.Object.use_dynamic_topology_sculpting

(default False, readonly)

**Type:**

bool

<a id="bpy.types.Object.use_empty_image_alpha"></a>

#### bpy.types.Object.use_empty_image_alpha

Use alpha blending instead of alpha test (can produce sorting artifacts) (default False)

**Type:**

bool

<a id="bpy.types.Object.use_grease_pencil_lights"></a>

#### bpy.types.Object.use_grease_pencil_lights

Lights affect Grease Pencil object (default True)

**Type:**

bool

<a id="bpy.types.Object.use_instance_faces_scale"></a>

#### bpy.types.Object.use_instance_faces_scale

Scale instance based on face size (default False)

**Type:**

bool

<a id="bpy.types.Object.use_instance_vertices_rotation"></a>

#### bpy.types.Object.use_instance_vertices_rotation

Rotate instance according to vertex normal (default False)

**Type:**

bool

<a id="bpy.types.Object.use_mesh_mirror_x"></a>

#### bpy.types.Object.use_mesh_mirror_x

Enable mesh symmetry in the X axis (default False)

**Type:**

bool

<a id="bpy.types.Object.use_mesh_mirror_y"></a>

#### bpy.types.Object.use_mesh_mirror_y

Enable mesh symmetry in the Y axis (default False)

**Type:**

bool

<a id="bpy.types.Object.use_mesh_mirror_z"></a>

#### bpy.types.Object.use_mesh_mirror_z

Enable mesh symmetry in the Z axis (default False)

**Type:**

bool

<a id="bpy.types.Object.use_parent_final_indices"></a>

#### bpy.types.Object.use_parent_final_indices

Use the final evaluated indices rather than the original mesh indices (default False)

**Type:**

bool

<a id="bpy.types.Object.use_shape_key_edit_mode"></a>

#### bpy.types.Object.use_shape_key_edit_mode

Display shape keys in edit mode (for meshes only) (default False)

**Type:**

bool

<a id="bpy.types.Object.use_simulation_cache"></a>

#### bpy.types.Object.use_simulation_cache

Cache frames during simulation nodes playback (default True)

**Type:**

bool

<a id="bpy.types.Object.vertex_groups"></a>

#### bpy.types.Object.vertex_groups

Vertex groups of the object (default None, readonly)

**Type:**

[`VertexGroups`](bpy.types.VertexGroups.md#bpy.types.VertexGroups "bpy.types.VertexGroups")[[`VertexGroup`](bpy.types.VertexGroup.md#bpy.types.VertexGroup "bpy.types.VertexGroup")]

<a id="bpy.types.Object.visible_camera"></a>

#### bpy.types.Object.visible_camera

Object visibility to camera rays (default True)

**Type:**

bool

<a id="bpy.types.Object.visible_diffuse"></a>

#### bpy.types.Object.visible_diffuse

Object visibility to diffuse rays (default True)

**Type:**

bool

<a id="bpy.types.Object.visible_glossy"></a>

#### bpy.types.Object.visible_glossy

Object visibility to glossy rays (default True)

**Type:**

bool

<a id="bpy.types.Object.visible_raycast"></a>

#### bpy.types.Object.visible_raycast

Object visibility to raycast rays. Implicitly false for Blended materials. (default True)

**Type:**

bool

<a id="bpy.types.Object.visible_shadow"></a>

#### bpy.types.Object.visible_shadow

Object visibility to shadow rays (default True)

**Type:**

bool

<a id="bpy.types.Object.visible_transmission"></a>

#### bpy.types.Object.visible_transmission

Object visibility to transmission rays (default True)

**Type:**

bool

<a id="bpy.types.Object.visible_volume_scatter"></a>

#### bpy.types.Object.visible_volume_scatter

Object visibility to volume scattering rays (default True)

**Type:**

bool

<a id="bpy.types.Object.children"></a>

#### bpy.types.Object.children

All the children of this object.

**Type:**

tuple[[`Object`](#bpy.types.Object "bpy.types.Object"), …]

> **Note:**
>
> Takes `O(len(bpy.data.objects))` time.

(readonly)

<a id="bpy.types.Object.children_recursive"></a>

#### bpy.types.Object.children_recursive

A list of all children from this object.

**Type:**

list[[`Object`](#bpy.types.Object "bpy.types.Object")]

> **Note:**
>
> Takes `O(len(bpy.data.objects))` time.

(readonly)

<a id="bpy.types.Object.users_collection"></a>

#### bpy.types.Object.users_collection

The collections this object is in.

**Type:**

tuple[[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection"), …]

> **Note:**
>
> Takes `O(len(bpy.data.collections) + len(bpy.data.scenes))` time.

(readonly)

<a id="bpy.types.Object.users_scene"></a>

#### bpy.types.Object.users_scene

The scenes this object is in.

**Type:**

tuple[[`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene"), …]

> **Note:**
>
> Takes `O(len(bpy.data.scenes) * len(bpy.data.objects))` time.

(readonly)

<a id="bpy.types.Object.select_get"></a>

#### bpy.types.Object.select_get(*, view_layer=None)

Test if the object is selected. The selection state is per view layer.

**Parameters:**

**view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – Use this instead of the active view layer (optional)

**Returns:**

Object selected

**Return type:**

bool

<a id="bpy.types.Object.select_set"></a>

#### bpy.types.Object.select_set(state, *, view_layer=None)

Select or deselect the object. The selection state is per view layer.

**Parameters:**

- **state** (bool) – Selection state to define
- **view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – Use this instead of the active view layer (optional)

<a id="bpy.types.Object.hide_get"></a>

#### bpy.types.Object.hide_get(*, view_layer=None)

Test if the object is hidden for viewport editing. This hiding state is per view layer.

**Parameters:**

**view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – Use this instead of the active view layer (optional)

**Returns:**

Object hidden

**Return type:**

bool

<a id="bpy.types.Object.hide_set"></a>

#### bpy.types.Object.hide_set(state, *, view_layer=None)

Hide the object for viewport editing. This hiding state is per view layer.

**Parameters:**

- **state** (bool) – Hide state to define
- **view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – Use this instead of the active view layer (optional)

<a id="bpy.types.Object.visible_get"></a>

#### bpy.types.Object.visible_get(*, view_layer=None, viewport=None)

Test if the object is visible in the 3D viewport, taking into account all visibility settings

**Parameters:**

- **view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – Use this instead of the active view layer (optional)
- **viewport** ([`SpaceView3D`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D "bpy.types.SpaceView3D") | None) – Use this instead of the active 3D viewport (optional)

**Returns:**

Object visible

**Return type:**

bool

<a id="bpy.types.Object.holdout_get"></a>

#### bpy.types.Object.holdout_get(*, view_layer=None)

Test if object is masked in the view layer

**Parameters:**

**view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – Use this instead of the active view layer (optional)

**Returns:**

Object holdout

**Return type:**

bool

<a id="bpy.types.Object.indirect_only_get"></a>

#### bpy.types.Object.indirect_only_get(*, view_layer=None)

Test if object is set to contribute only indirectly (through shadows and reflections) in the view layer

**Parameters:**

**view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – Use this instead of the active view layer (optional)

**Returns:**

Object indirect only

**Return type:**

bool

<a id="bpy.types.Object.local_view_get"></a>

#### bpy.types.Object.local_view_get(viewport)

Get the local view state for this object

**Parameters:**

**viewport** ([`SpaceView3D`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D "bpy.types.SpaceView3D") | None) – Viewport in local view (never None)

**Returns:**

Object local view state

**Return type:**

bool

<a id="bpy.types.Object.local_view_set"></a>

#### bpy.types.Object.local_view_set(viewport, state)

Set the local view state for this object

**Parameters:**

- **viewport** ([`SpaceView3D`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D "bpy.types.SpaceView3D") | None) – Viewport in local view (never None)
- **state** (bool) – Local view state to define

<a id="bpy.types.Object.visible_in_viewport_get"></a>

#### bpy.types.Object.visible_in_viewport_get(viewport)

Check for local view and local collections for this viewport and object

**Parameters:**

**viewport** ([`SpaceView3D`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D "bpy.types.SpaceView3D") | None) – Viewport in local collections (never None)

**Returns:**

Object viewport visibility

**Return type:**

bool

<a id="bpy.types.Object.convert_space"></a>

#### bpy.types.Object.convert_space(*, pose_bone=None, matrix=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)), from_space='WORLD', to_space='WORLD')

Convert (transform) the given matrix from one space to another

**Parameters:**

- **pose_bone** ([`PoseBone`](bpy.types.PoseBone.md#bpy.types.PoseBone "bpy.types.PoseBone") | None) – Bone to use to define spaces (may be None, in which case only the two ‘WORLD’ and ‘LOCAL’ spaces are usable) (optional)
- **matrix** ([`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix") | Sequence[Sequence[float]]) – The matrix to transform (multi-dimensional array of 4 * 4 items, in [-inf, inf], optional)
- **from_space** (Literal['WORLD', 'POSE', 'LOCAL_WITH_PARENT', 'LOCAL']) –

  The space in which ‘matrix’ is currently (optional)

  - `WORLD`
    World Space – The most global space in Blender.
  - `POSE`
    Pose Space – The pose space of a bone (its armature’s object space).
  - `LOCAL_WITH_PARENT`
    Local With Parent – The rest pose local space of a bone (this matrix includes parent transforms).
  - `LOCAL`
    Local Space – The local space of an object/bone.
- **to_space** (Literal['WORLD', 'POSE', 'LOCAL_WITH_PARENT', 'LOCAL']) –

  The space to which you want to transform ‘matrix’ (optional)

  - `WORLD`
    World Space – The most global space in Blender.
  - `POSE`
    Pose Space – The pose space of a bone (its armature’s object space).
  - `LOCAL_WITH_PARENT`
    Local With Parent – The rest pose local space of a bone (this matrix includes parent transforms).
  - `LOCAL`
    Local Space – The local space of an object/bone.

**Returns:**

The transformed matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf])

**Return type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Object.calc_matrix_camera"></a>

#### bpy.types.Object.calc_matrix_camera(depsgraph, *, x=1, y=1, scale_x=1.0, scale_y=1.0)

Generate the camera projection matrix of this object (mostly useful for Camera and Light types)

**Parameters:**

- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Depsgraph to get evaluated data from
- **x** (int) – Width of the render area (in [0, inf], optional)
- **y** (int) – Height of the render area (in [0, inf], optional)
- **scale_x** (float) – Width scaling factor (in [1e-06, inf], optional)
- **scale_y** (float) – Height scaling factor (in [1e-06, inf], optional)

**Returns:**

The camera projection matrix (multi-dimensional array of 4 * 4 items, in [-inf, inf])

**Return type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.Object.camera_fit_coords"></a>

#### bpy.types.Object.camera_fit_coords(depsgraph, coordinates)

Compute the coordinate (and scale for ortho cameras) given object should be to ‘see’ all given coordinates

**Parameters:**

- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Depsgraph to get evaluated data from
- **coordinates** (Sequence[float]) – Coordinates to fit in (array of 1 items, in [-inf, inf], never None)

**Returns:**

`co_return`, The location to aim to be able to see all given points, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`scale_return`, The ortho scale to aim to be able to see all given points (if relevant), float

**Return type:**

tuple[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), float]

<a id="bpy.types.Object.crazyspace_eval"></a>

#### bpy.types.Object.crazyspace_eval(depsgraph, scene)

Compute orientation mapping between vertices of an original object and object with shape keys and deforming modifiers applied.The evaluation is to be freed with the crazyspace_eval_free function

**Parameters:**

- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Dependency Graph, Evaluated dependency graph
- **scene** ([`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None) – Scene, Scene of the object

<a id="bpy.types.Object.crazyspace_displacement_to_deformed"></a>

#### bpy.types.Object.crazyspace_displacement_to_deformed(*, vertex_index=0, displacement=(0.0, 0.0, 0.0))

Convert displacement vector from non-deformed object space to deformed object space

**Parameters:**

- **vertex_index** (int) – vertex_index, (in [-inf, inf], optional)
- **displacement** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – displacement, (array of 3 items, in [-inf, inf], optional)

**Returns:**

displacement_deformed, (array of 3 items, in [-inf, inf])

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Object.crazyspace_displacement_to_original"></a>

#### bpy.types.Object.crazyspace_displacement_to_original(*, vertex_index=0, displacement=(0.0, 0.0, 0.0))

Free evaluated state of crazyspace

**Parameters:**

- **vertex_index** (int) – vertex_index, (in [-inf, inf], optional)
- **displacement** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – displacement, (array of 3 items, in [-inf, inf], optional)

**Returns:**

displacement_original, (array of 3 items, in [-inf, inf])

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.Object.crazyspace_eval_clear"></a>

#### bpy.types.Object.crazyspace_eval_clear()

crazyspace_eval_clear

<a id="bpy.types.Object.to_mesh"></a>

#### bpy.types.Object.to_mesh(*, preserve_all_data_layers=False, depsgraph=None)

Create a Mesh data-block from the current state of the object. The object owns the data-block. To force free it use to_mesh_clear(). The result is temporary and cannot be used by objects from the main database.

**Parameters:**

- **preserve_all_data_layers** (bool) – Preserve all data layers in the mesh, like UV maps and vertex groups. By default Blender only computes the subset of data layers needed for viewport display and rendering, for better performance. (optional)
- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Dependency Graph, Evaluated dependency graph which is required when preserve_all_data_layers is true (optional)

**Returns:**

Mesh created from object

**Return type:**

[`Mesh`](bpy.types.Mesh.md#bpy.types.Mesh "bpy.types.Mesh")

<a id="bpy.types.Object.to_mesh_clear"></a>

#### bpy.types.Object.to_mesh_clear()

Clears mesh data-block created by to_mesh()

<a id="bpy.types.Object.to_curve"></a>

#### bpy.types.Object.to_curve(depsgraph, *, apply_modifiers=False)

Create a Curve data-block from the current state of the object. This only works for curve and text objects. The object owns the data-block. To force free it, use to_curve_clear(). The result is temporary and cannot be used by objects from the main database.

**Parameters:**

- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Dependency Graph, Evaluated dependency graph
- **apply_modifiers** (bool) – Apply the deform modifiers on the control points of the curve. This is only supported for curve objects. (optional)

**Returns:**

Curve created from object

**Return type:**

[`Curve`](bpy.types.Curve.md#bpy.types.Curve "bpy.types.Curve")

<a id="bpy.types.Object.to_curve_clear"></a>

#### bpy.types.Object.to_curve_clear()

Clears curve data-block created by to_curve()

<a id="bpy.types.Object.find_armature"></a>

#### bpy.types.Object.find_armature()

Find armature influencing this object as a parent or via a modifier

**Returns:**

Armature object influencing this object or nullptr

**Return type:**

[`Object`](#bpy.types.Object "bpy.types.Object")

<a id="bpy.types.Object.shape_key_add"></a>

#### bpy.types.Object.shape_key_add(*, name='Key', from_mix=True)

Add shape key to this object

**Parameters:**

- **name** (str) – Unique name for the new key-block (optional, never None)
- **from_mix** (bool) – Create new shape from existing mix of shapes (optional)

**Returns:**

New shape key-block

**Return type:**

[`ShapeKey`](bpy.types.ShapeKey.md#bpy.types.ShapeKey "bpy.types.ShapeKey")

<a id="bpy.types.Object.shape_key_remove"></a>

#### bpy.types.Object.shape_key_remove(key)

Remove a Shape Key from this object

**Parameters:**

**key** ([`ShapeKey`](bpy.types.ShapeKey.md#bpy.types.ShapeKey "bpy.types.ShapeKey") | None) – Key-block to be removed (never None)

<a id="bpy.types.Object.shape_key_clear"></a>

#### bpy.types.Object.shape_key_clear()

Remove all Shape Keys from this object

<a id="bpy.types.Object.shape_keys_selected"></a>

#### bpy.types.Object.shape_keys_selected()

Return selected shape keys

**Returns:**

keyblocks

**Return type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ShapeKey`](bpy.types.ShapeKey.md#bpy.types.ShapeKey "bpy.types.ShapeKey")]

<a id="bpy.types.Object.ray_cast"></a>

#### bpy.types.Object.ray_cast(origin, direction, *, distance=1.70141e+38, depsgraph=None)

Cast a ray onto evaluated geometry, in object space (using context’s or provided depsgraph to get evaluated mesh if needed)

**Parameters:**

- **origin** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Origin of the ray, in object space (array of 3 items, in [-inf, inf])
- **direction** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Direction of the ray, in object space (array of 3 items, in [-inf, inf])
- **distance** (float) – Maximum distance (in [0, inf], optional)
- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Depsgraph to use to get evaluated data, when called from original object (only needed if current Context’s depsgraph is not suitable) (optional)

**Returns:**

`result`, Whether the ray successfully hit the geometry, bool

`location`, The hit location of this ray cast, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`normal`, The face normal at the ray cast hit location, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`index`, The face index, -1 when original data isn’t available, int

**Return type:**

tuple[bool, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), int]

<a id="bpy.types.Object.closest_point_on_mesh"></a>

#### bpy.types.Object.closest_point_on_mesh(origin, *, distance=1.84467e+19, depsgraph=None)

Find the nearest point on evaluated geometry, in object space (using context’s or provided depsgraph to get evaluated mesh if needed)

**Parameters:**

- **origin** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Point to find closest geometry from (in object space) (array of 3 items, in [-inf, inf])
- **distance** (float) – Maximum distance (in [0, inf], optional)
- **depsgraph** ([`Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph") | None) – Depsgraph to use to get evaluated data, when called from original object (only needed if current Context’s depsgraph is not suitable) (optional)

**Returns:**

`result`, Whether closest point on geometry was found, bool

`location`, The location on the object closest to the point, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`normal`, The face normal at the closest point, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

`index`, The face index, -1 when original data isn’t available, int

**Return type:**

tuple[bool, [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), [`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector"), int]

<a id="bpy.types.Object.is_modified"></a>

#### bpy.types.Object.is_modified(scene, settings)

Determine if this object is modified from the base mesh data

**Parameters:**

- **scene** ([`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None) – Scene in which to check the object (never None)
- **settings** (Literal['PREVIEW', 'RENDER']) –

  Modifier settings to apply

  - `PREVIEW`
    Preview – Apply modifier preview settings.
  - `RENDER`
    Render – Apply modifier render settings.

**Returns:**

Whether the object is modified

**Return type:**

bool

<a id="bpy.types.Object.is_deform_modified"></a>

#### bpy.types.Object.is_deform_modified(scene, settings)

Determine if this object is modified by a deformation from the base mesh data

**Parameters:**

- **scene** ([`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None) – Scene in which to check the object (never None)
- **settings** (Literal['PREVIEW', 'RENDER']) –

  Modifier settings to apply

  - `PREVIEW`
    Preview – Apply modifier preview settings.
  - `RENDER`
    Render – Apply modifier render settings.

**Returns:**

Whether the object is deform-modified

**Return type:**

bool

<a id="bpy.types.Object.update_from_editmode"></a>

#### bpy.types.Object.update_from_editmode()

Load the objects edit-mode data into the object data

**Returns:**

Success

**Return type:**

bool

<a id="bpy.types.Object.cache_release"></a>

#### bpy.types.Object.cache_release()

Release memory used by caches associated with this object. Intended to be used by render engines only.

<a id="bpy.types.Object.evaluated_geometry"></a>

#### bpy.types.Object.evaluated_geometry()

Get the evaluated geometry set of this evaluated object. This only works for
objects that contain geometry data like meshes and curves but not e.g. cameras.

**Returns:**

The evaluated geometry.

**Return type:**

[`GeometrySet`](bpy.types.GeometrySet.md#bpy.types.GeometrySet "bpy.types.GeometrySet")

<a id="bpy.types.Object.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Object.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Object.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Object.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Object.type "bpy.types.Object.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Object.type "bpy.types.Object.type")

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - `bpy.context.active_object` - `bpy.context.edit_object` - `bpy.context.editable_objects` - `bpy.context.image_paint_object` - `bpy.context.object` - `bpy.context.objects_in_mode` - `bpy.context.objects_in_mode_unique_data` - `bpy.context.particle_edit_object` - `bpy.context.pose_object` - `bpy.context.sculpt_object` - `bpy.context.selectable_objects` - `bpy.context.selected_editable_objects` - `bpy.context.selected_objects` - `bpy.context.vertex_paint_object` - `bpy.context.visible_objects` - `bpy.context.weight_paint_object` - [`Action.flip_with_pose`](bpy.types.Action.md#bpy.types.Action.flip_with_pose "bpy.types.Action.flip_with_pose") - [`ActionConstraint.target`](bpy.types.ActionConstraint.md#bpy.types.ActionConstraint.target "bpy.types.ActionConstraint.target") - [`ArmatureModifier.object`](bpy.types.ArmatureModifier.md#bpy.types.ArmatureModifier.object "bpy.types.ArmatureModifier.object") - [`ArrayModifier.curve`](bpy.types.ArrayModifier.md#bpy.types.ArrayModifier.curve "bpy.types.ArrayModifier.curve") - [`ArrayModifier.end_cap`](bpy.types.ArrayModifier.md#bpy.types.ArrayModifier.end_cap "bpy.types.ArrayModifier.end_cap") - [`ArrayModifier.offset_object`](bpy.types.ArrayModifier.md#bpy.types.ArrayModifier.offset_object "bpy.types.ArrayModifier.offset_object") - [`ArrayModifier.start_cap`](bpy.types.ArrayModifier.md#bpy.types.ArrayModifier.start_cap "bpy.types.ArrayModifier.start_cap") - [`BlendData.objects`](bpy.types.BlendData.md#bpy.types.BlendData.objects "bpy.types.BlendData.objects") - [`BlendDataMeshes.new_from_object`](bpy.types.BlendDataMeshes.md#bpy.types.BlendDataMeshes.new_from_object "bpy.types.BlendDataMeshes.new_from_object") - [`BlendDataObjects.new`](bpy.types.BlendDataObjects.md#bpy.types.BlendDataObjects.new "bpy.types.BlendDataObjects.new") - [`BlendDataObjects.remove`](bpy.types.BlendDataObjects.md#bpy.types.BlendDataObjects.remove "bpy.types.BlendDataObjects.remove") - [`BoidRuleAvoid.object`](bpy.types.BoidRuleAvoid.md#bpy.types.BoidRuleAvoid.object "bpy.types.BoidRuleAvoid.object") - [`BoidRuleFollowLeader.object`](bpy.types.BoidRuleFollowLeader.md#bpy.types.BoidRuleFollowLeader.object "bpy.types.BoidRuleFollowLeader.object") - [`BoidRuleGoal.object`](bpy.types.BoidRuleGoal.md#bpy.types.BoidRuleGoal.object "bpy.types.BoidRuleGoal.object") - [`BooleanModifier.object`](bpy.types.BooleanModifier.md#bpy.types.BooleanModifier.object "bpy.types.BooleanModifier.object") - [`CameraDOFSettings.focus_object`](bpy.types.CameraDOFSettings.md#bpy.types.CameraDOFSettings.focus_object "bpy.types.CameraDOFSettings.focus_object") - [`CastModifier.object`](bpy.types.CastModifier.md#bpy.types.CastModifier.object "bpy.types.CastModifier.object") - [`ChildOfConstraint.target`](bpy.types.ChildOfConstraint.md#bpy.types.ChildOfConstraint.target "bpy.types.ChildOfConstraint.target") - [`ClampToConstraint.target`](bpy.types.ClampToConstraint.md#bpy.types.ClampToConstraint.target "bpy.types.ClampToConstraint.target") - [`Collection.all_objects`](bpy.types.Collection.md#bpy.types.Collection.all_objects "bpy.types.Collection.all_objects") - [`Collection.objects`](bpy.types.Collection.md#bpy.types.Collection.objects "bpy.types.Collection.objects") - [`CollectionObjects.link`](bpy.types.CollectionObjects.md#bpy.types.CollectionObjects.link "bpy.types.CollectionObjects.link") - [`CollectionObjects.unlink`](bpy.types.CollectionObjects.md#bpy.types.CollectionObjects.unlink "bpy.types.CollectionObjects.unlink") - [`Constraint.space_object`](bpy.types.Constraint.md#bpy.types.Constraint.space_object "bpy.types.Constraint.space_object") - [`ConstraintTarget.target`](bpy.types.ConstraintTarget.md#bpy.types.ConstraintTarget.target "bpy.types.ConstraintTarget.target") - [`ConstraintTargetBone.target`](bpy.types.ConstraintTargetBone.md#bpy.types.ConstraintTargetBone.target "bpy.types.ConstraintTargetBone.target") - [`CopyLocationConstraint.target`](bpy.types.CopyLocationConstraint.md#bpy.types.CopyLocationConstraint.target "bpy.types.CopyLocationConstraint.target") - [`CopyRotationConstraint.target`](bpy.types.CopyRotationConstraint.md#bpy.types.CopyRotationConstraint.target "bpy.types.CopyRotationConstraint.target") - [`CopyScaleConstraint.target`](bpy.types.CopyScaleConstraint.md#bpy.types.CopyScaleConstraint.target "bpy.types.CopyScaleConstraint.target") - [`CopyTransformsConstraint.target`](bpy.types.CopyTransformsConstraint.md#bpy.types.CopyTransformsConstraint.target "bpy.types.CopyTransformsConstraint.target") - [`Curve.bevel_object`](bpy.types.Curve.md#bpy.types.Curve.bevel_object "bpy.types.Curve.bevel_object") - [`Curve.taper_object`](bpy.types.Curve.md#bpy.types.Curve.taper_object "bpy.types.Curve.taper_object") - [`CurveModifier.object`](bpy.types.CurveModifier.md#bpy.types.CurveModifier.object "bpy.types.CurveModifier.object") - [`Curves.surface`](bpy.types.Curves.md#bpy.types.Curves.surface "bpy.types.Curves.surface") - `CyclesRenderSettings.dicing_camera` - [`DampedTrackConstraint.target`](bpy.types.DampedTrackConstraint.md#bpy.types.DampedTrackConstraint.target "bpy.types.DampedTrackConstraint.target") - [`DataTransferModifier.object`](bpy.types.DataTransferModifier.md#bpy.types.DataTransferModifier.object "bpy.types.DataTransferModifier.object") - [`Depsgraph.objects`](bpy.types.Depsgraph.md#bpy.types.Depsgraph.objects "bpy.types.Depsgraph.objects") - [`DepsgraphObjectInstance.instance_object`](bpy.types.DepsgraphObjectInstance.md#bpy.types.DepsgraphObjectInstance.instance_object "bpy.types.DepsgraphObjectInstance.instance_object") - [`DepsgraphObjectInstance.object`](bpy.types.DepsgraphObjectInstance.md#bpy.types.DepsgraphObjectInstance.object "bpy.types.DepsgraphObjectInstance.object") - [`DepsgraphObjectInstance.parent`](bpy.types.DepsgraphObjectInstance.md#bpy.types.DepsgraphObjectInstance.parent "bpy.types.DepsgraphObjectInstance.parent") - [`DisplaceModifier.texture_coords_object`](bpy.types.DisplaceModifier.md#bpy.types.DisplaceModifier.texture_coords_object "bpy.types.DisplaceModifier.texture_coords_object") - [`DynamicPaintSurface.output_exists`](bpy.types.DynamicPaintSurface.md#bpy.types.DynamicPaintSurface.output_exists "bpy.types.DynamicPaintSurface.output_exists") - [`FieldSettings.source_object`](bpy.types.FieldSettings.md#bpy.types.FieldSettings.source_object "bpy.types.FieldSettings.source_object") - [`FloorConstraint.target`](bpy.types.FloorConstraint.md#bpy.types.FloorConstraint.target "bpy.types.FloorConstraint.target") - [`FluidDomainSettings.guide_parent`](bpy.types.FluidDomainSettings.md#bpy.types.FluidDomainSettings.guide_parent "bpy.types.FluidDomainSettings.guide_parent") - [`FollowPathConstraint.target`](bpy.types.FollowPathConstraint.md#bpy.types.FollowPathConstraint.target "bpy.types.FollowPathConstraint.target") - [`FollowTrackConstraint.camera`](bpy.types.FollowTrackConstraint.md#bpy.types.FollowTrackConstraint.camera "bpy.types.FollowTrackConstraint.camera") - [`FollowTrackConstraint.depth_object`](bpy.types.FollowTrackConstraint.md#bpy.types.FollowTrackConstraint.depth_object "bpy.types.FollowTrackConstraint.depth_object") - [`GPencilSculptGuide.reference_object`](bpy.types.GPencilSculptGuide.md#bpy.types.GPencilSculptGuide.reference_object "bpy.types.GPencilSculptGuide.reference_object") - [`GeometryAttributeConstraint.target`](bpy.types.GeometryAttributeConstraint.md#bpy.types.GeometryAttributeConstraint.target "bpy.types.GeometryAttributeConstraint.target") - [`GeometryNodeInputObject.object`](bpy.types.GeometryNodeInputObject.md#bpy.types.GeometryNodeInputObject.object "bpy.types.GeometryNodeInputObject.object") - [`GreasePencilArmatureModifier.object`](bpy.types.GreasePencilArmatureModifier.md#bpy.types.GreasePencilArmatureModifier.object "bpy.types.GreasePencilArmatureModifier.object") - [`GreasePencilArrayModifier.offset_object`](bpy.types.GreasePencilArrayModifier.md#bpy.types.GreasePencilArrayModifier.offset_object "bpy.types.GreasePencilArrayModifier.offset_object") - [`GreasePencilBuildModifier.object`](bpy.types.GreasePencilBuildModifier.md#bpy.types.GreasePencilBuildModifier.object "bpy.types.GreasePencilBuildModifier.object") - [`GreasePencilHookModifier.object`](bpy.types.GreasePencilHookModifier.md#bpy.types.GreasePencilHookModifier.object "bpy.types.GreasePencilHookModifier.object") - [`GreasePencilLatticeModifier.object`](bpy.types.GreasePencilLatticeModifier.md#bpy.types.GreasePencilLatticeModifier.object "bpy.types.GreasePencilLatticeModifier.object") - [`GreasePencilLayer.parent`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer.parent "bpy.types.GreasePencilLayer.parent") - [`GreasePencilLineartModifier.light_contour_object`](bpy.types.GreasePencilLineartModifier.md#bpy.types.GreasePencilLineartModifier.light_contour_object "bpy.types.GreasePencilLineartModifier.light_contour_object") - [`GreasePencilLineartModifier.source_camera`](bpy.types.GreasePencilLineartModifier.md#bpy.types.GreasePencilLineartModifier.source_camera "bpy.types.GreasePencilLineartModifier.source_camera") - [`GreasePencilLineartModifier.source_object`](bpy.types.GreasePencilLineartModifier.md#bpy.types.GreasePencilLineartModifier.source_object "bpy.types.GreasePencilLineartModifier.source_object") - [`GreasePencilMirrorModifier.object`](bpy.types.GreasePencilMirrorModifier.md#bpy.types.GreasePencilMirrorModifier.object "bpy.types.GreasePencilMirrorModifier.object") - [`GreasePencilOutlineModifier.object`](bpy.types.GreasePencilOutlineModifier.md#bpy.types.GreasePencilOutlineModifier.object "bpy.types.GreasePencilOutlineModifier.object") - [`GreasePencilShrinkwrapModifier.auxiliary_target`](bpy.types.GreasePencilShrinkwrapModifier.md#bpy.types.GreasePencilShrinkwrapModifier.auxiliary_target "bpy.types.GreasePencilShrinkwrapModifier.auxiliary_target") - [`GreasePencilShrinkwrapModifier.target`](bpy.types.GreasePencilShrinkwrapModifier.md#bpy.types.GreasePencilShrinkwrapModifier.target "bpy.types.GreasePencilShrinkwrapModifier.target") - [`GreasePencilTintModifier.object`](bpy.types.GreasePencilTintModifier.md#bpy.types.GreasePencilTintModifier.object "bpy.types.GreasePencilTintModifier.object") - [`GreasePencilWeightProximityModifier.object`](bpy.types.GreasePencilWeightProximityModifier.md#bpy.types.GreasePencilWeightProximityModifier.object "bpy.types.GreasePencilWeightProximityModifier.object") - [`HookModifier.object`](bpy.types.HookModifier.md#bpy.types.HookModifier.object "bpy.types.HookModifier.object") | - [`KinematicConstraint.pole_target`](bpy.types.KinematicConstraint.md#bpy.types.KinematicConstraint.pole_target "bpy.types.KinematicConstraint.pole_target") - [`KinematicConstraint.target`](bpy.types.KinematicConstraint.md#bpy.types.KinematicConstraint.target "bpy.types.KinematicConstraint.target") - [`LatticeModifier.object`](bpy.types.LatticeModifier.md#bpy.types.LatticeModifier.object "bpy.types.LatticeModifier.object") - [`LayerObjects.active`](bpy.types.LayerObjects.md#bpy.types.LayerObjects.active "bpy.types.LayerObjects.active") - [`LayerObjects.selected`](bpy.types.LayerObjects.md#bpy.types.LayerObjects.selected "bpy.types.LayerObjects.selected") - [`LimitDistanceConstraint.target`](bpy.types.LimitDistanceConstraint.md#bpy.types.LimitDistanceConstraint.target "bpy.types.LimitDistanceConstraint.target") - [`LineStyleAlphaModifier_DistanceFromObject.target`](bpy.types.LineStyleAlphaModifier_DistanceFromObject.md#bpy.types.LineStyleAlphaModifier_DistanceFromObject.target "bpy.types.LineStyleAlphaModifier_DistanceFromObject.target") - [`LineStyleColorModifier_DistanceFromObject.target`](bpy.types.LineStyleColorModifier_DistanceFromObject.md#bpy.types.LineStyleColorModifier_DistanceFromObject.target "bpy.types.LineStyleColorModifier_DistanceFromObject.target") - [`LineStyleThicknessModifier_DistanceFromObject.target`](bpy.types.LineStyleThicknessModifier_DistanceFromObject.md#bpy.types.LineStyleThicknessModifier_DistanceFromObject.target "bpy.types.LineStyleThicknessModifier_DistanceFromObject.target") - [`LockedTrackConstraint.target`](bpy.types.LockedTrackConstraint.md#bpy.types.LockedTrackConstraint.target "bpy.types.LockedTrackConstraint.target") - [`MaskModifier.armature`](bpy.types.MaskModifier.md#bpy.types.MaskModifier.armature "bpy.types.MaskModifier.armature") - [`MeshDeformModifier.object`](bpy.types.MeshDeformModifier.md#bpy.types.MeshDeformModifier.object "bpy.types.MeshDeformModifier.object") - [`MeshToVolumeModifier.object`](bpy.types.MeshToVolumeModifier.md#bpy.types.MeshToVolumeModifier.object "bpy.types.MeshToVolumeModifier.object") - [`MirrorModifier.mirror_object`](bpy.types.MirrorModifier.md#bpy.types.MirrorModifier.mirror_object "bpy.types.MirrorModifier.mirror_object") - [`NodeSocketObject.default_value`](bpy.types.NodeSocketObject.md#bpy.types.NodeSocketObject.default_value "bpy.types.NodeSocketObject.default_value") - [`NodeTreeInterfaceSocketObject.default_value`](bpy.types.NodeTreeInterfaceSocketObject.md#bpy.types.NodeTreeInterfaceSocketObject.default_value "bpy.types.NodeTreeInterfaceSocketObject.default_value") - [`NormalEditModifier.target`](bpy.types.NormalEditModifier.md#bpy.types.NormalEditModifier.target "bpy.types.NormalEditModifier.target") - [`Object.find_armature`](#bpy.types.Object.find_armature "bpy.types.Object.find_armature") - [`Object.parent`](#bpy.types.Object.parent "bpy.types.Object.parent") - [`ObjectBase.object`](bpy.types.ObjectBase.md#bpy.types.ObjectBase.object "bpy.types.ObjectBase.object") - [`ObjectSolverConstraint.camera`](bpy.types.ObjectSolverConstraint.md#bpy.types.ObjectSolverConstraint.camera "bpy.types.ObjectSolverConstraint.camera") - [`ParticleEdit.object`](bpy.types.ParticleEdit.md#bpy.types.ParticleEdit.object "bpy.types.ParticleEdit.object") - [`ParticleEdit.shape_object`](bpy.types.ParticleEdit.md#bpy.types.ParticleEdit.shape_object "bpy.types.ParticleEdit.shape_object") - [`ParticleHairKey.co_object`](bpy.types.ParticleHairKey.md#bpy.types.ParticleHairKey.co_object "bpy.types.ParticleHairKey.co_object") - [`ParticleHairKey.co_object_set`](bpy.types.ParticleHairKey.md#bpy.types.ParticleHairKey.co_object_set "bpy.types.ParticleHairKey.co_object_set") - [`ParticleInstanceModifier.object`](bpy.types.ParticleInstanceModifier.md#bpy.types.ParticleInstanceModifier.object "bpy.types.ParticleInstanceModifier.object") - [`ParticleSettings.instance_object`](bpy.types.ParticleSettings.md#bpy.types.ParticleSettings.instance_object "bpy.types.ParticleSettings.instance_object") - [`ParticleSettingsTextureSlot.object`](bpy.types.ParticleSettingsTextureSlot.md#bpy.types.ParticleSettingsTextureSlot.object "bpy.types.ParticleSettingsTextureSlot.object") - [`ParticleSystem.co_hair`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.co_hair "bpy.types.ParticleSystem.co_hair") - [`ParticleSystem.parent`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.parent "bpy.types.ParticleSystem.parent") - [`ParticleSystem.reactor_target_object`](bpy.types.ParticleSystem.md#bpy.types.ParticleSystem.reactor_target_object "bpy.types.ParticleSystem.reactor_target_object") - [`ParticleTarget.object`](bpy.types.ParticleTarget.md#bpy.types.ParticleTarget.object "bpy.types.ParticleTarget.object") - [`PivotConstraint.target`](bpy.types.PivotConstraint.md#bpy.types.PivotConstraint.target "bpy.types.PivotConstraint.target") - [`PoseBone.custom_shape`](bpy.types.PoseBone.md#bpy.types.PoseBone.custom_shape "bpy.types.PoseBone.custom_shape") - [`RenderEngine.bake`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.bake "bpy.types.RenderEngine.bake") - [`RenderEngine.camera_model_matrix`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.camera_model_matrix "bpy.types.RenderEngine.camera_model_matrix") - [`RenderEngine.camera_override`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.camera_override "bpy.types.RenderEngine.camera_override") - [`RenderEngine.camera_shift_x`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.camera_shift_x "bpy.types.RenderEngine.camera_shift_x") - [`RenderEngine.use_spherical_stereo`](bpy.types.RenderEngine.md#bpy.types.RenderEngine.use_spherical_stereo "bpy.types.RenderEngine.use_spherical_stereo") - [`RigidBodyConstraint.object1`](bpy.types.RigidBodyConstraint.md#bpy.types.RigidBodyConstraint.object1 "bpy.types.RigidBodyConstraint.object1") - [`RigidBodyConstraint.object2`](bpy.types.RigidBodyConstraint.md#bpy.types.RigidBodyConstraint.object2 "bpy.types.RigidBodyConstraint.object2") - [`RigidBodyWorld.convex_sweep_test`](bpy.types.RigidBodyWorld.md#bpy.types.RigidBodyWorld.convex_sweep_test "bpy.types.RigidBodyWorld.convex_sweep_test") - [`BakeSettings.cage_object`](bpy.types.BakeSettings.md#bpy.types.BakeSettings.cage_object "bpy.types.BakeSettings.cage_object") - [`Scene.camera`](bpy.types.Scene.md#bpy.types.Scene.camera "bpy.types.Scene.camera") - [`Scene.objects`](bpy.types.Scene.md#bpy.types.Scene.objects "bpy.types.Scene.objects") - [`Scene.ray_cast`](bpy.types.Scene.md#bpy.types.Scene.ray_cast "bpy.types.Scene.ray_cast") - [`Scene.uvedit_aspect`](bpy.types.Scene.md#bpy.types.Scene.uvedit_aspect "bpy.types.Scene.uvedit_aspect") - [`SceneStrip.scene_camera`](bpy.types.SceneStrip.md#bpy.types.SceneStrip.scene_camera "bpy.types.SceneStrip.scene_camera") - [`ScrewModifier.object`](bpy.types.ScrewModifier.md#bpy.types.ScrewModifier.object "bpy.types.ScrewModifier.object") - [`Sculpt.gravity_object`](bpy.types.Sculpt.md#bpy.types.Sculpt.gravity_object "bpy.types.Sculpt.gravity_object") - [`ShaderFxShadow.object`](bpy.types.ShaderFxShadow.md#bpy.types.ShaderFxShadow.object "bpy.types.ShaderFxShadow.object") - [`ShaderFxSwirl.object`](bpy.types.ShaderFxSwirl.md#bpy.types.ShaderFxSwirl.object "bpy.types.ShaderFxSwirl.object") - [`ShaderNodeTexCoord.object`](bpy.types.ShaderNodeTexCoord.md#bpy.types.ShaderNodeTexCoord.object "bpy.types.ShaderNodeTexCoord.object") - [`ShrinkwrapConstraint.target`](bpy.types.ShrinkwrapConstraint.md#bpy.types.ShrinkwrapConstraint.target "bpy.types.ShrinkwrapConstraint.target") - [`ShrinkwrapModifier.auxiliary_target`](bpy.types.ShrinkwrapModifier.md#bpy.types.ShrinkwrapModifier.auxiliary_target "bpy.types.ShrinkwrapModifier.auxiliary_target") - [`ShrinkwrapModifier.target`](bpy.types.ShrinkwrapModifier.md#bpy.types.ShrinkwrapModifier.target "bpy.types.ShrinkwrapModifier.target") - [`SimpleDeformModifier.origin`](bpy.types.SimpleDeformModifier.md#bpy.types.SimpleDeformModifier.origin "bpy.types.SimpleDeformModifier.origin") - [`SpaceView3D.camera`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D.camera "bpy.types.SpaceView3D.camera") - [`SpaceView3D.lock_object`](bpy.types.SpaceView3D.md#bpy.types.SpaceView3D.lock_object "bpy.types.SpaceView3D.lock_object") - [`SplineIKConstraint.target`](bpy.types.SplineIKConstraint.md#bpy.types.SplineIKConstraint.target "bpy.types.SplineIKConstraint.target") - [`StretchToConstraint.target`](bpy.types.StretchToConstraint.md#bpy.types.StretchToConstraint.target "bpy.types.StretchToConstraint.target") - [`SurfaceDeformModifier.target`](bpy.types.SurfaceDeformModifier.md#bpy.types.SurfaceDeformModifier.target "bpy.types.SurfaceDeformModifier.target") - [`TextCurve.follow_curve`](bpy.types.TextCurve.md#bpy.types.TextCurve.follow_curve "bpy.types.TextCurve.follow_curve") - [`TimelineMarker.camera`](bpy.types.TimelineMarker.md#bpy.types.TimelineMarker.camera "bpy.types.TimelineMarker.camera") - [`ToolSettings.anim_mirror_object`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.anim_mirror_object "bpy.types.ToolSettings.anim_mirror_object") - [`ToolSettings.anim_relative_object`](bpy.types.ToolSettings.md#bpy.types.ToolSettings.anim_relative_object "bpy.types.ToolSettings.anim_relative_object") - [`TrackToConstraint.target`](bpy.types.TrackToConstraint.md#bpy.types.TrackToConstraint.target "bpy.types.TrackToConstraint.target") - [`TransformConstraint.target`](bpy.types.TransformConstraint.md#bpy.types.TransformConstraint.target "bpy.types.TransformConstraint.target") - [`UVProjector.object`](bpy.types.UVProjector.md#bpy.types.UVProjector.object "bpy.types.UVProjector.object") - [`UVWarpModifier.object_from`](bpy.types.UVWarpModifier.md#bpy.types.UVWarpModifier.object_from "bpy.types.UVWarpModifier.object_from") - [`UVWarpModifier.object_to`](bpy.types.UVWarpModifier.md#bpy.types.UVWarpModifier.object_to "bpy.types.UVWarpModifier.object_to") - [`VertexWeightEditModifier.mask_tex_map_object`](bpy.types.VertexWeightEditModifier.md#bpy.types.VertexWeightEditModifier.mask_tex_map_object "bpy.types.VertexWeightEditModifier.mask_tex_map_object") - [`VertexWeightMixModifier.mask_tex_map_object`](bpy.types.VertexWeightMixModifier.md#bpy.types.VertexWeightMixModifier.mask_tex_map_object "bpy.types.VertexWeightMixModifier.mask_tex_map_object") - [`VertexWeightProximityModifier.mask_tex_map_object`](bpy.types.VertexWeightProximityModifier.md#bpy.types.VertexWeightProximityModifier.mask_tex_map_object "bpy.types.VertexWeightProximityModifier.mask_tex_map_object") - [`VertexWeightProximityModifier.target`](bpy.types.VertexWeightProximityModifier.md#bpy.types.VertexWeightProximityModifier.target "bpy.types.VertexWeightProximityModifier.target") - [`ViewLayer.objects`](bpy.types.ViewLayer.md#bpy.types.ViewLayer.objects "bpy.types.ViewLayer.objects") - [`VolumeDisplaceModifier.texture_map_object`](bpy.types.VolumeDisplaceModifier.md#bpy.types.VolumeDisplaceModifier.texture_map_object "bpy.types.VolumeDisplaceModifier.texture_map_object") - [`VolumeToMeshModifier.object`](bpy.types.VolumeToMeshModifier.md#bpy.types.VolumeToMeshModifier.object "bpy.types.VolumeToMeshModifier.object") - [`WarpModifier.object_from`](bpy.types.WarpModifier.md#bpy.types.WarpModifier.object_from "bpy.types.WarpModifier.object_from") - [`WarpModifier.object_to`](bpy.types.WarpModifier.md#bpy.types.WarpModifier.object_to "bpy.types.WarpModifier.object_to") - [`WarpModifier.texture_coords_object`](bpy.types.WarpModifier.md#bpy.types.WarpModifier.texture_coords_object "bpy.types.WarpModifier.texture_coords_object") - [`WaveModifier.start_position_object`](bpy.types.WaveModifier.md#bpy.types.WaveModifier.start_position_object "bpy.types.WaveModifier.start_position_object") - [`WaveModifier.texture_coords_object`](bpy.types.WaveModifier.md#bpy.types.WaveModifier.texture_coords_object "bpy.types.WaveModifier.texture_coords_object") - [`XrSessionSettings.base_pose_object`](bpy.types.XrSessionSettings.md#bpy.types.XrSessionSettings.base_pose_object "bpy.types.XrSessionSettings.base_pose_object") |
