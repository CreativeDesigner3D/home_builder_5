<!-- source: Blender Python API reference 5.2 / bpy.types.AnnotationLayer.html -->

<a id="annotationlayer-bpy-struct"></a>

# AnnotationLayer(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.AnnotationLayer"></a>

### class bpy.types.AnnotationLayer(bpy_struct)

Collection of related sketches

<a id="bpy.types.AnnotationLayer.active_frame"></a>

#### bpy.types.AnnotationLayer.active_frame

Frame currently being displayed for this layer (readonly)

**Type:**

[`AnnotationFrame`](bpy.types.AnnotationFrame.md#bpy.types.AnnotationFrame "bpy.types.AnnotationFrame") | None

<a id="bpy.types.AnnotationLayer.annotation_hide"></a>

#### bpy.types.AnnotationLayer.annotation_hide

Set annotation Visibility (default False)

**Type:**

bool

<a id="bpy.types.AnnotationLayer.annotation_onion_after_color"></a>

#### bpy.types.AnnotationLayer.annotation_onion_after_color

Base color for ghosts after the active frame (array of 3 items, in [0, 1], default (0.25, 0.1, 1.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.AnnotationLayer.annotation_onion_after_range"></a>

#### bpy.types.AnnotationLayer.annotation_onion_after_range

Maximum number of frames to show after current frame (in [-1, 120], default 0)

**Type:**

int

<a id="bpy.types.AnnotationLayer.annotation_onion_before_color"></a>

#### bpy.types.AnnotationLayer.annotation_onion_before_color

Base color for ghosts before the active frame (array of 3 items, in [0, 1], default (0.302, 0.851, 0.302))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.AnnotationLayer.annotation_onion_before_range"></a>

#### bpy.types.AnnotationLayer.annotation_onion_before_range

Maximum number of frames to show before current frame (in [-1, 120], default 0)

**Type:**

int

<a id="bpy.types.AnnotationLayer.annotation_onion_use_custom_color"></a>

#### bpy.types.AnnotationLayer.annotation_onion_use_custom_color

Use custom colors for onion skinning instead of the theme (default False)

**Type:**

bool

<a id="bpy.types.AnnotationLayer.annotation_opacity"></a>

#### bpy.types.AnnotationLayer.annotation_opacity

Annotation Layer Opacity (in [0, 1], default 0.0)

**Type:**

float

<a id="bpy.types.AnnotationLayer.color"></a>

#### bpy.types.AnnotationLayer.color

Color for all strokes in this layer (array of 3 items, in [0, 1], default (0.0, 0.0, 0.0))

**Type:**

[`mathutils.Color`](mathutils.md#mathutils.Color "mathutils.Color")

<a id="bpy.types.AnnotationLayer.frames"></a>

#### bpy.types.AnnotationLayer.frames

Sketches for this layer on different frames (default None, readonly)

**Type:**

[`AnnotationFrames`](bpy.types.AnnotationFrames.md#bpy.types.AnnotationFrames "bpy.types.AnnotationFrames")[[`AnnotationFrame`](bpy.types.AnnotationFrame.md#bpy.types.AnnotationFrame "bpy.types.AnnotationFrame")]

<a id="bpy.types.AnnotationLayer.info"></a>

#### bpy.types.AnnotationLayer.info

Layer name (default “”, never None)

**Type:**

str

<a id="bpy.types.AnnotationLayer.is_ruler"></a>

#### bpy.types.AnnotationLayer.is_ruler

This is a special ruler layer (default False, readonly)

**Type:**

bool

<a id="bpy.types.AnnotationLayer.lock"></a>

#### bpy.types.AnnotationLayer.lock

Protect layer from further editing and/or frame changes (default False)

**Type:**

bool

<a id="bpy.types.AnnotationLayer.lock_frame"></a>

#### bpy.types.AnnotationLayer.lock_frame

Lock current frame displayed by layer (default False)

**Type:**

bool

<a id="bpy.types.AnnotationLayer.select"></a>

#### bpy.types.AnnotationLayer.select

Layer is selected for editing in the Dope Sheet (default False)

**Type:**

bool

<a id="bpy.types.AnnotationLayer.show_in_front"></a>

#### bpy.types.AnnotationLayer.show_in_front

Make the layer display in front of objects (default True)

**Type:**

bool

<a id="bpy.types.AnnotationLayer.thickness"></a>

#### bpy.types.AnnotationLayer.thickness

Thickness of annotation strokes (in [1, 10], default 0)

**Type:**

int

<a id="bpy.types.AnnotationLayer.use_annotation_onion_skinning"></a>

#### bpy.types.AnnotationLayer.use_annotation_onion_skinning

Display annotation onion skins before and after the current frame (default False)

**Type:**

bool

<a id="bpy.types.AnnotationLayer.bl_rna_get_subclass"></a>

#### classmethod bpy.types.AnnotationLayer.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.AnnotationLayer.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.AnnotationLayer.bl_rna_get_subclass_py(id, default=None, /)

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
| - `bpy.context.active_annotation_layer` - [`Annotation.layers`](bpy.types.Annotation.md#bpy.types.Annotation.layers "bpy.types.Annotation.layers") | - [`AnnotationLayers.new`](bpy.types.AnnotationLayers.md#bpy.types.AnnotationLayers.new "bpy.types.AnnotationLayers.new") - [`AnnotationLayers.remove`](bpy.types.AnnotationLayers.md#bpy.types.AnnotationLayers.remove "bpy.types.AnnotationLayers.remove") |
