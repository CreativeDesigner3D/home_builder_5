<!-- source: Blender Python API reference 5.2 / bpy.types.FreestyleLineSet.html -->

<a id="freestylelineset-bpy-struct"></a>

# FreestyleLineSet(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.FreestyleLineSet"></a>

### class bpy.types.FreestyleLineSet(bpy_struct)

Line set for associating lines and style parameters

<a id="bpy.types.FreestyleLineSet.collection"></a>

#### bpy.types.FreestyleLineSet.collection

A collection of objects based on which feature edges are selected

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.FreestyleLineSet.collection_negation"></a>

#### bpy.types.FreestyleLineSet.collection_negation

Specify either inclusion or exclusion of feature edges belonging to a collection of objects (default `'INCLUSIVE'`)

- `INCLUSIVE`
  Inclusive – Select feature edges belonging to some object in the group.
- `EXCLUSIVE`
  Exclusive – Select feature edges not belonging to any object in the group.

**Type:**

Literal[‘INCLUSIVE’, ‘EXCLUSIVE’]

<a id="bpy.types.FreestyleLineSet.edge_type_combination"></a>

#### bpy.types.FreestyleLineSet.edge_type_combination

Specify a logical combination of selection conditions on feature edge types (default `'OR'`)

- `OR`
  Logical OR – Select feature edges satisfying at least one of edge type conditions.
- `AND`
  Logical AND – Select feature edges satisfying all edge type conditions.

**Type:**

Literal[‘OR’, ‘AND’]

<a id="bpy.types.FreestyleLineSet.edge_type_negation"></a>

#### bpy.types.FreestyleLineSet.edge_type_negation

Specify either inclusion or exclusion of feature edges selected by edge types (default `'INCLUSIVE'`)

- `INCLUSIVE`
  Inclusive – Select feature edges satisfying the given edge type conditions.
- `EXCLUSIVE`
  Exclusive – Select feature edges not satisfying the given edge type conditions.

**Type:**

Literal[‘INCLUSIVE’, ‘EXCLUSIVE’]

<a id="bpy.types.FreestyleLineSet.exclude_border"></a>

#### bpy.types.FreestyleLineSet.exclude_border

