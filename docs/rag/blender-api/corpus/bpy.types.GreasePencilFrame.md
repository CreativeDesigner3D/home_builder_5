<!-- source: Blender Python API reference 5.2 / bpy.types.GreasePencilFrame.html -->

<a id="greasepencilframe-bpy-struct"></a>

# GreasePencilFrame(bpy_struct)

base class — [`bpy_struct`](bpy.types.bpy_struct.md#bpy.types.bpy_struct "bpy.types.bpy_struct")

<a id="bpy.types.GreasePencilFrame"></a>

### class bpy.types.GreasePencilFrame(bpy_struct)

A Grease Pencil keyframe

<a id="bpy.types.GreasePencilFrame.drawing"></a>

#### bpy.types.GreasePencilFrame.drawing

A Grease Pencil drawing

**Type:**

[`GreasePencilDrawing`](bpy.types.GreasePencilDrawing.md#bpy.types.GreasePencilDrawing "bpy.types.GreasePencilDrawing") | None

<a id="bpy.types.GreasePencilFrame.frame_number"></a>

#### bpy.types.GreasePencilFrame.frame_number

The frame number in the scene (in [-1048574, 1048574], default 0, readonly)

**Type:**

int

<a id="bpy.types.GreasePencilFrame.keyframe_type"></a>

#### bpy.types.GreasePencilFrame.keyframe_type

Type of keyframe (default `'KEYFRAME'`)

- `KEYFRAME`
  Keyframe – Normal keyframe, e.g. for key poses.
- `BREAKDOWN`
  Breakdown – A breakdown pose, e.g. for transitions between key poses.
- `MOVING_HOLD`
  Moving Hold – A keyframe that is part of a moving hold.
- `EXTREME`
  Extreme – An ‘extreme’ pose, or some other purpose as needed.
- `JITTER`
  Jitter – A filler or baked keyframe for keying on ones, or some other purpose as needed.
- `GENERATED`
  Generated – A key generated automatically by a tool, not manually created.

**Type:**

Literal[‘KEYFRAME’, ‘BREAKDOWN’, ‘MOVING_HOLD’, ‘EXTREME’, ‘JITTER’, ‘GENERATED’]

<a id="bpy.types.GreasePencilFrame.select"></a>

#### bpy.types.GreasePencilFrame.select

Frame Selection in the Dope Sheet (default False)

**Type:**

bool

<a id="bpy.types.GreasePencilFrame.bl_rna_get_subclass"></a>

#### classmethod bpy.types.GreasePencilFrame.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.GreasePencilFrame.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.GreasePencilFrame.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`GreasePencilFrames.copy`](bpy.types.GreasePencilFrames.md#bpy.types.GreasePencilFrames.copy "bpy.types.GreasePencilFrames.copy") - [`GreasePencilFrames.move`](bpy.types.GreasePencilFrames.md#bpy.types.GreasePencilFrames.move "bpy.types.GreasePencilFrames.move") - [`GreasePencilFrames.new`](bpy.types.GreasePencilFrames.md#bpy.types.GreasePencilFrames.new "bpy.types.GreasePencilFrames.new") | - [`GreasePencilLayer.current_frame`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer.current_frame "bpy.types.GreasePencilLayer.current_frame") - [`GreasePencilLayer.frames`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer.frames "bpy.types.GreasePencilLayer.frames") - [`GreasePencilLayer.get_frame_at`](bpy.types.GreasePencilLayer.md#bpy.types.GreasePencilLayer.get_frame_at "bpy.types.GreasePencilLayer.get_frame_at") |
