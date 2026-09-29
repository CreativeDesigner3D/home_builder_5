<!-- source: Blender Python API reference 5.2 / bpy.types.MetaBallElements.html -->

<a id="metaballelements-bpy-prop-collection"></a>

# MetaBallElements(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.MetaBallElements"></a>

### class bpy.types.MetaBallElements(bpy_prop_collection)

Collection of metaball elements

<a id="bpy.types.MetaBallElements.active"></a>

#### bpy.types.MetaBallElements.active

Last selected element (readonly)

**Type:**

[`MetaElement`](bpy.types.MetaElement.md#bpy.types.MetaElement "bpy.types.MetaElement") | None

<a id="bpy.types.MetaBallElements.new"></a>

#### bpy.types.MetaBallElements.new(*, type='BALL')

Add a new element to the metaball

**Parameters:**

**type** (Literal[[Metaelem Type Items](bpy_types_enum_items/metaelem_type_items.md#rna-enum-metaelem-type-items)]) – Type for the new metaball element (optional)

**Returns:**

The newly created metaball element

**Return type:**

[`MetaElement`](bpy.types.MetaElement.md#bpy.types.MetaElement "bpy.types.MetaElement")

<a id="bpy.types.MetaBallElements.remove"></a>

#### bpy.types.MetaBallElements.remove(element)

Remove an element from the metaball

**Parameters:**

**element** ([`MetaElement`](bpy.types.MetaElement.md#bpy.types.MetaElement "bpy.types.MetaElement") | None) – The element to remove (never None)

<a id="bpy.types.MetaBallElements.clear"></a>

#### bpy.types.MetaBallElements.clear()

Remove all elements from the metaball

<a id="bpy.types.MetaBallElements.bl_rna_get_subclass"></a>

#### classmethod bpy.types.MetaBallElements.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.MetaBallElements.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.MetaBallElements.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MetaBall.elements`](bpy.types.MetaBall.md#bpy.types.MetaBall.elements "bpy.types.MetaBall.elements") |  |
