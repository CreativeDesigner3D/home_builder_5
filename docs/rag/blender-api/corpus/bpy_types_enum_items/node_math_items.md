<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/node_math_items.html -->

<a id="node-math-items"></a>

# Node Math Items

**Functions**

**ADD:**

Add.

A + B.

**SUBTRACT:**

Subtract.

A - B.

**MULTIPLY:**

Multiply.

A * B.

**DIVIDE:**

Divide.

A / B.

**MULTIPLY_ADD:**

Multiply Add.

A * B + C.

---

**POWER:**

Power.

A power B.

**LOGARITHM:**

Logarithm.

Logarithm A base B.

**SQRT:**

Square Root.

Square root of A.

**INVERSE_SQRT:**

Inverse Square Root.

1 / Square root of A.

**ABSOLUTE:**

Absolute.

Magnitude of A.

**EXPONENT:**

Exponent.

exp(A).

**Comparison**

**MINIMUM:**

Minimum.

The minimum from A and B.

**MAXIMUM:**

Maximum.

The maximum from A and B.

**LESS_THAN:**

Less Than.

1 if A < B else 0.

**GREATER_THAN:**

Greater Than.

1 if A > B else 0.

**SIGN:**

Sign.

Returns the sign of A.

**COMPARE:**

Compare.

1 if (A == B) within tolerance C else 0.

**SMOOTH_MIN:**

Smooth Minimum.

The minimum from A and B with smoothing C.

**SMOOTH_MAX:**

Smooth Maximum.

The maximum from A and B with smoothing C.

**Rounding**

**ROUND:**

Round.

Round A to the nearest integer. Round upward if the fraction part is 0.5.

**FLOOR:**

Floor.

The largest integer smaller than or equal A.

**CEIL:**

Ceil.

The smallest integer greater than or equal A.

**TRUNC:**

Truncate.

The integer part of A, removing fractional digits.

---

**FRACT:**

Fraction.

The fraction part of A.

**MODULO:**

Truncated Modulo.

The remainder of truncated division using fmod(A,B).

**FLOORED_MODULO:**

Floored Modulo.

The remainder of floored division.

**WRAP:**

Wrap.

Wrap value to range, wrap(A,B).

**SNAP:**

Snap.

Snap to increment, snap(A,B).

**PINGPONG:**

Ping-Pong.

Wraps a value and reverses every other cycle (A,B).

**Trigonometric**

**SINE:**

Sine.

sin(A).

**COSINE:**

Cosine.

cos(A).

**TANGENT:**

Tangent.

tan(A).

---

**ARCSINE:**

Arcsine.

arcsin(A).

**ARCCOSINE:**

Arccosine.

arccos(A).

**ARCTANGENT:**

Arctangent.

arctan(A).

**ARCTAN2:**

Arctan2.

The signed angle arctan(A / B).

---

**SINH:**

Hyperbolic Sine.

sinh(A).

**COSH:**

Hyperbolic Cosine.

cosh(A).

**TANH:**

Hyperbolic Tangent.

tanh(A).

**Conversion**

**RADIANS:**

To Radians.

Convert from degrees to radians.

**DEGREES:**

To Degrees.

Convert from radians to degrees.
