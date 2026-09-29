<!-- source: Blender Python API reference 5.2 / bpy.types.Region.html -->

<a id="region-bpy-struct"></a>

# Region(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Region"></a>

### class bpy.types.Region(bpy_struct)

Region in a subdivided screen area

<a id="bpy.types.Region.active_panel_category"></a>

#### bpy.types.Region.active_panel_category

The current active panel category, may be Null if the region does not support this feature (NOTE: these categories are generated at runtime, so list may be empty at initialization, before any drawing took place) (default `'UNSUPPORTED'`)

**Type:**

Literal[[Region Panel Category Items](bpy_types_enum_items/region_panel_category_items.md#rna-enum-region-panel-category-items)]

<a id="bpy.types.Region.alignment"></a>

#### bpy.types.Region.alignment

Alignment of the region within the area (default `'NONE'`, readonly)

- `NONE`
  None – Don’t use any fixed alignment, fill available space.
- `TOP`
  Top.
- `BOTTOM`
  Bottom.
- `LEFT`
  Left.
- `RIGHT`
  Right.
- `HORIZONTAL_SPLIT`
  Horizontal Split.
- `VERTICAL_SPLIT`
  Vertical Split.
- `FLOAT`
  Float – Region floats on screen, does not use any fixed alignment.
- `QUAD_SPLIT`
  Quad Split – Region is split horizontally and vertically.

**Type:**

Literal[‘NONE’, ‘TOP’, ‘BOTTOM’, ‘LEFT’, ‘RIGHT’, ‘HORIZONTAL_SPLIT’, ‘VERTICAL_SPLIT’, ‘FLOAT’, ‘QUAD_SPLIT’]

<a id="bpy.types.Region.data"></a>

#### bpy.types.Region.data

Region specific data (the type depends on the region type) (readonly)

**Type:**

[`AnyType`](bpy.types.AnyType.md#bpy.types.AnyType "bpy.types.AnyType") | None

<a id="bpy.types.Region.height"></a>

#### bpy.types.Region.height

Region height (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.Region.type"></a>

#### bpy.types.Region.type

Type of this region (default `'WINDOW'`, readonly)

**Type:**

Literal[[Region Type Items](bpy_types_enum_items/region_type_items.md#rna-enum-region-type-items)]

<a id="bpy.types.Region.view2d"></a>

#### bpy.types.Region.view2d

2D view of the region (readonly, never None)

**Type:**

[`View2D`](bpy.types.View2D.md#bpy.types.View2D "bpy.types.View2D")

<a id="bpy.types.Region.width"></a>

#### bpy.types.Region.width

Region width (in [0, 32767], default 0, readonly)

**Type:**

int

<a id="bpy.types.Region.x"></a>

#### bpy.types.Region.x

The window relative vertical location of the region (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Region.y"></a>

#### bpy.types.Region.y

The window relative horizontal location of the region (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.Region.tag_redraw"></a>

#### bpy.types.Region.tag_redraw()

tag_redraw

<a id="bpy.types.Region.tag_refresh_ui"></a>

#### bpy.types.Region.tag_refresh_ui()

tag_refresh_ui

<a id="bpy.types.Region.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Region.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Region.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Region.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.Region.type "bpy.types.Region.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.Region.type "bpy.types.Region.type")

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
| - [`Area.regions`](bpy.types.Area.md#bpy.types.Area.regions "bpy.types.Area.regions") - [`Context.region`](bpy.types.Context.md#bpy.types.Context.region "bpy.types.Context.region") | - [`Context.region_popup`](bpy.types.Context.md#bpy.types.Context.region_popup "bpy.types.Context.region_popup") |
