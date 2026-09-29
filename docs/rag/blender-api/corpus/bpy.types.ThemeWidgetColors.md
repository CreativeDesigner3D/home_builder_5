<!-- source: Blender Python API reference 5.2 / bpy.types.ThemeWidgetColors.html -->

<a id="themewidgetcolors-bpy-struct"></a>

# ThemeWidgetColors(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ThemeWidgetColors"></a>

### class bpy.types.ThemeWidgetColors(bpy_struct)

Theme settings for widget color sets

<a id="bpy.types.ThemeWidgetColors.inner"></a>

#### bpy.types.ThemeWidgetColors.inner

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeWidgetColors.inner_sel"></a>

#### bpy.types.ThemeWidgetColors.inner_sel

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeWidgetColors.item"></a>

#### bpy.types.ThemeWidgetColors.item

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeWidgetColors.outline"></a>

#### bpy.types.ThemeWidgetColors.outline

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeWidgetColors.outline_sel"></a>

#### bpy.types.ThemeWidgetColors.outline_sel

(array of 4 items, in [0, 1], default (0.0, 0.0, 0.0, 0.0))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[float]

<a id="bpy.types.ThemeWidgetColors.roundness"></a>

#### bpy.types.ThemeWidgetColors.roundness

Amount of edge rounding (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.ThemeWidgetColors.shadedown"></a>

#### bpy.types.ThemeWidgetColors.shadedown

(in [-100, 100], default 0)

**Type:**

int

<a id="bpy.types.ThemeWidgetColors.shadetop"></a>

#### bpy.types.ThemeWidgetColors.shadetop

(in [-100, 100], default 0)

**Type:**

int

<a id="bpy.types.ThemeWidgetColors.show_shaded"></a>

#### bpy.types.ThemeWidgetColors.show_shaded

(default False)

**Type:**

bool

<a id="bpy.types.ThemeWidgetColors.text"></a>

#### bpy.types.ThemeWidgetColors.text

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeWidgetColors.text_sel"></a>

#### bpy.types.ThemeWidgetColors.text_sel

(array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.ThemeWidgetColors.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ThemeWidgetColors.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ThemeWidgetColors.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ThemeWidgetColors.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ThemeUserInterface.wcol_box`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_box "bpy.types.ThemeUserInterface.wcol_box") - [`ThemeUserInterface.wcol_curve`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_curve "bpy.types.ThemeUserInterface.wcol_curve") - [`ThemeUserInterface.wcol_list_item`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_list_item "bpy.types.ThemeUserInterface.wcol_list_item") - [`ThemeUserInterface.wcol_menu`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_menu "bpy.types.ThemeUserInterface.wcol_menu") - [`ThemeUserInterface.wcol_menu_back`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_menu_back "bpy.types.ThemeUserInterface.wcol_menu_back") - [`ThemeUserInterface.wcol_menu_item`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_menu_item "bpy.types.ThemeUserInterface.wcol_menu_item") - [`ThemeUserInterface.wcol_num`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_num "bpy.types.ThemeUserInterface.wcol_num") - [`ThemeUserInterface.wcol_numslider`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_numslider "bpy.types.ThemeUserInterface.wcol_numslider") - [`ThemeUserInterface.wcol_option`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_option "bpy.types.ThemeUserInterface.wcol_option") - [`ThemeUserInterface.wcol_pie_menu`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_pie_menu "bpy.types.ThemeUserInterface.wcol_pie_menu") - [`ThemeUserInterface.wcol_progress`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_progress "bpy.types.ThemeUserInterface.wcol_progress") | - [`ThemeUserInterface.wcol_pulldown`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_pulldown "bpy.types.ThemeUserInterface.wcol_pulldown") - [`ThemeUserInterface.wcol_radio`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_radio "bpy.types.ThemeUserInterface.wcol_radio") - [`ThemeUserInterface.wcol_regular`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_regular "bpy.types.ThemeUserInterface.wcol_regular") - [`ThemeUserInterface.wcol_scroll`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_scroll "bpy.types.ThemeUserInterface.wcol_scroll") - [`ThemeUserInterface.wcol_tab`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_tab "bpy.types.ThemeUserInterface.wcol_tab") - [`ThemeUserInterface.wcol_text`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_text "bpy.types.ThemeUserInterface.wcol_text") - [`ThemeUserInterface.wcol_toggle`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_toggle "bpy.types.ThemeUserInterface.wcol_toggle") - [`ThemeUserInterface.wcol_tool`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_tool "bpy.types.ThemeUserInterface.wcol_tool") - [`ThemeUserInterface.wcol_toolbar_item`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_toolbar_item "bpy.types.ThemeUserInterface.wcol_toolbar_item") - [`ThemeUserInterface.wcol_tooltip`](bpy.types.ThemeUserInterface.md#bpy.types.ThemeUserInterface.wcol_tooltip "bpy.types.ThemeUserInterface.wcol_tooltip") |
