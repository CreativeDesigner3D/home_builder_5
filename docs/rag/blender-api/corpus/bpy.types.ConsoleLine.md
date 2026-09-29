<!-- source: Blender Python API reference 5.2 / bpy.types.ConsoleLine.html -->

<a id="consoleline-bpy-struct"></a>

# ConsoleLine(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ConsoleLine"></a>

### class bpy.types.ConsoleLine(bpy_struct)

Input line for the interactive console

<a id="bpy.types.ConsoleLine.body"></a>

#### bpy.types.ConsoleLine.body

Text in the line (default “”, never None)

**Type:**

str

<a id="bpy.types.ConsoleLine.current_character"></a>

#### bpy.types.ConsoleLine.current_character

(in [-inf, inf], default 0)

**Type:**

int

<a id="bpy.types.ConsoleLine.type"></a>

#### bpy.types.ConsoleLine.type

Console line type when used in scrollback (default `'OUTPUT'`)

**Type:**

Literal[‘OUTPUT’, ‘INPUT’, ‘INFO’, ‘ERROR’]

<a id="bpy.types.ConsoleLine.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ConsoleLine.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ConsoleLine.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ConsoleLine.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.ConsoleLine.type "bpy.types.ConsoleLine.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.ConsoleLine.type "bpy.types.ConsoleLine.type")

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
| - [`SpaceConsole.history`](bpy.types.SpaceConsole.md#bpy.types.SpaceConsole.history "bpy.types.SpaceConsole.history") | - [`SpaceConsole.scrollback`](bpy.types.SpaceConsole.md#bpy.types.SpaceConsole.scrollback "bpy.types.SpaceConsole.scrollback") |
