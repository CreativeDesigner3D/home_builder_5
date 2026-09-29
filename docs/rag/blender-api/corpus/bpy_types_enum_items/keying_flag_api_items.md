<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/keying_flag_api_items.html -->

<a id="keying-flag-api-items"></a>

# Keying Flag Api Items

**INSERTKEY_NEEDED:**

Only Needed.

Only insert keyframes where they’re needed in the relevant F-Curves.

**INSERTKEY_VISUAL:**

Visual Keying.

Insert keyframes based on ‘visual transforms’.

**INSERTKEY_REPLACE:**

Replace Existing.

Only replace existing keyframes.

**INSERTKEY_AVAILABLE:**

Only Available.

Don’t create F-Curves when they don’t already exist.

**INSERTKEY_CYCLE_AWARE:**

Cycle Aware Keying.

When inserting into a curve with cyclic extrapolation, remap the keyframe inside the cycle time range, and if changing an end key, also update the other one.
