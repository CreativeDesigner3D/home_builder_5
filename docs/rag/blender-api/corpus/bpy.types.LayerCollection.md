<!-- source: Blender Python API reference 5.2 / bpy.types.LayerCollection.html -->

<a id="layercollection-bpy-struct"></a>

# LayerCollection(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.LayerCollection"></a>

### class bpy.types.LayerCollection(bpy_struct)

Layer collection

<a id="bpy.types.LayerCollection.children"></a>

#### bpy.types.LayerCollection.children

Layer collection children (default None, readonly)

**Type:**

[`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")[[`LayerCollection`](#bpy.types.LayerCollection "bpy.types.LayerCollection")]

<a id="bpy.types.LayerCollection.collection"></a>

#### bpy.types.LayerCollection.collection

Collection this layer collection is wrapping (readonly, never None)

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection")

<a id="bpy.types.LayerCollection.exclude"></a>

#### bpy.types.LayerCollection.exclude

Exclude from view layer (default False)

**Type:**

bool

<a id="bpy.types.LayerCollection.hide_viewport"></a>

#### bpy.types.LayerCollection.hide_viewport

Temporarily hide in viewport (default False)

**Type:**

bool

<a id="bpy.types.LayerCollection.holdout"></a>

#### bpy.types.LayerCollection.holdout

Mask out objects in collection from view layer (default False)

**Type:**

bool

<a id="bpy.types.LayerCollection.indirect_only"></a>

#### bpy.types.LayerCollection.indirect_only

Objects in collection only contribute indirectly (through shadows and reflections) in the view layer (default False)

**Type:**

bool

<a id="bpy.types.LayerCollection.is_visible"></a>

#### bpy.types.LayerCollection.is_visible

Whether this collection is visible for the view layer, take into account the collection parent (default False, readonly)

**Type:**

bool

<a id="bpy.types.LayerCollection.name"></a>

#### bpy.types.LayerCollection.name

Name of this layer collection (same as its collection one) (default “”, readonly, never None)

**Type:**

str

<a id="bpy.types.LayerCollection.visible_get"></a>

#### bpy.types.LayerCollection.visible_get()

Whether this collection is visible, take into account the collection parent and the viewport

**Return type:**

bool

<a id="bpy.types.LayerCollection.has_objects"></a>

#### bpy.types.LayerCollection.has_objects()

**Return type:**

bool

<a id="bpy.types.LayerCollection.has_selected_objects"></a>

#### bpy.types.LayerCollection.has_selected_objects(view_layer)

**Parameters:**

**view_layer** ([`ViewLayer`](bpy.types.ViewLayer.md#bpy.types.ViewLayer "bpy.types.ViewLayer") | None) – View layer the layer collection belongs to

**Return type:**

bool

<a id="bpy.types.LayerCollection.bl_rna_get_subclass"></a>

#### classmethod bpy.types.LayerCollection.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.LayerCollection.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.LayerCollection.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.collection` - [`Context.layer_collection`](bpy.types.Context.md#bpy.types.Context.layer_collection "bpy.types.Context.layer_collection") - [`LayerCollection.children`](#bpy.types.LayerCollection.children "bpy.types.LayerCollection.children") | - [`ViewLayer.active_layer_collection`](bpy.types.ViewLayer.md#bpy.types.ViewLayer.active_layer_collection "bpy.types.ViewLayer.active_layer_collection") - [`ViewLayer.layer_collection`](bpy.types.ViewLayer.md#bpy.types.ViewLayer.layer_collection "bpy.types.ViewLayer.layer_collection") |