Exclude border edges (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.exclude_contour"></a>

#### bpy.types.FreestyleLineSet.exclude_contour

Exclude contours (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.exclude_crease"></a>

#### bpy.types.FreestyleLineSet.exclude_crease

Exclude crease edges (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.exclude_edge_mark"></a>

#### bpy.types.FreestyleLineSet.exclude_edge_mark

Exclude edge marks (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.exclude_external_contour"></a>

#### bpy.types.FreestyleLineSet.exclude_external_contour

Exclude external contours (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.exclude_material_boundary"></a>

#### bpy.types.FreestyleLineSet.exclude_material_boundary

Exclude edges at material boundaries (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.exclude_ridge_valley"></a>

#### bpy.types.FreestyleLineSet.exclude_ridge_valley

Exclude ridges and valleys (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.exclude_silhouette"></a>

#### bpy.types.FreestyleLineSet.exclude_silhouette

Exclude silhouette edges (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.exclude_suggestive_contour"></a>

#### bpy.types.FreestyleLineSet.exclude_suggestive_contour

Exclude suggestive contours (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.face_mark_condition"></a>

#### bpy.types.FreestyleLineSet.face_mark_condition

Specify a feature edge selection condition based on face marks (default `'ONE'`)

- `ONE`
  One Face – Select a feature edge if either of its adjacent faces is marked.
- `BOTH`
  Both Faces – Select a feature edge if both of its adjacent faces are marked.

**Type:**

Literal[‘ONE’, ‘BOTH’]

<a id="bpy.types.FreestyleLineSet.face_mark_negation"></a>

#### bpy.types.FreestyleLineSet.face_mark_negation

Specify either inclusion or exclusion of feature edges selected by face marks (default `'INCLUSIVE'`)

- `INCLUSIVE`
  Inclusive – Select feature edges satisfying the given face mark conditions.
- `EXCLUSIVE`
  Exclusive – Select feature edges not satisfying the given face mark conditions.

**Type:**

Literal[‘INCLUSIVE’, ‘EXCLUSIVE’]

<a id="bpy.types.FreestyleLineSet.linestyle"></a>

#### bpy.types.FreestyleLineSet.linestyle

Line style settings (never None)

**Type:**

[`FreestyleLineStyle`](bpy.types.FreestyleLineStyle.md#bpy.types.FreestyleLineStyle "bpy.types.FreestyleLineStyle")

<a id="bpy.types.FreestyleLineSet.name"></a>

#### bpy.types.FreestyleLineSet.name

Line set name (default “”, never None)

**Type:**

str

<a id="bpy.types.FreestyleLineSet.qi_end"></a>

#### bpy.types.FreestyleLineSet.qi_end

Last QI value of the QI range (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineSet.qi_start"></a>

#### bpy.types.FreestyleLineSet.qi_start

First QI value of the QI range (in [0, inf], default 0)

**Type:**

int

<a id="bpy.types.FreestyleLineSet.select_border"></a>

#### bpy.types.FreestyleLineSet.select_border

Select border edges (open mesh edges) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_by_collection"></a>

#### bpy.types.FreestyleLineSet.select_by_collection

Select feature edges based on a collection of objects (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_by_edge_types"></a>

#### bpy.types.FreestyleLineSet.select_by_edge_types

Select feature edges based on edge types (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_by_face_marks"></a>

#### bpy.types.FreestyleLineSet.select_by_face_marks

Select feature edges by face marks (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_by_image_border"></a>

#### bpy.types.FreestyleLineSet.select_by_image_border

Select feature edges by image border (less memory consumption) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_by_visibility"></a>

#### bpy.types.FreestyleLineSet.select_by_visibility

Select feature edges based on visibility (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_contour"></a>

#### bpy.types.FreestyleLineSet.select_contour

Select contours (outer silhouettes of each object) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_crease"></a>

#### bpy.types.FreestyleLineSet.select_crease

Select crease edges (those between two faces making an angle smaller than the Crease Angle) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_edge_mark"></a>

#### bpy.types.FreestyleLineSet.select_edge_mark

Select edge marks (edges annotated by Freestyle edge marks) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_external_contour"></a>

#### bpy.types.FreestyleLineSet.select_external_contour

Select external contours (outer silhouettes of occluding and occluded objects) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_material_boundary"></a>

#### bpy.types.FreestyleLineSet.select_material_boundary

Select edges at material boundaries (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_ridge_valley"></a>

#### bpy.types.FreestyleLineSet.select_ridge_valley

Select ridges and valleys (boundary lines between convex and concave areas of surface) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_silhouette"></a>

#### bpy.types.FreestyleLineSet.select_silhouette

Select silhouettes (edges at the boundary of visible and hidden faces) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.select_suggestive_contour"></a>

#### bpy.types.FreestyleLineSet.select_suggestive_contour

Select suggestive contours (almost silhouette/contour edges) (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.show_render"></a>

#### bpy.types.FreestyleLineSet.show_render

Enable or disable this line set during stroke rendering (default False)

**Type:**

bool

<a id="bpy.types.FreestyleLineSet.visibility"></a>

#### bpy.types.FreestyleLineSet.visibility

Determine how to use visibility for feature edge selection (default `'VISIBLE'`)

- `VISIBLE`
  Visible – Select visible feature edges.
- `HIDDEN`
  Hidden – Select hidden feature edges.
- `RANGE`
  Quantitative Invisibility – Select feature edges within a range of quantitative invisibility (QI) values.

**Type:**

Literal[‘VISIBLE’, ‘HIDDEN’, ‘RANGE’]

<a id="bpy.types.FreestyleLineSet.bl_rna_get_subclass"></a>

#### classmethod bpy.types.FreestyleLineSet.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.FreestyleLineSet.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.FreestyleLineSet.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`Linesets.active`](bpy.types.Linesets.md#bpy.types.Linesets.active "bpy.types.Linesets.active") - [`Linesets.new`](bpy.types.Linesets.md#bpy.types.Linesets.new "bpy.types.Linesets.new") | - [`Linesets.remove`](bpy.types.Linesets.md#bpy.types.Linesets.remove "bpy.types.Linesets.remove") - [`FreestyleSettings.linesets`](bpy.types.FreestyleSettings.md#bpy.types.FreestyleSettings.linesets "bpy.types.FreestyleSettings.linesets") |
