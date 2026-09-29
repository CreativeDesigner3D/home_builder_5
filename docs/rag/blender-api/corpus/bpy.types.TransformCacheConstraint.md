<!-- source: Blender Python API reference 5.2 / bpy.types.TransformCacheConstraint.html -->

<a id="transformcacheconstraint-constraint"></a>

# TransformCacheConstraint(Constraint)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint")

<a id="bpy.types.TransformCacheConstraint"></a>

### class bpy.types.TransformCacheConstraint(Constraint)

Look up transformation from an external file

<a id="bpy.types.TransformCacheConstraint.cache_file"></a>

#### bpy.types.TransformCacheConstraint.cache_file

**Type:**

[`CacheFile`](bpy.types.CacheFile.md#bpy.types.CacheFile "bpy.types.CacheFile") | None

<a id="bpy.types.TransformCacheConstraint.object_path"></a>

#### bpy.types.TransformCacheConstraint.object_path

Path to the object in the Alembic archive used to lookup the transform matrix (default “”, never None)

**Type:**

str

<a id="bpy.types.TransformCacheConstraint.bl_rna_get_subclass"></a>

#### classmethod bpy.types.TransformCacheConstraint.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.TransformCacheConstraint.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.TransformCacheConstraint.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Constraint.name, Constraint.type, Constraint.is_override_data, Constraint.owner_space, Constraint.target_space, Constraint.space_object, Constraint.space_subtarget, Constraint.mute, Constraint.enabled, Constraint.show_expanded, Constraint.is_valid, Constraint.active, Constraint.influence, Constraint.error_location, Constraint.error_rotation

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Constraint.bl_rna_get_subclass, Constraint.bl_rna_get_subclass_py
