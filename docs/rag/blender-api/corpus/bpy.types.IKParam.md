<!-- source: Blender Python API reference 5.2 / bpy.types.IKParam.html -->

<a id="ikparam-bpy-struct"></a>

# IKParam(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [Itasc(IKParam)](bpy.types.Itasc.md)

<a id="bpy.types.IKParam"></a>

### class bpy.types.IKParam(bpy_struct)

Base type for IK solver parameters

<a id="bpy.types.IKParam.ik_solver"></a>

#### bpy.types.IKParam.ik_solver

IK solver for which these parameters are defined (default `'LEGACY'`, readonly)

- `LEGACY`
  Standard – Original IK solver.
- `ITASC`
  iTaSC – Multi constraint, stateful IK solver.

**Type:**

Literal[‘LEGACY’, ‘ITASC’]

<a id="bpy.types.IKParam.bl_rna_get_subclass"></a>

#### classmethod bpy.types.IKParam.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.IKParam.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.IKParam.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Pose.ik_param`](bpy.types.Pose.md#bpy.types.Pose.ik_param "bpy.types.Pose.ik_param") |  |
