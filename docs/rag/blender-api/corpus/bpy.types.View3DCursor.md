<!-- source: Blender Python API reference 5.2 / bpy.types.View3DCursor.html -->

<a id="view3dcursor-bpy-struct"></a>

# View3DCursor(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.View3DCursor"></a>

### class bpy.types.View3DCursor(bpy_struct)

<a id="bpy.types.View3DCursor.location"></a>

#### bpy.types.View3DCursor.location

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.View3DCursor.matrix"></a>

#### bpy.types.View3DCursor.matrix

Matrix combining location and rotation of the cursor (multi-dimensional array of 4 * 4 items, in [-inf, inf], default ((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)))

**Type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy.types.View3DCursor.rotation_axis_angle"></a>

#### bpy.types.View3DCursor.rotation_axis_angle

Angle of Rotation for Axis-Angle rotation representation (array of 4 items, in [-inf, inf], default (0.0, 0.0, 1.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.View3DCursor.rotation_euler"></a>

#### bpy.types.View3DCursor.rotation_euler

3D rotation (array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler")

<a id="bpy.types.View3DCursor.rotation_mode"></a>

#### bpy.types.View3DCursor.rotation_mode

The kind of rotation to apply, values from other rotation modes are not used (default `'XYZ'`)

**Type:**

Literal[[Object Rotation Mode Items](bpy_types_enum_items/object_rotation_mode_items.md#rna-enum-object-rotation-mode-items)]

<a id="bpy.types.View3DCursor.rotation_quaternion"></a>

#### bpy.types.View3DCursor.rotation_quaternion

Rotation in quaternions (keep normalized) (array of 4 items, in [-inf, inf], default (1.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.View3DCursor.bl_rna_get_subclass"></a>

#### classmethod bpy.types.View3DCursor.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.View3DCursor.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.View3DCursor.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Scene.cursor`](bpy.types.Scene.md#bpy.types.Scene.cursor "bpy.types.Scene.cursor") |  |
