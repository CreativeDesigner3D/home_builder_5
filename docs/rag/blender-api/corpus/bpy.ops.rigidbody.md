<!-- source: Blender Python API reference 5.2 / bpy.ops.rigidbody.html -->

<a id="module-bpy.ops.rigidbody"></a>

# Rigidbody Operators

<a id="bpy.ops.rigidbody.bake_to_keyframes"></a>

### bpy.ops.rigidbody.bake_to_keyframes(*, frame_start=1, frame_end=250, step=1)

Bake rigid body transformations of selected objects to keyframes

**Parameters:**

- **frame_start** (int) – Start Frame, Start frame for baking (in [0, 300000], optional)
- **frame_end** (int) – End Frame, End frame for baking (in [1, 300000], optional)
- **step** (int) – Frame Step, Frame Step (in [1, 120], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/rigidbody.py:108](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/rigidbody.py#L108)

<a id="bpy.ops.rigidbody.connect"></a>

### bpy.ops.rigidbody.connect(*, con_type='FIXED', pivot_type='CENTER', connection_pattern='SELECTED_TO_ACTIVE')

Create rigid body constraints between selected rigid bodies

**Parameters:**

- **con_type** (Literal['FIXED', 'POINT', 'HINGE', 'SLIDER', 'PISTON', 'GENERIC', 'GENERIC_SPRING', 'MOTOR']) –

  Type, Type of generated constraint (optional)

  - `FIXED`
    Fixed – Glue rigid bodies together.
  - `POINT`
    Point – Constrain rigid bodies to move around common pivot point.
  - `HINGE`
    Hinge – Restrict rigid body rotation to one axis.
  - `SLIDER`
    Slider – Restrict rigid body translation to one axis.
  - `PISTON`
    Piston – Restrict rigid body translation and rotation to one axis.
  - `GENERIC`
    Generic – Restrict translation and rotation to specified axes.
  - `GENERIC_SPRING`
    Generic Spring – Restrict translation and rotation to specified axes with springs.
  - `MOTOR`
    Motor – Drive rigid body around or along an axis.
- **pivot_type** (Literal['CENTER', 'ACTIVE', 'SELECTED']) –

  Location, Constraint pivot location (optional)

  - `CENTER`
    Center – Pivot location is between the constrained rigid bodies.
  - `ACTIVE`
    Active – Pivot location is at the active object position.
  - `SELECTED`
    Selected – Pivot location is at the selected object position.
- **connection_pattern** (Literal['SELECTED_TO_ACTIVE', 'CHAIN_DISTANCE']) –

  Connection Pattern, Pattern used to connect objects (optional)

  - `SELECTED_TO_ACTIVE`
    Selected to Active – Connect selected objects to the active object.
  - `CHAIN_DISTANCE`
    Chain by Distance – Connect objects as a chain based on distance, starting at the active object.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/rigidbody.py:277](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/rigidbody.py#L277)

<a id="bpy.ops.rigidbody.constraint_add"></a>

### bpy.ops.rigidbody.constraint_add(*, type='FIXED')

Add Rigid Body Constraint to active object

**Parameters:**

**type** (Literal[[Rigidbody Constraint Type Items](bpy_types_enum_items/rigidbody_constraint_type_items.md#rna-enum-rigidbody-constraint-type-items)]) – Rigid Body Constraint Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.constraint_remove"></a>

### bpy.ops.rigidbody.constraint_remove()

Remove Rigid Body Constraint from Object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.mass_calculate"></a>

### bpy.ops.rigidbody.mass_calculate(*, material='DEFAULT', density=1.0)

Automatically calculate mass values for Rigid Body Objects based on volume

**Parameters:**

- **material** (Literal['DEFAULT']) – Material Preset, Type of material that objects are made of (determines material density) (optional)
- **density** (float) – Density, Density value (kg/m^3), allows custom value if the ‘Custom’ preset is used (in [1.17549e-38, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.object_add"></a>

### bpy.ops.rigidbody.object_add(*, type='ACTIVE')

Add active object as Rigid Body

**Parameters:**

**type** (Literal[[Rigidbody Object Type Items](bpy_types_enum_items/rigidbody_object_type_items.md#rna-enum-rigidbody-object-type-items)]) – Rigid Body Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.object_remove"></a>

### bpy.ops.rigidbody.object_remove()

Remove Rigid Body settings from Object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.object_settings_copy"></a>

### bpy.ops.rigidbody.object_settings_copy()

Copy Rigid Body settings from active object to selected

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/rigidbody.py:45](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/rigidbody.py#L45)

<a id="bpy.ops.rigidbody.objects_add"></a>

### bpy.ops.rigidbody.objects_add(*, type='ACTIVE')

Add selected objects as Rigid Bodies

**Parameters:**

**type** (Literal[[Rigidbody Object Type Items](bpy_types_enum_items/rigidbody_object_type_items.md#rna-enum-rigidbody-object-type-items)]) – Rigid Body Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.objects_remove"></a>

### bpy.ops.rigidbody.objects_remove()

Remove selected objects from Rigid Body simulation

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.shape_change"></a>

### bpy.ops.rigidbody.shape_change(*, type='MESH')

Change collision shapes for selected Rigid Body Objects

**Parameters:**

**type** (Literal[[Rigidbody Object Shape Items](bpy_types_enum_items/rigidbody_object_shape_items.md#rna-enum-rigidbody-object-shape-items)]) – Rigid Body Shape, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.world_add"></a>

### bpy.ops.rigidbody.world_add()

Add Rigid Body simulation world to the current scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.rigidbody.world_remove"></a>

### bpy.ops.rigidbody.world_remove()

Remove Rigid Body simulation world from the current scene

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
