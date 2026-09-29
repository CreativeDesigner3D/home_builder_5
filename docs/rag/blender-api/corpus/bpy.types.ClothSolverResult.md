<!-- source: Blender Python API reference 5.2 / bpy.types.ClothSolverResult.html -->

<a id="clothsolverresult-bpy-struct"></a>

# ClothSolverResult(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.ClothSolverResult"></a>

### class bpy.types.ClothSolverResult(bpy_struct)

Result of cloth solver iteration

<a id="bpy.types.ClothSolverResult.avg_error"></a>

#### bpy.types.ClothSolverResult.avg_error

Average error during substeps (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.ClothSolverResult.avg_iterations"></a>

#### bpy.types.ClothSolverResult.avg_iterations

Average iterations during substeps (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.ClothSolverResult.max_error"></a>

#### bpy.types.ClothSolverResult.max_error

Maximum error during substeps (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.ClothSolverResult.max_iterations"></a>

#### bpy.types.ClothSolverResult.max_iterations

Maximum iterations during substeps (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.ClothSolverResult.min_error"></a>

#### bpy.types.ClothSolverResult.min_error

Minimum error during substeps (in [-inf, inf], default 0.0, readonly)

**Type:**

float

<a id="bpy.types.ClothSolverResult.min_iterations"></a>

#### bpy.types.ClothSolverResult.min_iterations

Minimum iterations during substeps (in [-inf, inf], default 0, readonly)

**Type:**

int

<a id="bpy.types.ClothSolverResult.status"></a>

#### bpy.types.ClothSolverResult.status

Status of the solver iteration (default set(), readonly)

- `SUCCESS`
  Success – Computation was successful.
- `NUMERICAL_ISSUE`
  Numerical Issue – The provided data did not satisfy the prerequisites.
- `NO_CONVERGENCE`
  No Convergence – Iterative procedure did not converge.
- `INVALID_INPUT`
  Invalid Input – The inputs are invalid, or the algorithm has been improperly called.

**Type:**

set[Literal[‘SUCCESS’, ‘NUMERICAL_ISSUE’, ‘NO_CONVERGENCE’, ‘INVALID_INPUT’]]

<a id="bpy.types.ClothSolverResult.bl_rna_get_subclass"></a>

#### classmethod bpy.types.ClothSolverResult.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.ClothSolverResult.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.ClothSolverResult.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`ClothModifier.solver_result`](bpy.types.ClothModifier.md#bpy.types.ClothModifier.solver_result "bpy.types.ClothModifier.solver_result") |  |
