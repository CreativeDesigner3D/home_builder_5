<!-- source: Blender Python API reference 5.2 / bl_math.html -->

<a id="module-bl_math"></a>

# Additional Math Functions (bl_math)

Miscellaneous math utilities module.

<a id="bl_math.clamp"></a>

### bl_math.clamp(value, min=0, max=1)

Clamps the float value between minimum and maximum. To avoid
confusion, any call must use either one or all three arguments.

**Parameters:**

- **value** (float) – The value to clamp.
- **min** (float) – The minimum value, defaults to 0.
- **max** (float) – The maximum value, defaults to 1.

**Returns:**

The clamped value.

**Return type:**

float

<a id="bl_math.lerp"></a>

### bl_math.lerp(from_value, to_value, factor)

Linearly interpolate between two float values based on factor.

**Parameters:**

- **from_value** (float) – The value to return when factor is 0.
- **to_value** (float) – The value to return when factor is 1.
- **factor** (float) – The interpolation value, normally in [0.0, 1.0].

**Returns:**

The interpolated value.

**Return type:**

float

<a id="bl_math.smoothstep"></a>

### bl_math.smoothstep(from_value, to_value, value)

Performs smooth interpolation between 0 and 1 as value changes between from and to values.
Outside the range the function returns the same value as the nearest edge.

**Parameters:**

- **from_value** (float) – The edge value where the result is 0.
- **to_value** (float) – The edge value where the result is 1.
- **value** (float) – The interpolation value.

**Returns:**

The interpolated value in [0.0, 1.0].

**Return type:**

float
