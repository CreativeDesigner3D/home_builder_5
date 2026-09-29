<!-- source: Blender Python API reference 5.2 / bpy.types.MetaElement.html -->

<a id="metaelement-bpy-struct"></a>

# MetaElement(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.MetaElement"></a>

### class bpy.types.MetaElement(bpy_struct)

Blobby element in a metaball data-block

<a id="bpy.types.MetaElement.co"></a>

#### bpy.types.MetaElement.co

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.MetaElement.hide"></a>

#### bpy.types.MetaElement.hide

Hide element (default False)

**Type:**

bool

<a id="bpy.types.MetaElement.radius"></a>

#### bpy.types.MetaElement.radius

(in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.MetaElement.rotation"></a>

#### bpy.types.MetaElement.rotation

Normalized quaternion rotation (array of 4 items, in [-inf, inf], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`mathutils.Quaternion`](mathutils.md#mathutils.Quaternion "mathutils.Quaternion")

<a id="bpy.types.MetaElement.select"></a>

#### bpy.types.MetaElement.select

Select element (default False)

**Type:**

bool

<a id="bpy.types.MetaElement.size_x"></a>

#### bpy.types.MetaElement.size_x

Size of element, use of components depends on element type (in [0, 20], default 0.0)

**Type:**

float

<a id="bpy.types.MetaElement.size_y"></a>

#### bpy.types.MetaElement.size_y

Size of element, use of components depends on element type (in [0, 20], default 0.0)

**Type:**

float

<a id="bpy.types.MetaElement.size_z"></a>

#### bpy.types.MetaElement.size_z

Size of element, use of components depends on element type (in [0, 20], default 0.0)

**Type:**

float

<a id="bpy.types.MetaElement.stiffness"></a>

#### bpy.types.MetaElement.stiffness

Stiffness defines how much of the element to fill (in [0, 10], default 0.0)

**Type:**

float

<a id="bpy.types.MetaElement.type"></a>

#### bpy.types.MetaElement.type

Metaball type (default `'BALL'`)

**Type:**

Literal[[Metaelem Type Items](bpy_types_enum_items/metaelem_type_items.md#rna-enum-metaelem-type-items)]

<a id="bpy.types.MetaElement.use_negative"></a>

#### bpy.types.MetaElement.use_negative

Set metaball as negative one (default False)

**Type:**

bool

<a id="bpy.types.MetaElement.use_scale_stiffness"></a>

#### bpy.types.MetaElement.use_scale_stiffness

Scale stiffness instead of radius (default True)

**Type:**

bool

<a id="bpy.types.MetaElement.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MetaElement.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MetaElement.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MetaElement.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.MetaElement.type "bpy.types.MetaElement.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.MetaElement.type "bpy.types.MetaElement.type")

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
| - [`MetaBall.elements`](bpy.types.MetaBall.md#bpy.types.MetaBall.elements "bpy.types.MetaBall.elements") - [`MetaBallElements.active`](bpy.types.MetaBallElements.md#bpy.types.MetaBallElements.active "bpy.types.MetaBallElements.active") | - [`MetaBallElements.new`](bpy.types.MetaBallElements.md#bpy.types.MetaBallElements.new "bpy.types.MetaBallElements.new") - [`MetaBallElements.remove`](bpy.types.MetaBallElements.md#bpy.types.MetaBallElements.remove "bpy.types.MetaBallElements.remove") |
