<!-- source: Blender Python API reference 5.2 / bpy.types.Macro.html -->

<a id="macro-bpy-struct"></a>

# Macro(bpy_struct)

<a id="example-macro"></a>

## Example Macro

This example creates a simple macro operator that
moves the active object and then rotates it.
It demonstrates:

- Defining a macro operator class.
- Registering it and defining sub-operators.
- Setting property values for each step.

```python
import bpy

class OBJECT_OT_simple_macro(bpy.types.Macro):
    bl_idname = "object.simple_macro"
    bl_label = "Simple Transform Macro"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

def register():
    bpy.utils.register_class(OBJECT_OT_simple_macro)

    # Define steps after registration and set operator values via .properties
    step = OBJECT_OT_simple_macro.define("transform.translate")
    props = step.properties
    props.value = (1.0, 0.0, 0.0)
    props.constraint_axis = (True, False, False)

    step = OBJECT_OT_simple_macro.define("transform.rotate")
    props = step.properties
    props.value = 0.785398  # 45 degrees in radians
    props.orient_axis = 'Z'

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_simple_macro)

if __name__ == "__main__":
    register()

    # To run the macro:
    bpy.ops.object.simple_macro()
```

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Macro"></a>

### class bpy.types.Macro(bpy_struct)

Storage of a macro operator being executed, or registered after execution

<a id="bpy.types.Macro.bl_cursor_pending"></a>

#### bpy.types.Macro.bl_cursor_pending

Cursor to use when waiting for the user to select a location to activate the operator (when `bl_options` has `DEPENDS_ON_CURSOR` set) (default `'DEFAULT'`)

**Type:**

Literal[[Window Cursor Items](bpy_types_enum_items/window_cursor_items.md#rna-enum-window-cursor-items)]

<a id="bpy.types.Macro.bl_description"></a>

#### bpy.types.Macro.bl_description

(default “”, never None)

**Type:**

str

<a id="bpy.types.Macro.bl_idname"></a>

#### bpy.types.Macro.bl_idname

(default “”, never None)

**Type:**

str

<a id="bpy.types.Macro.bl_label"></a>

#### bpy.types.Macro.bl_label

(default “”, never None)

**Type:**

str

<a id="bpy.types.Macro.bl_options"></a>

#### bpy.types.Macro.bl_options

Options for this operator type (default set())

**Type:**

set[Literal[[Operator Type Flag Items](bpy_types_enum_items/operator_type_flag_items.md#rna-enum-operator-type-flag-items)]]

<a id="bpy.types.Macro.bl_translation_context"></a>

#### bpy.types.Macro.bl_translation_context

(default “Operator”, never None)

**Type:**

str

<a id="bpy.types.Macro.bl_undo_group"></a>

#### bpy.types.Macro.bl_undo_group

(default “”, never None)

**Type:**

str

<a id="bpy.types.Macro.has_reports"></a>

#### bpy.types.Macro.has_reports

Operator has a set of reports (warnings and errors) from last execution (default False, readonly)

**Type:**

bool

<a id="bpy.types.Macro.name"></a>

#### bpy.types.Macro.name

(default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.Macro.properties"></a>

#### bpy.types.Macro.properties

(readonly, never None)

**Type:**

[`OperatorProperties`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties "bpy.types.OperatorProperties")

<a id="bpy.types.Macro.report"></a>

#### bpy.types.Macro.report(type, message)

report

**Parameters:**

- **type** (set[Literal[[Wm Report Items](bpy_types_enum_items/wm_report_items.md#rna-enum-wm-report-items)]]) – Type
- **message** (str) – Report Message, (never None)

<a id="bpy.types.Macro.poll"></a>

#### classmethod bpy.types.Macro.poll(context)

Test if the operator can be called or not

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

**Return type:**

bool

<a id="bpy.types.Macro.draw"></a>

#### bpy.types.Macro.draw(context)

Draw function for the operator

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.Macro.define"></a>

#### classmethod bpy.types.Macro.define(operator)

Append an operator to a registered macro class.

**Parameters:**

**operator** (str) – Identifier of the operator. This does not have to be defined when this function is called.

**Returns:**

The operator macro for property access.

**Return type:**

[`OperatorMacro`](bpy.types.OperatorMacro.md#bpy.types.OperatorMacro "bpy.types.OperatorMacro")

<a id="bpy.types.Macro.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Macro.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Macro.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Macro.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

### Inherited Properties

bpy_struct.id_data

<a id="inherited-functions"></a>

### Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - [`Operator.macros`](bpy.types.Operator.md#bpy.types.Operator.macros "bpy.types.Operator.macros") |  |
