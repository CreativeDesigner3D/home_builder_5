<!-- source: Blender Python API reference 5.2 / bpy.types.Header.html -->

<a id="header-bpy-struct"></a>

# Header(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.Header"></a>

### class bpy.types.Header(bpy_struct)

Editor header containing UI elements

<a id="bpy.types.Header.bl_idname"></a>

#### bpy.types.Header.bl_idname

If this is set, the header gets a custom ID, otherwise it takes the name of the class used to define the header; for example, if the class name is “OBJECT_HT_hello”, and bl_idname is not set by the script, then bl_idname = “OBJECT_HT_hello” (default “”, never None)

**Type:**

str

<a id="bpy.types.Header.bl_region_type"></a>

#### bpy.types.Header.bl_region_type

The region where the header is going to be used in (defaults to header region) (default `'HEADER'`)

**Type:**

Literal[[Region Type Items](bpy_types_enum_items/region_type_items.md#rna-enum-region-type-items)]

<a id="bpy.types.Header.bl_space_type"></a>

#### bpy.types.Header.bl_space_type

The space where the header is going to be used in (default `'EMPTY'`)

**Type:**

Literal[[Space Type Items](bpy_types_enum_items/space_type_items.md#rna-enum-space-type-items)]

<a id="bpy.types.Header.layout"></a>

#### bpy.types.Header.layout

Structure of the header in the UI (readonly)

**Type:**

[`UILayout`](bpy.types.UILayout.md#bpy.types.UILayout "bpy.types.UILayout") | None

<a id="bpy.types.Header.draw"></a>

#### bpy.types.Header.draw(context)

Draw UI elements into the header UI layout

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context

<a id="bpy.types.Header.append"></a>

#### classmethod bpy.types.Header.append(draw_func)

Append a draw function to this menu,
takes the same arguments as the menus draw function

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function to append.

<a id="bpy.types.Header.is_extended"></a>

#### classmethod bpy.types.Header.is_extended()

Test if any draw function has been added via [`append()`](#bpy.types.Header.append "bpy.types.Header.append") or [`prepend()`](#bpy.types.Header.prepend "bpy.types.Header.prepend").

**Returns:**

True when at least one draw function has been added.

**Return type:**

bool

<a id="bpy.types.Header.prepend"></a>

#### classmethod bpy.types.Header.prepend(draw_func)

Prepend a draw function to this menu, takes the same arguments as
the menus draw function

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function to prepend.

<a id="bpy.types.Header.remove"></a>

#### classmethod bpy.types.Header.remove(draw_func)

Remove a draw function that has been added to this menu.

**Parameters:**

**draw_func** (Callable[[Self, [`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")], None]) – Draw function previously registered via [`append()`](#bpy.types.Header.append "bpy.types.Header.append") or [`prepend()`](#bpy.types.Header.prepend "bpy.types.Header.prepend").

<a id="bpy.types.Header.bl_rna_get_subclass"></a>

#### classmethod bpy.types.Header.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.Header.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.Header.bl_rna_get_subclass_py(id, default=None, /)

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
