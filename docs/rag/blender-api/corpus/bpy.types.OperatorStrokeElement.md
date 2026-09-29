<!-- source: Blender Python API reference 5.2 / bpy.types.OperatorStrokeElement.html -->

<a id="operatorstrokeelement-propertygroup"></a>

# OperatorStrokeElement(PropertyGroup)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.OperatorStrokeElement"></a>

### class bpy.types.OperatorStrokeElement(PropertyGroup)

<a id="bpy.types.OperatorStrokeElement.is_start"></a>

#### bpy.types.OperatorStrokeElement.is_start

(default False)

**Type:**

bool

<a id="bpy.types.OperatorStrokeElement.location"></a>

#### bpy.types.OperatorStrokeElement.location

(array of 3 items, in [-inf, inf], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.OperatorStrokeElement.mouse"></a>

#### bpy.types.OperatorStrokeElement.mouse

(array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.OperatorStrokeElement.mouse_event"></a>

#### bpy.types.OperatorStrokeElement.mouse_event

(array of 2 items, in [-inf, inf], default (0.0, 0.0))

**Type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="bpy.types.OperatorStrokeElement.pressure"></a>

#### bpy.types.OperatorStrokeElement.pressure

Tablet pressure (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.OperatorStrokeElement.size"></a>

#### bpy.types.OperatorStrokeElement.size

Brush size in screen space (in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.OperatorStrokeElement.time"></a>

#### bpy.types.OperatorStrokeElement.time

(in [0, inf], default 0.0)

**Type:**

float

<a id="bpy.types.OperatorStrokeElement.x_tilt"></a>

#### bpy.types.OperatorStrokeElement.x_tilt

Pen tilt from left (-1.0) to right (+1.0) (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.OperatorStrokeElement.y_tilt"></a>

#### bpy.types.OperatorStrokeElement.y_tilt

Pen tilt from backward (-1.0) to forward (+1.0) (in [-1, 1], default 0.0)

**Type:**

float

<a id="bpy.types.OperatorStrokeElement.bl_rna_get_subclass"></a>

#### classmethod bpy.types.OperatorStrokeElement.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.OperatorStrokeElement.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.OperatorStrokeElement.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, PropertyGroup.name

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, PropertyGroup.bl_system_properties_get, PropertyGroup.bl_rna_get_subclass, PropertyGroup.bl_rna_get_subclass_py
