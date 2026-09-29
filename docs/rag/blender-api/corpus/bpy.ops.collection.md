<!-- source: Blender Python API reference 5.2 / bpy.ops.collection.html -->

<a id="module-bpy.ops.collection"></a>

# Collection Operators

<a id="bpy.ops.collection.create"></a>

### bpy.ops.collection.create(*, name='')

Create an object collection from selected objects

**Parameters:**

**name** (str) – Name, Name of the new collection (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.export_all"></a>

### bpy.ops.collection.export_all()

Invoke all configured exporters on this collection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.exporter_add"></a>

### bpy.ops.collection.exporter_add(*, name='')

Add exporter to the exporter list

**Parameters:**

**name** (str) – Name, FileHandler idname (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.exporter_export"></a>

### bpy.ops.collection.exporter_export(*, index=0)

Invoke the export operation

**Parameters:**

**index** (int) – Index, Exporter index (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.exporter_move"></a>

### bpy.ops.collection.exporter_move(*, direction='UP')

Move exporter up or down in the exporter list

**Parameters:**

**direction** (Literal['UP', 'DOWN']) – Direction, Direction to move the active exporter (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.exporter_remove"></a>

### bpy.ops.collection.exporter_remove(*, index=0)

Remove exporter from the exporter list

**Parameters:**

**index** (int) – Index, Exporter index (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.importer_add"></a>

### bpy.ops.collection.importer_add(*, name='')

Add Importer

**Parameters:**

**name** (str) – Name, FileHandler idname (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.importer_remove"></a>

### bpy.ops.collection.importer_remove()

Remove Importer

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.objects_add_active"></a>

### bpy.ops.collection.objects_add_active(*, collection='')

Add selected objects to one of the collections the active-object is part of. Optionally add to “All Collections” to ensure selected objects are included in the same collections as the active object

**Parameters:**

**collection** (str) – Collection, The collection to add other selected objects to (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.objects_remove"></a>

### bpy.ops.collection.objects_remove(*, collection='')

Remove selected objects from a collection

**Parameters:**

**collection** (str) – Collection, The collection to remove this object from (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.objects_remove_active"></a>

### bpy.ops.collection.objects_remove_active(*, collection='')

Remove the object from an object collection that contains the active object

**Parameters:**

**collection** (str) – Collection, The collection to remove other selected objects from (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.collection.objects_remove_all"></a>

### bpy.ops.collection.objects_remove_all()

Remove selected objects from all collections

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
