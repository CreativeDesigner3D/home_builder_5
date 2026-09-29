<!-- source: Blender Python API reference 5.2 / bpy.types.SurfaceCurve.html -->

<a id="surfacecurve-curve"></a>

# SurfaceCurve(Curve)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`ID`](bpy.types.ID.md#bpy.types.ID "bpy.types.ID"), [`Curve`](bpy.types.Curve.md#bpy.types.Curve "bpy.types.Curve")

<a id="bpy.types.SurfaceCurve"></a>

### class bpy.types.SurfaceCurve(Curve)

Curve data-block used for storing surfaces

<a id="bpy.types.SurfaceCurve.bl_rna_get_subclass"></a>

#### classmethod bpy.types.SurfaceCurve.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.SurfaceCurve.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.SurfaceCurve.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, ID.name, ID.name_full, ID.id_type, ID.session_uid, ID.is_evaluated, ID.original, ID.users, ID.use_fake_user, ID.use_extra_user, ID.is_embedded_data, ID.is_linked_packed, ID.is_missing, ID.is_runtime_data, ID.is_editable, ID.tag, ID.is_library_indirect, ID.library, ID.library_weak_reference, ID.asset_data, ID.override_library, ID.preview, Curve.shape_keys, Curve.splines, Curve.path_duration, Curve.use_path, Curve.use_path_follow, Curve.use_path_clamp, Curve.use_stretch, Curve.use_deform_bounds, Curve.use_radius, Curve.bevel_mode, Curve.bevel_profile, Curve.bevel_resolution, Curve.offset, Curve.extrude, Curve.bevel_depth, Curve.resolution_u, Curve.resolution_v, Curve.render_resolution_u, Curve.render_resolution_v, Curve.eval_time, Curve.bevel_object, Curve.taper_object, Curve.dimensions, Curve.fill_mode, Curve.fill_solver, Curve.fill_rule, Curve.twist_mode, Curve.taper_radius_mode, Curve.bevel_factor_mapping_start, Curve.bevel_factor_mapping_end, Curve.twist_smooth, Curve.use_fill_caps, Curve.use_map_taper, Curve.use_auto_texspace, Curve.texspace_location, Curve.texspace_size, Curve.materials, Curve.bevel_factor_start, Curve.bevel_factor_end, Curve.is_editmode, Curve.animation_data, Curve.cycles

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, ID.bl_system_properties_get, ID.rename, ID.evaluated_get, ID.copy, ID.asset_mark, ID.asset_clear, ID.asset_generate_preview, ID.override_create, ID.override_hierarchy_create, ID.user_clear, ID.user_remap, ID.make_local, ID.user_of_id, ID.animation_data_create, ID.animation_data_clear, ID.update_tag, ID.preview_ensure, ID.bl_rna_get_subclass, ID.bl_rna_get_subclass_py, Curve.transform, Curve.validate_material_indices, Curve.update_gpu_tag, Curve.bl_rna_get_subclass, Curve.bl_rna_get_subclass_py
