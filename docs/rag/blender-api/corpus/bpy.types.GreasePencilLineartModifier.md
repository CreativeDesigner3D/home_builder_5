<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilLineartModifier.html -->

<a id="greasepencillineartmodifier-modifier"></a>

# GreasePencilLineartModifier(Modifier)

base classes — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct"), [`Modifier`](bpy.types.Modifier.md#bpy.types.Modifier "bpy.types.Modifier")

<a id="bpy.types.GreasePencilLineartModifier"></a>

### class bpy.types.GreasePencilLineartModifier(Modifier)

Generate Line Art strokes from selected source

<a id="bpy.types.GreasePencilLineartModifier.chaining_image_threshold"></a>

#### bpy.types.GreasePencilLineartModifier.chaining_image_threshold

Segments with an image distance smaller than this will be chained together (in [0, 0.3], default 0.001)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.crease_threshold"></a>

#### bpy.types.GreasePencilLineartModifier.crease_threshold

Angles smaller than this will be treated as creases. Crease angle priority: object Line Art crease override > mesh auto smooth angle > Line Art default crease. (in [0, 3.14159], default 2.44346)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.fill_strokes"></a>

#### bpy.types.GreasePencilLineartModifier.fill_strokes

Generate filled strokes instead of only outline (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.invert_source_vertex_group"></a>

#### bpy.types.GreasePencilLineartModifier.invert_source_vertex_group

Invert source vertex group values (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.is_baked"></a>

#### bpy.types.GreasePencilLineartModifier.is_baked

This modifier has baked data (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.level_end"></a>

#### bpy.types.GreasePencilLineartModifier.level_end

Maximum number of occlusions for the generated strokes (in [0, 128], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilLineartModifier.level_start"></a>

#### bpy.types.GreasePencilLineartModifier.level_start

Minimum number of occlusions for the generated strokes (in [0, 128], default 0)

**Type:**

int

<a id="bpy.types.GreasePencilLineartModifier.light_contour_object"></a>

#### bpy.types.GreasePencilLineartModifier.light_contour_object

Use this light object to generate light contour

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilLineartModifier.opacity"></a>

#### bpy.types.GreasePencilLineartModifier.opacity

The strength value for the generate strokes (in [0, 1], default 1.0)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.overscan"></a>

#### bpy.types.GreasePencilLineartModifier.overscan

A margin to prevent strokes from ending abruptly at the edge of the image (in [0, 0.5], default 0.1)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.radius"></a>

#### bpy.types.GreasePencilLineartModifier.radius

The radius for the generated strokes (in [0, 1], default 0.0025)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.shadow_camera_far"></a>

#### bpy.types.GreasePencilLineartModifier.shadow_camera_far

Far clipping distance of shadow camera (in [0, 10000], default 200.0)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.shadow_camera_near"></a>

#### bpy.types.GreasePencilLineartModifier.shadow_camera_near

Near clipping distance of shadow camera (in [0, 10000], default 0.1)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.shadow_camera_size"></a>

#### bpy.types.GreasePencilLineartModifier.shadow_camera_size

Represents the “Orthographic Scale” of an orthographic camera. If the camera is positioned at the light’s location with this scale, it will represent the coverage of the shadow “camera”. (in [0, 10000], default 200.0)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.shadow_region_filtering"></a>

#### bpy.types.GreasePencilLineartModifier.shadow_region_filtering

Select feature lines that comes from lit or shaded regions. Will not affect cast shadow and light contour since they are at the border. (default `'NONE'`)

- `NONE`
  None – Not filtering any lines based on illumination region.
- `ILLUMINATED`
  Illuminated – Only selecting lines from illuminated regions.
- `SHADED`
  Shaded – Only selecting lines from shaded regions.
- `ILLUMINATED_ENCLOSED`
  Illuminated (Enclosed Shapes) – Selecting lines from lit regions, and make the combination of contour, light contour and shadow lines into enclosed shapes.

**Type:**

Literal[‘NONE’, ‘ILLUMINATED’, ‘SHADED’, ‘ILLUMINATED_ENCLOSED’]

<a id="bpy.types.GreasePencilLineartModifier.silhouette_filtering"></a>

#### bpy.types.GreasePencilLineartModifier.silhouette_filtering

Select contour or silhouette (default `'NONE'`)

**Type:**

Literal[‘NONE’, ‘GROUP’, ‘INDIVIDUAL’]

<a id="bpy.types.GreasePencilLineartModifier.smooth_tolerance"></a>

#### bpy.types.GreasePencilLineartModifier.smooth_tolerance

Strength of smoothing applied on jagged chains (in [0, 30], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.source_camera"></a>

#### bpy.types.GreasePencilLineartModifier.source_camera

Use specified camera object for generating Line Art strokes

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilLineartModifier.source_collection"></a>

#### bpy.types.GreasePencilLineartModifier.source_collection

Generate strokes from the objects in this collection

**Type:**

[`Collection`](bpy.types.Collection.md#bpy.types.Collection "bpy.types.Collection") | None

<a id="bpy.types.GreasePencilLineartModifier.source_object"></a>

#### bpy.types.GreasePencilLineartModifier.source_object

Generate strokes from this object

**Type:**

[`Object`](bpy.types.Object.md#bpy.types.Object "bpy.types.Object") | None

<a id="bpy.types.GreasePencilLineartModifier.source_type"></a>

#### bpy.types.GreasePencilLineartModifier.source_type

Line Art stroke source type (default `'COLLECTION'`)

**Type:**

Literal[‘COLLECTION’, ‘OBJECT’, ‘SCENE’]

<a id="bpy.types.GreasePencilLineartModifier.source_vertex_group"></a>

#### bpy.types.GreasePencilLineartModifier.source_vertex_group

Match the beginning of vertex group names from mesh objects, match all when left empty (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilLineartModifier.split_angle"></a>

#### bpy.types.GreasePencilLineartModifier.split_angle

Angle in screen space below which a stroke is split in two (in [0, 3.14159], default 0.0)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.stroke_depth_offset"></a>

#### bpy.types.GreasePencilLineartModifier.stroke_depth_offset

Move strokes slightly towards the camera to avoid clipping while preserve depth for the viewport (in [-0.1, inf], default 0.05)

**Type:**

float

<a id="bpy.types.GreasePencilLineartModifier.target_layer"></a>

#### bpy.types.GreasePencilLineartModifier.target_layer

Grease Pencil layer to which assign the generated strokes (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilLineartModifier.target_material"></a>

#### bpy.types.GreasePencilLineartModifier.target_material

Grease Pencil material assigned to the generated strokes

**Type:**

[`Material`](bpy.types.Material.md#bpy.types.Material "bpy.types.Material") | None

<a id="bpy.types.GreasePencilLineartModifier.use_back_face_culling"></a>

#### bpy.types.GreasePencilLineartModifier.use_back_face_culling

Remove all back faces to speed up calculation, this will create edges in different occlusion levels than when disabled (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_cache"></a>

#### bpy.types.GreasePencilLineartModifier.use_cache

Use cached scene data from the first Line Art modifier in the stack. Certain settings will be unavailable. (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_clip_plane_boundaries"></a>

#### bpy.types.GreasePencilLineartModifier.use_clip_plane_boundaries

Allow lines generated by the near/far clipping plane to be shown (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_contour"></a>

#### bpy.types.GreasePencilLineartModifier.use_contour

Generate strokes from contours lines (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_crease"></a>

#### bpy.types.GreasePencilLineartModifier.use_crease

Generate strokes from creased edges (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_crease_on_sharp"></a>

#### bpy.types.GreasePencilLineartModifier.use_crease_on_sharp

Allow crease to show on sharp edges (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_crease_on_smooth"></a>

#### bpy.types.GreasePencilLineartModifier.use_crease_on_smooth

Allow crease edges to show inside smooth surfaces (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_custom_camera"></a>

#### bpy.types.GreasePencilLineartModifier.use_custom_camera

Use custom camera instead of the active camera (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_detail_preserve"></a>

#### bpy.types.GreasePencilLineartModifier.use_detail_preserve

Keep the zig-zag “noise” in initial chaining (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_edge_mark"></a>

#### bpy.types.GreasePencilLineartModifier.use_edge_mark

Generate strokes from Freestyle marked edges (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_edge_overlap"></a>

#### bpy.types.GreasePencilLineartModifier.use_edge_overlap

Allow edges in the same location (i.e. from edge split) to show properly. May run slower. (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_face_mark"></a>

#### bpy.types.GreasePencilLineartModifier.use_face_mark

Filter feature lines using Freestyle face marks (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_face_mark_boundaries"></a>

#### bpy.types.GreasePencilLineartModifier.use_face_mark_boundaries

Filter feature lines based on face mark boundaries (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_face_mark_invert"></a>

#### bpy.types.GreasePencilLineartModifier.use_face_mark_invert

Invert face mark filtering (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_face_mark_keep_contour"></a>

#### bpy.types.GreasePencilLineartModifier.use_face_mark_keep_contour

Preserve contour lines while filtering (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_fuzzy_all"></a>

#### bpy.types.GreasePencilLineartModifier.use_fuzzy_all

Treat all lines as the same line type so they can be chained together (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_fuzzy_intersections"></a>

#### bpy.types.GreasePencilLineartModifier.use_fuzzy_intersections

Treat intersection and contour lines as if they were the same type so they can be chained together (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_geometry_space_chain"></a>

#### bpy.types.GreasePencilLineartModifier.use_geometry_space_chain

Use geometry distance for chaining instead of image space (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_image_boundary_trimming"></a>

#### bpy.types.GreasePencilLineartModifier.use_image_boundary_trimming

Trim all edges right at the boundary of image (including overscan region) (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_intersection"></a>

#### bpy.types.GreasePencilLineartModifier.use_intersection

Generate strokes from intersections (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_intersection_mask"></a>

#### bpy.types.GreasePencilLineartModifier.use_intersection_mask

Mask bits to match from Collection Line Art settings (array of 8 items, default (False, False, False, False, False, False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.GreasePencilLineartModifier.use_intersection_match"></a>

#### bpy.types.GreasePencilLineartModifier.use_intersection_match

Require matching all intersection masks instead of just one (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_invert_collection"></a>

#### bpy.types.GreasePencilLineartModifier.use_invert_collection

Select everything except lines from specified collection (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_invert_silhouette"></a>

#### bpy.types.GreasePencilLineartModifier.use_invert_silhouette

Select anti-silhouette lines (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_light_contour"></a>

#### bpy.types.GreasePencilLineartModifier.use_light_contour

Generate light/shadow separation lines from a reference light object (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_loose"></a>

#### bpy.types.GreasePencilLineartModifier.use_loose

Generate strokes from loose edges (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_loose_as_contour"></a>

#### bpy.types.GreasePencilLineartModifier.use_loose_as_contour

Loose edges will have contour type (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_loose_edge_chain"></a>

#### bpy.types.GreasePencilLineartModifier.use_loose_edge_chain

Allow loose edges to be chained together (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_material"></a>

#### bpy.types.GreasePencilLineartModifier.use_material

Generate strokes from borders between materials (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_material_mask"></a>

#### bpy.types.GreasePencilLineartModifier.use_material_mask

Use material masks to filter out occluded strokes (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_material_mask_bits"></a>

#### bpy.types.GreasePencilLineartModifier.use_material_mask_bits

Mask bits to match from Material Line Art settings (array of 8 items, default (False, False, False, False, False, False, False, False))

**Type:**

[`bpy_prop_array`](bpy.types.bpy_prop_array.md#bpy.types.bpy_prop_array "bpy.types.bpy_prop_array")[bool]

<a id="bpy.types.GreasePencilLineartModifier.use_material_mask_match"></a>

#### bpy.types.GreasePencilLineartModifier.use_material_mask_match

Require matching all material masks instead of just one (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_multiple_levels"></a>

#### bpy.types.GreasePencilLineartModifier.use_multiple_levels

Generate strokes from a range of occlusion levels (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_object_instances"></a>

#### bpy.types.GreasePencilLineartModifier.use_object_instances

Allow particle objects and face/vertex instances to show in Line Art (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_offset_towards_custom_camera"></a>

#### bpy.types.GreasePencilLineartModifier.use_offset_towards_custom_camera

Offset strokes towards selected camera instead of the active camera (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_output_vertex_group_match_by_name"></a>

#### bpy.types.GreasePencilLineartModifier.use_output_vertex_group_match_by_name

Match output vertex group based on name (default True)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_overlap_edge_type_support"></a>

#### bpy.types.GreasePencilLineartModifier.use_overlap_edge_type_support

Allow an edge to have multiple overlapping types. This will create a separate stroke for each overlapping type. (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.use_shadow"></a>

#### bpy.types.GreasePencilLineartModifier.use_shadow

Project contour lines using a light source object (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilLineartModifier.vertex_group"></a>

#### bpy.types.GreasePencilLineartModifier.vertex_group

Vertex group name for selected strokes (default “”, never None)

**Type:**

str

<a id="bpy.types.GreasePencilLineartModifier.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilLineartModifier.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilLineartModifier.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilLineartModifier.bl_rna_get_subclass_py(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** (type | None) – The value to return when not found.

**Returns:**

The class or default when not found.

**Return type:**

type

<a id="inherited-properties"></a>

## Inherited Properties

bpy_struct.id_data, Modifier.name, Modifier.type, Modifier.show_viewport, Modifier.show_render, Modifier.show_in_editmode, Modifier.show_on_cage, Modifier.show_expanded, Modifier.is_active, Modifier.use_pin_to_last, Modifier.is_override_data, Modifier.use_apply_on_spline, Modifier.execution_time, Modifier.persistent_uid

<a id="inherited-functions"></a>

## Inherited Functions

bpy_struct.as_pointer, bpy_struct.driver_add, bpy_struct.driver_remove, bpy_struct.get, bpy_struct.id_properties_clear, bpy_struct.id_properties_ensure, bpy_struct.id_properties_ui, bpy_struct.is_property_hidden, bpy_struct.is_property_overridable_library, bpy_struct.is_property_readonly, bpy_struct.is_property_set, bpy_struct.items, bpy_struct.keyframe_delete, bpy_struct.keyframe_insert, bpy_struct.keys, bpy_struct.path_from_id, bpy_struct.path_from_module, bpy_struct.path_resolve, bpy_struct.pop, bpy_struct.property_overridable_library_set, bpy_struct.property_unset, bpy_struct.rna_ancestors, bpy_struct.type_recast, bpy_struct.values, Modifier.bl_rna_get_subclass, Modifier.bl_rna_get_subclass_py
