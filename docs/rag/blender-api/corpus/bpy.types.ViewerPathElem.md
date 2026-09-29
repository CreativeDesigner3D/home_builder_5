<!-- source: Blender Python API reference 5.2 / bpy.types.ViewerPathElem.html -->

<a id="viewerpathelem-bpy-struct"></a>

# ViewerPathElem(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [EvaluateClosureNodeViewerPathElem(ViewerPathElem)](bpy.types.EvaluateClosureNodeViewerPathElem.md)
- [ForeachGeometryElementZoneViewerPathElem(ViewerPathElem)](bpy.types.ForeachGeometryElementZoneViewerPathElem.md)
- [GroupNodeViewerPathElem(ViewerPathElem)](bpy.types.GroupNodeViewerPathElem.md)
- [IDViewerPathElem(ViewerPathElem)](bpy.types.IDViewerPathElem.md)
- [ModifierViewerPathElem(ViewerPathElem)](bpy.types.ModifierViewerPathElem.md)
- [RepeatZoneViewerPathElem(ViewerPathElem)](bpy.types.RepeatZoneViewerPathElem.md)
- [SimulationZoneViewerPathElem(ViewerPathElem)](bpy.types.SimulationZoneViewerPathElem.md)
- [ViewerNodeViewerPathElem(ViewerPathElem)](bpy.types.ViewerNodeViewerPathElem.md)

<a id="bpy.types.ViewerPathElem"></a>

### class bpy.types.ViewerPathElem(bpy_struct)

Element of a viewer path

<a id="bpy.types.ViewerPathElem.type"></a>

#### bpy.types.ViewerPathElem.type

Type of the path element (default `'ID'`, readonly)

**Type:**

Literal[‘ID’, ‘MODIFIER’, ‘GROUP_NODE’, ‘SIMULATION_ZONE’, ‘VIEWER_NODE’, ‘REPEAT_ZONE’, ‘FOREACH_GEOMETRY_ELEMENT_ZONE’, ‘EVALUATE_CLOSURE’]

<a id="bpy.types.ViewerPathElem.ui_name"></a>

#### bpy.types.ViewerPathElem.ui_name

Name that can be displayed in the UI for this element (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.ViewerPathElem.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ViewerPathElem.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ViewerPathElem.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ViewerPathElem.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([type](#bpy.types.ViewerPathElem.type "bpy.types.ViewerPathElem.type") | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

[type](#bpy.types.ViewerPathElem.type "bpy.types.ViewerPathElem.type")

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
| - [`ViewerPath.path`](bpy.types.ViewerPath.md#bpy.types.ViewerPath.path "bpy.types.ViewerPath.path") |  |
