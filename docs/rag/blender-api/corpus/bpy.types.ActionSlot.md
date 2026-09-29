<!-- source: Blender Python API reference 5.2 / bpy.types.ActionSlot.html -->

<a id="actionslot-bpy-struct"></a>

# ActionSlot(bpy_struct)

Action Slots organize animation data within an action. Each action has slots with specific animation
data. An animated data-block specifies an action and a slot, determining the animation data it uses.
See the [Blender Manual](https://docs.blender.org/manual/en/5.1/animation/actions.html#action-slots)
for how Action Slots are used, or the
[technical documentation](https://developer.blender.org/docs/features/animation/)
for details on the animation system’s architecture.

<a id="create-access-an-action-slot"></a>

## Create & Access an Action Slot

To get started with Action Slots, you can easily create them by inserting a keyframe on an object. When you do this,
Blender automatically creates an Action & Slot for that data-block.

```python
import bpy

# Assume Suzanne mesh is present in the scene.
suzanne = bpy.data.objects["Suzanne"]

# Create animation data and an action for Suzanne:
# Slot will be automatically created.
suzanne.keyframe_insert("location", index=0)

# Action slots can be accessed like this:
action = suzanne.animation_data.action
for slot in action.slots:
    print(f"Slot Identifier {slot.identifier!r} "
          f"with name {slot.name_display!r} "
          f"targets ID type {slot.target_id_type!r}")
```

<a id="manually-create-an-action-slot"></a>

## Manually Create an Action Slot

If required you can also manually create Action Slots on an Action. Note the `target_id_type`
that matches the data-block type. Identifiers start with a prefix based on the ID type,
e.g. “OB” for objects, followed by the name. There can be identifiers like `OBSuzanne`
and `MESuzanne` and the name (`Suzanne`) can be shared between them. This is intentional,
so that the slots and the datablocks can have the same name.

```python
import bpy

# Actions creation.
action = bpy.data.actions.new("SuzanneAction")

# Creation of slots requires an ID type and a name.
slot = action.slots.new(id_type='OBJECT', name="Suzanne")
print(f"slot type={slot.target_id_type!r} "
      f"name={slot.name_display!r} "
      f"identifier={slot.identifier!r}")

# Output:
#   slot type=OBJECT name=Suzanne identifier=OBSuzanne
```

<a id="explicitly-assigning-action-slots"></a>

## Explicitly Assigning Action Slots

An action slot is compatible with a data-block if the slot’s `target_id_type` matches the data-block’s type.
If there are multiple slots on the Action, and you want to just pick the first one that’s
compatible, use the following code. `anim_data.action_suitable_slots` can be used after the
Action has been assigned; it is a list of action slots of that Action, but only the ones that
are actually compatible with the owner of anim_data (in this case, Suzanne).

```python
import bpy

# Assume Suzanne mesh is present in the scene.
suzanne = bpy.data.objects["Suzanne"]

# Create an action with an object slot.
action = bpy.data.actions.new("SuzanneAction")
action.slots.new(id_type='OBJECT', name="Suzanne")

# If there are multiple slots on the Action, pick the first one that's compatible.
anim_data = suzanne.animation_data_create()
anim_data.action = action
assert anim_data.action_suitable_slots, "expecting at least one suitable slot"
anim_data.action_slot = anim_data.action_suitable_slots[0]
```

<a id="finding-action-slot-users"></a>

## Finding Action Slot Users

To return a list of the data-blocks that are animated by a specific slot of an Action,
use the `users()` method of the ActionSlot.

```python
import bpy

# Iterate through all actions in the Blender data.
print("Action & slot users:")
for action in bpy.data.actions:
    for slot in action.slots:
        # Return the data-blocks that are animated by this slot of this action
        users = slot.users()
        print(f"{action.name:20} slot={slot.identifier:12s} users: {users}")
```

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ActionSlot"></a>

### class bpy.types.ActionSlot(bpy_struct)

Identifier for a set of channels in this Action, that can be used by a data-block to specify what it gets animated by

<a id="bpy.types.ActionSlot.active"></a>

#### bpy.types.ActionSlot.active

Whether this is the active slot, can be set by assigning to action.slots.active (default False, readonly)

**Type:**

bool

<a id="bpy.types.ActionSlot.handle"></a>

#### bpy.types.ActionSlot.handle

Number specific to this Slot, unique within the Action.
This is used, for example, on a ActionKeyframeStrip to look up the ActionChannelbag for this Slot

(in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.ActionSlot.identifier"></a>

#### bpy.types.ActionSlot.identifier

Used when connecting an Action to a data-block, to find the correct slot handle. This is the display name, prefixed by two characters determined by the slot’s ID type (default “”, never None)

**Type:**

str

<a id="bpy.types.ActionSlot.name_display"></a>

#### bpy.types.ActionSlot.name_display

Name of the slot, for display in the user interface. This name combined with the slot’s data-block type is unique within its Action (default “”, never None)

**Type:**

str

<a id="bpy.types.ActionSlot.select"></a>

#### bpy.types.ActionSlot.select

Selection state of the slot (default False)

**Type:**

bool

<a id="bpy.types.ActionSlot.show_expanded"></a>

#### bpy.types.ActionSlot.show_expanded

Expanded state of the slot (default False)

**Type:**

bool

<a id="bpy.types.ActionSlot.target_id_type"></a>

#### bpy.types.ActionSlot.target_id_type

Type of data-block that this slot is intended to animate; can be set when ‘UNSPECIFIED’ but is otherwise read-only (default `'UNSPECIFIED'`)

- `ACTION`
  Action.
- `ARMATURE`
  Armature.
- `BRUSH`
  Brush.
- `CACHEFILE`
  Cache File.
- `CAMERA`
  Camera.
- `COLLECTION`
  Collection.
- `CURVE`
  Curve.
- `CURVES`
  Curves.
- `FONT`
  Font.
- `GREASEPENCIL`
  Grease Pencil.
- `GREASEPENCIL_V3`
  Grease Pencil v3.
- `IMAGE`
  Image.
- `KEY`
  Key.
- `LATTICE`
  Lattice.
- `LIBRARY`
  Library.
- `LIGHT`
  Light.
- `LIGHT_PROBE`
  Light Probe.
- `LINESTYLE`
  Line Style.
- `MASK`
  Mask.
- `MATERIAL`
  Material.
- `MESH`
  Mesh.
- `META`
  Metaball.
- `MOVIECLIP`
  Movie Clip.
- `NODETREE`
  Node Tree.
- `OBJECT`
  Object.
- `PAINTCURVE`
  Paint Curve.
- `PALETTE`
  Palette.
- `PARTICLE`
  Particle.
- `POINTCLOUD`
  Point Cloud.
- `SCENE`
  Scene.
- `SCREEN`
  Screen.
- `SOUND`
  Sound.
- `SPEAKER`
  Speaker.
- `TEXT`
  Text.
- `TEXTURE`
  Texture.
- `VOLUME`
  Volume.
- `WINDOWMANAGER`
  Window Manager.
- `WORKSPACE`
  Workspace.
- `WORLD`
  World.
- `UNSPECIFIED`
  Unspecified – Not yet specified. When this slot is first assigned to a data-block, this will be set to the type of that data-block.

**Type:**

Literal[‘ACTION’, ‘ARMATURE’, ‘BRUSH’, ‘CACHEFILE’, ‘CAMERA’, ‘COLLECTION’, ‘CURVE’, ‘CURVES’, ‘FONT’, ‘GREASEPENCIL’, ‘GREASEPENCIL_V3’, ‘IMAGE’, ‘KEY’, ‘LATTICE’, ‘LIBRARY’, ‘LIGHT’, ‘LIGHT_PROBE’, ‘LINESTYLE’, ‘MASK’, ‘MATERIAL’, ‘MESH’, ‘META’, ‘MOVIECLIP’, ‘NODETREE’, ‘OBJECT’, ‘PAINTCURVE’, ‘PALETTE’, ‘PARTICLE’, ‘POINTCLOUD’, ‘SCENE’, ‘SCREEN’, ‘SOUND’, ‘SPEAKER’, ‘TEXT’, ‘TEXTURE’, ‘VOLUME’, ‘WINDOWMANAGER’, ‘WORKSPACE’, ‘WORLD’, ‘UNSPECIFIED’]

<a id="bpy.types.ActionSlot.target_id_type_icon"></a>

#### bpy.types.ActionSlot.target_id_type_icon

(in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.ActionSlot.users"></a>

#### bpy.types.ActionSlot.users()

Return the data-blocks that are animated by this slot of this action

**Returns:**

users

**Return type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID")]

<a id="bpy.types.ActionSlot.duplicate"></a>

#### bpy.types.ActionSlot.duplicate()

Duplicate this slot, including all the animation data associated with it

**Returns:**

Duplicated Slot, The slot created by duplicating this one

**Return type:**

[`ActionSlot`](#bpy.types.ActionSlot "bpy.types.ActionSlot")

<a id="bpy.types.ActionSlot.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ActionSlot.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ActionSlot.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ActionSlot.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - [`Action.slots`](bpy.types.Action.md#bpy.types.Action.slots "bpy.types.Action.slots") - [`ActionChannelbag.slot`](bpy.types.ActionChannelbag.md#bpy.types.ActionChannelbag.slot "bpy.types.ActionChannelbag.slot") - [`ActionChannelbags.new`](bpy.types.ActionChannelbags.md#bpy.types.ActionChannelbags.new "bpy.types.ActionChannelbags.new") - [`ActionConstraint.action_slot`](bpy.types.ActionConstraint.md#bpy.types.ActionConstraint.action_slot "bpy.types.ActionConstraint.action_slot") - [`ActionConstraint.action_suitable_slots`](bpy.types.ActionConstraint.md#bpy.types.ActionConstraint.action_suitable_slots "bpy.types.ActionConstraint.action_suitable_slots") - [`ActionKeyframeStrip.channelbag`](bpy.types.ActionKeyframeStrip.md#bpy.types.ActionKeyframeStrip.channelbag "bpy.types.ActionKeyframeStrip.channelbag") - [`ActionKeyframeStrip.key_insert`](bpy.types.ActionKeyframeStrip.md#bpy.types.ActionKeyframeStrip.key_insert "bpy.types.ActionKeyframeStrip.key_insert") - [`ActionSlot.duplicate`](#bpy.types.ActionSlot.duplicate "bpy.types.ActionSlot.duplicate") | - [`ActionSlots.active`](bpy.types.ActionSlots.md#bpy.types.ActionSlots.active "bpy.types.ActionSlots.active") - [`ActionSlots.new`](bpy.types.ActionSlots.md#bpy.types.ActionSlots.new "bpy.types.ActionSlots.new") - [`ActionSlots.remove`](bpy.types.ActionSlots.md#bpy.types.ActionSlots.remove "bpy.types.ActionSlots.remove") - [`AnimData.action_slot`](bpy.types.AnimData.md#bpy.types.AnimData.action_slot "bpy.types.AnimData.action_slot") - [`AnimData.action_suitable_slots`](bpy.types.AnimData.md#bpy.types.AnimData.action_suitable_slots "bpy.types.AnimData.action_suitable_slots") - [`NlaStrip.action_slot`](bpy.types.NlaStrip.md#bpy.types.NlaStrip.action_slot "bpy.types.NlaStrip.action_slot") - [`NlaStrip.action_suitable_slots`](bpy.types.NlaStrip.md#bpy.types.NlaStrip.action_suitable_slots "bpy.types.NlaStrip.action_suitable_slots") |
