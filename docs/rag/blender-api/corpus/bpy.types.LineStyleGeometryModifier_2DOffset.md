<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleGeometryModifier_2DOffset.html -->

<a id="linestylegeometrymodifier-2doffset-linestylegeometrymodifier"></a>

# LineStyleGeometryModifier_2DOffset(LineStyleGeometryModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`LineStyleModifier`](bpy.types.LineStyleModifier.md#bpy.types.LineStyleModifier "bpy.types.LineStyleModifier"), [`LineStyleGeometryModifier`](bpy.types.LineStyleGeometryModifier.md#bpy.types.LineStyleGeometryModifier "bpy.types.LineStyleGeometryModifier")

<a id="bpy.types.LineStyleGeometryModifier_2DOffset"></a>

### class bpy.types.LineStyleGeometryModifier_2DOffset(LineStyleGeometryModifier)

Add two-dimensional offsets to stroke backbone geometry

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.end"></a>

#### bpy.types.LineStyleGeometryModifier_2DOffset.end

Displacement that is applied from the end of the stroke (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.expanded"></a>

#### bpy.types.LineStyleGeometryModifier_2DOffset.expanded

True if the modifier tab is expanded (default False)

**Type:**

bool

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.start"></a>

#### bpy.types.LineStyleGeometryModifier_2DOffset.start

Displacement that is applied from the beginning of the stroke (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.type"></a>

#### bpy.types.LineStyleGeometryModifier_2DOffset.type

Type of the modifier (default `'2D_OFFSET'`, readonly)

**Type:**

Literal[[Linestyle Geometry Modifier Type Items](bpy_types_enum_items/linestyle_geometry_modifier_type_items.md#rna-enum-linestyle-geometry-modifier-type-items)]

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.use"></a>

#### bpy.types.LineStyleGeometryModifier_2DOffset.use

Enable or disable this modifier during stroke rendering (default False)

**Type:**

bool

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.x"></a>

#### bpy.types.LineStyleGeometryModifier_2DOffset.x

Displacement that is applied to the X coordinates of stroke vertices (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.y"></a>

#### bpy.types.LineStyleGeometryModifier_2DOffset.y

Displacement that is applied to the Y coordinates of stroke vertices (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleGeometryModifier_2DOffset.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleGeometryModifier_2DOffset.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleGeometryModifier_2DOffset.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.LineStyleGeometryModifier_2DOffset.type "bpy.types.LineStyleGeometryModifier_2DOffset.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.LineStyleGeometryModifier_2DOffset.type "bpy.types.LineStyleGeometryModifier_2DOffset.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, LineStyleGeometryModifier.name

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, LineStyleModifier.bl_rna_get_subclass, LineStyleModifier.bl_rna_get_subclass_py, LineStyleGeometryModifier.bl_rna_get_subclass, LineStyleGeometryModifier.bl_rna_get_subclass_py
