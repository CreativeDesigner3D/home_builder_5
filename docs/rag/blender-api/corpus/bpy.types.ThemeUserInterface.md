<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeUserInterface.html -->

<a id="themeuserinterface-bpy-struct"></a>

# ThemeUserInterface(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeUserInterface"></a>

### class bpy.types.ThemeUserInterface(bpy_struct)

Theme settings for user interface elements

<a id="bpy.types.ThemeUserInterface.axis_w"></a>

#### bpy.types.ThemeUserInterface.axis_w

W-axis for quaternion and axis-angle rotations (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.axis_x"></a>

#### bpy.types.ThemeUserInterface.axis_x

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.axis_y"></a>

#### bpy.types.ThemeUserInterface.axis_y

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.axis_z"></a>

#### bpy.types.ThemeUserInterface.axis_z

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.editor_border"></a>

#### bpy.types.ThemeUserInterface.editor_border

Color of the border between editors (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.editor_outline"></a>

#### bpy.types.ThemeUserInterface.editor_outline

Color of the outline of each editor, except the active one (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.editor_outline_active"></a>

#### bpy.types.ThemeUserInterface.editor_outline_active

Color of the outline of the active editor (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.gizmo_a"></a>

#### bpy.types.ThemeUserInterface.gizmo_a

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.gizmo_b"></a>

#### bpy.types.ThemeUserInterface.gizmo_b

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.gizmo_hi"></a>

#### bpy.types.ThemeUserInterface.gizmo_hi

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.gizmo_primary"></a>

#### bpy.types.ThemeUserInterface.gizmo_primary

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.gizmo_secondary"></a>

#### bpy.types.ThemeUserInterface.gizmo_secondary

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.gizmo_view_align"></a>

#### bpy.types.ThemeUserInterface.gizmo_view_align

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.icon_alpha"></a>

#### bpy.types.ThemeUserInterface.icon_alpha

Transparency of icons in the interface, to reduce contrast (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ThemeUserInterface.icon_autokey"></a>

#### bpy.types.ThemeUserInterface.icon_autokey

Color of Auto Keying indicator when enabled (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.icon_border_intensity"></a>

#### bpy.types.ThemeUserInterface.icon_border_intensity

Control the intensity of the border around themes icons (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ThemeUserInterface.icon_collection"></a>

#### bpy.types.ThemeUserInterface.icon_collection

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.icon_folder"></a>

#### bpy.types.ThemeUserInterface.icon_folder

Color of folders in the file browser (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.icon_modifier"></a>

#### bpy.types.ThemeUserInterface.icon_modifier

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.icon_object"></a>

#### bpy.types.ThemeUserInterface.icon_object

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.icon_object_data"></a>

#### bpy.types.ThemeUserInterface.icon_object_data

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.icon_saturation"></a>

#### bpy.types.ThemeUserInterface.icon_saturation

Saturation of icons in the interface (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ThemeUserInterface.icon_scene"></a>

#### bpy.types.ThemeUserInterface.icon_scene

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.icon_shading"></a>

#### bpy.types.ThemeUserInterface.icon_shading

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.link"></a>

#### bpy.types.ThemeUserInterface.link

Color of link widgets (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.menu_shadow_fac"></a>

#### bpy.types.ThemeUserInterface.menu_shadow_fac

Blending factor for panel and menu shadows (in [0.01, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ThemeUserInterface.menu_shadow_width"></a>

#### bpy.types.ThemeUserInterface.menu_shadow_width

Width of panel and menu shadows, set to zero to disable (in [0, 24], default 0)

**Type:**

int

<a id="bpy.types.ThemeUserInterface.panel_active"></a>

#### bpy.types.ThemeUserInterface.panel_active

Color of the outline of top-level panels that are active (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.panel_back"></a>

#### bpy.types.ThemeUserInterface.panel_back

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.panel_header"></a>

#### bpy.types.ThemeUserInterface.panel_header

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.panel_outline"></a>

#### bpy.types.ThemeUserInterface.panel_outline

Color of the outline of top-level panels (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.panel_roundness"></a>

#### bpy.types.ThemeUserInterface.panel_roundness

Roundness of the corners of panels and sub-panels (in [0, 1], default 0.4)

**Type:**

float

<a id="bpy.types.ThemeUserInterface.panel_sub_back"></a>

#### bpy.types.ThemeUserInterface.panel_sub_back

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.panel_text"></a>

#### bpy.types.ThemeUserInterface.panel_text

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.panel_title"></a>

#### bpy.types.ThemeUserInterface.panel_title

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.transparent_checker_primary"></a>

#### bpy.types.ThemeUserInterface.transparent_checker_primary

Primary color of checkerboard pattern indicating transparent areas (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.transparent_checker_secondary"></a>

#### bpy.types.ThemeUserInterface.transparent_checker_secondary

Secondary color of checkerboard pattern indicating transparent areas (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.transparent_checker_size"></a>

#### bpy.types.ThemeUserInterface.transparent_checker_size

Size of checkerboard pattern indicating transparent areas (in [2, 48], default 0)

**Type:**

int

<a id="bpy.types.ThemeUserInterface.wcol_box"></a>

#### bpy.types.ThemeUserInterface.wcol_box

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_curve"></a>

#### bpy.types.ThemeUserInterface.wcol_curve

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_list_item"></a>

#### bpy.types.ThemeUserInterface.wcol_list_item

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_menu"></a>

#### bpy.types.ThemeUserInterface.wcol_menu

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_menu_back"></a>

#### bpy.types.ThemeUserInterface.wcol_menu_back

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_menu_item"></a>

#### bpy.types.ThemeUserInterface.wcol_menu_item

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_num"></a>

#### bpy.types.ThemeUserInterface.wcol_num

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_numslider"></a>

#### bpy.types.ThemeUserInterface.wcol_numslider

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_option"></a>

#### bpy.types.ThemeUserInterface.wcol_option

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_pie_menu"></a>

#### bpy.types.ThemeUserInterface.wcol_pie_menu

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_progress"></a>

#### bpy.types.ThemeUserInterface.wcol_progress

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_pulldown"></a>

#### bpy.types.ThemeUserInterface.wcol_pulldown

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_radio"></a>

#### bpy.types.ThemeUserInterface.wcol_radio

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_regular"></a>

#### bpy.types.ThemeUserInterface.wcol_regular

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_scroll"></a>

#### bpy.types.ThemeUserInterface.wcol_scroll

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_state"></a>

#### bpy.types.ThemeUserInterface.wcol_state

(readonly, never None)

**Type:**

[`ThemeWidgetStateColors`](bpy.types.ThemeWidgetStateColors.md#bpy.types.ThemeWidgetStateColors "bpy.types.ThemeWidgetStateColors")

<a id="bpy.types.ThemeUserInterface.wcol_tab"></a>

#### bpy.types.ThemeUserInterface.wcol_tab

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_text"></a>

#### bpy.types.ThemeUserInterface.wcol_text

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_toggle"></a>

#### bpy.types.ThemeUserInterface.wcol_toggle

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_tool"></a>

#### bpy.types.ThemeUserInterface.wcol_tool

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_toolbar_item"></a>

#### bpy.types.ThemeUserInterface.wcol_toolbar_item

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.wcol_tooltip"></a>

#### bpy.types.ThemeUserInterface.wcol_tooltip

(readonly, never None)

**Type:**

[`ThemeWidgetColors`](bpy.types.ThemeWidgetColors.md#bpy.types.ThemeWidgetColors "bpy.types.ThemeWidgetColors")

<a id="bpy.types.ThemeUserInterface.widget_emboss"></a>

#### bpy.types.ThemeUserInterface.widget_emboss

Color of the 1px shadow line underlying widgets (array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeUserInterface.widget_text_cursor"></a>

#### bpy.types.ThemeUserInterface.widget_text_cursor

Color of the text insertion cursor (caret) (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeUserInterface.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeUserInterface.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeUserInterface.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeUserInterface.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Theme.user_interface`](bpy.types.Theme.md#bpy.types.Theme.user_interface "bpy.types.Theme.user_interface") |  |
