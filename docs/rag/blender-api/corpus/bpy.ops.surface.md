<!-- source: Blender Python API reference 5.2 / bpy.ops.surface.html -->

<a id="module-bpy.ops.surface"></a>

# Surface Operators

<a id="bpy.ops.surface.primitive_nurbs_surface_circle_add"></a>

### bpy.ops.surface.primitive_nurbs_surface_circle_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a NURBS surface circle

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.surface.primitive_nurbs_surface_curve_add"></a>

### bpy.ops.surface.primitive_nurbs_surface_curve_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a NURBS surface curve

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.surface.primitive_nurbs_surface_cylinder_add"></a>

### bpy.ops.surface.primitive_nurbs_surface_cylinder_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a NURBS surface cylinder

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.surface.primitive_nurbs_surface_sphere_add"></a>

### bpy.ops.surface.primitive_nurbs_surface_sphere_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a NURBS surface sphere

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.surface.primitive_nurbs_surface_surface_add"></a>

### bpy.ops.surface.primitive_nurbs_surface_surface_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a NURBS surface patch

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.surface.primitive_nurbs_surface_torus_add"></a>

### bpy.ops.surface.primitive_nurbs_surface_torus_add(*, radius=1.0, enter_editmode=False, align='WORLD', location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), scale=(0.0, 0.0, 0.0))

Construct a NURBS surface torus

**Parameters:**

- **radius** (float) – Radius, (in [0, inf], optional)
- **enter_editmode** (bool) – Enter Edit Mode, Enter edit mode when adding this object (optional)
- **align** (Literal['WORLD', 'VIEW', 'CURSOR']) –

  Align, The alignment of the new object (optional)

  - `WORLD`
    World – Align the new object to the world.
  - `VIEW`
    View – Align the new object to the view.
  - `CURSOR`
    3D Cursor – Use the 3D cursor orientation for the new object.
- **location** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Location, Location for the newly added object (array of 3 items, in [-inf, inf], optional)
- **rotation** ([`mathutils.Euler`](mathutils.md#mathutils.Euler "mathutils.Euler") | Sequence[float]) – Rotation, Rotation for the newly added object (array of 3 items, in [-inf, inf], optional)
- **scale** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Scale, Scale for the newly added object (array of 3 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
