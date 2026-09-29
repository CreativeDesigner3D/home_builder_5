<!-- source: Blender Python API reference 5.2 / bpy.types.FileHandler.html -->

<a id="filehandler-bpy-struct"></a>

# FileHandler(bpy_struct)

<a id="basic-filehandler-for-importing-a-single-file"></a>

## Basic FileHandler for importing a single file

A file handler allows custom drag-and-drop behavior to be associated with a given `Operator`
([`FileHandler.bl_import_operator`](#bpy.types.FileHandler.bl_import_operator "bpy.types.FileHandler.bl_import_operator")) and set of file extensions
([`FileHandler.bl_file_extensions`](#bpy.types.FileHandler.bl_file_extensions "bpy.types.FileHandler.bl_file_extensions")). Control over which area of the UI accepts the
drag-in-drop action is specified using the [`FileHandler.poll_drop`](#bpy.types.FileHandler.poll_drop "bpy.types.FileHandler.poll_drop") method.

Similar to operators that use a file select window, operators participating in drag-and-drop, and
only accepting a single file, must define the following property:

```python
filepath: bpy.props.StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'})
```

This `filepath` property will be set to the full path of the file dropped by the user.

```python
import bpy

class CurveTextImport(bpy.types.Operator):
    """
    Creates a text object from a text file.
    """
    bl_idname = "curve.text_import"
    bl_label = "Import a text file as text object"

    # This Operator supports processing one `.txt` file at a time. The following file-path
    # property must be defined.
    filepath: bpy.props.StringProperty(subtype='FILE_PATH', options={'SKIP_SAVE'})

    @classmethod
    def poll(cls, context):
        return (context.area and context.area.type == "VIEW_3D")

    def execute(self, context):
        # Direct calls to this Operator may use unsupported file-paths. Ensure the incoming
        # file-path is one that is supported.
        if not self.filepath or not self.filepath.endswith(".txt"):
            return {'CANCELLED'}

        # Create a Blender Text object from the contents of the provided file.
        with open(self.filepath) as file:
            text_curve = bpy.data.curves.new(type="FONT", name="Text")
            text_curve.body = ''.join(file.readlines())
            text_object = bpy.data.objects.new(name="Text", object_data=text_curve)
            bpy.context.scene.collection.objects.link(text_object)
        return {'FINISHED'}

    # By default the file handler invokes the operator with the file-path property set. If the
    # operator also supports being invoked with no file-path set, and allows the user to pick from a
    # file select window instead, the following logic can be used.
    #
    # Note: It is important to use `options={'SKIP_SAVE'}` when defining the file-path property to
    # avoid prior values from being reused on subsequent calls.

    def invoke(self, context, event):
        if self.filepath:
            return self.execute(context)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Define a file handler that supports the following set of conditions:
#  - Execute the `curve.text_import` operator
#  - When `.txt` files are dropped in the 3D Viewport
class CURVE_FH_text_import(bpy.types.FileHandler):
    bl_idname = "CURVE_FH_text_import"
    bl_label = "File handler for curve text object import"
    bl_import_operator = "curve.text_import"
    bl_file_extensions = ".txt"

    @classmethod
    def poll_drop(cls, context):
        return (context.area and context.area.type == 'VIEW_3D')

bpy.utils.register_class(CurveTextImport)
bpy.utils.register_class(CURVE_FH_text_import)
```

<a id="filehandler-for-importing-multiple-files-and-exposing-operator-options"></a>

## FileHandler for Importing multiple files and exposing Operator options

Operators which support being executed with multiple files from drag-and-drop require the
following properties be defined:

```python
directory: StringProperty(subtype='DIR_PATH', options={'SKIP_SAVE', 'HIDDEN'})
files: CollectionProperty(type=OperatorFileListElement, options={'SKIP_SAVE', 'HIDDEN'})
```

These `directory` and `files` properties will be set with the necessary data from the
drag-and-drop operation.

Additionally, if the operator provides operator properties that need to be accessible to the user,
the `ImportHelper.invoke_popup` method can be used to show a dialog leveraging the standard
[`Operator.draw`](bpy.types.Operator.md#bpy.types.Operator.draw "bpy.types.Operator.draw") method for layout and display.

```python
import bpy
from bpy_extras.io_utils import ImportHelper
from mathutils import Vector

class ShaderScriptImport(bpy.types.Operator, ImportHelper):
    """
    Creates one or more Shader Script nodes from text files.
    """
    bl_idname = "shader.script_import"
    bl_label = "Import a text file as a script node"

    # This Operator supports processing multiple `.txt` files at a time. The following properties
    # must be defined.
    directory: bpy.props.StringProperty(subtype='DIR_PATH', options={'SKIP_SAVE', 'HIDDEN'})
    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'SKIP_SAVE', 'HIDDEN'})

    # Allow the user to choose whether the node's label is set or not
    set_label: bpy.props.BoolProperty(name="Set Label", default=False)

    @classmethod
    def poll(cls, context):
        return (
            context.region and context.region.type == 'WINDOW' and
            context.area and context.area.ui_type == 'ShaderNodeTree' and
            context.object and context.object.type == 'MESH' and
            context.material
        )

    def execute(self, context):
        # The directory property must be set.
        if not self.directory:
            return {'CANCELLED'}

        x = 0.0
        y = 0.0
        for file in self.files:
            # Direct calls to this Operator may use unsupported file-paths. Ensure the incoming
            # files are ones that are supported.
            if file.name.endswith(".txt"):
                import os
                filepath = os.path.join(self.directory, file.name)

                node_tree = context.material.node_tree
                text_node = node_tree.nodes.new(type="ShaderNodeScript")
                text_node.mode = 'EXTERNAL'
                text_node.filepath = filepath
                text_node.location = Vector((x, y))

                # Set the node's title to the file name.
                if self.set_label:
                    text_node.label = file.name

                x += 20.0
                y -= 20.0

        return {'FINISHED'}

    # Use ImportHelper's invoke_popup() to handle the invocation so that this operator's properties
    # are shown in a popup. This allows the user to configure additional settings on the operator
    # like the `set_label` property. Consider having a draw() method on the operator in order to
    # layout the properties in the UI appropriately.
    #
    # If filepath information is not provided the file select window will be invoked instead.

    def invoke(self, context, event):
        return self.invoke_popup(context)

# Define a file handler that supports the following set of conditions:
#  - Execute the `shader.script_import` operator
#  - When `.txt` files are dropped in the Shader Editor
class SHADER_FH_script_import(bpy.types.FileHandler):
    bl_idname = "SHADER_FH_script_import"
    bl_label = "File handler for shader script node import"
    bl_import_operator = "shader.script_import"
    bl_file_extensions = ".txt"

    @classmethod
    def poll_drop(cls, context):
        return (
            context.region and context.region.type == 'WINDOW' and
            context.area and context.area.ui_type == 'ShaderNodeTree'
        )

bpy.utils.register_class(ShaderScriptImport)
bpy.utils.register_class(SHADER_FH_script_import)
```

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

Subclasses

- [IMAGE_FH_drop_handler(FileHandler)](bpy.types.IMAGE_FH_drop_handler.md)
- [IO_FH_gltf2(FileHandler)](bpy.types.IO_FH_gltf2.md)
- [IO_FH_svg_as_curves(FileHandler)](bpy.types.IO_FH_svg_as_curves.md)
- [NODE_FH_image_node(FileHandler)](bpy.types.NODE_FH_image_node.md)
- [SEQUENCER_FH_image_strip(FileHandler)](bpy.types.SEQUENCER_FH_image_strip.md)
- [SEQUENCER_FH_movie_strip(FileHandler)](bpy.types.SEQUENCER_FH_movie_strip.md)
- [SEQUENCER_FH_sound_strip(FileHandler)](bpy.types.SEQUENCER_FH_sound_strip.md)
- [VIEW3D_FH_camera_background_image(FileHandler)](bpy.types.VIEW3D_FH_camera_background_image.md)
- [VIEW3D_FH_empty_image(FileHandler)](bpy.types.VIEW3D_FH_empty_image.md)
- [VIEW3D_FH_vdb_volume(FileHandler)](bpy.types.VIEW3D_FH_vdb_volume.md)

<a id="bpy.types.FileHandler"></a>

### class bpy.types.FileHandler(bpy_struct)

Extends functionality to operators that manages files, such as adding drag and drop support

<a id="bpy.types.FileHandler.bl_export_operator"></a>

#### bpy.types.FileHandler.bl_export_operator

Operator that can handle export for files with the extensions given in bl_file_extensions (default “”, never None)

**Type:**

str

<a id="bpy.types.FileHandler.bl_file_extensions"></a>

#### bpy.types.FileHandler.bl_file_extensions

Formatted string of file extensions supported by the file handler, each extension should start with a “.” and be separated by “;”.
For Example: `".blend;.ble"`

(default “”, never None)

**Type:**

str

<a id="bpy.types.FileHandler.bl_idname"></a>

#### bpy.types.FileHandler.bl_idname

If this is set, the file handler gets a custom ID, otherwise it takes the name of the class used to define the file handler (for example, if the class name is “OBJECT_FH_hello”, and bl_idname is not set by the script, then bl_idname = “OBJECT_FH_hello”) (default “”, never None)

**Type:**

str

<a id="bpy.types.FileHandler.bl_import_operator"></a>

#### bpy.types.FileHandler.bl_import_operator

Operator that can handle import for files with the extensions given in bl_file_extensions (default “”, never None)

**Type:**

str

<a id="bpy.types.FileHandler.bl_label"></a>

#### bpy.types.FileHandler.bl_label

The file handler label (default “”, never None)

**Type:**

str

<a id="bpy.types.FileHandler.poll_drop"></a>

#### classmethod bpy.types.FileHandler.poll_drop(context)

If this method returns True, can be used to handle the drop of a drag-and-drop action

**Parameters:**

**context** ([`Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context") | None) – The context

**Return type:**

bool

<a id="bpy.types.FileHandler.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FileHandler.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FileHandler.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FileHandler.bl_rna_get_subclass_py(id, default=None, /)

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
