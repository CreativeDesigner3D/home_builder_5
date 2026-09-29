<!-- source: Blender Python API reference 5.2 / bpy.types.FluidModifier.html -->

<a id="fluidmodifier-modifier"></a>

# FluidModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.FluidModifier"></a>

### class bpy.types.FluidModifier(Modifier)

Fluid simulation modifier

<a id="bpy.types.FluidModifier.domain_settings"></a>

#### bpy.types.FluidModifier.domain_settings

(readonly)

**Type:**

[`FluidDomainSettings`](bpy.types.FluidDomainSettings.md#bpy.types.FluidDomainSettings "bpy.types.FluidDomainSettings") | None

<a id="bpy.types.FluidModifier.effector_settings"></a>

#### bpy.types.FluidModifier.effector_settings

(readonly)

**Type:**

[`FluidEffectorSettings`](bpy.types.FluidEffectorSettings.md#bpy.types.FluidEffectorSettings "bpy.types.FluidEffectorSettings") | None

<a id="bpy.types.FluidModifier.flow_settings"></a>

#### bpy.types.FluidModifier.flow_settings

(readonly)

**Type:**

[`FluidFlowSettings`](bpy.types.FluidFlowSettings.md#bpy.types.FluidFlowSettings "bpy.types.FluidFlowSettings") | None

<a id="bpy.types.FluidModifier.fluid_type"></a>

#### bpy.types.FluidModifier.fluid_type

(default `'NONE'`)

- `NONE`
  None.
- `DOMAIN`
  Domain – Container of the fluid simulation.
- `FLOW`
  Flow – Add or remove fluid to a domain object.
- `EFFECTOR`
  Effector – Deflect fluids and influence the fluid flow.

**Type:**

Literal[‘NONE’, ‘DOMAIN’, ‘FLOW’, ‘EFFECTOR’]

<a id="bpy.types.FluidModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FluidModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FluidModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FluidModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Modifier.name, Modifier.type, Modifier.show_viewport, Modifier.show_render, Modifier.show_in_editmode, Modifier.show_on_cage, Modifier.show_expanded, Modifier.is_active, Modifier.use_pin_to_last, Modifier.is_override_data, Modifier.use_apply_on_spline, Modifier.execution_time, Modifier.persistent_uid

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Modifier.bl_rna_get_subclass, Modifier.bl_rna_get_subclass_py
