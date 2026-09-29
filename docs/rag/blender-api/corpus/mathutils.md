<!-- source: Blender Python API reference 5.2 / mathutils.html -->

<a id="module-mathutils"></a>

# Math Types & Utilities (mathutils)

This module provides access to math operations.

> **Note:**
>
> Classes, methods and attributes that accept vectors also accept other numeric sequences,
> such as tuples, lists.

The [`mathutils`](#module-mathutils "mathutils") module provides the following classes:

- [`Color`](#mathutils.Color "mathutils.Color"),
- [`Euler`](#mathutils.Euler "mathutils.Euler"),
- [`Matrix`](#mathutils.Matrix "mathutils.Matrix"),
- [`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion"),
- [`Vector`](#mathutils.Vector "mathutils.Vector"),

Submodules

- [Geometry Utilities (mathutils.geometry)](mathutils.geometry.md)
- [BVHTree Utilities (mathutils.bvhtree)](mathutils.bvhtree.md)
- [KDTree Utilities (mathutils.kdtree)](mathutils.kdtree.md)
- [Interpolation Utilities (mathutils.interpolate)](mathutils.interpolate.md)
- [Noise Utilities (mathutils.noise)](mathutils.noise.md)

```python
import mathutils
from math import radians

vec = mathutils.Vector((1.0, 2.0, 3.0))

mat_rot = mathutils.Matrix.Rotation(radians(90.0), 4, 'X')
mat_trans = mathutils.Matrix.Translation(vec)

mat = mat_trans @ mat_rot
mat.invert()

mat3 = mat.to_3x3()
quat1 = mat.to_quaternion()
quat2 = mat3.to_quaternion()

quat_diff = quat1.rotation_difference(quat2)

print(quat_diff.angle)
```

<a id="mathutils.Color"></a>

### class mathutils.Color(rgb=(0.0, 0.0, 0.0), /)

This object gives access to Colors in Blender.

Most colors returned by Blender APIs are in scene linear color space, as defined by the OpenColorIO configuration. The notable exception is user interface theming colors, which are in sRGB color space.

**Parameters:**

**rgb** (Sequence[float]) – (red, green, blue) color values where (0, 0, 0) is black & (1, 1, 1) is white.

```python
import mathutils

# Color values are represented as RGB values from 0 - 1, this is blue.
col = mathutils.Color((0.0, 0.0, 1.0))

# As well as r/g/b attribute access you can adjust them by h/s/v.
col.s *= 0.5

# You can access its components by attribute or index.
print("Color R:", col.r)
print("Color G:", col[1])
print("Color B:", col[-1])
print("Color HSV: {:.2f}, {:.2f}, {:.2f}".format(*col))

# Components of an existing color can be set.
col[:] = 0.0, 0.5, 1.0

# Components of an existing color can use slice notation to get a tuple.
print("Values: {:f}, {:f}, {:f}".format(*col))

# Colors can be added and subtracted.
col += mathutils.Color((0.25, 0.0, 0.0))

# Color can be multiplied, in this example color is scaled to 0-255
# can printed as integers.
print("Color: {:d}, {:d}, {:d}".format(*(int(c) for c in (col * 255.0))))

# This example prints the color as hexadecimal.
print("Hexadecimal: {:02x}{:02x}{:02x}".format(int(col.r * 255), int(col.g * 255), int(col.b * 255)))

# Direct buffer access is supported.
print(memoryview(col).tobytes())
```

<a id="mathutils.Color.copy"></a>

#### mathutils.Color.copy()

Returns a copy of this color.

**Returns:**

A copy of the color.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

> **Note:**
>
> use this to get a copy of a wrapped color with
> no reference to the original data.

<a id="mathutils.Color.freeze"></a>

#### mathutils.Color.freeze()

Make this object immutable.

After this the object can be hashed, used in dictionaries & sets.

**Returns:**

An instance of this object.

**Return type:**

Self

<a id="mathutils.Color.from_aces_to_scene_linear"></a>

#### mathutils.Color.from_aces_to_scene_linear()

Convert from ACES2065-1 linear to scene linear color space.

**Returns:**

A color in scene linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_acescg_to_scene_linear"></a>

#### mathutils.Color.from_acescg_to_scene_linear()

Convert from ACEScg linear to scene linear color space.

**Returns:**

A color in scene linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_rec2020_linear_to_scene_linear"></a>

#### mathutils.Color.from_rec2020_linear_to_scene_linear()

Convert from Rec.2020 linear color space to scene linear color space.

**Returns:**

A color in scene linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_rec709_linear_to_scene_linear"></a>

#### mathutils.Color.from_rec709_linear_to_scene_linear()

Convert from Rec.709 linear color space to scene linear color space.

**Returns:**

A color in scene linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_scene_linear_to_aces"></a>

#### mathutils.Color.from_scene_linear_to_aces()

Convert from scene linear to ACES2065-1 linear color space.

**Returns:**

A color in ACES2065-1 linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_scene_linear_to_acescg"></a>

#### mathutils.Color.from_scene_linear_to_acescg()

Convert from scene linear to ACEScg linear color space.

**Returns:**

A color in ACEScg linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_scene_linear_to_rec2020_linear"></a>

#### mathutils.Color.from_scene_linear_to_rec2020_linear()

Convert from scene linear to Rec.2020 linear color space.

**Returns:**

A color in Rec.2020 linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_scene_linear_to_rec709_linear"></a>

#### mathutils.Color.from_scene_linear_to_rec709_linear()

Convert from scene linear to Rec.709 linear color space.

**Returns:**

A color in Rec.709 linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_scene_linear_to_srgb"></a>

#### mathutils.Color.from_scene_linear_to_srgb()

Convert from scene linear to sRGB color space.

**Returns:**

A color in sRGB color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_scene_linear_to_xyz_d65"></a>

#### mathutils.Color.from_scene_linear_to_xyz_d65()

Convert from scene linear to CIE XYZ (Illuminant D65) color space.

**Returns:**

A color in XYZ color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_srgb_to_scene_linear"></a>

#### mathutils.Color.from_srgb_to_scene_linear()

Convert from sRGB to scene linear color space.

**Returns:**

A color in scene linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.from_xyz_d65_to_scene_linear"></a>

#### mathutils.Color.from_xyz_d65_to_scene_linear()

Convert from CIE XYZ (Illuminant D65) to scene linear color space.

**Returns:**

A color in scene linear color space.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.b"></a>

#### mathutils.Color.b

Blue color channel.

**Type:**

float

<a id="mathutils.Color.g"></a>

#### mathutils.Color.g

Green color channel.

**Type:**

float

<a id="mathutils.Color.h"></a>

#### mathutils.Color.h

HSV Hue component in [0, 1].

**Type:**

float

<a id="mathutils.Color.hsv"></a>

#### mathutils.Color.hsv

HSV Values in [0, 1].

**Type:**

tuple[float, float, float]

<a id="mathutils.Color.is_frozen"></a>

#### mathutils.Color.is_frozen

True when this object has been frozen (read-only).

**Type:**

bool

<a id="mathutils.Color.is_valid"></a>

#### mathutils.Color.is_valid

True when the owner of this data is valid.

**Type:**

bool

<a id="mathutils.Color.is_wrapped"></a>

#### mathutils.Color.is_wrapped

True when this object wraps external data (read-only).

**Type:**

bool

<a id="mathutils.Color.owner"></a>

#### mathutils.Color.owner

The item this is wrapping or None (read-only).

**Type:**

Any

<a id="mathutils.Color.r"></a>

#### mathutils.Color.r

Red color channel.

**Type:**

float

<a id="mathutils.Color.s"></a>

#### mathutils.Color.s

HSV Saturation component in [0, 1].

**Type:**

float

<a id="mathutils.Color.v"></a>

#### mathutils.Color.v

HSV Value component in [0, 1].

**Type:**

float

Special Methods

<a id="mathutils.Color.__add__"></a>

#### mathutils.Color.__add__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__eq__"></a>

#### mathutils.Color.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Color.__getitem__"></a>

#### mathutils.Color.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="mathutils.Color.__hash__"></a>

#### mathutils.Color.__hash__()

**Return type:**

int

<a id="mathutils.Color.__iadd__"></a>

#### mathutils.Color.__iadd__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__imul__"></a>

#### mathutils.Color.__imul__(other)

**Parameters:**

**other** (float) – Scalar.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__isub__"></a>

#### mathutils.Color.__isub__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__itruediv__"></a>

#### mathutils.Color.__itruediv__(other)

**Parameters:**

**other** (float) – Scalar divisor.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__len__"></a>

#### mathutils.Color.__len__()

**Return type:**

int

<a id="mathutils.Color.__mul__"></a>

#### mathutils.Color.__mul__(other)

**Parameters:**

**other** (float) – Scalar.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__ne__"></a>

#### mathutils.Color.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Color.__neg__"></a>

#### mathutils.Color.__neg__()

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__pos__"></a>

#### mathutils.Color.__pos__()

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__repr__"></a>

#### mathutils.Color.__repr__()

**Return type:**

str

<a id="mathutils.Color.__rmul__"></a>

#### mathutils.Color.__rmul__(other)

**Parameters:**

**other** (float) – Scalar.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__setitem__"></a>

#### mathutils.Color.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="mathutils.Color.__str__"></a>

#### mathutils.Color.__str__()

**Return type:**

str

<a id="mathutils.Color.__sub__"></a>

#### mathutils.Color.__sub__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Color.__truediv__"></a>

#### mathutils.Color.__truediv__(other)

**Parameters:**

**other** (float) – Scalar divisor.

**Return type:**

[`Color`](#mathutils.Color "mathutils.Color")

<a id="mathutils.Euler"></a>

### class mathutils.Euler(angles=(0.0, 0.0, 0.0), order='XYZ', /)

This object gives access to Eulers in Blender.

> **See also:**
>
> [Euler angles](https://en.wikipedia.org/wiki/Euler_angles) on Wikipedia.

**Parameters:**

- **angles** (Sequence[float]) – (X, Y, Z) angles in radians.
- **order** (Literal['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']) – Euler rotation order.

```python
import mathutils
import math

# Create a new euler with default axis rotation order.
eul = mathutils.Euler((0.0, math.radians(45.0), 0.0), 'XYZ')

# Rotate the euler.
eul.rotate_axis('Z', math.radians(10.0))

# You can access its components by attribute or index.
print("Euler X", eul.x)
print("Euler Y", eul[1])
print("Euler Z", eul[-1])

# Components of an existing euler can be set.
eul[:] = 1.0, 2.0, 3.0

# Components of an existing euler can use slice notation to get a tuple.
print("Values: {:f}, {:f}, {:f}".format(*eul))

# The order can be set at any time too.
eul.order = 'ZYX'

# Eulers can be used to rotate vectors.
vec = mathutils.Vector((0.0, 0.0, 1.0))
vec.rotate(eul)

# Often its useful to convert the euler into a matrix so it can be used as
# transformations with more flexibility.
mat_rot = eul.to_matrix()
mat_loc = mathutils.Matrix.Translation((2.0, 3.0, 4.0))
mat = mat_loc @ mat_rot.to_4x4()

# Direct buffer access is supported.
print(memoryview(eul).tobytes())
```

<a id="mathutils.Euler.copy"></a>

#### mathutils.Euler.copy()

Returns a copy of this euler.

**Returns:**

A copy of the euler.

**Return type:**

[`Euler`](#mathutils.Euler "mathutils.Euler")

> **Note:**
>
> use this to get a copy of a wrapped euler with
> no reference to the original data.

<a id="mathutils.Euler.freeze"></a>

#### mathutils.Euler.freeze()

Make this object immutable.

After this the object can be hashed, used in dictionaries & sets.

**Returns:**

An instance of this object.

**Return type:**

Self

<a id="mathutils.Euler.make_compatible"></a>

#### mathutils.Euler.make_compatible(other, /)

Make this euler compatible with another,
so interpolating between them works as intended.

**Parameters:**

**other** ([`Euler`](#mathutils.Euler "mathutils.Euler")) – Other euler rotation.

> **Note:**
>
> the rotation order is not taken into account for this function.

<a id="mathutils.Euler.rotate"></a>

#### mathutils.Euler.rotate(other, /)

Rotates the euler by another mathutils value.

**Parameters:**

**other** ([`Euler`](#mathutils.Euler "mathutils.Euler") | [`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion") | [`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – rotation component of mathutils value

<a id="mathutils.Euler.rotate_axis"></a>

#### mathutils.Euler.rotate_axis(axis, angle, /)

Rotates the euler a certain amount, wrapping the result to produce
a unique euler rotation (no 720 degree pitches).

**Parameters:**

- **axis** (Literal['X', 'Y', 'Z']) – An axis string.
- **angle** (float) – angle in radians.

<a id="mathutils.Euler.to_matrix"></a>

#### mathutils.Euler.to_matrix()

Return a matrix representation of the euler.

**Returns:**

A 3x3 rotation matrix representation of the euler.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Euler.to_quaternion"></a>

#### mathutils.Euler.to_quaternion()

Return a quaternion representation of the euler.

**Returns:**

Quaternion representation of the euler.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Euler.zero"></a>

#### mathutils.Euler.zero()

Set all values to zero.

<a id="mathutils.Euler.is_frozen"></a>

#### mathutils.Euler.is_frozen

True when this object has been frozen (read-only).

**Type:**

bool

<a id="mathutils.Euler.is_valid"></a>

#### mathutils.Euler.is_valid

True when the owner of this data is valid.

**Type:**

bool

<a id="mathutils.Euler.is_wrapped"></a>

#### mathutils.Euler.is_wrapped

True when this object wraps external data (read-only).

**Type:**

bool

<a id="mathutils.Euler.order"></a>

#### mathutils.Euler.order

Euler rotation order.

**Type:**

Literal[‘XYZ’, ‘XZY’, ‘YXZ’, ‘YZX’, ‘ZXY’, ‘ZYX’]

<a id="mathutils.Euler.owner"></a>

#### mathutils.Euler.owner

The item this is wrapping or None (read-only).

**Type:**

Any

<a id="mathutils.Euler.x"></a>

#### mathutils.Euler.x

Euler axis angle in radians.

**Type:**

float

<a id="mathutils.Euler.y"></a>

#### mathutils.Euler.y

Euler axis angle in radians.

**Type:**

float

<a id="mathutils.Euler.z"></a>

#### mathutils.Euler.z

Euler axis angle in radians.

**Type:**

float

Special Methods

<a id="mathutils.Euler.__eq__"></a>

#### mathutils.Euler.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Euler.__getitem__"></a>

#### mathutils.Euler.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="mathutils.Euler.__hash__"></a>

#### mathutils.Euler.__hash__()

**Return type:**

int

<a id="mathutils.Euler.__len__"></a>

#### mathutils.Euler.__len__()

**Return type:**

int

<a id="mathutils.Euler.__ne__"></a>

#### mathutils.Euler.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Euler.__repr__"></a>

#### mathutils.Euler.__repr__()

**Return type:**

str

<a id="mathutils.Euler.__setitem__"></a>

#### mathutils.Euler.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="mathutils.Euler.__str__"></a>

#### mathutils.Euler.__str__()

**Return type:**

str

<a id="mathutils.Matrix"></a>

### class mathutils.Matrix(rows=((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)), /)

This object gives access to Matrices in Blender, supporting square and rectangular
matrices from 2x2 up to 4x4.

**Parameters:**

**rows** (Sequence[Sequence[float]]) – Sequence of rows.

```python
import mathutils
import math

# Create a location matrix.
mat_loc = mathutils.Matrix.Translation((2.0, 3.0, 4.0))

# Create an identity matrix.
mat_sca = mathutils.Matrix.Scale(0.5, 4, (0.0, 0.0, 1.0))

# Create a rotation matrix.
mat_rot = mathutils.Matrix.Rotation(math.radians(45.0), 4, 'X')

# Combine transformations.
mat_out = mat_loc @ mat_rot @ mat_sca
print(mat_out)

# Extract components back out of the matrix as two vectors and a quaternion.
loc, rot, sca = mat_out.decompose()
print(loc, rot, sca)

# Recombine extracted components.
mat_out2 = mathutils.Matrix.LocRotScale(loc, rot, sca)
print(mat_out2)

# It can also be useful to access components of a matrix directly.
mat = mathutils.Matrix()
mat[0][0], mat[1][0], mat[2][0] = 0.0, 1.0, 2.0

mat[0][0:3] = 0.0, 1.0, 2.0

# Each item in a matrix is a vector so vector utility functions can be used.
mat[0].xyz = 0.0, 1.0, 2.0

# Direct buffer access is supported.
print(memoryview(mat).tobytes())
```

<a id="mathutils.Matrix.Diagonal"></a>

#### classmethod mathutils.Matrix.Diagonal(vector, /)

Create a diagonal (scaling) matrix using the values from the vector.

**Parameters:**

**vector** (Sequence[float]) – The vector of values for the diagonal.

**Returns:**

A diagonal matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.Identity"></a>

#### classmethod mathutils.Matrix.Identity(size, /)

Create an identity matrix.

**Parameters:**

**size** (int) – The size of the identity matrix to construct [2, 4].

**Returns:**

A new identity matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.LocRotScale"></a>

#### classmethod mathutils.Matrix.LocRotScale(location, rotation, scale, /)

Create a matrix combining translation, rotation and scale,
acting as the inverse of the decompose() method.

Any of the inputs may be replaced with None if not needed.

**Parameters:**

- **location** (Sequence[float] | None) – The translation component.
- **rotation** ([`Matrix`](#mathutils.Matrix "mathutils.Matrix") | [`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion") | [`Euler`](#mathutils.Euler "mathutils.Euler") | None) – The rotation component as a 3x3 matrix, quaternion, euler or None for no rotation.
- **scale** (Sequence[float] | None) – The scale component.

**Returns:**

Combined transformation as a 4x4 matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

```python
# Compute local object transformation matrix:

import bpy
import mathutils

obj = bpy.context.object
if obj.rotation_mode == 'QUATERNION':
    matrix = mathutils.Matrix.LocRotScale(obj.location, obj.rotation_quaternion, obj.scale)
else:
    matrix = mathutils.Matrix.LocRotScale(obj.location, obj.rotation_euler, obj.scale)
```

<a id="mathutils.Matrix.OrthoProjection"></a>

#### classmethod mathutils.Matrix.OrthoProjection(axis, size, /)

Create a matrix to represent an orthographic projection.

**Parameters:**

- **axis** (Literal['X', 'Y', 'XY', 'XZ', 'YZ'] | Sequence[float]) – An axis string,
  where a single axis is for a 2D matrix.
  Or a vector for an arbitrary axis
- **size** (int) – The size of the projection matrix to construct [2, 4].

**Returns:**

A new projection matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.Rotation"></a>

#### classmethod mathutils.Matrix.Rotation(angle, size, axis=None, /)

Create a matrix representing a rotation.

**Parameters:**

- **angle** (float) – The angle of rotation desired, in radians.
- **size** (int) – The size of the rotation matrix to construct [2, 4].
- **axis** (Literal['X', 'Y', 'Z'] | Sequence[float] | None) – Axis of rotation: a single-character string (‘X’, ‘Y’ or ‘Z’)
  or a 3D vector. Required for `size` 3 or 4. Must be None (or omitted)
  when `size` is 2 - 2D rotation has no axis.

**Returns:**

A new rotation matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.Scale"></a>

#### classmethod mathutils.Matrix.Scale(factor, size, axis=None, /)

Create a matrix representing a scaling.

**Parameters:**

- **factor** (float) – The factor of scaling to apply.
- **size** (int) – The size of the scale matrix to construct [2, 4].
- **axis** (Sequence[float] | None) – Direction along which to scale. When None (or omitted),
  `factor` is applied uniformly along all axes.

**Returns:**

A new scale matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.Shear"></a>

#### classmethod mathutils.Matrix.Shear(plane, size, factor, /)

Create a matrix to represent a shear transformation.

**Parameters:**

- **plane** (Literal['X', 'Y', 'XY', 'XZ', 'YZ']) – An axis string,
  where a single axis is for a 2D matrix only.
- **size** (int) – The size of the shear matrix to construct [2, 4].
- **factor** (float | Sequence[float]) – The factor of shear to apply. For a 2 size matrix use a single float. For a 3 or 4 size matrix pass a pair of floats corresponding with the plane axis.

**Returns:**

A new shear matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.Translation"></a>

#### classmethod mathutils.Matrix.Translation(vector, /)

Create a matrix representing a translation.

**Parameters:**

**vector** (Sequence[float]) – The translation vector.

**Returns:**

An identity matrix with a translation.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.adjugate"></a>

#### mathutils.Matrix.adjugate()

Set the matrix to its adjugate.

**Raises:**

**ValueError** – if the matrix cannot be adjugated.

> **See also:**
>
> [Adjugate matrix](https://en.wikipedia.org/wiki/Adjugate_matrix) on Wikipedia.

<a id="mathutils.Matrix.adjugated"></a>

#### mathutils.Matrix.adjugated()

Return an adjugated copy of the matrix.

**Returns:**

the adjugated matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

**Raises:**

**ValueError** – if the matrix cannot be adjugated

<a id="mathutils.Matrix.copy"></a>

#### mathutils.Matrix.copy()

Returns a copy of this matrix.

**Returns:**

A copy of the matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.decompose"></a>

#### mathutils.Matrix.decompose()

Return the translation, rotation, and scale components of this 4x4 matrix.

**Returns:**

Tuple of translation, rotation, and scale.

**Return type:**

tuple[[`Vector`](#mathutils.Vector "mathutils.Vector"), [`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion"), [`Vector`](#mathutils.Vector "mathutils.Vector")]

<a id="mathutils.Matrix.determinant"></a>

#### mathutils.Matrix.determinant()

Return the determinant of a matrix.

**Returns:**

Return the determinant of a matrix.

**Return type:**

float

> **See also:**
>
> [Determinant](https://en.wikipedia.org/wiki/Determinant) on Wikipedia.

<a id="mathutils.Matrix.freeze"></a>

#### mathutils.Matrix.freeze()

Make this object immutable.

After this the object can be hashed, used in dictionaries & sets.

**Returns:**

An instance of this object.

**Return type:**

Self

<a id="mathutils.Matrix.identity"></a>

#### mathutils.Matrix.identity()

Set the matrix to the identity matrix.

> **Note:**
>
> An object with a location and rotation of zero, and a scale of one
> will have an identity matrix.

> **See also:**
>
> [Identity matrix](https://en.wikipedia.org/wiki/Identity_matrix) on Wikipedia.

<a id="mathutils.Matrix.invert"></a>

#### mathutils.Matrix.invert(fallback=None, /)

Set the matrix to its inverse.

**Parameters:**

**fallback** ([`Matrix`](#mathutils.Matrix "mathutils.Matrix") | None) – Set the matrix to this value when the inverse cannot be calculated
(instead of raising a `ValueError` exception).

> **See also:**
>
> [Inverse matrix](https://en.wikipedia.org/wiki/Inverse_matrix) on Wikipedia.

<a id="mathutils.Matrix.invert_safe"></a>

#### mathutils.Matrix.invert_safe()

Set the matrix to its inverse, will never error.
If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
If tweaked matrix is still degenerated, set to the identity matrix instead.

> **See also:**
>
> [Inverse Matrix](https://en.wikipedia.org/wiki/Inverse_matrix) on Wikipedia.

<a id="mathutils.Matrix.inverted"></a>

#### mathutils.Matrix.inverted(fallback=None, /)

Return an inverted copy of the matrix.

**Parameters:**

**fallback** (Any) – return this when the inverse can’t be calculated
(instead of raising a `ValueError`).

**Returns:**

The inverted matrix or fallback when given.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix") | Any

<a id="mathutils.Matrix.inverted_safe"></a>

#### mathutils.Matrix.inverted_safe()

Return an inverted copy of the matrix, will never error.
If degenerated (e.g. zero scale on an axis), add some epsilon to its diagonal, to get an invertible one.
If tweaked matrix is still degenerated, return the identity matrix instead.

**Returns:**

the inverted matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.lerp"></a>

#### mathutils.Matrix.lerp(other, factor, /)

Returns the interpolation of two matrices. Uses polar decomposition, see “Matrix Animation and Polar Decomposition”, Shoemake and Duff, 1992.

**Parameters:**

- **other** ([`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – value to interpolate with.
- **factor** (float) – The interpolation value in [0.0, 1.0].

**Returns:**

The interpolated matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.normalize"></a>

#### mathutils.Matrix.normalize()

Normalize each of the matrix columns (3x3 and 4x4 only).

> **Note:**
>
> for 4x4 matrices, the 4th column (translation) is left untouched.

<a id="mathutils.Matrix.normalized"></a>

#### mathutils.Matrix.normalized()

Return a column normalized matrix (3x3 and 4x4 only).

**Returns:**

a column normalized matrix

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

> **Note:**
>
> for 4x4 matrices, the 4th column (translation) is left untouched.

<a id="mathutils.Matrix.resize_4x4"></a>

#### mathutils.Matrix.resize_4x4()

Resize the matrix to 4x4.

<a id="mathutils.Matrix.rotate"></a>

#### mathutils.Matrix.rotate(other, /)

Rotates the matrix by another mathutils value.

> **Note:**
>
> The matrix must be 3x3.

> **Note:**
>
> If any of the columns are not unit length this may not have desired results.

**Parameters:**

**other** ([`Euler`](#mathutils.Euler "mathutils.Euler") | [`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion") | [`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – rotation component of mathutils value

<a id="mathutils.Matrix.to_2x2"></a>

#### mathutils.Matrix.to_2x2()

Return a 2x2 copy of this matrix.

**Returns:**

a new matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.to_3x3"></a>

#### mathutils.Matrix.to_3x3()

Return a 3x3 copy of this matrix.

**Returns:**

a new matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.to_4x4"></a>

#### mathutils.Matrix.to_4x4()

Return a 4x4 copy of this matrix.

**Returns:**

a new matrix.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.to_euler"></a>

#### mathutils.Matrix.to_euler(order='XYZ', euler_compat=None, /)

Return an Euler representation of the rotation matrix
(3x3 or 4x4 matrix only).

**Parameters:**

- **order** (Literal['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']) – A rotation order string.
- **euler_compat** ([`Euler`](#mathutils.Euler "mathutils.Euler") | None) – Optional euler argument the new euler will be made
  compatible with (no axis flipping between them).
  Useful for converting a series of matrices to animation curves.

**Returns:**

Euler representation of the matrix.

**Return type:**

[`Euler`](#mathutils.Euler "mathutils.Euler")

<a id="mathutils.Matrix.to_quaternion"></a>

#### mathutils.Matrix.to_quaternion()

Return a quaternion representation of the rotation matrix.

**Returns:**

Quaternion representation of the rotation matrix.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Matrix.to_scale"></a>

#### mathutils.Matrix.to_scale()

Return the scale part of a 3x3 or 4x4 matrix.

**Returns:**

Return the scale of a matrix.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

> **Note:**
>
> This method does not return a negative scale on any axis because it is not possible to obtain this data from the matrix alone.

<a id="mathutils.Matrix.to_translation"></a>

#### mathutils.Matrix.to_translation()

Return the translation part of a 4x4 matrix.

**Returns:**

Return the translation of a matrix.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Matrix.transpose"></a>

#### mathutils.Matrix.transpose()

Set the matrix to its transpose.

> **See also:**
>
> [Transpose](https://en.wikipedia.org/wiki/Transpose) on Wikipedia.

<a id="mathutils.Matrix.transposed"></a>

#### mathutils.Matrix.transposed()

Return a new, transposed matrix.

**Returns:**

a transposed matrix

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.zero"></a>

#### mathutils.Matrix.zero()

Set all the matrix values to zero.

<a id="mathutils.Matrix.col"></a>

#### mathutils.Matrix.col

Access the matrix by columns (read-only).

**Type:**

[`MatrixAccess`](#mathutils.MatrixAccess "mathutils.MatrixAccess")

<a id="mathutils.Matrix.is_frozen"></a>

#### mathutils.Matrix.is_frozen

True when this object has been frozen (read-only).

**Type:**

bool

<a id="mathutils.Matrix.is_identity"></a>

#### mathutils.Matrix.is_identity

True if this is an identity matrix (read-only).

**Type:**

bool

<a id="mathutils.Matrix.is_negative"></a>

#### mathutils.Matrix.is_negative

True if this matrix results in a negative scale, 3x3 and 4x4 only, (read-only).

**Type:**

bool

<a id="mathutils.Matrix.is_orthogonal"></a>

#### mathutils.Matrix.is_orthogonal

True if this matrix is orthogonal, 3x3 and 4x4 only, (read-only).

**Type:**

bool

<a id="mathutils.Matrix.is_orthogonal_axis_vectors"></a>

#### mathutils.Matrix.is_orthogonal_axis_vectors

True if this matrix has orthogonal axis vectors, 3x3 and 4x4 only, (read-only).

**Type:**

bool

<a id="mathutils.Matrix.is_valid"></a>

#### mathutils.Matrix.is_valid

True when the owner of this data is valid.

**Type:**

bool

<a id="mathutils.Matrix.is_wrapped"></a>

#### mathutils.Matrix.is_wrapped

True when this object wraps external data (read-only).

**Type:**

bool

<a id="mathutils.Matrix.median_scale"></a>

#### mathutils.Matrix.median_scale

The average scale applied to each axis (read-only).

**Type:**

float

<a id="mathutils.Matrix.owner"></a>

#### mathutils.Matrix.owner

The item this is wrapping or None (read-only).

**Type:**

Any

<a id="mathutils.Matrix.row"></a>

#### mathutils.Matrix.row

Access the matrix by rows (default), (read-only).

**Type:**

[`MatrixAccess`](#mathutils.MatrixAccess "mathutils.MatrixAccess")

<a id="mathutils.Matrix.translation"></a>

#### mathutils.Matrix.translation

The translation component of the matrix.

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

Special Methods

<a id="mathutils.Matrix.__add__"></a>

#### mathutils.Matrix.__add__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.__eq__"></a>

#### mathutils.Matrix.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Matrix.__getitem__"></a>

#### mathutils.Matrix.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Matrix.__hash__"></a>

#### mathutils.Matrix.__hash__()

**Return type:**

int

<a id="mathutils.Matrix.__imatmul__"></a>

#### mathutils.Matrix.__imatmul__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.__imul__"></a>

#### mathutils.Matrix.__imul__(other)

**Parameters:**

**other** ([`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – The other operand.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

#### __imul__(other)

**Parameters:**

**other** (float) – The other operand.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.__invert__"></a>

#### mathutils.Matrix.__invert__()

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.__len__"></a>

#### mathutils.Matrix.__len__()

**Return type:**

int

<a id="mathutils.Matrix.__matmul__"></a>

#### mathutils.Matrix.__matmul__(other)

**Parameters:**

**other** ([`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – The other operand.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

#### __matmul__(other)

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Matrix.__mul__"></a>

#### mathutils.Matrix.__mul__(other)

**Parameters:**

**other** ([`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – The other operand.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

#### __mul__(other)

**Parameters:**

**other** (float) – The other operand.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.__ne__"></a>

#### mathutils.Matrix.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Matrix.__repr__"></a>

#### mathutils.Matrix.__repr__()

**Return type:**

str

<a id="mathutils.Matrix.__rmul__"></a>

#### mathutils.Matrix.__rmul__(other)

**Parameters:**

**other** (float) – Scalar.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Matrix.__setitem__"></a>

#### mathutils.Matrix.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="mathutils.Matrix.__str__"></a>

#### mathutils.Matrix.__str__()

**Return type:**

str

<a id="mathutils.Matrix.__sub__"></a>

#### mathutils.Matrix.__sub__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.MatrixAccess"></a>

### class mathutils.MatrixAccess

An indexable type for accessing matrix rows or columns as [`Vector`](#mathutils.Vector "mathutils.Vector") types.

Special Methods

<a id="mathutils.MatrixAccess.__getitem__"></a>

#### mathutils.MatrixAccess.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="mathutils.MatrixAccess.__iter__"></a>

#### mathutils.MatrixAccess.__iter__()

**Return type:**

[`MatrixAccess`](#mathutils.MatrixAccess "mathutils.MatrixAccess")

<a id="mathutils.MatrixAccess.__len__"></a>

#### mathutils.MatrixAccess.__len__()

**Return type:**

int

<a id="mathutils.MatrixAccess.__setitem__"></a>

#### mathutils.MatrixAccess.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="mathutils.Quaternion"></a>

### class mathutils.Quaternion(seq=(1.0, 0.0, 0.0, 0.0), angle=0.0, /)

This object gives access to Quaternions in Blender.

**Parameters:**

- **seq** (Sequence[float]) – A (w, x, y, z) quaternion, a 3D exponential map vector,
  or a 3D axis vector (when angle is also provided).
- **angle** (float) – rotation angle, in radians

The constructor takes arguments in various forms:

(), *no args*
:   Create an identity quaternion

(*wxyz*)
:   Create a quaternion from a `(w, x, y, z)` vector.

(*exponential_map*)
:   Create a quaternion from a 3d exponential map vector.

    > **See also:**
    >
    > [`to_exponential_map()`](#mathutils.Quaternion.to_exponential_map "mathutils.Quaternion.to_exponential_map")

(*axis, angle*)
:   Create a quaternion representing a rotation of *angle* radians over *axis*.

    > **See also:**
    >
    > [`to_axis_angle()`](#mathutils.Quaternion.to_axis_angle "mathutils.Quaternion.to_axis_angle")

```python
import mathutils
import math

# A new rotation 90 degrees about the Y axis.
quat_a = mathutils.Quaternion((0.7071068, 0.0, 0.7071068, 0.0))

# Passing values to Quaternion's directly can be confusing so axis, angle
# is supported for initializing too.
quat_b = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))

print("Check quaternions match", quat_a == quat_b)

# Like matrices, quaternions can be multiplied to accumulate rotational values.
quat_a = mathutils.Quaternion((0.0, 1.0, 0.0), math.radians(90.0))
quat_b = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(45.0))
quat_out = quat_a @ quat_b

# Print the quaternion, euler degrees for mere mortals and (axis, angle).
print("Final Rotation:")
print(quat_out)
print("{:.2f}, {:.2f}, {:.2f}".format(*(math.degrees(a) for a in quat_out.to_euler())))
print("({:.2f}, {:.2f}, {:.2f}), {:.2f}".format(*quat_out.axis, math.degrees(quat_out.angle)))

# Multiple rotations can be interpolated using the exponential map.
quat_c = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(15.0))
exp_avg = (quat_a.to_exponential_map() +
           quat_b.to_exponential_map() +
           quat_c.to_exponential_map()) / 3.0
quat_avg = mathutils.Quaternion(exp_avg)
print("Average rotation:")
print(quat_avg)

# Direct buffer access is supported.
print(memoryview(quat_avg).tobytes())
```

<a id="mathutils.Quaternion.conjugate"></a>

#### mathutils.Quaternion.conjugate()

Set the quaternion to its conjugate (negate x, y, z).

<a id="mathutils.Quaternion.conjugated"></a>

#### mathutils.Quaternion.conjugated()

Return a new conjugated quaternion.

**Returns:**

a new quaternion.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.copy"></a>

#### mathutils.Quaternion.copy()

Returns a copy of this quaternion.

**Returns:**

A copy of the quaternion.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

> **Note:**
>
> use this to get a copy of a wrapped quaternion with
> no reference to the original data.

<a id="mathutils.Quaternion.cross"></a>

#### mathutils.Quaternion.cross(other, /)

Return the cross product of this quaternion and another.

**Parameters:**

**other** ([`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")) – The other quaternion to perform the cross product with.

**Returns:**

The cross product.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.dot"></a>

#### mathutils.Quaternion.dot(other, /)

Return the dot product of this quaternion and another.

**Parameters:**

**other** ([`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")) – The other quaternion to perform the dot product with.

**Returns:**

The dot product.

**Return type:**

float

<a id="mathutils.Quaternion.freeze"></a>

#### mathutils.Quaternion.freeze()

Make this object immutable.

After this the object can be hashed, used in dictionaries & sets.

**Returns:**

An instance of this object.

**Return type:**

Self

<a id="mathutils.Quaternion.identity"></a>

#### mathutils.Quaternion.identity()

Set the quaternion to an identity quaternion.

<a id="mathutils.Quaternion.invert"></a>

#### mathutils.Quaternion.invert()

Set the quaternion to its inverse.

<a id="mathutils.Quaternion.inverted"></a>

#### mathutils.Quaternion.inverted()

Return a new, inverted quaternion.

**Returns:**

the inverted value.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.make_compatible"></a>

#### mathutils.Quaternion.make_compatible(other, /)

Make this quaternion compatible with another,
so interpolating between them works as intended.

**Parameters:**

**other** ([`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")) – The reference quaternion to make this one compatible with.

<a id="mathutils.Quaternion.negate"></a>

#### mathutils.Quaternion.negate()

Set the quaternion to its negative.

<a id="mathutils.Quaternion.normalize"></a>

#### mathutils.Quaternion.normalize()

Normalize the quaternion.

<a id="mathutils.Quaternion.normalized"></a>

#### mathutils.Quaternion.normalized()

Return a new normalized quaternion.

**Returns:**

a normalized copy.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.rotate"></a>

#### mathutils.Quaternion.rotate(other, /)

Rotates the quaternion by another mathutils value.

**Parameters:**

**other** ([`Euler`](#mathutils.Euler "mathutils.Euler") | [`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion") | [`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – rotation component of mathutils value

<a id="mathutils.Quaternion.rotation_difference"></a>

#### mathutils.Quaternion.rotation_difference(other, /)

Returns a quaternion representing the rotational difference.

**Parameters:**

**other** ([`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")) – second quaternion.

**Returns:**

the rotational difference between the two quat rotations.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.slerp"></a>

#### mathutils.Quaternion.slerp(other, factor, /)

Returns the interpolation of two quaternions.

**Parameters:**

- **other** ([`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")) – value to interpolate with.
- **factor** (float) – The interpolation value in [0.0, 1.0].

**Returns:**

The interpolated rotation.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.to_axis_angle"></a>

#### mathutils.Quaternion.to_axis_angle()

Return the axis, angle representation of the quaternion.

**Returns:**

Axis, angle.

**Return type:**

tuple[[`Vector`](#mathutils.Vector "mathutils.Vector"), float]

<a id="mathutils.Quaternion.to_euler"></a>

#### mathutils.Quaternion.to_euler(order='XYZ', euler_compat=None, /)

Return Euler representation of the quaternion.

**Parameters:**

- **order** (Literal['XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX']) – Rotation order.
- **euler_compat** ([`Euler`](#mathutils.Euler "mathutils.Euler") | None) – Optional euler argument the new euler will be made
  compatible with (no axis flipping between them).
  Useful for converting a series of quaternions to animation curves.

**Returns:**

Euler representation of the quaternion.

**Return type:**

[`Euler`](#mathutils.Euler "mathutils.Euler")

<a id="mathutils.Quaternion.to_exponential_map"></a>

#### mathutils.Quaternion.to_exponential_map()

Return the exponential map representation of the quaternion.

This representation consists of the rotation axis multiplied by the rotation angle.
Such a representation is useful for interpolation between multiple orientations.

**Returns:**

3D exponential map.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

To convert back to a quaternion, pass it to the [`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion") constructor.

<a id="mathutils.Quaternion.to_matrix"></a>

#### mathutils.Quaternion.to_matrix()

Return a matrix representation of the quaternion.

**Returns:**

A 3x3 rotation matrix representation of the quaternion.

**Return type:**

[`Matrix`](#mathutils.Matrix "mathutils.Matrix")

<a id="mathutils.Quaternion.to_swing_twist"></a>

#### mathutils.Quaternion.to_swing_twist(axis, /)

Split the rotation into a swing quaternion with the specified
axis fixed at zero, and the remaining twist rotation angle.

**Parameters:**

**axis** (Literal['X', 'Y', 'Z']) – Twist axis as a string.

**Returns:**

Swing, twist angle.

**Return type:**

tuple[[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion"), float]

<a id="mathutils.Quaternion.angle"></a>

#### mathutils.Quaternion.angle

Angle of the quaternion.

**Type:**

float

<a id="mathutils.Quaternion.axis"></a>

#### mathutils.Quaternion.axis

Quaternion axis as a vector.

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Quaternion.is_frozen"></a>

#### mathutils.Quaternion.is_frozen

True when this object has been frozen (read-only).

**Type:**

bool

<a id="mathutils.Quaternion.is_valid"></a>

#### mathutils.Quaternion.is_valid

True when the owner of this data is valid.

**Type:**

bool

<a id="mathutils.Quaternion.is_wrapped"></a>

#### mathutils.Quaternion.is_wrapped

True when this object wraps external data (read-only).

**Type:**

bool

<a id="mathutils.Quaternion.magnitude"></a>

#### mathutils.Quaternion.magnitude

Size of the quaternion (read-only).

**Type:**

float

<a id="mathutils.Quaternion.owner"></a>

#### mathutils.Quaternion.owner

The item this is wrapping or None (read-only).

**Type:**

Any

<a id="mathutils.Quaternion.w"></a>

#### mathutils.Quaternion.w

Quaternion component value.

**Type:**

float

<a id="mathutils.Quaternion.x"></a>

#### mathutils.Quaternion.x

Quaternion component value.

**Type:**

float

<a id="mathutils.Quaternion.y"></a>

#### mathutils.Quaternion.y

Quaternion component value.

**Type:**

float

<a id="mathutils.Quaternion.z"></a>

#### mathutils.Quaternion.z

Quaternion component value.

**Type:**

float

Special Methods

<a id="mathutils.Quaternion.__add__"></a>

#### mathutils.Quaternion.__add__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.__eq__"></a>

#### mathutils.Quaternion.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Quaternion.__getitem__"></a>

#### mathutils.Quaternion.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="mathutils.Quaternion.__hash__"></a>

#### mathutils.Quaternion.__hash__()

**Return type:**

int

<a id="mathutils.Quaternion.__imatmul__"></a>

#### mathutils.Quaternion.__imatmul__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.__imul__"></a>

#### mathutils.Quaternion.__imul__(other)

**Parameters:**

**other** ([`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")) – The other operand.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

#### __imul__(other)

**Parameters:**

**other** (float) – The other operand.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.__len__"></a>

#### mathutils.Quaternion.__len__()

**Return type:**

int

<a id="mathutils.Quaternion.__matmul__"></a>

#### mathutils.Quaternion.__matmul__(other)

**Parameters:**

**other** ([`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")) – The other operand.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

#### __matmul__(other)

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Quaternion.__mul__"></a>

#### mathutils.Quaternion.__mul__(other)

**Parameters:**

**other** ([`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")) – The other operand.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

#### __mul__(other)

**Parameters:**

**other** (float) – The other operand.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.__ne__"></a>

#### mathutils.Quaternion.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Quaternion.__neg__"></a>

#### mathutils.Quaternion.__neg__()

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.__pos__"></a>

#### mathutils.Quaternion.__pos__()

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.__repr__"></a>

#### mathutils.Quaternion.__repr__()

**Return type:**

str

<a id="mathutils.Quaternion.__rmul__"></a>

#### mathutils.Quaternion.__rmul__(other)

**Parameters:**

**other** (float) – Scalar.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Quaternion.__setitem__"></a>

#### mathutils.Quaternion.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="mathutils.Quaternion.__str__"></a>

#### mathutils.Quaternion.__str__()

**Return type:**

str

<a id="mathutils.Quaternion.__sub__"></a>

#### mathutils.Quaternion.__sub__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Vector"></a>

### class mathutils.Vector(seq=(0.0, 0.0, 0.0), /)

This object gives access to Vectors in Blender.

**Parameters:**

**seq** (Sequence[float]) – Components of the vector, must be a sequence of at least two.

```python
import mathutils

# Zero length vector.
vec = mathutils.Vector((0.0, 0.0, 1.0))

# Unit length vector.
vec_a = vec.normalized()

vec_b = mathutils.Vector((0.0, 1.0, 2.0))

vec2d = mathutils.Vector((1.0, 2.0))
vec3d = mathutils.Vector((1.0, 0.0, 0.0))
vec4d = vec_a.to_4d()

# Other `mathutils` types.
quat = mathutils.Quaternion()
matrix = mathutils.Matrix()

# Comparison operators can be done on Vector classes:

# (In)equality operators == and != test component values, e.g. 1,2,3 != 3,2,1
vec_a == vec_b
vec_a != vec_b

# Ordering operators >, >=, > and <= test vector length.
vec_a > vec_b
vec_a >= vec_b
vec_a < vec_b
vec_a <= vec_b

# Math can be performed on Vector classes.
vec_a + vec_b
vec_a - vec_b
vec_a @ vec_b
vec_a * 10.0
matrix @ vec_a
quat @ vec_a
-vec_a

# You can access a vector object like a sequence.
x = vec_a[0]
len(vec)
vec_a[:] = vec_b
vec_a[:] = 1.0, 2.0, 3.0
vec2d[:] = vec3d[:2]

# Vectors support 'swizzle' operations.
# See https://en.wikipedia.org/wiki/Swizzling_(computer_graphics)
vec.xyz = vec.zyx
vec.xy = vec4d.zw
vec.xyz = vec4d.wzz
vec4d.wxyz = vec.yxyx

# Direct buffer access is supported.
raw_data = memoryview(vec).tobytes()
```

<a id="mathutils.Vector.Fill"></a>

#### classmethod mathutils.Vector.Fill(size, fill=0.0, /)

Create a vector of length size with all values set to fill.

**Parameters:**

- **size** (int) – The length of the vector to be created.
- **fill** (float) – The value used to fill the vector.

**Returns:**

A new vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.Linspace"></a>

#### classmethod mathutils.Vector.Linspace(start, stop, size, /)

Create a vector of the specified size which is filled with linearly spaced values between start and stop values.

**Parameters:**

- **start** (float) – The start of the range used to fill the vector.
- **stop** (float) – The end of the range used to fill the vector.
- **size** (int) – The size of the vector to be created.

**Returns:**

A new vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.Range"></a>

#### classmethod mathutils.Vector.Range(start, stop, step=1, /)

Create a vector filled with a range of values.

This method can also be called with a single argument, in which case the argument is interpreted as `stop` and `start` defaults to 0.

**Parameters:**

- **start** (int) – The start of the range used to fill the vector.
- **stop** (int) – The end of the range used to fill the vector.
- **step** (int) – The step between successive values in the vector.

**Returns:**

A new vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.Repeat"></a>

#### classmethod mathutils.Vector.Repeat(vector, size, /)

Create a vector by repeating the values in vector until the required size is reached.

**Parameters:**

- **vector** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – The vector to draw values from.
- **size** (int) – The size of the vector to be created.

**Returns:**

A new vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.angle"></a>

#### mathutils.Vector.angle(other, fallback=None, /)

Return the angle between two vectors.

> **Note:**
>
> For 4D vectors, only the x, y, z components are used.

**Parameters:**

- **other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – another vector to compare the angle with
- **fallback** (Any) – return this when the angle can’t be calculated (zero length vector),
  (instead of raising a `ValueError`).

**Returns:**

angle in radians or fallback when given

**Return type:**

float | Any

<a id="mathutils.Vector.angle_signed"></a>

#### mathutils.Vector.angle_signed(other, fallback=None, /)

Return the signed angle between two 2D vectors (clockwise is positive).

**Parameters:**

- **other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – another vector to compare the angle with
- **fallback** (Any) – return this when the angle can’t be calculated (zero length vector),
  (instead of raising a `ValueError`).

**Returns:**

angle in radians or fallback when given

**Return type:**

float | Any

<a id="mathutils.Vector.copy"></a>

#### mathutils.Vector.copy()

Returns a copy of this vector.

**Returns:**

A copy of the vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

> **Note:**
>
> use this to get a copy of a wrapped vector with
> no reference to the original data.

<a id="mathutils.Vector.cross"></a>

#### mathutils.Vector.cross(other, /)

Return the cross product of this vector and another.

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – The other vector to perform the cross product with.

**Returns:**

The cross product as a vector or a float when 2D vectors are used.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector") | float

> **Note:**
>
> both vectors must be 2D or 3D

<a id="mathutils.Vector.dot"></a>

#### mathutils.Vector.dot(other, /)

Return the dot product of this vector and another.

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – The other vector to perform the dot product with.

**Returns:**

The dot product.

**Return type:**

float

<a id="mathutils.Vector.freeze"></a>

#### mathutils.Vector.freeze()

Make this object immutable.

After this the object can be hashed, used in dictionaries & sets.

**Returns:**

An instance of this object.

**Return type:**

Self

<a id="mathutils.Vector.lerp"></a>

#### mathutils.Vector.lerp(other, factor, /)

Returns the interpolation of two vectors.

**Parameters:**

- **other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – value to interpolate with.
- **factor** (float) – The interpolation value in [0.0, 1.0].

**Returns:**

The interpolated vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.negate"></a>

#### mathutils.Vector.negate()

Set all values to their negative.

<a id="mathutils.Vector.normalize"></a>

#### mathutils.Vector.normalize()

Normalize the vector, making the length of the vector always 1.0.

> **Warning:**
>
> Normalizing a vector where all values are zero has no effect.

> **Note:**
>
> For 4D vectors, only the x, y, z components are normalized;
> the w component is left untouched.
> The resulting 4D vector may not have unit length.

<a id="mathutils.Vector.normalized"></a>

#### mathutils.Vector.normalized()

Return a new, normalized vector.

> **Note:**
>
> For 4D vectors, only the x, y, z components are normalized;
> the w component is left untouched.
> The resulting 4D vector may not have unit length.

**Returns:**

a normalized copy of the vector

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.orthogonal"></a>

#### mathutils.Vector.orthogonal()

Return a perpendicular vector.

**Returns:**

a new vector 90 degrees from this vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

> **Note:**
>
> the axis is undefined, only use when any orthogonal vector is acceptable.

<a id="mathutils.Vector.project"></a>

#### mathutils.Vector.project(other, /)

Return the projection of this vector onto the *other*.

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – second vector.

**Returns:**

the parallel projection vector

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.reflect"></a>

#### mathutils.Vector.reflect(mirror, /)

Return the reflection vector from the *mirror* argument.

**Parameters:**

**mirror** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – This vector could be a normal from the reflecting surface.

**Returns:**

The reflected vector matching the size of this vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.resize"></a>

#### mathutils.Vector.resize(size, /)

Resize the vector to have size number of elements.

**Parameters:**

**size** (int) – The new size of the vector.

<a id="mathutils.Vector.resize_2d"></a>

#### mathutils.Vector.resize_2d()

Resize the vector to 2D (x, y).

<a id="mathutils.Vector.resize_3d"></a>

#### mathutils.Vector.resize_3d()

Resize the vector to 3D (x, y, z).

<a id="mathutils.Vector.resize_4d"></a>

#### mathutils.Vector.resize_4d()

Resize the vector to 4D (x, y, z, w).

<a id="mathutils.Vector.resized"></a>

#### mathutils.Vector.resized(size, /)

Return a resized copy of the vector with size number of elements.

**Parameters:**

**size** (int) – The new size of the vector.

**Returns:**

A new vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.rotate"></a>

#### mathutils.Vector.rotate(other, /)

Rotate the vector by a rotation value.

> **Note:**
>
> 2D vectors are a special case that can only be rotated by a 2x2 matrix.

**Parameters:**

**other** ([`Euler`](#mathutils.Euler "mathutils.Euler") | [`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion") | [`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – rotation component of mathutils value

<a id="mathutils.Vector.rotation_difference"></a>

#### mathutils.Vector.rotation_difference(other, /)

Returns a quaternion representing the rotational difference between this
vector and another.

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – second vector.

**Returns:**

the rotational difference between the two vectors.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

> **Note:**
>
> 2D vectors raise an `AttributeError`.

<a id="mathutils.Vector.slerp"></a>

#### mathutils.Vector.slerp(other, factor, fallback=None, /)

Returns the interpolation of two non-zero vectors (spherical coordinates).

**Parameters:**

- **other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – value to interpolate with.
- **factor** (float) – The interpolation value typically in [0.0, 1.0].
- **fallback** (Any) – return this when the vector can’t be calculated (zero length vector or direct opposites),
  (instead of raising a `ValueError`).

**Returns:**

The interpolated vector.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.to_2d"></a>

#### mathutils.Vector.to_2d()

Return a 2d copy of the vector.

**Returns:**

a new vector

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.to_3d"></a>

#### mathutils.Vector.to_3d()

Return a 3d copy of the vector.

**Returns:**

a new vector

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.to_4d"></a>

#### mathutils.Vector.to_4d()

Return a 4d copy of the vector.

**Returns:**

a new vector

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.to_track_quat"></a>

#### mathutils.Vector.to_track_quat(track='Z', up='Y', /)

Return a quaternion rotation from the vector and the track and up axis.

**Parameters:**

- **track** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Track axis string.
- **up** (Literal['X', 'Y', 'Z']) – Up axis string.

**Returns:**

rotation from the vector and the track and up axis.

**Return type:**

[`Quaternion`](#mathutils.Quaternion "mathutils.Quaternion")

<a id="mathutils.Vector.to_tuple"></a>

#### mathutils.Vector.to_tuple(precision=-1, /)

Return this vector as a tuple with a given precision.

**Parameters:**

**precision** (int) – The number to round the value to in [-1, 21].

**Returns:**

the values of the vector rounded by precision

**Return type:**

tuple[float, …]

<a id="mathutils.Vector.zero"></a>

#### mathutils.Vector.zero()

Set all values to zero.

<a id="mathutils.Vector.is_frozen"></a>

#### mathutils.Vector.is_frozen

True when this object has been frozen (read-only).

**Type:**

bool

<a id="mathutils.Vector.is_valid"></a>

#### mathutils.Vector.is_valid

True when the owner of this data is valid.

**Type:**

bool

<a id="mathutils.Vector.is_wrapped"></a>

#### mathutils.Vector.is_wrapped

True when this object wraps external data (read-only).

**Type:**

bool

<a id="mathutils.Vector.length"></a>

#### mathutils.Vector.length

Vector Length.

**Type:**

float

<a id="mathutils.Vector.length_squared"></a>

#### mathutils.Vector.length_squared

Vector length squared (v.dot(v)).

**Type:**

float

<a id="mathutils.Vector.magnitude"></a>

#### mathutils.Vector.magnitude

Vector Length.

**Type:**

float

<a id="mathutils.Vector.owner"></a>

#### mathutils.Vector.owner

The item this is wrapping or None (read-only).

**Type:**

Any

<a id="mathutils.Vector.w"></a>

#### mathutils.Vector.w

Vector W axis (4D Vectors only).

**Type:**

float

<a id="mathutils.Vector.ww"></a>

#### mathutils.Vector.ww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.www"></a>

#### mathutils.Vector.www

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwww"></a>

#### mathutils.Vector.wwww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwwx"></a>

#### mathutils.Vector.wwwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwwy"></a>

#### mathutils.Vector.wwwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwwz"></a>

#### mathutils.Vector.wwwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwx"></a>

#### mathutils.Vector.wwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwxw"></a>

#### mathutils.Vector.wwxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwxx"></a>

#### mathutils.Vector.wwxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwxy"></a>

#### mathutils.Vector.wwxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwxz"></a>

#### mathutils.Vector.wwxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwy"></a>

#### mathutils.Vector.wwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwyw"></a>

#### mathutils.Vector.wwyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwyx"></a>

#### mathutils.Vector.wwyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwyy"></a>

#### mathutils.Vector.wwyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwyz"></a>

#### mathutils.Vector.wwyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwz"></a>

#### mathutils.Vector.wwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwzw"></a>

#### mathutils.Vector.wwzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwzx"></a>

#### mathutils.Vector.wwzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwzy"></a>

#### mathutils.Vector.wwzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wwzz"></a>

#### mathutils.Vector.wwzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wx"></a>

#### mathutils.Vector.wx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxw"></a>

#### mathutils.Vector.wxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxww"></a>

#### mathutils.Vector.wxww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxwx"></a>

#### mathutils.Vector.wxwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxwy"></a>

#### mathutils.Vector.wxwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxwz"></a>

#### mathutils.Vector.wxwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxx"></a>

#### mathutils.Vector.wxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxxw"></a>

#### mathutils.Vector.wxxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxxx"></a>

#### mathutils.Vector.wxxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxxy"></a>

#### mathutils.Vector.wxxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxxz"></a>

#### mathutils.Vector.wxxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxy"></a>

#### mathutils.Vector.wxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxyw"></a>

#### mathutils.Vector.wxyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxyx"></a>

#### mathutils.Vector.wxyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxyy"></a>

#### mathutils.Vector.wxyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxyz"></a>

#### mathutils.Vector.wxyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxz"></a>

#### mathutils.Vector.wxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxzw"></a>

#### mathutils.Vector.wxzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxzx"></a>

#### mathutils.Vector.wxzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxzy"></a>

#### mathutils.Vector.wxzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wxzz"></a>

#### mathutils.Vector.wxzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wy"></a>

#### mathutils.Vector.wy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyw"></a>

#### mathutils.Vector.wyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyww"></a>

#### mathutils.Vector.wyww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wywx"></a>

#### mathutils.Vector.wywx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wywy"></a>

#### mathutils.Vector.wywy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wywz"></a>

#### mathutils.Vector.wywz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyx"></a>

#### mathutils.Vector.wyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyxw"></a>

#### mathutils.Vector.wyxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyxx"></a>

#### mathutils.Vector.wyxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyxy"></a>

#### mathutils.Vector.wyxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyxz"></a>

#### mathutils.Vector.wyxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyy"></a>

#### mathutils.Vector.wyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyyw"></a>

#### mathutils.Vector.wyyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyyx"></a>

#### mathutils.Vector.wyyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyyy"></a>

#### mathutils.Vector.wyyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyyz"></a>

#### mathutils.Vector.wyyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyz"></a>

#### mathutils.Vector.wyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyzw"></a>

#### mathutils.Vector.wyzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyzx"></a>

#### mathutils.Vector.wyzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyzy"></a>

#### mathutils.Vector.wyzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wyzz"></a>

#### mathutils.Vector.wyzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wz"></a>

#### mathutils.Vector.wz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzw"></a>

#### mathutils.Vector.wzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzww"></a>

#### mathutils.Vector.wzww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzwx"></a>

#### mathutils.Vector.wzwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzwy"></a>

#### mathutils.Vector.wzwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzwz"></a>

#### mathutils.Vector.wzwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzx"></a>

#### mathutils.Vector.wzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzxw"></a>

#### mathutils.Vector.wzxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzxx"></a>

#### mathutils.Vector.wzxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzxy"></a>

#### mathutils.Vector.wzxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzxz"></a>

#### mathutils.Vector.wzxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzy"></a>

#### mathutils.Vector.wzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzyw"></a>

#### mathutils.Vector.wzyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzyx"></a>

#### mathutils.Vector.wzyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzyy"></a>

#### mathutils.Vector.wzyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzyz"></a>

#### mathutils.Vector.wzyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzz"></a>

#### mathutils.Vector.wzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzzw"></a>

#### mathutils.Vector.wzzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzzx"></a>

#### mathutils.Vector.wzzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzzy"></a>

#### mathutils.Vector.wzzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.wzzz"></a>

#### mathutils.Vector.wzzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.x"></a>

#### mathutils.Vector.x

Vector X axis.

**Type:**

float

<a id="mathutils.Vector.xw"></a>

#### mathutils.Vector.xw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xww"></a>

#### mathutils.Vector.xww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwww"></a>

#### mathutils.Vector.xwww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwwx"></a>

#### mathutils.Vector.xwwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwwy"></a>

#### mathutils.Vector.xwwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwwz"></a>

#### mathutils.Vector.xwwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwx"></a>

#### mathutils.Vector.xwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwxw"></a>

#### mathutils.Vector.xwxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwxx"></a>

#### mathutils.Vector.xwxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwxy"></a>

#### mathutils.Vector.xwxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwxz"></a>

#### mathutils.Vector.xwxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwy"></a>

#### mathutils.Vector.xwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwyw"></a>

#### mathutils.Vector.xwyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwyx"></a>

#### mathutils.Vector.xwyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwyy"></a>

#### mathutils.Vector.xwyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwyz"></a>

#### mathutils.Vector.xwyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwz"></a>

#### mathutils.Vector.xwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwzw"></a>

#### mathutils.Vector.xwzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwzx"></a>

#### mathutils.Vector.xwzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwzy"></a>

#### mathutils.Vector.xwzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xwzz"></a>

#### mathutils.Vector.xwzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xx"></a>

#### mathutils.Vector.xx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxw"></a>

#### mathutils.Vector.xxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxww"></a>

#### mathutils.Vector.xxww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxwx"></a>

#### mathutils.Vector.xxwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxwy"></a>

#### mathutils.Vector.xxwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxwz"></a>

#### mathutils.Vector.xxwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxx"></a>

#### mathutils.Vector.xxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxxw"></a>

#### mathutils.Vector.xxxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxxx"></a>

#### mathutils.Vector.xxxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxxy"></a>

#### mathutils.Vector.xxxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxxz"></a>

#### mathutils.Vector.xxxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxy"></a>

#### mathutils.Vector.xxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxyw"></a>

#### mathutils.Vector.xxyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxyx"></a>

#### mathutils.Vector.xxyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxyy"></a>

#### mathutils.Vector.xxyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxyz"></a>

#### mathutils.Vector.xxyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxz"></a>

#### mathutils.Vector.xxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxzw"></a>

#### mathutils.Vector.xxzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxzx"></a>

#### mathutils.Vector.xxzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxzy"></a>

#### mathutils.Vector.xxzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xxzz"></a>

#### mathutils.Vector.xxzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xy"></a>

#### mathutils.Vector.xy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyw"></a>

#### mathutils.Vector.xyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyww"></a>

#### mathutils.Vector.xyww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xywx"></a>

#### mathutils.Vector.xywx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xywy"></a>

#### mathutils.Vector.xywy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xywz"></a>

#### mathutils.Vector.xywz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyx"></a>

#### mathutils.Vector.xyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyxw"></a>

#### mathutils.Vector.xyxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyxx"></a>

#### mathutils.Vector.xyxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyxy"></a>

#### mathutils.Vector.xyxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyxz"></a>

#### mathutils.Vector.xyxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyy"></a>

#### mathutils.Vector.xyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyyw"></a>

#### mathutils.Vector.xyyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyyx"></a>

#### mathutils.Vector.xyyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyyy"></a>

#### mathutils.Vector.xyyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyyz"></a>

#### mathutils.Vector.xyyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyz"></a>

#### mathutils.Vector.xyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyzw"></a>

#### mathutils.Vector.xyzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyzx"></a>

#### mathutils.Vector.xyzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyzy"></a>

#### mathutils.Vector.xyzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xyzz"></a>

#### mathutils.Vector.xyzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xz"></a>

#### mathutils.Vector.xz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzw"></a>

#### mathutils.Vector.xzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzww"></a>

#### mathutils.Vector.xzww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzwx"></a>

#### mathutils.Vector.xzwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzwy"></a>

#### mathutils.Vector.xzwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzwz"></a>

#### mathutils.Vector.xzwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzx"></a>

#### mathutils.Vector.xzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzxw"></a>

#### mathutils.Vector.xzxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzxx"></a>

#### mathutils.Vector.xzxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzxy"></a>

#### mathutils.Vector.xzxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzxz"></a>

#### mathutils.Vector.xzxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzy"></a>

#### mathutils.Vector.xzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzyw"></a>

#### mathutils.Vector.xzyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzyx"></a>

#### mathutils.Vector.xzyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzyy"></a>

#### mathutils.Vector.xzyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzyz"></a>

#### mathutils.Vector.xzyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzz"></a>

#### mathutils.Vector.xzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzzw"></a>

#### mathutils.Vector.xzzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzzx"></a>

#### mathutils.Vector.xzzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzzy"></a>

#### mathutils.Vector.xzzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.xzzz"></a>

#### mathutils.Vector.xzzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.y"></a>

#### mathutils.Vector.y

Vector Y axis.

**Type:**

float

<a id="mathutils.Vector.yw"></a>

#### mathutils.Vector.yw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yww"></a>

#### mathutils.Vector.yww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywww"></a>

#### mathutils.Vector.ywww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywwx"></a>

#### mathutils.Vector.ywwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywwy"></a>

#### mathutils.Vector.ywwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywwz"></a>

#### mathutils.Vector.ywwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywx"></a>

#### mathutils.Vector.ywx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywxw"></a>

#### mathutils.Vector.ywxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywxx"></a>

#### mathutils.Vector.ywxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywxy"></a>

#### mathutils.Vector.ywxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywxz"></a>

#### mathutils.Vector.ywxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywy"></a>

#### mathutils.Vector.ywy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywyw"></a>

#### mathutils.Vector.ywyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywyx"></a>

#### mathutils.Vector.ywyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywyy"></a>

#### mathutils.Vector.ywyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywyz"></a>

#### mathutils.Vector.ywyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywz"></a>

#### mathutils.Vector.ywz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywzw"></a>

#### mathutils.Vector.ywzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywzx"></a>

#### mathutils.Vector.ywzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywzy"></a>

#### mathutils.Vector.ywzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.ywzz"></a>

#### mathutils.Vector.ywzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yx"></a>

#### mathutils.Vector.yx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxw"></a>

#### mathutils.Vector.yxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxww"></a>

#### mathutils.Vector.yxww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxwx"></a>

#### mathutils.Vector.yxwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxwy"></a>

#### mathutils.Vector.yxwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxwz"></a>

#### mathutils.Vector.yxwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxx"></a>

#### mathutils.Vector.yxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxxw"></a>

#### mathutils.Vector.yxxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxxx"></a>

#### mathutils.Vector.yxxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxxy"></a>

#### mathutils.Vector.yxxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxxz"></a>

#### mathutils.Vector.yxxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxy"></a>

#### mathutils.Vector.yxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxyw"></a>

#### mathutils.Vector.yxyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxyx"></a>

#### mathutils.Vector.yxyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxyy"></a>

#### mathutils.Vector.yxyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxyz"></a>

#### mathutils.Vector.yxyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxz"></a>

#### mathutils.Vector.yxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxzw"></a>

#### mathutils.Vector.yxzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxzx"></a>

#### mathutils.Vector.yxzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxzy"></a>

#### mathutils.Vector.yxzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yxzz"></a>

#### mathutils.Vector.yxzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yy"></a>

#### mathutils.Vector.yy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyw"></a>

#### mathutils.Vector.yyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyww"></a>

#### mathutils.Vector.yyww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yywx"></a>

#### mathutils.Vector.yywx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yywy"></a>

#### mathutils.Vector.yywy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yywz"></a>

#### mathutils.Vector.yywz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyx"></a>

#### mathutils.Vector.yyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyxw"></a>

#### mathutils.Vector.yyxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyxx"></a>

#### mathutils.Vector.yyxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyxy"></a>

#### mathutils.Vector.yyxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyxz"></a>

#### mathutils.Vector.yyxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyy"></a>

#### mathutils.Vector.yyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyyw"></a>

#### mathutils.Vector.yyyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyyx"></a>

#### mathutils.Vector.yyyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyyy"></a>

#### mathutils.Vector.yyyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyyz"></a>

#### mathutils.Vector.yyyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyz"></a>

#### mathutils.Vector.yyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyzw"></a>

#### mathutils.Vector.yyzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyzx"></a>

#### mathutils.Vector.yyzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyzy"></a>

#### mathutils.Vector.yyzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yyzz"></a>

#### mathutils.Vector.yyzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yz"></a>

#### mathutils.Vector.yz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzw"></a>

#### mathutils.Vector.yzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzww"></a>

#### mathutils.Vector.yzww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzwx"></a>

#### mathutils.Vector.yzwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzwy"></a>

#### mathutils.Vector.yzwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzwz"></a>

#### mathutils.Vector.yzwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzx"></a>

#### mathutils.Vector.yzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzxw"></a>

#### mathutils.Vector.yzxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzxx"></a>

#### mathutils.Vector.yzxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzxy"></a>

#### mathutils.Vector.yzxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzxz"></a>

#### mathutils.Vector.yzxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzy"></a>

#### mathutils.Vector.yzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzyw"></a>

#### mathutils.Vector.yzyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzyx"></a>

#### mathutils.Vector.yzyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzyy"></a>

#### mathutils.Vector.yzyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzyz"></a>

#### mathutils.Vector.yzyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzz"></a>

#### mathutils.Vector.yzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzzw"></a>

#### mathutils.Vector.yzzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzzx"></a>

#### mathutils.Vector.yzzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzzy"></a>

#### mathutils.Vector.yzzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.yzzz"></a>

#### mathutils.Vector.yzzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.z"></a>

#### mathutils.Vector.z

Vector Z axis (3D Vectors only).

**Type:**

float

<a id="mathutils.Vector.zw"></a>

#### mathutils.Vector.zw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zww"></a>

#### mathutils.Vector.zww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwww"></a>

#### mathutils.Vector.zwww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwwx"></a>

#### mathutils.Vector.zwwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwwy"></a>

#### mathutils.Vector.zwwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwwz"></a>

#### mathutils.Vector.zwwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwx"></a>

#### mathutils.Vector.zwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwxw"></a>

#### mathutils.Vector.zwxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwxx"></a>

#### mathutils.Vector.zwxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwxy"></a>

#### mathutils.Vector.zwxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwxz"></a>

#### mathutils.Vector.zwxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwy"></a>

#### mathutils.Vector.zwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwyw"></a>

#### mathutils.Vector.zwyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwyx"></a>

#### mathutils.Vector.zwyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwyy"></a>

#### mathutils.Vector.zwyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwyz"></a>

#### mathutils.Vector.zwyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwz"></a>

#### mathutils.Vector.zwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwzw"></a>

#### mathutils.Vector.zwzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwzx"></a>

#### mathutils.Vector.zwzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwzy"></a>

#### mathutils.Vector.zwzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zwzz"></a>

#### mathutils.Vector.zwzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zx"></a>

#### mathutils.Vector.zx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxw"></a>

#### mathutils.Vector.zxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxww"></a>

#### mathutils.Vector.zxww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxwx"></a>

#### mathutils.Vector.zxwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxwy"></a>

#### mathutils.Vector.zxwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxwz"></a>

#### mathutils.Vector.zxwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxx"></a>

#### mathutils.Vector.zxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxxw"></a>

#### mathutils.Vector.zxxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxxx"></a>

#### mathutils.Vector.zxxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxxy"></a>

#### mathutils.Vector.zxxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxxz"></a>

#### mathutils.Vector.zxxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxy"></a>

#### mathutils.Vector.zxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxyw"></a>

#### mathutils.Vector.zxyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxyx"></a>

#### mathutils.Vector.zxyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxyy"></a>

#### mathutils.Vector.zxyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxyz"></a>

#### mathutils.Vector.zxyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxz"></a>

#### mathutils.Vector.zxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxzw"></a>

#### mathutils.Vector.zxzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxzx"></a>

#### mathutils.Vector.zxzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxzy"></a>

#### mathutils.Vector.zxzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zxzz"></a>

#### mathutils.Vector.zxzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zy"></a>

#### mathutils.Vector.zy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyw"></a>

#### mathutils.Vector.zyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyww"></a>

#### mathutils.Vector.zyww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zywx"></a>

#### mathutils.Vector.zywx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zywy"></a>

#### mathutils.Vector.zywy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zywz"></a>

#### mathutils.Vector.zywz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyx"></a>

#### mathutils.Vector.zyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyxw"></a>

#### mathutils.Vector.zyxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyxx"></a>

#### mathutils.Vector.zyxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyxy"></a>

#### mathutils.Vector.zyxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyxz"></a>

#### mathutils.Vector.zyxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyy"></a>

#### mathutils.Vector.zyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyyw"></a>

#### mathutils.Vector.zyyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyyx"></a>

#### mathutils.Vector.zyyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyyy"></a>

#### mathutils.Vector.zyyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyyz"></a>

#### mathutils.Vector.zyyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyz"></a>

#### mathutils.Vector.zyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyzw"></a>

#### mathutils.Vector.zyzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyzx"></a>

#### mathutils.Vector.zyzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyzy"></a>

#### mathutils.Vector.zyzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zyzz"></a>

#### mathutils.Vector.zyzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zz"></a>

#### mathutils.Vector.zz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzw"></a>

#### mathutils.Vector.zzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzww"></a>

#### mathutils.Vector.zzww

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzwx"></a>

#### mathutils.Vector.zzwx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzwy"></a>

#### mathutils.Vector.zzwy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzwz"></a>

#### mathutils.Vector.zzwz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzx"></a>

#### mathutils.Vector.zzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzxw"></a>

#### mathutils.Vector.zzxw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzxx"></a>

#### mathutils.Vector.zzxx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzxy"></a>

#### mathutils.Vector.zzxy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzxz"></a>

#### mathutils.Vector.zzxz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzy"></a>

#### mathutils.Vector.zzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzyw"></a>

#### mathutils.Vector.zzyw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzyx"></a>

#### mathutils.Vector.zzyx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzyy"></a>

#### mathutils.Vector.zzyy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzyz"></a>

#### mathutils.Vector.zzyz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzz"></a>

#### mathutils.Vector.zzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzzw"></a>

#### mathutils.Vector.zzzw

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzzx"></a>

#### mathutils.Vector.zzzx

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzzy"></a>

#### mathutils.Vector.zzzy

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.zzzz"></a>

#### mathutils.Vector.zzzz

**Type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

Special Methods

<a id="mathutils.Vector.__add__"></a>

#### mathutils.Vector.__add__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__eq__"></a>

#### mathutils.Vector.__eq__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Vector.__ge__"></a>

#### mathutils.Vector.__ge__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="mathutils.Vector.__getitem__"></a>

#### mathutils.Vector.__getitem__(key)

**Parameters:**

**key** (int) – Index or key.

**Return type:**

float

<a id="mathutils.Vector.__gt__"></a>

#### mathutils.Vector.__gt__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="mathutils.Vector.__hash__"></a>

#### mathutils.Vector.__hash__()

**Return type:**

int

<a id="mathutils.Vector.__iadd__"></a>

#### mathutils.Vector.__iadd__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__imul__"></a>

#### mathutils.Vector.__imul__(other)

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

#### __imul__(other)

**Parameters:**

**other** (float) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__isub__"></a>

#### mathutils.Vector.__isub__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__itruediv__"></a>

#### mathutils.Vector.__itruediv__(other)

**Parameters:**

**other** (float) – Scalar divisor.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__le__"></a>

#### mathutils.Vector.__le__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="mathutils.Vector.__len__"></a>

#### mathutils.Vector.__len__()

**Return type:**

int

<a id="mathutils.Vector.__lt__"></a>

#### mathutils.Vector.__lt__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

bool

<a id="mathutils.Vector.__matmul__"></a>

#### mathutils.Vector.__matmul__(other)

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – The other operand.

**Return type:**

float

#### __matmul__(other)

**Parameters:**

**other** ([`Matrix`](#mathutils.Matrix "mathutils.Matrix")) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__mul__"></a>

#### mathutils.Vector.__mul__(other)

**Parameters:**

**other** ([`Vector`](#mathutils.Vector "mathutils.Vector")) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

#### __mul__(other)

**Parameters:**

**other** (float) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__ne__"></a>

#### mathutils.Vector.__ne__(other)

**Parameters:**

**other** (object) – The other operand.

**Return type:**

bool

<a id="mathutils.Vector.__neg__"></a>

#### mathutils.Vector.__neg__()

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__pos__"></a>

#### mathutils.Vector.__pos__()

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__repr__"></a>

#### mathutils.Vector.__repr__()

**Return type:**

str

<a id="mathutils.Vector.__rmul__"></a>

#### mathutils.Vector.__rmul__(other)

**Parameters:**

**other** (float) – Scalar.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__setitem__"></a>

#### mathutils.Vector.__setitem__(key, value)

**Parameters:**

- **key** (int) – Index or key.
- **value** (object) – Value to assign.

<a id="mathutils.Vector.__str__"></a>

#### mathutils.Vector.__str__()

**Return type:**

str

<a id="mathutils.Vector.__sub__"></a>

#### mathutils.Vector.__sub__(other)

**Parameters:**

**other** (Self) – The other operand.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")

<a id="mathutils.Vector.__truediv__"></a>

#### mathutils.Vector.__truediv__(other)

**Parameters:**

**other** (float) – Scalar divisor.

**Return type:**

[`Vector`](#mathutils.Vector "mathutils.Vector")
