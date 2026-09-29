<!-- source: Blender Python API reference 5.2 / bpy.ops.render.html -->

<a id="module-bpy.ops.render"></a>

# Render Operators

<a id="bpy.ops.render.clear_texture_cache"></a>

### bpy.ops.render.clear_texture_cache()

Delete Cycles texture cache files from disk

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.render.color_management_white_balance_preset_add"></a>

### bpy.ops.render.color_management_white_balance_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove a white balance preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.render.cycles_integrator_preset_add"></a>

### bpy.ops.render.cycles_integrator_preset_add(*, name='', remove_name=False, remove_active=False)

Add an Integrator Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.render.cycles_performance_preset_add"></a>

### bpy.ops.render.cycles_performance_preset_add(*, name='', remove_name=False, remove_active=False)

Add an Performance Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.render.cycles_sampling_preset_add"></a>

### bpy.ops.render.cycles_sampling_preset_add(*, name='', remove_name=False, remove_active=False)

Add a Sampling Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.render.cycles_viewport_sampling_preset_add"></a>

### bpy.ops.render.cycles_viewport_sampling_preset_add(*, name='', remove_name=False, remove_active=False)

Add a Viewport Sampling Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.render.eevee_raytracing_preset_add"></a>

### bpy.ops.render.eevee_raytracing_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove an EEVEE ray-tracing preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.render.generate_texture_cache"></a>

### bpy.ops.render.generate_texture_cache(*, generate_sequences=True)

Generate Cycles texture cache files for all images used in shader nodes

**Parameters:**

**generate_sequences** (bool) – Image Sequences, Generate texture cache files for all frames of image sequences (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.render.opengl"></a>

### bpy.ops.render.opengl(*, animation=False, render_keyed_only=False, sequencer=False, write_still=False, view_context=True)

Take a snapshot of the active viewport

**Parameters:**

- **animation** (bool) – Animation, Render files from the animation range of this scene (optional)
- **render_keyed_only** (bool) – Render Keyframes Only, Render only those frames where selected objects have a key in their animation data. Only used when rendering animation (optional)
- **sequencer** (bool) – Sequencer, Render using the sequencer’s OpenGL display (optional)
- **write_still** (bool) – Write Image, Save the rendered image to the output path (used only when animation is disabled) (optional)
- **view_context** (bool) – View Context, Use the current 3D view for rendering, else use scene settings (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.render.play_rendered_anim"></a>

### bpy.ops.render.play_rendered_anim()

Play back rendered frames/movies using an external player

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/screen_play_rendered_anim.py:137](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/screen_play_rendered_anim.py#L137)

<a id="bpy.ops.render.preset_add"></a>

### bpy.ops.render.preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove a Render Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.render.render"></a>

### bpy.ops.render.render(*, animation=False, write_still=False, use_viewport=False, use_sequencer_scene=False, layer='', scene='', frame_start=0, frame_end=0)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **animation** (bool) – Animation, Render files from the animation range of this scene (optional)
- **write_still** (bool) – Write Image, Save the rendered image to the output path (used only when animation is disabled) (optional)
- **use_viewport** (bool) – Use 3D Viewport, When inside a 3D viewport, use layers and camera of the viewport (optional)
- **use_sequencer_scene** (bool) – Use Sequencer Scene, Render the sequencer scene instead of the active scene (optional)
- **layer** (str) – Render Layer, Single render layer to re-render (used only when animation is disabled) (optional, never None)
- **scene** (str) – Scene, Scene to render, current scene if not specified (optional, never None)
- **frame_start** (int) – Start Frame, Frame to start rendering animation at. If not specified, the scene start frame will be assumed. This should only be specified if doing an animation render (in [-inf, inf], optional)
- **frame_end** (int) – End Frame, Frame to end rendering animation at. If not specified, the scene end frame will be assumed. This should only be specified if doing an animation render (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.render.shutter_curve_preset"></a>

### bpy.ops.render.shutter_curve_preset(*, shape='SMOOTH')

Set shutter curve

**Parameters:**

**shape** (Literal['SHARP', 'SMOOTH', 'MAX', 'LINE', 'ROUND', 'ROOT']) – Mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.render.swap_dimensions"></a>

### bpy.ops.render.swap_dimensions()

Flip X and Y resolutions

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/render.py:14](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/render.py#L14)

<a id="bpy.ops.render.view_cancel"></a>

### bpy.ops.render.view_cancel()

Cancel showing the render view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.render.view_show"></a>

### bpy.ops.render.view_show()

Toggle show render view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
