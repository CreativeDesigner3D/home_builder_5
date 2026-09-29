<!-- source: Blender Python API reference 5.2 / bpy.ops.particle.html -->

<a id="module-bpy.ops.particle"></a>

# Particle Operators

<a id="bpy.ops.particle.brush_edit"></a>

### bpy.ops.particle.brush_edit(*, stroke=None, pen_flip=False)

Apply a stroke of brush to the particles

**Parameters:**

- **stroke** (`bpy_prop_collection`[`OperatorStrokeElement`] | None) – Stroke, (optional)
- **pen_flip** (bool) – Pen Flip, Whether a tablet’s eraser mode is being used (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.connect_hair"></a>

### bpy.ops.particle.connect_hair(*, all=False)

Connect hair to the emitter mesh

**Parameters:**

**all** (bool) – All Hair, Connect all hair systems to the emitter mesh (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.copy_particle_systems"></a>

### bpy.ops.particle.copy_particle_systems(*, space='OBJECT', remove_target_particles=True, use_active=False)

Copy particle systems from the active object to selected objects

**Parameters:**

- **space** (Literal['OBJECT', 'WORLD']) –

  Space, Space transform for copying from one object to another (optional)

  - `OBJECT`
    Object – Copy inside each object’s local space.
  - `WORLD`
    World – Copy in world space.
- **remove_target_particles** (bool) – Remove Target Particles, Remove particle systems on the target objects (optional)
- **use_active** (bool) – Use Active, Use the active particle system from the context (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.delete"></a>

### bpy.ops.particle.delete(*, type='PARTICLE')

Delete selected particles or keys

**Parameters:**

**type** (Literal['PARTICLE', 'KEY']) – Type, Delete a full particle or only keys (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.disconnect_hair"></a>

### bpy.ops.particle.disconnect_hair(*, all=False)

Disconnect hair from the emitter mesh

**Parameters:**

**all** (bool) – All Hair, Disconnect all hair systems from the emitter mesh (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.duplicate_particle_system"></a>

### bpy.ops.particle.duplicate_particle_system(*, use_duplicate_settings=False)

Duplicate particle system within the active object

**Parameters:**

**use_duplicate_settings** (bool) – Duplicate Settings, Duplicate settings as well, so the new particle system uses its own settings (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.dupliob_copy"></a>

### bpy.ops.particle.dupliob_copy()

Duplicate the current instance object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.dupliob_move_down"></a>

### bpy.ops.particle.dupliob_move_down()

Move instance object down in the list

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.dupliob_move_up"></a>

### bpy.ops.particle.dupliob_move_up()

Move instance object up in the list

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.dupliob_refresh"></a>

### bpy.ops.particle.dupliob_refresh()

Refresh list of instance objects and their weights

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.dupliob_remove"></a>

### bpy.ops.particle.dupliob_remove()

Remove the selected instance object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.edited_clear"></a>

### bpy.ops.particle.edited_clear()

Undo all edition performed on the particle system

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.hair_dynamics_preset_add"></a>

### bpy.ops.particle.hair_dynamics_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove a Hair Dynamics Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.particle.hide"></a>

### bpy.ops.particle.hide(*, unselected=False)

Hide selected particles

**Parameters:**

**unselected** (bool) – Unselected, Hide unselected rather than selected (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.mirror"></a>

### bpy.ops.particle.mirror()

Duplicate and mirror the selected particles along the local X axis

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.new"></a>

### bpy.ops.particle.new()

Add new particle settings

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.new_target"></a>

### bpy.ops.particle.new_target()

Add a new particle target

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.particle_edit_toggle"></a>

### bpy.ops.particle.particle_edit_toggle()

Toggle particle edit mode

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.particle_system_remove_all"></a>

### bpy.ops.particle.particle_system_remove_all()

Remove all particle system within the active object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.rekey"></a>

### bpy.ops.particle.rekey(*, keys_number=2)

Change the number of keys of selected particles (root and tip keys included)

**Parameters:**

**keys_number** (int) – Number of Keys, (in [2, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.remove_doubles"></a>

### bpy.ops.particle.remove_doubles(*, threshold=0.0002)

Remove selected particles close enough to others

**Parameters:**

**threshold** (float) – Merge Distance, Threshold distance within which particles are removed (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.reveal"></a>

### bpy.ops.particle.reveal(*, select=True)

Show hidden particles

**Parameters:**

**select** (bool) – Select, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.select_all"></a>

### bpy.ops.particle.select_all(*, action='TOGGLE')

(De)select all particles’ keys

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.select_less"></a>

### bpy.ops.particle.select_less()

Deselect boundary selected keys of each particle

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.select_linked"></a>

### bpy.ops.particle.select_linked()

Select all keys linked to already selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.select_linked_pick"></a>

### bpy.ops.particle.select_linked_pick(*, deselect=False, location=(0, 0))

Select nearest particle from mouse pointer

**Parameters:**

- **deselect** (bool) – Deselect, Deselect linked keys rather than selecting them (optional)
- **location** (Sequence[int]) – Location, (array of 2 items, in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.select_more"></a>

### bpy.ops.particle.select_more()

Select keys linked to boundary selected keys of each particle

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.select_random"></a>

### bpy.ops.particle.select_random(*, ratio=0.5, seed=0, action='SELECT', type='HAIR')

Select a randomly distributed set of hair or points

**Parameters:**

- **ratio** (float) – Ratio, Portion of items to select randomly (in [0, 1], optional)
- **seed** (int) – Random Seed, Seed for the random number generator (in [0, inf], optional)
- **action** (Literal['SELECT', 'DESELECT']) –

  Action, Selection action to execute (optional)

  - `SELECT`
    Select – Select all elements.
  - `DESELECT`
    Deselect – Deselect all elements.
- **type** (Literal['HAIR', 'POINTS']) – Type, Select either hair or points (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.select_roots"></a>

### bpy.ops.particle.select_roots(*, action='SELECT')

Select roots of all visible particles

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.select_tips"></a>

### bpy.ops.particle.select_tips(*, action='SELECT')

Select tips of all visible particles

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.shape_cut"></a>

### bpy.ops.particle.shape_cut()

Cut hair to conform to the set shape object

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.subdivide"></a>

### bpy.ops.particle.subdivide()

Subdivide selected particles segments (adds keys)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.target_move_down"></a>

### bpy.ops.particle.target_move_down()

Move particle target down in the list

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.target_move_up"></a>

### bpy.ops.particle.target_move_up()

Move particle target up in the list

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.target_remove"></a>

### bpy.ops.particle.target_remove()

Remove the selected particle target

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.unify_length"></a>

### bpy.ops.particle.unify_length()

Make selected hair the same length

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.particle.weight_set"></a>

### bpy.ops.particle.weight_set(*, factor=1.0)

Set the weight of selected keys

**Parameters:**

**factor** (float) – Factor, Interpolation factor between current brush weight, and keys’ weights (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
