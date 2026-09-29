<!-- source: Blender Python API reference 5.2 / bpy.types.Panel.html -->

<a id="panel-bpy-struct"></a>

# Panel(bpy_struct)

<a id="basic-panel-example"></a>

## Basic Panel Example

This script is a simple panel which will draw into the object properties
section.

Notice the ‘CATEGORY_PT_name’ [`Panel.bl_idname`](#bpy.types.Panel.bl_idname "bpy.types.Panel.bl_idname"), this is a naming
convention for panels.

> **Note:**
>
> Panel subclasses must be registered for Blender to use them.

```python
import bpy

class HelloWorldPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_hello_world"
    bl_label = "Hello World"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        self.layout.label(text="Hello World")

bpy.utils.register_class(HelloWorldPanel)
```

<a id="simple-object-panel"></a>

## Simple Object Panel

This panel has a [`Panel.poll`](#bpy.types.Panel.poll "bpy.types.Panel.poll") and [`Panel.draw_header`](#bpy.types.Panel.draw_header "bpy.types.Panel.draw_header") function,
even though the contents is basic this closely resembles blenders panels.

```python
import bpy

class ObjectSelectPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_select"
    bl_label = "Select"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="My Select Panel")

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Selection Tools")
        box.operator("object.select_all").action = 'TOGGLE'
        row = box.row()
        row.operator("object.select_all").action = 'INVERT'
        row.operator("object.select_random")

bpy.utils.register_class(ObjectSelectPanel)
```

<a id="mix-in-classes"></a>

## Mix-in Classes

A mix-in parent class can be used to share common properties and
[`Menu.poll`](bpy.types.Menu.md#bpy.types.Menu.poll "bpy.types.Menu.poll") function.

```python
import bpy

class View3DPanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"

    @classmethod
    def poll(cls, context):
        return (context.object is not None)

class PanelOne(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_1"
    bl_label = "Panel One"

    def draw(self, context):
        self.layout.label(text="Small Class")

class PanelTwo(View3DPanel, bpy.types.Panel):
    bl_idname = "VIEW3D_PT_test_2"
    bl_label = "Panel Two"

    def draw(self, context):
        self.layout.label(text="Also Small Class")

bpy.utils.register_class(PanelOne)
bpy.utils.register_class(PanelTwo)
```

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Panel"></a>

### class bpy.types.Panel(bpy_struct)

Panel containing UI elements

<a id="bpy.types.Panel.bl_category"></a>

#### bpy.types.Panel.bl_category

The category (tab) in which the panel will be displayed, when applicable (default “”, never None)

**Type:**

str

<a id="bpy.types.Panel.bl_context"></a>

#### bpy.types.Panel.bl_context

The context in which the panel belongs to. (TODO: explain the possible combinations bl_context/bl_region_type/bl_space_type) (default “”, never None)

**Type:**

str

<a id="bpy.types.Panel.bl_description"></a>

#### bpy.types.Panel.bl_description

The panel tooltip (default “”)

**Type:**

str

<a id="bpy.types.Panel.bl_icon"></a>

#### bpy.types.Panel.bl_icon

Icon override for the panel category tab (default `'NONE'`)

**Type:**

Literal[[Icon Items](bpy_types_enum_items/icon_items.md#rna-enum-icon-items)]

<a id="bpy.types.Panel.bl_icon_value"></a>

#### bpy.types.Panel.bl_icon_value

Icon value override for the panel category tab (in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.Panel.bl_idname"></a>

#### bpy.types.Panel.bl_idname

If this is set, the panel gets a custom ID, otherwise it takes the name of the class used to define the panel. For example, if the class name is “OBJECT_PT_hello”, and bl_idname is not set by the script, then bl_idname = “OBJECT_PT_hello”. (default “”, never None)

**Type:**

str

<a id="bpy.types.Panel.bl_label"></a>

#### bpy.types.Panel.bl_label

The panel label, shows up in the panel header at the right of the triangle used to collapse the panel (default “”, never None)

**Type:**

str

<a id="bpy.types.Panel.bl_options"></a>

#### bpy.types.Panel.bl_options

Options for this panel type (default set())

- `DEFAULT_CLOSED`
  Default Closed – Defines if the panel has to be open or collapsed at the time of its creation.
- `HIDE_HEADER`
  Hide Header – If set to False, the panel shows a header, which contains a clickable arrow to collapse the panel and the label (see bl_label).
- `INSTANCED`
  Instanced Panel – Multiple panels with this type can be used as part of a list depending on data external to the UI. Used to create panels for the modifiers and other stacks..
- `HEADER_LAYOUT_EXPAND`
  Expand Header Layout – Allow buttons in the header to stretch and shrink to fill the entire layout width.

**Type:**

set[Literal[‘DEFAULT_CLOSED’, ‘HIDE_HEADER’, ‘INSTANCED’, ‘HEADER_LAYOUT_EXPAND’]]

<a id="bpy.types.Panel.bl_order"></a>

#### bpy.types.Panel.bl_order

Panels with lower numbers are default ordered before panels with higher numbers (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.Panel.bl_owner_id"></a>

#### bpy.types.Panel.bl_owner_id

The ID owning the data displayed in the panel, if any (default “”, never None)

**Type:**

str

<a id="bpy.types.Panel.bl_parent_id"></a>

#### bpy.types.Panel.bl_parent_id

If this is set, the panel becomes a sub-panel (default “”, never None)

**Type:**

str

<a id="bpy.types.Panel.bl_region_type"></a>

#### bpy.types.Panel.bl_region_type

The region where the panel is going to be used in (default `'WINDOW'`)

**Type:**

Literal[[Region Type Items](bpy_types_enum_items/region_type_items.md#rna-enum-region-type-items)]

<a id="bpy.types.Panel.bl_space_type"></a>

#### bpy.types.Panel.bl_space_type

The space where the panel is going to be used in (default `'EMPTY'`)

**Type:**

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]

<a id="bpy.types.Panel.bl_translation_context"></a>

#### bpy.types.Panel.bl_translation_context

Specific translation context, only define when the label needs to be disambiguated from others using the exact same label (default “*”, never None)

**Type:**

str

<a id="bpy.types.Panel.bl_ui_units_x"></a>

#### bpy.types.Panel.bl_ui_units_x

When set, defines popup panel width (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.Panel.custom_data"></a>

#### bpy.types.Panel.custom_data

Panel data (readonly)

**Type:**

[`Constraint`](bpy.types.Constraint.md#bpy.types.Constraint "bpy.types.Constraint") | None

<a id="bpy.types.Panel.is_popover"></a>

#### bpy.types.Panel.is_popover

(default False, readonly)

**Type:**

bool

<a id="bpy.types.Panel.layout"></a>

#### bpy.types.Panel.layout

Defines the structure of the panel in the UI (readonly)

**Type:**

[`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None

<a id="bpy.types.Panel.text"></a>

#### bpy.types.Panel.text

Override for the panel label in the UI (default “”, never None)

**Type:**

str

<a id="bpy.types.Panel.use_pin"></a>

#### bpy.types.Panel.use_pin

Show the panel on all tabs (default False)

**Type:**

bool

<a id="bpy.types.Panel.poll"></a>

#### classmethod bpy.types.Panel.poll(context)

If this method returns a non-null output, then the panel can be drawn

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

**Return type:**

bool

<a id="bpy.types.Panel.draw"></a>

#### bpy.types.Panel.draw(context)

Draw UI elements into the panel UI layout

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.Panel.draw_header"></a>

#### bpy.types.Panel.draw_header(context)

Draw UI elements into the panel’s header UI layout

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.Panel.draw_header_preset"></a>

#### bpy.types.Panel.draw_header_preset(context)

Draw UI elements for presets in the panel’s header

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – (never None)

<a id="bpy.types.Panel.append"></a>

#### classmethod bpy.types.Panel.append(draw_func)

Append a draw function to this menu,
takes the same arguments as the menus draw function

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function to append.

<a id="bpy.types.Panel.is_extended"></a>

#### classmethod bpy.types.Panel.is_extended()

Test if any draw function has been added via [`append()`](#bpy.types.Panel.append "bpy.types.Panel.append") or [`prepend()`](#bpy.types.Panel.prepend "bpy.types.Panel.prepend").

**Returns:**

True when at least one draw function has been added.

**Return type:**

bool

<a id="bpy.types.Panel.prepend"></a>

#### classmethod bpy.types.Panel.prepend(draw_func)

Prepend a draw function to this menu, takes the same arguments as
the menus draw function

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function to prepend.

<a id="bpy.types.Panel.remove"></a>

#### classmethod bpy.types.Panel.remove(draw_func)

Remove a draw function that has been added to this menu.

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function previously registered via [`append()`](#bpy.types.Panel.append "bpy.types.Panel.append") or [`prepend()`](#bpy.types.Panel.prepend "bpy.types.Panel.prepend").

<a id="bpy.types.Panel.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Panel.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Panel.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Panel.bl_rna_get_subclass_py(id, default=None, /)

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
