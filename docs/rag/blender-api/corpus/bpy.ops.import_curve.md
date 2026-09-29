<!-- source: Blender Python API reference 5.2 / bpy.ops.import_curve.html -->

<a id="module-bpy.ops.import_curve"></a>

# Import Curve Operators

<a id="bpy.ops.import_curve.svg"></a>

### bpy.ops.import_curve.svg(*, filepath='', filter_glob='*.svg', directory='', files=None)

Load a SVG file

**Parameters:**

- **filepath** (str) – File Path, Filepath used for importing the file (optional, never None)
- **filter_glob** (str) – filter_glob, (optional, never None)
- **directory** (str) – directory, (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – File Path, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_curve_svg/__init__.py:61](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_curve_svg/__init__.py#L61)
