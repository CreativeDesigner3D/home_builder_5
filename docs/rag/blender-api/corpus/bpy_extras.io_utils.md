<!-- source: Blender Python API reference 5.2 / bpy_extras.io_utils.html -->

<a id="module-bpy_extras.io_utils"></a>

# bpy_extras submodule (bpy_extras.io_utils)

<a id="bpy_extras.io_utils.orientation_helper"></a>

### bpy_extras.io_utils.orientation_helper(axis_forward='Y', axis_up='Z')

A decorator for import/export classes, generating properties needed by the axis conversion system and IO helpers,
with specified default values (axes).

**Parameters:**

- **axis_forward** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – The default forward axis.
- **axis_up** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – The default up axis.

**Returns:**

A class decorator.

**Return type:**

Callable[[type], type]

<a id="bpy_extras.io_utils.axis_conversion"></a>

### bpy_extras.io_utils.axis_conversion(from_forward='Y', from_up='Z', to_forward='Y', to_up='Z')

Each argument is an axis
where the first 2 are a source and the second 2 are the target.

**Parameters:**

- **from_forward** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Source forward axis.
- **from_up** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Source up axis.
- **to_forward** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Target forward axis.
- **to_up** (Literal['X', 'Y', 'Z', '-X', '-Y', '-Z']) – Target up axis.

**Returns:**

The conversion matrix.

**Return type:**

