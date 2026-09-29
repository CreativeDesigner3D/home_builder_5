<!-- source: Blender Python API reference 5.2 / bpy.types.LineStyleGeometryModifier_2DTransform.html -->

<a id="linestylegeometrymodifier-2dtransform-linestylegeometrymodifier"></a>

# LineStyleGeometryModifier_2DTransform(LineStyleGeometryModifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`LineStyleModifier`](bpy.types.LineStyleModifier.md#bpy.types.LineStyleModifier "bpy.types.LineStyleModifier"), [`LineStyleGeometryModifier`](bpy.types.LineStyleGeometryModifier.md#bpy.types.LineStyleGeometryModifier "bpy.types.LineStyleGeometryModifier")

<a id="bpy.types.LineStyleGeometryModifier_2DTransform"></a>

### class bpy.types.LineStyleGeometryModifier_2DTransform(LineStyleGeometryModifier)

Apply two-dimensional scaling and rotation to stroke backbone geometry

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.angle"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.angle

Rotation angle (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.expanded"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.expanded

True if the modifier tab is expanded (default False)

**Type:**

bool

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.pivot"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.pivot

Pivot of scaling and rotation operations (default `'CENTER'`)

**Type:**

Literal[‘CENTER’, ‘START’, ‘END’, ‘PARAM’, ‘ABSOLUTE’]

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.pivot_u"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.pivot_u

Pivot in terms of the stroke point parameter u (0 <= u <= 1) (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.pivot_x"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.pivot_x

2D X coordinate of the absolute pivot (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.pivot_y"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.pivot_y

2D Y coordinate of the absolute pivot (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.scale_x"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.scale_x

Scaling factor that is applied along the X axis (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.scale_y"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.scale_y

Scaling factor that is applied along the Y axis (in [-inf, inf], default 0.0)

**Type:**

float

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.type"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.type

Type of the modifier (default `'2D_OFFSET'`, readonly)

**Type:**

Literal[[Linestyle Geometry Modifier Type Items](bpy_types_enum_items/linestyle_geometry_modifier_type_items.md#rna-enum-linestyle-geometry-modifier-type-items)]

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.use"></a>

#### bpy.types.LineStyleGeometryModifier_2DTransform.use

Enable or disable this modifier during stroke rendering (default False)

**Type:**

bool

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LineStyleGeometryModifier_2DTransform.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LineStyleGeometryModifier_2DTransform.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LineStyleGeometryModifier_2DTransform.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.LineStyleGeometryModifier_2DTransform.type "bpy.types.LineStyleGeometryModifier_2DTransform.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.LineStyleGeometryModifier_2DTransform.type "bpy.types.LineStyleGeometryModifier_2DTransform.type")

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, LineStyleGeometryModifier.name

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, LineStyleModifier.bl_rna_get_subclass, LineStyleModifier.bl_rna_get_subclass_py, LineStyleGeometryModifier.bl_rna_get_subclass, LineStyleGeometryModifier.bl_rna_get_subclass_py
