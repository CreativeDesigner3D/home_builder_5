<!-- source: Blender Python API reference 5.2 / bpy.types.PropertyGroup.html -->

<a id="propertygroup-bpy-struct"></a>

# PropertyGroup(bpy_struct)

<a id="custom-properties"></a>

## Custom Properties

PropertyGroups are the base class for dynamically defined sets of properties.

They can be used to extend existing Blender data with your own types which can
be animated, accessed from the user interface and from Python.

> **Note:**
>
> The values assigned to Blender data are saved to disk but the class
> definitions are not, this means whenever you load Blender the class needs
> to be registered too.
>
> This is best done by creating an add-on which loads on startup and registers
> your properties.

> **Note:**
>
> PropertyGroups must be registered before assigning them to Blender data.

> **See also:**
>
> Property types used in class declarations are all in [`bpy.props`](bpy.props.md#module-bpy.props "bpy.props")

```python
import bpy

class MyPropertyGroup(bpy.types.PropertyGroup):
    custom_1: bpy.props.FloatProperty(name="My Float")
    custom_2: bpy.props.IntProperty(name="My Int")

bpy.utils.register_class(MyPropertyGroup)

bpy.types.Object.my_prop_grp = bpy.props.PointerProperty(type=MyPropertyGroup)

# Test this worked.
bpy.data.objects[0].my_prop_grp.custom_1 = 22.0
```

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [OperatorFileListElement(PropertyGroup)](bpy.types.OperatorFileListElement.md)
- [OperatorMousePath(PropertyGroup)](bpy.types.OperatorMousePath.md)
- [OperatorStrokeElement(PropertyGroup)](bpy.types.OperatorStrokeElement.md)
- [SelectedUvElement(PropertyGroup)](bpy.types.SelectedUvElement.md)

<a id="bpy.types.PropertyGroup"></a>

### class bpy.types.PropertyGroup(bpy_struct)

Group of ID properties

<a id="bpy.types.PropertyGroup.name"></a>

#### bpy.types.PropertyGroup.name

Unique name used in the code and scripting, can be re-defined in Python sub-classes if needed (default “”, never None)

**Type:**

str

<a id="bpy.types.PropertyGroup.bl_system_properties_get"></a>

#### bpy.types.PropertyGroup.bl_system_properties_get(*, do_create=False)

DEBUG ONLY. Internal access to runtime-defined RNA data storage, intended solely for testing and debugging purposes. Do not access it in regular scripting work, and in particular, do not assume that it contains writable data

**Parameters:**

**do_create** (bool) – Ensure that system properties are created if they do not exist yet (optional)

**Returns:**

The system properties root container, or None if there are no system properties stored in this data yet, and its creation was not requested

**Return type:**

[`PropertyGroup`](#bpy.types.PropertyGroup "bpy.types.PropertyGroup")

<a id="bpy.types.PropertyGroup.bl_rna_get_subclass"></a>

#### classmethod bpy.types.PropertyGroup.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.PropertyGroup.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.PropertyGroup.bl_rna_get_subclass_py(id, default=None, /)

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

<a id="references"></a>

### References

|  |  |
| --- | --- |
| - [`AddonPreferences.bl_system_properties_get`](bpy.types.AddonPreferences.md#bpy.types.AddonPreferences.bl_system_properties_get "bpy.types.AddonPreferences.bl_system_properties_get") - [`Bone.bl_system_properties_get`](bpy.types.Bone.md#bpy.types.Bone.bl_system_properties_get "bpy.types.Bone.bl_system_properties_get") - [`BoneCollection.bl_system_properties_get`](bpy.types.BoneCollection.md#bpy.types.BoneCollection.bl_system_properties_get "bpy.types.BoneCollection.bl_system_properties_get") - [`CollectionExport.export_properties`](bpy.types.CollectionExport.md#bpy.types.CollectionExport.export_properties "bpy.types.CollectionExport.export_properties") - [`CollectionImport.import_properties`](bpy.types.CollectionImport.md#bpy.types.CollectionImport.import_properties "bpy.types.CollectionImport.import_properties") - [`EditBone.bl_system_properties_get`](bpy.types.EditBone.md#bpy.types.EditBone.bl_system_properties_get "bpy.types.EditBone.bl_system_properties_get") - [`GizmoGroupProperties.bl_system_properties_get`](bpy.types.GizmoGroupProperties.md#bpy.types.GizmoGroupProperties.bl_system_properties_get "bpy.types.GizmoGroupProperties.bl_system_properties_get") - [`GizmoProperties.bl_system_properties_get`](bpy.types.GizmoProperties.md#bpy.types.GizmoProperties.bl_system_properties_get "bpy.types.GizmoProperties.bl_system_properties_get") - [`ID.bl_system_properties_get`](bpy.types.ID.md#bpy.types.ID.bl_system_properties_get "bpy.types.ID.bl_system_properties_get") - [`IDPropertyWrapPtr.bl_system_properties_get`](bpy.types.IDPropertyWrapPtr.md#bpy.types.IDPropertyWrapPtr.bl_system_properties_get "bpy.types.IDPropertyWrapPtr.bl_system_properties_get") - [`KeyConfigPreferences.bl_system_properties_get`](bpy.types.KeyConfigPreferences.md#bpy.types.KeyConfigPreferences.bl_system_properties_get "bpy.types.KeyConfigPreferences.bl_system_properties_get") - [`Node.bl_system_properties_get`](bpy.types.Node.md#bpy.types.Node.bl_system_properties_get "bpy.types.Node.bl_system_properties_get") - [`NodeSocket.bl_system_properties_get`](bpy.types.NodeSocket.md#bpy.types.NodeSocket.bl_system_properties_get "bpy.types.NodeSocket.bl_system_properties_get") - [`NodeTreeInterfaceSocket.bl_system_properties_get`](bpy.types.NodeTreeInterfaceSocket.md#bpy.types.NodeTreeInterfaceSocket.bl_system_properties_get "bpy.types.NodeTreeInterfaceSocket.bl_system_properties_get") - [`NodesModifierProperties.bl_system_properties_get`](bpy.types.NodesModifierProperties.md#bpy.types.NodesModifierProperties.bl_system_properties_get "bpy.types.NodesModifierProperties.bl_system_properties_get") | - [`NodesModifierPropertiesEmpty.bl_system_properties_get`](bpy.types.NodesModifierPropertiesEmpty.md#bpy.types.NodesModifierPropertiesEmpty.bl_system_properties_get "bpy.types.NodesModifierPropertiesEmpty.bl_system_properties_get") - [`OperatorProperties.bl_system_properties_get`](bpy.types.OperatorProperties.md#bpy.types.OperatorProperties.bl_system_properties_get "bpy.types.OperatorProperties.bl_system_properties_get") - [`PoseBone.bl_system_properties_get`](bpy.types.PoseBone.md#bpy.types.PoseBone.bl_system_properties_get "bpy.types.PoseBone.bl_system_properties_get") - [`PropertyGroup.bl_system_properties_get`](#bpy.types.PropertyGroup.bl_system_properties_get "bpy.types.PropertyGroup.bl_system_properties_get") - [`PropertyGroupItem.collection`](bpy.types.PropertyGroupItem.md#bpy.types.PropertyGroupItem.collection "bpy.types.PropertyGroupItem.collection") - [`PropertyGroupItem.group`](bpy.types.PropertyGroupItem.md#bpy.types.PropertyGroupItem.group "bpy.types.PropertyGroupItem.group") - [`PropertyGroupItem.idp_array`](bpy.types.PropertyGroupItem.md#bpy.types.PropertyGroupItem.idp_array "bpy.types.PropertyGroupItem.idp_array") - [`SequencerCompositorModifierProperties.bl_system_properties_get`](bpy.types.SequencerCompositorModifierProperties.md#bpy.types.SequencerCompositorModifierProperties.bl_system_properties_get "bpy.types.SequencerCompositorModifierProperties.bl_system_properties_get") - [`SequencerCompositorModifierPropertiesEmpty.bl_system_properties_get`](bpy.types.SequencerCompositorModifierPropertiesEmpty.md#bpy.types.SequencerCompositorModifierPropertiesEmpty.bl_system_properties_get "bpy.types.SequencerCompositorModifierPropertiesEmpty.bl_system_properties_get") - [`Strip.bl_system_properties_get`](bpy.types.Strip.md#bpy.types.Strip.bl_system_properties_get "bpy.types.Strip.bl_system_properties_get") - [`TimelineMarker.bl_system_properties_get`](bpy.types.TimelineMarker.md#bpy.types.TimelineMarker.bl_system_properties_get "bpy.types.TimelineMarker.bl_system_properties_get") - [`UIList.bl_system_properties_get`](bpy.types.UIList.md#bpy.types.UIList.bl_system_properties_get "bpy.types.UIList.bl_system_properties_get") - [`View3DShading.bl_system_properties_get`](bpy.types.View3DShading.md#bpy.types.View3DShading.bl_system_properties_get "bpy.types.View3DShading.bl_system_properties_get") - [`ViewLayer.bl_system_properties_get`](bpy.types.ViewLayer.md#bpy.types.ViewLayer.bl_system_properties_get "bpy.types.ViewLayer.bl_system_properties_get") |
