<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/property_flag_enum_items.html -->

<a id="property-flag-enum-items"></a>

# Property Flag Enum Items

**READ_ONLY:**

Read Only.

When set, the property cannot be edited.

**HIDDEN:**

Hidden.

For operators: hide from places in the user interface where Blender would add the property automatically, like Adjust Last Operation. Also this property is not written to presets..

**SKIP_SAVE:**

Skip Save.

For operators: the value of this property will not be remembered between invocations of the operator; instead, each invocation will start by using the default value. Also this property is not written to presets..

**ANIMATABLE:**

Animatable.

**LIBRARY_EDITABLE:**

Library Editable.

This property can be edited, even when it is used on linked data (which normally is read-only). Note that edits to the property will not be saved to the blend file..

**ENUM_FLAG:**

Enum Flag.