[`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")

<a id="bpy_extras.io_utils.axis_conversion_ensure"></a>

### bpy_extras.io_utils.axis_conversion_ensure(operator, forward_attr, up_attr)

Function to ensure an operator has valid axis conversion settings, intended
to be used from [`bpy.types.Operator.check`](bpy.types.Operator.md#bpy.types.Operator.check "bpy.types.Operator.check").

**Parameters:**

- **operator** ([`bpy.types.Operator`](bpy.types.Operator.md#bpy.types.Operator "bpy.types.Operator")) – the operator to access axis attributes from.
- **forward_attr** (str) – attribute storing the forward axis
- **up_attr** (str) – attribute storing the up axis

**Returns:**

True if the value was modified.

**Return type:**

bool

<a id="bpy_extras.io_utils.create_derived_objects"></a>

### bpy_extras.io_utils.create_derived_objects(depsgraph, objects)

This function takes a sequence of objects, returning their instances.

**Parameters:**

- **depsgraph** ([`bpy.types.Depsgraph`](bpy.types.Depsgraph.md#bpy.types.Depsgraph "bpy.types.Depsgraph")) – The evaluated depsgraph.
- **objects** (Sequence[[`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object")]) – A sequence of objects.

**Returns:**

A dictionary where each key is an object from `objects`,
values are lists of (object, matrix) tuples representing instances.

**Return type:**

dict[[`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object"), list[tuple[[`bpy.types.Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object"), [`mathutils.Matrix`](mathutils.md#mathutils.Matrix "mathutils.Matrix")]]]

<a id="bpy_extras.io_utils.poll_file_object_drop"></a>

### bpy_extras.io_utils.poll_file_object_drop(context)

A default implementation for FileHandler poll_drop methods. Allows for both the 3D Viewport and
the Outliner (in ViewLayer display mode) to be targets for file drag and drop.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

Whether the drop target is valid.

**Return type:**

bool

<a id="bpy_extras.io_utils.unpack_list"></a>

### bpy_extras.io_utils.unpack_list(list_of_tuples)

Flatten a sequence of tuples into a single list.

**Parameters:**

**list_of_tuples** (Sequence[tuple]) – A sequence of tuples to unpack.

**Returns:**

A flat list of all values.

**Return type:**

list

<a id="bpy_extras.io_utils.unpack_face_list"></a>

### bpy_extras.io_utils.unpack_face_list(list_of_tuples)

Unpack a list of faces (triangles or quads) into a flat list,
padding triangles with a zero to fit into groups of four.

**Parameters:**

**list_of_tuples** (Sequence[tuple[int, ...]]) – A sequence of face index tuples (3 or 4 elements each).

**Returns:**

A flat list of face indices, padded with zeros.

**Return type:**

list[int]

<a id="bpy_extras.io_utils.path_reference"></a>

### bpy_extras.io_utils.path_reference(filepath, base_src, base_dst, mode='AUTO', copy_subdir='', copy_set=None, library=None)

Return a filepath relative to a destination directory, for use with
exporters.

**Parameters:**

- **filepath** (str) – the file path to return,
  supporting blenders relative ‘//’ prefix.
- **base_src** (str) – the directory the filepath is relative to
  (normally the blend file).
- **base_dst** (str) – the directory the filepath will be referenced from
  (normally the export path).
- **mode** (Literal['AUTO', 'ABSOLUTE', 'RELATIVE', 'MATCH', 'STRIP', 'COPY']) – the method used to reference the path.
- **copy_subdir** (str) – the subdirectory of base_dst to use when mode=’COPY’.
- **copy_set** (set[tuple[str, str]] | None) – collect from/to pairs when mode=’COPY’,
  pass to path_reference_copy when exporting is done.
- **library** ([`bpy.types.Library`](bpy.types.Library.md#bpy.types.Library "bpy.types.Library") | None) – The library this path is relative to.

**Returns:**

the new filepath.

**Return type:**

str

<a id="bpy_extras.io_utils.path_reference_copy"></a>

### bpy_extras.io_utils.path_reference_copy(copy_set, report=print)

Execute copying files of path_reference

**Parameters:**

- **copy_set** (set[tuple[str, str]]) – set of (from, to) pairs to copy.
- **report** (Callable[[str], None]) – function used for reporting warnings, takes a string argument.

<a id="bpy_extras.io_utils.unique_name"></a>

### bpy_extras.io_utils.unique_name(key, name, name_dict, name_max=-1, clean_func=None, sep='.')

Helper function for storing unique names which may have special characters
stripped and restricted to a maximum length.

**Parameters:**

- **key** (Any) – Unique item this name belongs to, name_dict[key] will be reused
  when available.
  This can be the object, mesh, material, etc instance itself.
  Any hashable object associated with the name.
- **name** (str) – The name used to create a unique value in name_dict.
- **name_dict** (dict[Any, str]) – This is used to cache namespace to ensure no collisions
  occur, this should be an empty dict initially and only modified by this
  function.
- **name_max** (int) – Maximum length of the name. When `-1` the name is unlimited.
- **clean_func** (Callable[[str], str] | None) – Function to call on name before creating a unique value.
- **sep** (str) – Separator to use when between the name and a number when a
  duplicate name is found.

**Returns:**

A unique name.

**Return type:**

str

<a id="bpy_extras.io_utils.ExportHelper"></a>

### class bpy_extras.io_utils.ExportHelper

<a id="bpy_extras.io_utils.ExportHelper.check"></a>

#### bpy_extras.io_utils.ExportHelper.check(context)

Validate the filepath and axis conversion settings.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

True when a property was updated.

**Return type:**

bool

<a id="bpy_extras.io_utils.ExportHelper.invoke"></a>

#### bpy_extras.io_utils.ExportHelper.invoke(context, event)

Invoke the file selector for exporting, setting a default filepath
based on the current blend file name.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **event** ([`bpy.types.Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event")) – The window event.

**Returns:**

The operator return value.

**Return type:**

set[str]

<a id="bpy_extras.io_utils.ImportHelper"></a>

### class bpy_extras.io_utils.ImportHelper

<a id="bpy_extras.io_utils.ImportHelper.check"></a>

#### bpy_extras.io_utils.ImportHelper.check(context)

Validate axis conversion settings.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

True when a property was updated.

**Return type:**

bool

<a id="bpy_extras.io_utils.ImportHelper.invoke"></a>

#### bpy_extras.io_utils.ImportHelper.invoke(context, event)

Invoke the file selector for importing.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **event** ([`bpy.types.Event`](bpy.types.Event.md#bpy.types.Event "bpy.types.Event")) – The window event.

**Returns:**

The operator return value.

**Return type:**

set[str]

<a id="bpy_extras.io_utils.ImportHelper.invoke_popup"></a>

#### bpy_extras.io_utils.ImportHelper.invoke_popup(context, confirm_text='')

Invoke as a popup confirmation dialog when a filepath is already set,
otherwise fall back to the file selector.

**Parameters:**

- **context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.
- **confirm_text** (str) – Label for the confirm button,
  defaults to the operator label.

**Returns:**

The operator return value.

**Return type:**

set[str]
