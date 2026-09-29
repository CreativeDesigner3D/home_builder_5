<!-- source: Blender Python API reference 5.2 / bpy.types.Menu.html -->

<a id="menu-bpy-struct"></a>

# Menu(bpy_struct)

<a id="basic-menu-example"></a>

## Basic Menu Example

Here is an example of a simple menu. Menus differ from panels in that they must
reference from a header, panel or another menu.

Notice the ‘CATEGORY_MT_name’ in [`Menu.bl_idname`](#bpy.types.Menu.bl_idname "bpy.types.Menu.bl_idname"), this is a naming
convention for menus.

> **Note:**
>
> Menu subclasses must be registered before referencing them from Blender.

> **Note:**
>
> Menus have their [`UILayout.operator_context`](bpy.types.UILayout.md#bpy.types.UILayout.operator_context "bpy.types.UILayout.operator_context") initialized as
> ‘EXEC_REGION_WIN’ rather than ‘INVOKE_REGION_WIN’ (see [Execution Context](bpy_types_enum_items/operator_context_items.md#rna-enum-operator-context-items)).
> If the operator context needs to initialize inputs from the
> [`Operator.invoke`](bpy.types.Operator.md#bpy.types.Operator.invoke "bpy.types.Operator.invoke") function, then this needs to be explicitly set.
> When a menu is added to UI elements such as a panel or header,
> the operator execution context will be inherited from them.

```python
import bpy

class BasicMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_select_test"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")

bpy.utils.register_class(BasicMenu)

# Test call to display immediately.
bpy.ops.wm.call_menu(name="OBJECT_MT_select_test")
```

<a id="submenus"></a>

## Submenus

This menu demonstrates some different functions.

```python
import bpy

class SubMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_select_submenu"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")

        # Access this operator as a sub-menu.
        layout.operator_menu_enum("object.select_by_type", "type", text="Select All by Type")

        layout.separator()

        # Expand each operator option into this menu.
        layout.operator_enum("object.light_add", "type")

        layout.separator()

        # Use existing menu.
        layout.menu("VIEW3D_MT_transform")

bpy.utils.register_class(SubMenu)

# Test call to display immediately.
bpy.ops.wm.call_menu(name="OBJECT_MT_select_submenu")
```

<a id="extending-menus"></a>

## Extending Menus

When creating menus for add-ons you can’t reference menus
in Blender’s default scripts.
Instead, the add-on can add menu items to existing menus.

The function menu_draw acts like [`Menu.draw`](#bpy.types.Menu.draw "bpy.types.Menu.draw").

```python
import bpy

def menu_draw(self, context):
    self.layout.operator("wm.save_homefile")

bpy.types.TOPBAR_MT_file.append(menu_draw)
```

<a id="preset-menus"></a>

## Preset Menus

Preset menus are simply a convention that uses a menu sub-class
to perform the common task of managing presets.

This example shows how you can add a preset menu.

This example uses the object display options,
however you can use properties defined by your own scripts too.

```python
import bpy
from bpy.types import Operator, Menu
from bl_operators.presets import AddPresetBase

class OBJECT_MT_display_presets(Menu):
    bl_label = "Object Display Presets"
    preset_subdir = "object/display"
    preset_operator = "script.execute_preset"
    draw = Menu.draw_preset

class AddPresetObjectDisplay(AddPresetBase, Operator):
    '''Add a Object Display Preset'''
    bl_idname = "camera.object_display_preset_add"
    bl_label = "Add Object Display Preset"
    preset_menu = "OBJECT_MT_display_presets"

    # Variable used for all preset values.
    preset_defines = [
        "obj = bpy.context.object"
    ]

    # Properties to store in the preset.
    preset_values = [
        "obj.display_type",
        "obj.show_bounds",
        "obj.display_bounds_type",
        "obj.show_name",
        "obj.show_axis",
        "obj.show_wire",
    ]

    # Where to store the preset.
    preset_subdir = "object/display"

# Display into an existing panel.
def panel_func(self, context):
    layout = self.layout

    row = layout.row(align=True)
    row.menu(OBJECT_MT_display_presets.__name__, text=OBJECT_MT_display_presets.bl_label)
    row.operator(AddPresetObjectDisplay.bl_idname, text="", icon='ZOOM_IN')
    row.operator(AddPresetObjectDisplay.bl_idname, text="", icon='ZOOM_OUT').remove_active = True

classes = (
    OBJECT_MT_display_presets,
    AddPresetObjectDisplay,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.OBJECT_PT_display.prepend(panel_func)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.OBJECT_PT_display.remove(panel_func)

if __name__ == "__main__":
    register()
```

<a id="extending-the-button-context-menu"></a>

## Extending the Button Context Menu

This example enables you to insert your own menu entry into the common
right click menu that you get while hovering over a UI button (e.g. operator,
value field, color, string, etc.)

To make the example work, you have to first select an object
then right click on an user interface element (maybe a color in the
material properties) and choose *Execute Custom Action*.

Executing the operator will then print all values.

```python
import bpy

def dump(obj, text):
    for attr in dir(obj):
        print("{!r}.{:s} = {!s}".format(obj, attr, getattr(obj, attr)))

class WM_OT_button_context_test(bpy.types.Operator):
    """Right click entry test"""
    bl_idname = "wm.button_context_test"
    bl_label = "Run Context Test"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        value = getattr(context, "button_pointer", None)
        if value is not None:
            dump(value, "button_pointer")

        value = getattr(context, "button_prop", None)
        if value is not None:
            dump(value, "button_prop")

        value = getattr(context, "button_operator", None)
        if value is not None:
            dump(value, "button_operator")

        return {'FINISHED'}

def draw_menu(self, context):
    layout = self.layout
    layout.separator()
    layout.operator(WM_OT_button_context_test.bl_idname)

def register():
    bpy.utils.register_class(WM_OT_button_context_test)
    bpy.types.UI_MT_button_context_menu.append(draw_menu)

def unregister():
    bpy.types.UI_MT_button_context_menu.remove(draw_menu)
    bpy.utils.unregister_class(WM_OT_button_context_test)

if __name__ == "__main__":
    register()
```

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Menu"></a>

### class bpy.types.Menu(bpy_struct)

Editor menu containing buttons

<a id="bpy.types.Menu.bl_description"></a>

#### bpy.types.Menu.bl_description

(default “”)

**Type:**

str

<a id="bpy.types.Menu.bl_idname"></a>

#### bpy.types.Menu.bl_idname

If this is set, the menu gets a custom ID, otherwise it takes the name of the class used to define the menu (for example, if the class name is “OBJECT_MT_hello”, and bl_idname is not set by the script, then bl_idname = “OBJECT_MT_hello”) (default “”, never None)

**Type:**

str

<a id="bpy.types.Menu.bl_label"></a>

#### bpy.types.Menu.bl_label

The menu label (default “”, never None)

**Type:**

str

<a id="bpy.types.Menu.bl_options"></a>

#### bpy.types.Menu.bl_options

Options for this menu type (default set())

- `SEARCH_ON_KEY_PRESS`
  Search on Key Press – Open a menu search when a key pressed while the menu is open.

**Type:**

set[Literal[‘SEARCH_ON_KEY_PRESS’]]

<a id="bpy.types.Menu.bl_owner_id"></a>

#### bpy.types.Menu.bl_owner_id

(default “”, never None)

**Type:**

str

<a id="bpy.types.Menu.bl_translation_context"></a>

#### bpy.types.Menu.bl_translation_context

(default “*”, never None)

**Type:**

str

<a id="bpy.types.Menu.layout"></a>

#### bpy.types.Menu.layout

Defines the structure of the menu in the UI (readonly)

**Type:**

[`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None

<a id="bpy.types.Menu.poll"></a>

#### classmethod bpy.types.Menu.poll(context)

If this method returns a non-null output, then the menu can be drawn

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context

**Return type:**

bool

<a id="bpy.types.Menu.draw"></a>

#### bpy.types.Menu.draw(context)

Draw UI elements into the menu UI layout

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context

<a id="bpy.types.Menu.append"></a>

#### classmethod bpy.types.Menu.append(draw_func)

Append a draw function to this menu,
takes the same arguments as the menus draw function

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function to append.

<a id="bpy.types.Menu.draw_collapsible"></a>

#### classmethod bpy.types.Menu.draw_collapsible(context, layout)

Draw the menu inline when the header shows menus, otherwise draw it
as a collapsed icon. Intended for use within header draw functions.

**Parameters:**

- **context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **layout** ([`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout")) – The layout to draw into.

<a id="bpy.types.Menu.draw_preset"></a>

#### bpy.types.Menu.draw_preset(context)

Define these on the subclass:
- preset_operator (string)
- preset_subdir (string)

Optionally:
- preset_add_operator (string)
- preset_extensions (set of strings)
- preset_operator_defaults (dict of keyword args)

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

<a id="bpy.types.Menu.is_extended"></a>

#### classmethod bpy.types.Menu.is_extended()

Test if any draw function has been added via [`append()`](#bpy.types.Menu.append "bpy.types.Menu.append") or [`prepend()`](#bpy.types.Menu.prepend "bpy.types.Menu.prepend").

**Returns:**

True when at least one draw function has been added.

**Return type:**

bool

<a id="bpy.types.Menu.path_menu"></a>

#### bpy.types.Menu.path_menu(searchpaths, operator, *, props_default=None, prop_filepath='filepath', filter_ext=None, filter_path=None, display_name=None, add_operator=None, add_operator_props=None, translate=True, recursive_paths=False)

Populate a menu from a list of paths.

**Parameters:**

- **searchpaths** (Sequence[str]) – Paths to scan.
- **operator** (str) – The operator id to use with each file.
- **prop_filepath** (str) – Optional operator filepath property (defaults to “filepath”).
- **props_default** (dict[str, Any] | None) – Properties to assign to each operator.
- **filter_ext** (Callable[[str], bool] | None) –

  Optional callback that takes the file extensions.

  Returning false excludes the file from the list.
- **filter_path** (Callable[[str], bool] | None) – Optional callback that takes the file name, returns false to exclude it.
- **display_name** (Callable[[str], str] | None) – Optional callback that takes the full path, returns the name to display.
- **add_operator** (str | None) – Optional operator id used to add or remove entries.
- **add_operator_props** (dict[str, Any] | None) – Properties to assign to the add/remove operator.
- **translate** (bool) – Translate the displayed names.
- **recursive_paths** (bool) – Add submenus for sub-directories instead of listing their contents.

<a id="bpy.types.Menu.prepend"></a>

#### classmethod bpy.types.Menu.prepend(draw_func)

Prepend a draw function to this menu, takes the same arguments as
the menus draw function

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function to prepend.

<a id="bpy.types.Menu.remove"></a>

#### classmethod bpy.types.Menu.remove(draw_func)

Remove a draw function that has been added to this menu.

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function previously registered via [`append()`](#bpy.types.Menu.append "bpy.types.Menu.append") or [`prepend()`](#bpy.types.Menu.prepend "bpy.types.Menu.prepend").

<a id="bpy.types.Menu.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Menu.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Menu.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Menu.bl_rna_get_subclass_py(id, default=None, /)

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
