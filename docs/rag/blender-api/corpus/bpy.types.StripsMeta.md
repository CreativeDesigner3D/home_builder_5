<!-- source: Blender Python API reference 5.2 / bpy.types.StripsMeta.html -->

<a id="stripsmeta-bpy-prop-collection"></a>

# StripsMeta(bpy_prop_collection)

base class — [`bpy_prop_collection`](bpy.types.bpy_prop_collection.md#bpy.types.bpy_prop_collection "bpy.types.bpy_prop_collection")

<a id="bpy.types.StripsMeta"></a>

### class bpy.types.StripsMeta(bpy_prop_collection)

Collection of Strips

<a id="bpy.types.StripsMeta.new_clip"></a>

#### bpy.types.StripsMeta.new_clip(name, clip, channel, frame_start)

Add a new movie clip strip

**Parameters:**

- **name** (str) – Name for the new strip (never None)
- **clip** ([`MovieClip`](bpy.types.MovieClip.md#bpy.types.MovieClip "bpy.types.MovieClip") | None) – Movie clip to add (never None)
- **channel** (int) – Channel, The channel for the new strip (in [1, 128])
- **frame_start** (int) – The start frame for the new strip (in [-1048574, 1048574])

**Returns:**

New Strip

**Return type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.StripsMeta.new_mask"></a>

#### bpy.types.StripsMeta.new_mask(name, mask, channel, frame_start)

Add a new mask strip

**Parameters:**

- **name** (str) – Name for the new strip (never None)
- **mask** ([`Mask`](bpy.types.Mask.md#bpy.types.Mask "bpy.types.Mask") | None) – Mask to add (never None)
- **channel** (int) – Channel, The channel for the new strip (in [1, 128])
- **frame_start** (int) – The start frame for the new strip (in [-1048574, 1048574])

**Returns:**

New Strip

**Return type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.StripsMeta.new_scene"></a>

#### bpy.types.StripsMeta.new_scene(name, scene, channel, frame_start)

Add a new scene strip

**Parameters:**

- **name** (str) – Name for the new strip (never None)
- **scene** ([`Scene`](bpy.types.Scene.md#bpy.types.Scene "bpy.types.Scene") | None) – Scene to add (never None)
- **channel** (int) – Channel, The channel for the new strip (in [1, 128])
- **frame_start** (int) – The start frame for the new strip (in [-1048574, 1048574])

**Returns:**

New Strip

**Return type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.StripsMeta.new_image"></a>

#### bpy.types.StripsMeta.new_image(name, filepath, channel, frame_start, *, fit_method='ORIGINAL')

Add a new image strip

**Parameters:**

- **name** (str) – Name for the new strip (never None)
- **filepath** (str) – Filepath to image (never None)
- **channel** (int) – Channel, The channel for the new strip (in [1, 128])
- **frame_start** (int) – The start frame for the new strip (in [-1048574, 1048574])
- **fit_method** (Literal[[Strip Scale Method Items](bpy_types_enum_items/strip_scale_method_items.md#rna-enum-strip-scale-method-items)]) – Image Fit Method, Mode for fitting the image to the canvas (optional)

**Returns:**

New Strip

**Return type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.StripsMeta.new_movie"></a>

#### bpy.types.StripsMeta.new_movie(name, filepath, channel, frame_start, *, fit_method='ORIGINAL', stream=0)

Add a new movie strip

**Parameters:**

- **name** (str) – Name for the new strip (never None)
- **filepath** (str) – Filepath to movie (never None)
- **channel** (int) – Channel, The channel for the new strip (in [1, 128])
- **frame_start** (int) – The start frame for the new strip (in [-1048574, 1048574])
- **fit_method** (Literal[[Strip Scale Method Items](bpy_types_enum_items/strip_scale_method_items.md#rna-enum-strip-scale-method-items)]) – Image Fit Method, Mode for fitting the image to the canvas (optional)
- **stream** (int) – Stream, Stream index for multi-stream files (in [0, 32767], optional)

**Returns:**

New Strip

**Return type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.StripsMeta.new_sound"></a>

#### bpy.types.StripsMeta.new_sound(name, filepath, channel, frame_start, *, stream=0)

Add a new sound strip

**Parameters:**

- **name** (str) – Name for the new strip (never None)
- **filepath** (str) – Filepath to movie (never None)
- **channel** (int) – Channel, The channel for the new strip (in [1, 128])
- **frame_start** (int) – The start frame for the new strip (in [-1048574, 1048574])
- **stream** (int) – Stream, Stream index for multi-stream files (in [0, 32767], optional)

**Returns:**

New Strip

**Return type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.StripsMeta.new_meta"></a>

#### bpy.types.StripsMeta.new_meta(name, channel, frame_start)

Add a new meta strip

**Parameters:**

- **name** (str) – Name for the new strip (never None)
- **channel** (int) – Channel, The channel for the new strip (in [1, 128])
- **frame_start** (int) – The start frame for the new strip (in [-1048574, 1048574])

**Returns:**

New Strip

**Return type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.StripsMeta.new_effect"></a>

#### bpy.types.StripsMeta.new_effect(name, type, channel, frame_start, *, length=0, input1=None, input2=None)

Add a new effect strip

**Parameters:**

- **name** (str) – Name for the new strip (never None)
- **type** (Literal['CROSS', 'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER', 'GAMMA_CROSS', 'COMPOSITOR', 'MULTIPLY', 'WIPE', 'GLOW', 'COLOR', 'SPEED', 'MULTICAM', 'ADJUSTMENT', 'GAUSSIAN_BLUR', 'TEXT', 'COLORMIX']) –

  Type, type for the new strip

  - `CROSS`
    Crossfade – Fade out of one video, fading into another.
  - `ADD`
    Add – Add together color channels from two videos.
  - `SUBTRACT`
    Subtract – Subtract one strip’s color from another.
  - `ALPHA_OVER`
    Alpha Over – Blend alpha on top of another video.
  - `ALPHA_UNDER`
    Alpha Under – Blend alpha below another video.
  - `GAMMA_CROSS`
    Gamma Crossfade – Crossfade with color correction.
  - `COMPOSITOR`
    Compositor – Compositor based effect.
  - `MULTIPLY`
    Multiply – Multiply color channels from two videos.
  - `WIPE`
    Wipe – Sweep a transition line across the frame.
  - `GLOW`
    Glow – Add blur and brightness to light areas.
  - `COLOR`
    Color – Add a simple color strip.
  - `SPEED`
    Speed – Timewarp video strips, modifying playback speed.
  - `MULTICAM`
    Multicam Selector – Control active camera angles.
  - `ADJUSTMENT`
    Adjustment Layer – Apply nondestructive effects.
  - `GAUSSIAN_BLUR`
    Gaussian Blur – Soften details along axes.
  - `TEXT`
    Text – Add a simple text strip.
  - `COLORMIX`
    Color Mix – Combine two strips using blend modes.
- **channel** (int) – Channel, The channel for the new strip (in [1, 128])
- **frame_start** (int) – The start frame for the new strip (in [-inf, inf])
- **length** (int) – Length of the strip in frames, or the length of each strip if multiple are added (in [-inf, inf], optional)
- **input1** ([`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip") | None) – First input strip for effect (optional)
- **input2** ([`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip") | None) – Second input strip for effect (optional)

**Returns:**

New Strip

**Return type:**

[`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip")

<a id="bpy.types.StripsMeta.remove"></a>

#### bpy.types.StripsMeta.remove(sequence)

Remove a Strip

**Parameters:**

**sequence** ([`Strip`](bpy.types.Strip.md#bpy.types.Strip "bpy.types.Strip") | None) – Strip to remove (never None)

<a id="bpy.types.StripsMeta.bl_rna_get_subclass"></a>

#### classmethod bpy.types.StripsMeta.bl_rna_get_subclass(id, default=None, /)

**Parameters:**

- **id** (str) – The RNA type identifier.
- **default** ([`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct") | None) – The value to return when not found.

**Returns:**

The RNA type or default when not found.

**Return type:**

[`bpy.types.Struct`](bpy.types.Struct.md#bpy.types.Struct "bpy.types.Struct")

<a id="bpy.types.StripsMeta.bl_rna_get_subclass_py"></a>

#### classmethod bpy.types.StripsMeta.bl_rna_get_subclass_py(id, default=None, /)

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
| - [`MetaStrip.strips`](bpy.types.MetaStrip.md#bpy.types.MetaStrip.strips "bpy.types.MetaStrip.strips") |  |
