<!-- source: Blender Python API reference 5.2 / bpy.types.AddonPreferences.html -->

<a id="addonpreferences-bpy-struct"></a>

# AddonPreferences(bpy_struct)

```python
bl_info = {
    "name": "Example Add-on Preferences",
    "author": "Your Name Here",
    "version": (1, 0),
    "blender": (2, 65, 0),
    "location": "SpaceBar Search -> Add-on Preferences Example",
    "description": "Example Add-on",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Object",
}

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty

class ExampleAddonPreferences(AddonPreferences):
    # This must match the add-on name, use `__package__`
    # when defining this for add-on extensions or a sub-module of a Python package.
    bl_idname = __name__

    filepath: StringProperty(
        name="Example File Path",
        subtype='FILE_PATH',
    )
    number: IntProperty(
        name="Example Number",
        default=4,
    )
    boolean: BoolProperty(
        name="Example Boolean",
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our add-on")
        layout.prop(self, "filepath")
        layout.prop(self, "number")
        layout.prop(self, "boolean")

class OBJECT_OT_addon_prefs_example(Operator):
    """Display example preferences"""
    bl_idname = "object.addon_prefs_example"
    bl_label = "Add-on Preferences Example"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        info = "Path: {:s}, Number: {:d}, Boolean {!r}".format(
            addon_prefs.filepath, addon_prefs.number, addon_prefs.boolean,
        )
        self.report({'INFO'}, info)
        print(info)

        return {'FINISHED'}

# Registration
def register():
    bpy.utils.register_class(OBJECT_OT_addon_prefs_example)
    bpy.utils.register_class(ExampleAddonPreferences)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_addon_prefs_example)
    bpy.utils.unregister_class(ExampleAddonPreferences)
```

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.AddonPreferences"></a>

### class bpy.types.AddonPreferences(bpy_struct)

<a id="bpy.types.AddonPreferences.bl_idname"></a>

#### bpy.types.AddonPreferences.bl_idname

(default “”, never None)

**Type:**

str

<a id="bpy.types.AddonPreferences.bl_system_properties_get"></a>

#### bpy.types.AddonPreferences.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](bpy.types.PropertyGroup.md#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.AddonPreferences.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AddonPreferences.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AddonPreferences.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AddonPreferences.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

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
| - [`Addon.preferences`](bpy.types.Addon.md#bpy.types.Addon.preferences "bpy.types.Addon.preferences") |  |
