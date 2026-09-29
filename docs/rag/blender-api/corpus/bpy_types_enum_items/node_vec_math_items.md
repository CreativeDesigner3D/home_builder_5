<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/node_vec_math_items.html -->

<a id="node-vec-math-items"></a>

# Node Vec Math Items

**ADD:**

Add.

A + B.

**SUBTRACT:**

Subtract.

A - B.

**MULTIPLY:**

Multiply.

Entry-wise multiply.

**DIVIDE:**

Divide.

Entry-wise divide.

**MULTIPLY_ADD:**

Multiply Add.

A * B + C.

---

**CROSS_PRODUCT:**

Cross Product.

A cross B.

**PROJECT:**

Project.

Project A onto B.

**REFLECT:**

Reflect.

Reflect A around the normal B. B does not need to be normalized..

**REFRACT:**

Refract.

For a given incident vector A, surface normal B and ratio of indices of refraction, Ior, refract returns the refraction vector, R.

**FACEFORWARD:**

Faceforward.

Orients a vector A to point away from a surface B as defined by its normal C. Returns (dot(B, C) < 0) ? A : -A.

**DOT_PRODUCT:**

Dot Product.

A dot B.

---

**DISTANCE:**

Distance.

Distance between A and B.

**LENGTH:**

Length.

Length of A.

**SCALE:**

Scale.

A multiplied by Scale.

**NORMALIZE:**

Normalize.

Normalize A.

---

**ABSOLUTE:**

Absolute.

Entry-wise absolute.

**POWER:**

Power.

Entry-wise power.

**SIGN:**

Sign.

Entry-wise sign.

**MINIMUM:**

Minimum.

Entry-wise minimum.

**MAXIMUM:**

Maximum.

Entry-wise maximum.

**ROUND:**

Round.

Entry-wise round to the nearest integer. Round upward if the fraction part is 0.5.

**FLOOR:**

Floor.

Entry-wise floor.

**CEIL:**

Ceil.

Entry-wise ceil.

**FRACTION:**

Fraction.

The fraction part of A entry-wise.

**MODULO:**

Modulo.

Entry-wise modulo using fmod(A,B).

**WRAP:**

Wrap.

Entry-wise wrap(A,B).

**SNAP:**

Snap.

Round A to the largest integer multiple of B less than or equal A.

---

**SINE:**

Sine.

Entry-wise sin(A).

**COSINE:**

Cosine.

Entry-wise cos(A).

**TANGENT:**

Tangent.

Entry-wise tan(A).
