<!-- source: Blender Python API reference 5.2 / bpy.ops.wm.html -->

<a id="module-bpy.ops.wm"></a>

# Wm Operators

<a id="bpy.ops.wm.alembic_export"></a>

### bpy.ops.wm.alembic_export(*, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=True, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', filter_glob='*.abc', start=-2147483648, end=-2147483648, xsamples=1, gsamples=1, sh_open=0.0, sh_close=1.0, selected=False, flatten=False, collection='', uvs=True, packuv=True, normals=True, vcolors=False, orcos=True, face_sets=False, subdiv_schema=False, apply_subdiv=False, curves_as_mesh=False, use_instancing=True, global_scale=1.0, triangulate=False, quad_method='SHORTEST_DIAGONAL', ngon_method='BEAUTY', export_hair=True, export_particles=True, export_custom_properties=True, as_background_job=False, evaluation_mode='RENDER', init_scene_frame_range=True)

Export current scene in an Alembic archive

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **filter_glob** (str) – (optional, never None)
- **start** (int) – Start Frame, Start frame of the export, use the default value to take the start frame of the current scene (in [-inf, inf], optional)
- **end** (int) – End Frame, End frame of the export, use the default value to take the end frame of the current scene (in [-inf, inf], optional)
- **xsamples** (int) – Transform Samples, Number of times per frame transformations are sampled (in [1, 128], optional)
- **gsamples** (int) – Geometry Samples, Number of times per frame object data are sampled (in [1, 128], optional)
- **sh_open** (float) – Shutter Open, Time at which the shutter is open (in [-1, 1], optional)
- **sh_close** (float) – Shutter Close, Time at which the shutter is closed (in [-1, 1], optional)
- **selected** (bool) – Selected Objects Only, Export only selected objects (optional)
- **flatten** (bool) – Flatten Hierarchy, Do not preserve objects’ parent/children relationship (optional)
- **collection** (str) – Collection, (optional, never None)
- **uvs** (bool) – UV Coordinates, Export UV coordinates (optional)
- **packuv** (bool) – Merge UVs, (optional)
- **normals** (bool) – Normals, Export normals (optional)
- **vcolors** (bool) – Color Attributes, Export color attributes (optional)
- **orcos** (bool) – Generated Coordinates, Export undeformed mesh vertex coordinates (optional)
- **face_sets** (bool) – Face Sets, Export per face shading group assignments (optional)
- **subdiv_schema** (bool) – Use Subdivision Schema, Export meshes using Alembic’s subdivision schema (optional)
- **apply_subdiv** (bool) – Apply Subdivision Surface, Export subdivision surfaces as meshes (optional)
- **curves_as_mesh** (bool) – Curves as Mesh, Export curves and NURBS surfaces as meshes (optional)
- **use_instancing** (bool) – Use Instancing, Export data of duplicated objects as Alembic instances; speeds up the export and can be disabled for compatibility with other software (optional)
- **global_scale** (float) – Scale, Value by which to enlarge or shrink the objects with respect to the world’s origin (in [0.0001, 1000], optional)
- **triangulate** (bool) – Triangulate, Export polygons (quads and n-gons) as triangles (optional)
- **quad_method** (Literal[[Modifier Triangulate Quad Method Items](bpy_types_enum_items/modifier_triangulate_quad_method_items.md#rna-enum-modifier-triangulate-quad-method-items)]) – Quad Method, Method for splitting the quads into triangles (optional)
- **ngon_method** (Literal[[Modifier Triangulate Ngon Method Items](bpy_types_enum_items/modifier_triangulate_ngon_method_items.md#rna-enum-modifier-triangulate-ngon-method-items)]) – N-gon Method, Method for splitting the n-gons into triangles (optional)
- **export_hair** (bool) – Export Hair, Exports hair particle systems as animated curves (optional)
- **export_particles** (bool) – Export Particles, Exports non-hair particle systems (optional)
- **export_custom_properties** (bool) – Export Custom Properties, Export custom properties to Alembic .userProperties (optional)
- **as_background_job** (bool) – Run as Background Job, Enable this to run the import in the background, disable to block Blender while importing. This option is deprecated; EXECUTE this operator to run in the foreground, and INVOKE it to run as a background job (optional)
- **evaluation_mode** (Literal['RENDER', 'VIEWPORT']) –

  Settings, Determines visibility of objects, modifier settings, and other areas where there are different settings for viewport and rendering (optional)

  - `RENDER`
    Render – Use Render settings for object visibility, modifier settings, etc.
  - `VIEWPORT`
    Viewport – Use Viewport settings for object visibility, modifier settings, etc.
- **init_scene_frame_range** (bool) – (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.alembic_import"></a>

### bpy.ops.wm.alembic_import(*, filepath='', directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=True, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, relative_path=True, display_type='DEFAULT', sort_method='', filter_glob='*.abc', scale=1.0, set_frame_range=True, validate_meshes=False, always_add_cache_reader=False, is_sequence=False, as_background_job=False)

Load an Alembic archive

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **filter_glob** (str) – (optional, never None)
- **scale** (float) – Scale, Value by which to enlarge or shrink the objects with respect to the world’s origin (in [0.0001, 1000], optional)
- **set_frame_range** (bool) – Set Frame Range, If checked, update scene’s start and end frame to match those of the Alembic archive (optional)
- **validate_meshes** (bool) – Validate Meshes, Ensure the data is valid (when disabled, data may be imported which causes crashes displaying or editing) (optional)
- **always_add_cache_reader** (bool) – Always Add Cache Reader, Add cache modifiers and constraints to imported objects even if they are not animated so that they can be updated when reloading the Alembic archive (optional)
- **is_sequence** (bool) – Is Sequence, Set to true if the cache is split into separate files (optional)
- **as_background_job** (bool) – Run as Background Job, Enable this to run the export in the background, disable to block Blender while exporting. This option is deprecated; EXECUTE this operator to run in the foreground, and INVOKE it to run as a background job (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.append"></a>

### bpy.ops.wm.append(*, filepath='', directory='', filename='', files=None, check_existing=False, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=True, filemode=1, display_type='DEFAULT', sort_method='', link=False, do_reuse_local_id=False, clear_asset_data=False, autoselect=True, active_collection=True, instance_collections=False, instance_object_data=True, set_fake=False, use_recursive=True)

Append from a Library .blend file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **filename** (str) – File Name, Name of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **link** (bool) – Link, Link the objects or data-blocks rather than appending (optional)
- **do_reuse_local_id** (bool) – Re-Use Local Data, Try to re-use previously matching appended data-blocks instead of appending a new copy (optional)
- **clear_asset_data** (bool) – Clear Asset Data, Don’t add asset meta-data or tags from the original data-block (optional)
- **autoselect** (bool) – Select, Select new objects (optional)
- **active_collection** (bool) – Active Collection, Put new objects on the active collection (optional)
- **instance_collections** (bool) – Instance Collections, Create instances for collections, rather than adding them directly to the scene (optional)
- **instance_object_data** (bool) – Instance Object Data, Create instances for object data which are not referenced by any objects (optional)
- **set_fake** (bool) – Fake User, Set “Fake User” for appended items (except objects and collections) (optional)
- **use_recursive** (bool) – Localize All, Localize all appended data, including those indirectly linked from other libraries (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.batch_rename"></a>

### bpy.ops.wm.batch_rename(*, data_type='OBJECT', data_source='SELECT', actions=None)

Rename multiple items at once

**Parameters:**

- **data_type** (Literal['OBJECT', 'COLLECTION', 'MATERIAL', 'MESH', 'CURVE', 'META', 'VOLUME', 'GREASEPENCIL', 'ARMATURE', 'LATTICE', 'LIGHT', 'LIGHT_PROBE', 'CAMERA', 'SPEAKER', 'BONE', 'NODE', 'SEQUENCE_STRIP', 'ACTION_CLIP', 'SCENE', 'BRUSH']) – Type, Type of data to rename (optional)
- **data_source** (Literal['SELECT', 'ALL']) – Source, (optional)
- **actions** (`bpy_prop_collection`[`BatchRenameAction`] | None) – actions, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:3315](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L3315)

<a id="bpy.ops.wm.blend_strings_utf8_validate"></a>

### bpy.ops.wm.blend_strings_utf8_validate()

Check and fix all strings in current .blend file to be valid UTF-8 Unicode (needed for some old, 2.4x area files)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/file.py:289](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/file.py#L289)

<a id="bpy.ops.wm.call_asset_shelf_popover"></a>

### bpy.ops.wm.call_asset_shelf_popover(*, name='')

Open a predefined asset shelf in a popup

**Parameters:**

**name** (str) – Asset Shelf Name, Identifier of the asset shelf to display (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.call_menu"></a>

### bpy.ops.wm.call_menu(*, name='')

Open a predefined menu

**Parameters:**

**name** (str) – Name, Name of the menu (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.call_menu_pie"></a>

### bpy.ops.wm.call_menu_pie(*, name='')

Open a predefined pie menu

**Parameters:**

**name** (str) – Name, Name of the pie menu (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.call_panel"></a>

### bpy.ops.wm.call_panel(*, name='', keep_open=True)

Open a predefined panel

**Parameters:**

- **name** (str) – Name, Name of the menu (optional, never None)
- **keep_open** (bool) – Keep Open, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.clear_recent_files"></a>

### bpy.ops.wm.clear_recent_files(*, remove='ALL')

Clear the recent files list

**Parameters:**

**remove** (Literal['ALL', 'MISSING']) – Remove, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.collection_export_all"></a>

### bpy.ops.wm.collection_export_all()

Invoke all configured exporters for all collections

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.context_collection_boolean_set"></a>

### bpy.ops.wm.context_collection_boolean_set(*, data_path_iter='', data_path_item='', type='TOGGLE')

Set boolean values for a collection of items

**Parameters:**

- **data_path_iter** (str) – data_path_iter, The data path relative to the context, must point to an iterable (optional, never None)
- **data_path_item** (str) – data_path_item, The data path from each iterable to the value (int or float) (optional, never None)
- **type** (Literal['TOGGLE', 'ENABLE', 'DISABLE']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:875](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L875)

<a id="bpy.ops.wm.context_cycle_array"></a>

### bpy.ops.wm.context_cycle_array(*, data_path='', reverse=False)

Set a context array value (useful for cycling the active mesh edit mode)

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **reverse** (bool) – Reverse, Cycle backwards (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:673](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L673)

<a id="bpy.ops.wm.context_cycle_enum"></a>

### bpy.ops.wm.context_cycle_enum(*, data_path='', reverse=False, wrap=False)

Toggle a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **reverse** (bool) – Reverse, Cycle backwards (optional)
- **wrap** (bool) – Wrap, Wrap back to the first/last values (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:624](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L624)

<a id="bpy.ops.wm.context_cycle_int"></a>

### bpy.ops.wm.context_cycle_int(*, data_path='', reverse=False, wrap=False)

Set a context value (useful for cycling active material, shape keys, groups, etc.)

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **reverse** (bool) – Reverse, Cycle backwards (optional)
- **wrap** (bool) – Wrap, Wrap back to the first/last values (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:584](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L584)

<a id="bpy.ops.wm.context_menu_enum"></a>

### bpy.ops.wm.context_menu_enum(*, data_path='')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:703](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L703)

<a id="bpy.ops.wm.context_modal_mouse"></a>

### bpy.ops.wm.context_modal_mouse(*, data_path_iter='', data_path_item='', header_text='', input_scale=0.01, invert=False, initial_x=0)

Adjust arbitrary values with mouse input

**Parameters:**

- **data_path_iter** (str) – data_path_iter, The data path relative to the context, must point to an iterable (optional, never None)
- **data_path_item** (str) – data_path_item, The data path from each iterable to the value (int or float) (optional, never None)
- **header_text** (str) – Header Text, Text to display in header during scale (optional, never None)
- **input_scale** (float) – input_scale, Scale the mouse movement by this value before applying the delta (in [-inf, inf], optional)
- **invert** (bool) – invert, Invert the mouse input (optional)
- **initial_x** (int) – initial_x, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:1023](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L1023)

<a id="bpy.ops.wm.context_pie_enum"></a>

### bpy.ops.wm.context_pie_enum(*, data_path='')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

**data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:735](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L735)

<a id="bpy.ops.wm.context_scale_float"></a>

### bpy.ops.wm.context_scale_float(*, data_path='', value=1.0)

Scale a float context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (float) – Value, Assign value (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:338](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L338)

<a id="bpy.ops.wm.context_scale_int"></a>

### bpy.ops.wm.context_scale_int(*, data_path='', value=1.0, always_step=True)

Scale an int context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (float) – Value, Assign value (in [-inf, inf], optional)
- **always_step** (bool) – Always Step, Always adjust the value by a minimum of 1 when ‘value’ is not 1.0 (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:376](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L376)

<a id="bpy.ops.wm.context_set_boolean"></a>

### bpy.ops.wm.context_set_boolean(*, data_path='', value=True)

Set a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (bool) – Value, Assignment value (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:267](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L267)

<a id="bpy.ops.wm.context_set_enum"></a>

### bpy.ops.wm.context_set_enum(*, data_path='', value='')

Set a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (str) – Value, Assignment value (as a string) (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:267](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L267)

<a id="bpy.ops.wm.context_set_float"></a>

### bpy.ops.wm.context_set_float(*, data_path='', value=0.0, relative=False)

Set a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (float) – Value, Assignment value (in [-inf, inf], optional)
- **relative** (bool) – Relative, Apply relative to the current value (delta) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:267](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L267)

<a id="bpy.ops.wm.context_set_id"></a>

### bpy.ops.wm.context_set_id(*, data_path='', value='')

Set a context value to an ID data-block

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (str) – Value, Assign value (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:817](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L817)

<a id="bpy.ops.wm.context_set_int"></a>

### bpy.ops.wm.context_set_int(*, data_path='', value=0, relative=False)

Set a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (int) – Value, Assign value (in [-inf, inf], optional)
- **relative** (bool) – Relative, Apply relative to the current value (delta) (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:267](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L267)

<a id="bpy.ops.wm.context_set_string"></a>

### bpy.ops.wm.context_set_string(*, data_path='', value='')

Set a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (str) – Value, Assign value (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:267](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L267)

<a id="bpy.ops.wm.context_set_value"></a>

### bpy.ops.wm.context_set_value(*, data_path='', value='')

Set a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value** (str) – Value, Assignment value (as a string) (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:480](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L480)

<a id="bpy.ops.wm.context_toggle"></a>

### bpy.ops.wm.context_toggle(*, data_path='', module='')

Toggle a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **module** (str) – Module, Optionally override the context with a module (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:504](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L504)

<a id="bpy.ops.wm.context_toggle_enum"></a>

### bpy.ops.wm.context_toggle_enum(*, data_path='', value_1='', value_2='')

Toggle a context value

**Parameters:**

- **data_path** (str) – Context Attributes, Context data-path (expanded using visible windows in the current .blend file) (optional, never None)
- **value_1** (str) – Value, Toggle enum (optional, never None)
- **value_2** (str) – Value, Toggle enum (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:545](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L545)

<a id="bpy.ops.wm.debug_menu"></a>

### bpy.ops.wm.debug_menu(*, debug_value=0)

Open a popup to set the debug level

**Parameters:**

**debug_value** (int) – Debug Value, (in [-32768, 32767], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.doc_view"></a>

### bpy.ops.wm.doc_view(*, doc_id='')

Open online reference docs in a web browser

**Parameters:**

**doc_id** (str) – Doc ID, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:1379](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L1379)

<a id="bpy.ops.wm.doc_view_manual"></a>

### bpy.ops.wm.doc_view_manual(*, doc_id='')

Load online manual

**Parameters:**

**doc_id** (str) – Doc ID, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:1352](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L1352)

<a id="bpy.ops.wm.doc_view_manual_ui_context"></a>

### bpy.ops.wm.doc_view_manual_ui_context()

View a context based online manual in a web browser

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.drop_blend_file"></a>

### bpy.ops.wm.drop_blend_file(*, filepath='', use_scripts=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **filepath** (str) – filepath, (optional, never None)
- **use_scripts** (bool) – Trusted Source, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:3736](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L3736)

<a id="bpy.ops.wm.drop_import_file"></a>

### bpy.ops.wm.drop_import_file(*, directory='', files=None)

Operator that allows file handlers to receive file drops

**Parameters:**

- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.fbx_import"></a>

### bpy.ops.wm.fbx_import(*, filepath='', directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', global_scale=1.0, mtl_name_collision_mode='MAKE_UNIQUE', import_colors='SRGB', use_custom_normals=True, use_custom_props=True, use_custom_props_enum_as_string=True, import_subdivision=False, ignore_leaf_bones=False, validate_meshes=True, use_anim=True, anim_offset=1.0, filter_glob='*.fbx')

Import FBX file into current scene

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **global_scale** (float) – Scale, (in [1e-06, 1e+06], optional)
- **mtl_name_collision_mode** (Literal['MAKE_UNIQUE', 'REFERENCE_EXISTING']) –

  Material Name Collision, Behavior when the name of an imported material conflicts with an existing material (optional)

  - `MAKE_UNIQUE`
    Make Unique – Import each FBX material as a unique Blender material.
  - `REFERENCE_EXISTING`
    Reference Existing – If a material with the same name already exists, reference that instead of importing.
- **import_colors** (Literal['NONE', 'SRGB', 'LINEAR']) –

  Vertex Colors, Import vertex color attributes (optional)

  - `NONE`
    None – Do not import color attributes.
  - `SRGB`
    sRGB – Vertex colors in the file are in sRGB color space.
  - `LINEAR`
    Linear – Vertex colors in the file are in linear color space.
- **use_custom_normals** (bool) – Custom Normals, Import custom normals, if available (otherwise Blender will compute them) (optional)
- **use_custom_props** (bool) – Custom Properties, Import user properties as custom properties (optional)
- **use_custom_props_enum_as_string** (bool) – Enums As Strings, Store custom property enumeration values as strings (optional)
- **import_subdivision** (bool) – Subdivision Data, Import FBX subdivision information as subdivision surface modifiers (optional)
- **ignore_leaf_bones** (bool) – Ignore Leaf Bones, Ignore the last bone at the end of each chain (used to mark the length of the previous bone) (optional)
- **validate_meshes** (bool) – Validate Meshes, Ensure the data is valid (when disabled, data may be imported which causes crashes displaying or editing) (optional)
- **use_anim** (bool) – Import Animation, Import FBX animation (optional)
- **anim_offset** (float) – Offset, Offset to apply to animation timestamps, in frames (in [-1e+06, 1e+06], optional)
- **filter_glob** (str) – Extension Filter, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.grease_pencil_export_pdf"></a>

### bpy.ops.wm.grease_pencil_export_pdf(*, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=True, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', use_fill=True, selected_object_type='ACTIVE', frame_mode='ACTIVE', stroke_sample=0.0, use_uniform_width=False)

Export Grease Pencil to PDF

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **use_fill** (bool) – Fill, Export strokes with fill enabled (optional)
- **selected_object_type** (Literal['ACTIVE', 'SELECTED', 'VISIBLE']) –

  Object, Which objects to include in the export (optional)

  - `ACTIVE`
    Active – Include only the active object.
  - `SELECTED`
    Selected – Include selected objects.
  - `VISIBLE`
    Visible – Include all visible objects.
- **frame_mode** (Literal['ACTIVE', 'SELECTED', 'SCENE']) –

  Frames, Which frames to include in the export (optional)

  - `ACTIVE`
    Active – Include only active frame.
  - `SELECTED`
    Selected – Include selected frames.
  - `SCENE`
    Scene – Include all scene frames.
- **stroke_sample** (float) – Sampling, Precision of stroke sampling. Low values mean a more precise result, and zero disables sampling (in [0, 100], optional)
- **use_uniform_width** (bool) – Uniform Width, Export strokes with uniform width (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.grease_pencil_export_svg"></a>

### bpy.ops.wm.grease_pencil_export_svg(*, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=True, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', use_fill=True, selected_object_type='ACTIVE', frame_mode='ACTIVE', stroke_sample=0.0, use_uniform_width=False, use_clip_camera=False)

Export Grease Pencil to SVG

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **use_fill** (bool) – Fill, Export strokes with fill enabled (optional)
- **selected_object_type** (Literal['ACTIVE', 'SELECTED', 'VISIBLE']) –

  Object, Which objects to include in the export (optional)

  - `ACTIVE`
    Active – Include only the active object.
  - `SELECTED`
    Selected – Include selected objects.
  - `VISIBLE`
    Visible – Include all visible objects.
- **frame_mode** (Literal['ACTIVE', 'SELECTED', 'SCENE']) –

  Frames, Which frames to include in the export (optional)

  - `ACTIVE`
    Active – Include only active frame.
  - `SELECTED`
    Selected – Include selected frames.
  - `SCENE`
    Scene – Include all scene frames.
- **stroke_sample** (float) – Sampling, Precision of stroke sampling. Low values mean a more precise result, and zero disables sampling (in [0, 100], optional)
- **use_uniform_width** (bool) – Uniform Width, Export strokes with uniform width (optional)
- **use_clip_camera** (bool) – Clip Camera, Clip drawings to camera size when exporting in camera view (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.grease_pencil_import_svg"></a>

### bpy.ops.wm.grease_pencil_import_svg(*, filepath='', directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=True, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, relative_path=True, display_type='DEFAULT', sort_method='', resolution=10, scale=10.0, use_scene_unit=False, recenter_bounds=True)

Import SVG into Grease Pencil

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **resolution** (int) – Resolution, Resolution of the generated strokes (in [1, 100000], optional)
- **scale** (float) – Scale, Scale of the final strokes (in [1e-06, 1e+06], optional)
- **use_scene_unit** (bool) – Scene Unit, Apply current scene’s unit (as defined by unit scale) to imported data (optional)
- **recenter_bounds** (bool) – Center on Bounds, Center the imported SVG on its bounding box (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.id_linked_relocate"></a>

### bpy.ops.wm.id_linked_relocate(*, id_session_uid=0, filepath='', directory='', filename='', check_existing=False, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=True, filemode=1, relative_path=True, display_type='DEFAULT', sort_method='', link=True, do_reuse_local_id=False, clear_asset_data=False, autoselect=True, active_collection=False, instance_collections=False, instance_object_data=False)

Relocate a linked ID, i.e. select another ID to link, and remap its local usages to that newly linked data-block). Currently only designed as an internal operator, not directly exposed to the user

**Parameters:**

- **id_session_uid** (int) – Linked ID Session UID, Unique runtime identifier for the linked ID to relocate (in [0, inf], optional)
- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **filename** (str) – File Name, Name of the file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **link** (bool) – Link, Link the objects or data-blocks rather than appending (optional)
- **do_reuse_local_id** (bool) – Re-Use Local Data, Try to re-use previously matching appended data-blocks instead of appending a new copy (optional)
- **clear_asset_data** (bool) – Clear Asset Data, Don’t add asset meta-data or tags from the original data-block (optional)
- **autoselect** (bool) – Select, Select new objects (optional)
- **active_collection** (bool) – Active Collection, Put new objects on the active collection (optional)
- **instance_collections** (bool) – Instance Collections, Create instances for collections, rather than adding them directly to the scene (optional)
- **instance_object_data** (bool) – Instance Object Data, Create instances for object data which are not referenced by any objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.interface_theme_preset_add"></a>

### bpy.ops.wm.interface_theme_preset_add(*, name='', remove_name=False, remove_active=False)

Add a custom theme to the preset list

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

<a id="bpy.ops.wm.interface_theme_preset_remove"></a>

### bpy.ops.wm.interface_theme_preset_remove(*, name='', remove_name=False, remove_active=True)

Remove a custom theme from the preset list

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

<a id="bpy.ops.wm.interface_theme_preset_save"></a>

### bpy.ops.wm.interface_theme_preset_save(*, name='', remove_name=False, remove_active=True)

Save a custom theme in the preset list

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:754](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L754)

<a id="bpy.ops.wm.keyconfig_preset_add"></a>

### bpy.ops.wm.keyconfig_preset_add(*, name='', remove_name=False, remove_active=False)

Add a custom keymap configuration to the preset list

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

<a id="bpy.ops.wm.keyconfig_preset_remove"></a>

### bpy.ops.wm.keyconfig_preset_remove(*, name='', remove_name=False, remove_active=True)

Remove a custom keymap configuration from the preset list

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

<a id="bpy.ops.wm.lib_reload"></a>

### bpy.ops.wm.lib_reload(*, library='', filepath='', directory='', filename='', hide_props_region=True, check_existing=False, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, relative_path=True, display_type='DEFAULT', sort_method='')

Reload the given library

**Parameters:**

- **library** (str) – Library, Library to reload (optional, never None)
- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **filename** (str) – File Name, Name of the file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.lib_relocate"></a>

### bpy.ops.wm.lib_relocate(*, library='', filepath='', directory='', filename='', files=None, hide_props_region=True, check_existing=False, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, relative_path=True, display_type='DEFAULT', sort_method='')

Relocate the given library to one or several others

**Parameters:**

- **library** (str) – Library, Library to relocate (optional, never None)
- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **filename** (str) – File Name, Name of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.link"></a>

### bpy.ops.wm.link(*, filepath='', directory='', filename='', files=None, check_existing=False, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=True, filemode=1, relative_path=True, display_type='DEFAULT', sort_method='', link=True, do_reuse_local_id=False, clear_asset_data=False, autoselect=True, active_collection=True, instance_collections=True, instance_object_data=True)

Link from a Library .blend file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **filename** (str) – File Name, Name of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **link** (bool) – Link, Link the objects or data-blocks rather than appending (optional)
- **do_reuse_local_id** (bool) – Re-Use Local Data, Try to re-use previously matching appended data-blocks instead of appending a new copy (optional)
- **clear_asset_data** (bool) – Clear Asset Data, Don’t add asset meta-data or tags from the original data-block (optional)
- **autoselect** (bool) – Select, Select new objects (optional)
- **active_collection** (bool) – Active Collection, Put new objects on the active collection (optional)
- **instance_collections** (bool) – Instance Collections, Create instances for collections, rather than adding them directly to the scene (optional)
- **instance_object_data** (bool) – Instance Object Data, Create instances for object data which are not referenced by any objects (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.memory_statistics"></a>

### bpy.ops.wm.memory_statistics()

Print memory statistics to the console

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.obj_export"></a>

### bpy.ops.wm.obj_export(*, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', export_animation=False, start_frame=-2147483648, end_frame=2147483647, forward_axis='NEGATIVE_Z', up_axis='Y', global_scale=1.0, apply_modifiers=True, apply_transform=True, export_eval_mode='DAG_EVAL_VIEWPORT', export_selected_objects=False, export_uv=True, export_normals=True, export_colors=False, export_materials=True, export_pbr_extensions=False, path_mode='AUTO', export_triangulated_mesh=False, export_curves_as_nurbs=False, export_object_groups=False, export_material_groups=False, export_vertex_groups=False, export_smooth_groups=False, smooth_group_bitflags=False, filter_glob='*.obj;*.mtl', collection='')

Save the scene to a Wavefront OBJ file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **export_animation** (bool) – Export Animation, Export multiple frames instead of the current frame only (optional)
- **start_frame** (int) – Start Frame, The first frame to be exported (in [-inf, inf], optional)
- **end_frame** (int) – End Frame, The last frame to be exported (in [-inf, inf], optional)
- **forward_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Forward Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **up_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Up Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **global_scale** (float) – Scale, Value by which to enlarge or shrink the objects with respect to the world’s origin (in [0.0001, 10000], optional)
- **apply_modifiers** (bool) – Apply Modifiers, Apply modifiers to exported meshes (optional)
- **apply_transform** (bool) – Apply Transform, Apply object transforms to exported vertices (optional)
- **export_eval_mode** (Literal['DAG_EVAL_RENDER', 'DAG_EVAL_VIEWPORT']) –

  Object Properties, Determines properties like object visibility, modifiers etc., where they differ for Render and Viewport (optional)

  - `DAG_EVAL_RENDER`
    Render – Export objects as they appear in render.
  - `DAG_EVAL_VIEWPORT`
    Viewport – Export objects as they appear in the viewport.
- **export_selected_objects** (bool) – Export Selected Objects, Export only selected objects instead of all supported objects (optional)
- **export_uv** (bool) – Export UVs, (optional)
- **export_normals** (bool) – Export Normals, Export per-face normals if the face is flat-shaded, per-face-corner normals if smooth-shaded (optional)
- **export_colors** (bool) – Export Colors, Export per-vertex colors (optional)
- **export_materials** (bool) – Export Materials, Export MTL library. There must be a Principled-BSDF node for image textures to be exported to the MTL file (optional)
- **export_pbr_extensions** (bool) – Export Materials with PBR Extensions, Export MTL library using PBR extensions (roughness, metallic, sheen, coat, anisotropy, transmission) (optional)
- **path_mode** (Literal['AUTO', 'ABSOLUTE', 'RELATIVE', 'MATCH', 'STRIP', 'COPY']) –

  Path Mode, Method used to reference paths (optional)

  - `AUTO`
    Auto – Use relative paths with subdirectories only.
  - `ABSOLUTE`
    Absolute – Always write absolute paths.
  - `RELATIVE`
    Relative – Write relative paths where possible.
  - `MATCH`
    Match – Match absolute/relative setting with input path.
  - `STRIP`
    Strip – Write filename only.
  - `COPY`
    Copy – Copy the file to the destination path.
- **export_triangulated_mesh** (bool) – Export Triangulated Mesh, All ngons with four or more vertices will be triangulated. Meshes in the scene will not be affected. Behaves like Triangulate Modifier with ngon-method: “Beauty”, quad-method: “Shortest Diagonal”, min vertices: 4 (optional)
- **export_curves_as_nurbs** (bool) – Export Curves as NURBS, Export curves in parametric form instead of exporting as mesh (optional)
- **export_object_groups** (bool) – Export Object Groups, Append mesh name to object name, separated by a ‘_’ (optional)
- **export_material_groups** (bool) – Export Material Groups, Generate an OBJ group for each part of a geometry using a different material (optional)
- **export_vertex_groups** (bool) – Export Vertex Groups, Export the name of the vertex group of a face. It is approximated by choosing the vertex group with the most members among the vertices of a face (optional)
- **export_smooth_groups** (bool) – Export Smooth Groups, Generate smooth groups identifiers for each group of smooth faces, as unique integer values by default (optional)
- **smooth_group_bitflags** (bool) – Bitflags Smooth Groups, If exporting smoothgroups, generate ‘bitflags’ values for the groups, instead of unique integer values. The same bitflag value can be re-used for different groups of smooth faces, as long as they have no common sharp edges or vertices (optional)
- **filter_glob** (str) – Extension Filter, (optional, never None)
- **collection** (str) – Collection, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.obj_import"></a>

### bpy.ops.wm.obj_import(*, filepath='', directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', global_scale=1.0, clamp_size=0.0, forward_axis='NEGATIVE_Z', up_axis='Y', use_split_objects=True, use_split_groups=False, import_vertex_groups=False, validate_meshes=True, close_spline_loops=True, collection_separator='', mtl_name_collision_mode='MAKE_UNIQUE', filter_glob='*.obj;*.mtl')

Load a Wavefront OBJ scene

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **global_scale** (float) – Scale, Value by which to enlarge or shrink the objects with respect to the world’s origin (in [0.0001, 10000], optional)
- **clamp_size** (float) – Clamp Bounding Box, Resize the objects to keep bounding box under this value. Value 0 disables clamping (in [0, 1000], optional)
- **forward_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Forward Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **up_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Up Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **use_split_objects** (bool) – Split By Object, Import each OBJ ‘o’ as a separate object (optional)
- **use_split_groups** (bool) – Split By Group, Import each OBJ ‘g’ as a separate object (optional)
- **import_vertex_groups** (bool) – Vertex Groups, Import OBJ groups as vertex groups (optional)
- **validate_meshes** (bool) – Validate Meshes, Ensure the data is valid (when disabled, data may be imported which causes crashes displaying or editing) (optional)
- **close_spline_loops** (bool) – Detect Cyclic Curves, Join curve endpoints if overlapping control points are detected (if disabled, no curves will be cyclic) (optional)
- **collection_separator** (str) – Path Separator, Character used to separate objects name into hierarchical structure (optional, never None)
- **mtl_name_collision_mode** (Literal['MAKE_UNIQUE', 'REFERENCE_EXISTING']) –

  Material Name Collision, How to handle naming collisions when importing materials (optional)

  - `MAKE_UNIQUE`
    Make Unique – Create new materials with unique names for each OBJ file.
  - `REFERENCE_EXISTING`
    Reference Existing – Use existing materials with same name instead of creating new ones.
- **filter_glob** (str) – Extension Filter, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.open_mainfile"></a>

### bpy.ops.wm.open_mainfile(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', load_ui=True, use_scripts=False, display_file_selector=True, state=0)

Open a Blender file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **load_ui** (bool) – Load UI, Load user interface setup in the .blend file (optional)
- **use_scripts** (bool) – Trusted Source, Allow .blend file to execute scripts automatically, default available from system preferences (optional)
- **display_file_selector** (bool) – Display File Selector, (optional)
- **state** (int) – State, (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.operator_cheat_sheet"></a>

### bpy.ops.wm.operator_cheat_sheet()

List all the operators in a text-block, useful for scripting

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2289](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2289)

<a id="bpy.ops.wm.operator_defaults"></a>

### bpy.ops.wm.operator_defaults()

Set the active operator to its default values

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.operator_pie_enum"></a>

### bpy.ops.wm.operator_pie_enum(*, data_path='', prop_string='')

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **data_path** (str) – Operator, Operator name (in Python as string) (optional, never None)
- **prop_string** (str) – Property, Property name (as a string) (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:777](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L777)

<a id="bpy.ops.wm.operator_preset_add"></a>

### bpy.ops.wm.operator_preset_add(*, name='', remove_name=False, remove_active=False, operator='')

Add or remove an Operator Preset

**Parameters:**

- **name** (str) – Name, Name of the preset, used to make the path name (optional, never None)
- **remove_name** (bool) – remove_name, (optional)
- **remove_active** (bool) – remove_active, (optional)
- **operator** (str) – Operator, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:119](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L119)

<a id="bpy.ops.wm.operator_presets_cleanup"></a>

### bpy.ops.wm.operator_presets_cleanup(*, operator='', properties=None)

Remove outdated operator properties from presets that may cause problems

**Parameters:**

- **operator** (str) – operator, (optional, never None)
- **properties** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – properties, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/presets.py:967](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/presets.py#L967)

<a id="bpy.ops.wm.owner_disable"></a>

### bpy.ops.wm.owner_disable(*, owner_id='')

Disable add-on for workspace

**Parameters:**

**owner_id** (str) – UI Tag, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2337](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2337)

<a id="bpy.ops.wm.owner_enable"></a>

### bpy.ops.wm.owner_enable(*, owner_id='')

Enable add-on for workspace

**Parameters:**

**owner_id** (str) – UI Tag, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2322](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2322)

<a id="bpy.ops.wm.path_open"></a>

### bpy.ops.wm.path_open(*, filepath='')

Open a path in a file browser

**Parameters:**

**filepath** (str) – filepath, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:1185](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L1185)

<a id="bpy.ops.wm.ply_export"></a>

### bpy.ops.wm.ply_export(*, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', forward_axis='Y', up_axis='Z', global_scale=1.0, apply_modifiers=True, export_selected_objects=False, collection='', export_uv=True, export_normals=False, export_colors='SRGB', export_attributes=True, export_triangulated_mesh=False, ascii_format=False, filter_glob='*.ply')

Save the scene to a PLY file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **forward_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Forward Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **up_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Up Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **global_scale** (float) – Scale, Value by which to enlarge or shrink the objects with respect to the world’s origin (in [0.0001, 10000], optional)
- **apply_modifiers** (bool) – Apply Modifiers, Apply modifiers to exported meshes (optional)
- **export_selected_objects** (bool) – Export Selected Objects, Export only selected objects instead of all supported objects (optional)
- **collection** (str) – Source Collection, Export only objects from this collection (and its children) (optional, never None)
- **export_uv** (bool) – Export UVs, (optional)
- **export_normals** (bool) – Export Vertex Normals, Export specific vertex normals if available, export calculated normals otherwise (optional)
- **export_colors** (Literal['NONE', 'SRGB', 'LINEAR']) –

  Export Vertex Colors, Export vertex color attributes (optional)

  - `NONE`
    None – Do not import/export color attributes.
  - `SRGB`
    sRGB – Vertex colors in the file are in sRGB color space.
  - `LINEAR`
    Linear – Vertex colors in the file are in linear color space.
- **export_attributes** (bool) – Export Vertex Attributes, Export custom vertex attributes (optional)
- **export_triangulated_mesh** (bool) – Export Triangulated Mesh, All ngons with four or more vertices will be triangulated. Meshes in the scene will not be affected. Behaves like Triangulate Modifier with ngon-method: “Beauty”, quad-method: “Shortest Diagonal”, min vertices: 4 (optional)
- **ascii_format** (bool) – ASCII Format, Export file in ASCII format, export as binary otherwise (optional)
- **filter_glob** (str) – Extension Filter, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.ply_import"></a>

### bpy.ops.wm.ply_import(*, filepath='', directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', global_scale=1.0, use_scene_unit=False, forward_axis='Y', up_axis='Z', merge_verts=False, import_colors='SRGB', import_attributes=True, filter_glob='*.ply')

Import an PLY file as an object

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **global_scale** (float) – Scale, (in [1e-06, 1e+06], optional)
- **use_scene_unit** (bool) – Scene Unit, Apply current scene’s unit (as defined by unit scale) to imported data (optional)
- **forward_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Forward Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **up_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Up Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **merge_verts** (bool) – Merge Vertices, Merges vertices by distance (optional)
- **import_colors** (Literal['NONE', 'SRGB', 'LINEAR']) –

  Vertex Colors, Import vertex color attributes (optional)

  - `NONE`
    None – Do not import/export color attributes.
  - `SRGB`
    sRGB – Vertex colors in the file are in sRGB color space.
  - `LINEAR`
    Linear – Vertex colors in the file are in linear color space.
- **import_attributes** (bool) – Vertex Attributes, Import custom vertex attributes (optional)
- **filter_glob** (str) – Extension Filter, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.previews_batch_clear"></a>

### bpy.ops.wm.previews_batch_clear(*, files=None, directory='', filter_blender=True, filter_folder=True, use_scenes=True, use_collections=True, use_objects=True, use_intern_data=True, use_trusted=False, use_backups=True)

Clear selected .blend file’s previews

**Parameters:**

- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – files, (optional)
- **directory** (str) – directory, (optional, never None)
- **filter_blender** (bool) – filter_blender, (optional)
- **filter_folder** (bool) – filter_folder, (optional)
- **use_scenes** (bool) – Scenes, Clear scenes’ previews (optional)
- **use_collections** (bool) – Collections, Clear collections’ previews (optional)
- **use_objects** (bool) – Objects, Clear objects’ previews (optional)
- **use_intern_data** (bool) – Materials & Textures, Clear ‘internal’ previews (materials, textures, images, etc.) (optional)
- **use_trusted** (bool) – Trusted Blend Files, Enable Python evaluation for selected files (optional)
- **use_backups** (bool) – Save Backups, Keep a backup (.blend1) version of the files when saving with cleared previews (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/file.py:204](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/file.py#L204)

<a id="bpy.ops.wm.previews_batch_generate"></a>

### bpy.ops.wm.previews_batch_generate(*, files=None, directory='', filter_blender=True, filter_folder=True, use_scenes=True, use_collections=True, use_objects=True, use_intern_data=True, use_trusted=False, use_backups=True)

Generate selected .blend file’s previews

**Parameters:**

- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Collection of file paths with common `directory` root (optional)
- **directory** (str) – Root path of all files listed in `files` collection (optional, never None)
- **filter_blender** (bool) – Show Blender files in the File Browser (optional)
- **filter_folder** (bool) – Show folders in the File Browser (optional)
- **use_scenes** (bool) – Scenes, Generate scenes’ previews (optional)
- **use_collections** (bool) – Collections, Generate collections’ previews (optional)
- **use_objects** (bool) – Objects, Generate objects’ previews (optional)
- **use_intern_data** (bool) – Materials & Textures, Generate ‘internal’ previews (materials, textures, images, etc.) (optional)
- **use_trusted** (bool) – Trusted Blend Files, Enable Python evaluation for selected files (optional)
- **use_backups** (bool) – Save Backups, Keep a backup (.blend1) version of the files when saving with generated previews (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/file.py:95](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/file.py#L95)

<a id="bpy.ops.wm.previews_clear"></a>

### bpy.ops.wm.previews_clear(*, id_type=set())

Clear data-block previews (only for some types like objects, materials, textures, etc.)

**Parameters:**

**id_type** (set[Literal['ALL', 'GEOMETRY', 'SHADING', 'SCENE', 'COLLECTION', 'OBJECT', 'MATERIAL', 'LIGHT', 'WORLD', 'TEXTURE', 'IMAGE']]) –

Data-Block Type, Which data-block previews to clear (optional)

- `ALL`
  All Types.
- `GEOMETRY`
  All Geometry Types – Clear previews for scenes, collections and objects.
- `SHADING`
  All Shading Types – Clear previews for materials, lights, worlds, textures and images.
- `SCENE`
  Scenes.
- `COLLECTION`
  Collections.
- `OBJECT`
  Objects.
- `MATERIAL`
  Materials.
- `LIGHT`
  Lights.
- `WORLD`
  Worlds.
- `TEXTURE`
  Textures.
- `IMAGE`
  Images.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.previews_ensure"></a>

### bpy.ops.wm.previews_ensure()

Ensure data-block previews are available and up-to-date (to be saved in .blend file, only for some types like materials, textures, etc.)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.properties_add"></a>

### bpy.ops.wm.properties_add(*, data_path='')

Add your own property to the data-block

**Parameters:**

**data_path** (str) – Property Edit, Property data_path edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2171](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2171)

<a id="bpy.ops.wm.properties_context_change"></a>

### bpy.ops.wm.properties_context_change(*, context='')

Jump to a different tab inside the properties editor

**Parameters:**

**context** (str) – Context, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2214](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2214)

<a id="bpy.ops.wm.properties_edit"></a>

### bpy.ops.wm.properties_edit(*, data_path='', property_name='', property_type='FLOAT', is_overridable_library=False, description='', use_soft_limits=False, array_length=3, default_int=(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0), min_int=-10000, max_int=10000, soft_min_int=-10000, soft_max_int=10000, step_int=1, default_bool=(False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False), default_float=(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), min_float=-10000.0, max_float=-10000.0, soft_min_float=-10000.0, soft_max_float=-10000.0, precision=3, step_float=0.1, subtype='', default_string='', id_type='OBJECT', eval_string='')

Change a custom property’s type, or adjust how it is displayed in the interface

**Parameters:**

- **data_path** (str) – Property Edit, Property data_path edit (optional, never None)
- **property_name** (str) – Property Name, Property name edit (optional, never None)
- **property_type** (Literal['FLOAT', 'FLOAT_ARRAY', 'INT', 'INT_ARRAY', 'BOOL', 'BOOL_ARRAY', 'STRING', 'DATA_BLOCK', 'PYTHON']) –

  Type, (optional)

  - `FLOAT`
    Float – A single floating-point value.
  - `FLOAT_ARRAY`
    Float Array – An array of floating-point values.
  - `INT`
    Integer – A single integer.
  - `INT_ARRAY`
    Integer Array – An array of integers.
  - `BOOL`
    Boolean – A true or false value.
  - `BOOL_ARRAY`
    Boolean Array – An array of true or false values.
  - `STRING`
    String – A string value.
  - `DATA_BLOCK`
    Data-Block – A data-block value.
  - `PYTHON`
    Python – Edit a Python value directly, for unsupported property types.
- **is_overridable_library** (bool) – Library Overridable, Allow the property to be overridden when the data-block is linked (optional)
- **description** (str) – Description, (optional, never None)
- **use_soft_limits** (bool) – Soft Limits, Limits the Property Value slider to a range, values outside the range must be inputted numerically (optional)
- **array_length** (int) – Array Length, (in [1, 32], optional)
- **default_int** (Sequence[int]) – Default Value, (array of 32 items, in [-inf, inf], optional)
- **min_int** (int) – Min, (in [-inf, inf], optional)
- **max_int** (int) – Max, (in [-inf, inf], optional)
- **soft_min_int** (int) – Soft Min, (in [-inf, inf], optional)
- **soft_max_int** (int) – Soft Max, (in [-inf, inf], optional)
- **step_int** (int) – Step, (in [1, inf], optional)
- **default_bool** (Sequence[bool]) – Default Value, (array of 32 items, optional)
- **default_float** (Sequence[float]) – Default Value, (array of 32 items, in [-inf, inf], optional)
- **min_float** (float) – Min, (in [-inf, inf], optional)
- **max_float** (float) – Max, (in [-inf, inf], optional)
- **soft_min_float** (float) – Soft Min, (in [-inf, inf], optional)
- **soft_max_float** (float) – Soft Max, (in [-inf, inf], optional)
- **precision** (int) – Precision, (in [0, 8], optional)
- **step_float** (float) – Step, (in [0.001, inf], optional)
- **subtype** (str) – Subtype, (optional)
- **default_string** (str) – Default Value, (optional, never None)
- **id_type** (Literal['ACTION', 'ARMATURE', 'BRUSH', 'CACHEFILE', 'CAMERA', 'COLLECTION', 'CURVE', 'CURVES', 'FONT', 'GREASEPENCIL', 'GREASEPENCIL_V3', 'IMAGE', 'KEY', 'LATTICE', 'LIBRARY', 'LIGHT', 'LIGHT_PROBE', 'LINESTYLE', 'MASK', 'MATERIAL', 'MESH', 'META', 'MOVIECLIP', 'NODETREE', 'OBJECT', 'PAINTCURVE', 'PALETTE', 'PARTICLE', 'POINTCLOUD', 'SCENE', 'SCREEN', 'SOUND', 'SPEAKER', 'TEXT', 'TEXTURE', 'VOLUME', 'WINDOWMANAGER', 'WORKSPACE', 'WORLD']) – ID Type, (optional)
- **eval_string** (str) – Value, Python value for unsupported custom property types (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:1904](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L1904)

<a id="bpy.ops.wm.properties_edit_value"></a>

### bpy.ops.wm.properties_edit_value(*, data_path='', property_name='', eval_string='')

Edit the value of a custom property

**Parameters:**

- **data_path** (str) – Property Edit, Property data_path edit (optional, never None)
- **property_name** (str) – Property Name, Property name edit (optional, never None)
- **eval_string** (str) – Value, Value for custom property types that can only be edited as a Python expression (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2128](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2128)

<a id="bpy.ops.wm.properties_remove"></a>

### bpy.ops.wm.properties_remove(*, data_path='', property_name='')

Internal use (edit a property data_path)

**Parameters:**

- **data_path** (str) – Property Edit, Property data_path edit (optional, never None)
- **property_name** (str) – Property Name, Property name edit (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2228](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2228)

<a id="bpy.ops.wm.quit_blender"></a>

### bpy.ops.wm.quit_blender()

Quit Blender

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.radial_control"></a>

### bpy.ops.wm.radial_control(*, data_path_primary='', data_path_secondary='', use_secondary='', rotation_path='', color_path='', fill_color_path='', fill_color_override_path='', fill_color_override_test_path='', zoom_path='', image_id='', secondary_tex=False, release_confirm=False)

Set some size property (e.g. brush size) with mouse wheel

**Parameters:**

- **data_path_primary** (str) – Primary Data Path, Primary path of property to be set by the radial control (optional, never None)
- **data_path_secondary** (str) – Secondary Data Path, Secondary path of property to be set by the radial control (optional, never None)
- **use_secondary** (str) – Use Secondary, Path of property to select between the primary and secondary data paths (optional, never None)
- **rotation_path** (str) – Rotation Path, Path of property used to rotate the texture display (optional, never None)
- **color_path** (str) – Color Path, Path of property used to set the color of the control (optional, never None)
- **fill_color_path** (str) – Fill Color Path, Path of property used to set the fill color of the control (optional, never None)
- **fill_color_override_path** (str) – Fill Color Override Path, (optional, never None)
- **fill_color_override_test_path** (str) – Fill Color Override Test, (optional, never None)
- **zoom_path** (str) – Zoom Path, Path of property used to set the zoom level for the control (optional, never None)
- **image_id** (str) – Image ID, Path of ID that is used to generate an image for the control (optional, never None)
- **secondary_tex** (bool) – Secondary Texture, Tweak brush secondary/mask texture (optional)
- **release_confirm** (bool) – Confirm On Release, Finish operation on key release (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.read_factory_settings"></a>

### bpy.ops.wm.read_factory_settings(*, use_factory_startup_app_template_only=False, app_template='Template', use_empty=False)

Load factory default startup file and preferences. To make changes permanent, use “Save Startup File” and “Save Preferences”

**Parameters:**

- **use_factory_startup_app_template_only** (bool) – Factory Startup App-Template Only, (optional)
- **app_template** (str) – (optional, never None)
- **use_empty** (bool) – Empty, After loading, remove everything except scenes, windows, and workspaces. This makes it possible to load the startup file with its scene configuration and window layout intact, but no objects, materials, animations, … (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.read_factory_userpref"></a>

### bpy.ops.wm.read_factory_userpref(*, use_factory_startup_app_template_only=False)

Load factory default preferences. To make changes to preferences permanent, use “Save Preferences”

**Parameters:**

**use_factory_startup_app_template_only** (bool) – Factory Startup App-Template Only, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.read_history"></a>

### bpy.ops.wm.read_history()

Reloads history and bookmarks

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.read_homefile"></a>

### bpy.ops.wm.read_homefile(*, filepath='', load_ui=True, use_splash=False, use_factory_startup=False, use_factory_startup_app_template_only=False, app_template='Template', use_empty=False)

Open the default file

**Parameters:**

- **filepath** (str) – File Path, Path to an alternative start-up file (optional, never None)
- **load_ui** (bool) – Load UI, Load user interface setup from the .blend file (optional)
- **use_splash** (bool) – Splash, (optional)
- **use_factory_startup** (bool) – Factory Startup, Load the default (‘factory startup’) blend file. This is independent of the normal start-up file that the user can save (optional)
- **use_factory_startup_app_template_only** (bool) – Factory Startup App-Template Only, (optional)
- **app_template** (str) – (optional, never None)
- **use_empty** (bool) – Empty, After loading, remove everything except scenes, windows, and workspaces. This makes it possible to load the startup file with its scene configuration and window layout intact, but no objects, materials, animations, … (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.read_userpref"></a>

### bpy.ops.wm.read_userpref()

Load last saved preferences

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.recover_auto_save"></a>

### bpy.ops.wm.recover_auto_save(*, filepath='', hide_props_region=True, check_existing=False, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=False, filter_blenlib=False, filemode=8, display_type='LIST_VERTICAL', sort_method='', use_scripts=False)

Open an automatically saved file to recover it

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **use_scripts** (bool) – Trusted Source, Allow .blend file to execute scripts automatically, default available from system preferences (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.recover_last_session"></a>

### bpy.ops.wm.recover_last_session(*, use_scripts=False)

Open the last closed file (“quit.blend”)

**Parameters:**

**use_scripts** (bool) – Trusted Source, Allow .blend file to execute scripts automatically, default available from system preferences (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.redraw_timer"></a>

### bpy.ops.wm.redraw_timer(*, type='DRAW', iterations=10, time_limit=0.0)

Simple redraw timer to test the speed of updating the interface

**Parameters:**

- **type** (Literal['DRAW', 'DRAW_SWAP', 'DRAW_WIN', 'DRAW_WIN_SWAP', 'ANIM_STEP', 'ANIM_PLAY', 'UNDO']) –

  Type, (optional)

  - `DRAW`
    Draw Region – Draw region.
  - `DRAW_SWAP`
    Draw Region & Swap – Draw region and swap.
  - `DRAW_WIN`
    Draw Window – Draw window.
  - `DRAW_WIN_SWAP`
    Draw Window & Swap – Draw window and swap.
  - `ANIM_STEP`
    Animation Step – Animation steps.
  - `ANIM_PLAY`
    Animation Play – Animation playback.
  - `UNDO`
    Undo/Redo – Undo and redo.
- **iterations** (int) – Iterations, Number of times to redraw (in [1, inf], optional)
- **time_limit** (float) – Time Limit, Seconds to run the test for (override iterations) (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.revert_mainfile"></a>

### bpy.ops.wm.revert_mainfile(*, use_scripts=False)

Reload the saved file

**Parameters:**

**use_scripts** (bool) – Trusted Source, Allow .blend file to execute scripts automatically, default available from system preferences (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.save_as_mainfile"></a>

### bpy.ops.wm.save_as_mainfile(*, filepath='', hide_props_region=True, check_existing=True, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', compress=False, relative_remap=True, copy=False, show_save_modified_images_dialog=False)

Save the current file in the desired location

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **compress** (bool) – Compress, Write compressed .blend file (optional)
- **relative_remap** (bool) – Remap Relative, Remap relative paths when saving to a different directory (optional)
- **copy** (bool) – Save Copy, Save a copy of the actual working state but does not make saved file active (optional)
- **show_save_modified_images_dialog** (bool) – Show Save Modified Images Dialog, Show a popup dialog to save modified images before saving the blend file (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.save_auto_save"></a>

### bpy.ops.wm.save_auto_save()

Create an autosave in the temp directory for the current file

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.save_homefile"></a>

### bpy.ops.wm.save_homefile()

Make the current file the default startup file

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.save_mainfile"></a>

### bpy.ops.wm.save_mainfile(*, filepath='', hide_props_region=True, check_existing=True, filter_blender=True, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', compress=False, relative_remap=False, exit=False, incremental=False, show_save_modified_images_dialog=False)

Save the current Blender file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **hide_props_region** (bool) – Hide Operator Properties, Collapse the region displaying the operator settings (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **compress** (bool) – Compress, Write compressed .blend file (optional)
- **relative_remap** (bool) – Remap Relative, Remap relative paths when saving to a different directory (optional)
- **exit** (bool) – Exit, Exit Blender after saving (optional)
- **incremental** (bool) – Incremental, Save the current Blender file with a numerically incremented name that does not overwrite any existing files (optional)
- **show_save_modified_images_dialog** (bool) – Show Save Modified Images Dialog, Show a popup dialog to save modified images before saving the blend file (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.save_userpref"></a>

### bpy.ops.wm.save_userpref()

Make the current preferences default

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.search_menu"></a>

### bpy.ops.wm.search_menu()

Pop-up a search over all menus in the current context

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.search_operator"></a>

### bpy.ops.wm.search_operator()

Pop-up a search over all available operators in current context

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.search_single_menu"></a>

### bpy.ops.wm.search_single_menu(*, menu_idname='', initial_query='')

Pop-up a search for a menu in current context

**Parameters:**

- **menu_idname** (str) – Menu Name, Menu to search in (optional, never None)
- **initial_query** (str) – Initial Query, Query to insert into the search box (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.set_stereo_3d"></a>

### bpy.ops.wm.set_stereo_3d(*, display_mode='ANAGLYPH', anaglyph_type='RED_CYAN', interlace_type='ROW_INTERLEAVED', use_interlace_swap=False, use_sidebyside_crosseyed=False)

Toggle 3D stereo support for current window (or change the display mode)

**Parameters:**

- **display_mode** (Literal[[Stereo3D Display Items](bpy_types_enum_items/stereo3d_display_items.md#rna-enum-stereo3d-display-items)]) – Display Mode, (optional)
- **anaglyph_type** (Literal[[Stereo3D Anaglyph Type Items](bpy_types_enum_items/stereo3d_anaglyph_type_items.md#rna-enum-stereo3d-anaglyph-type-items)]) – Anaglyph Type, (optional)
- **interlace_type** (Literal[[Stereo3D Interlace Type Items](bpy_types_enum_items/stereo3d_interlace_type_items.md#rna-enum-stereo3d-interlace-type-items)]) – Interlace Type, (optional)
- **use_interlace_swap** (bool) – Swap Left/Right, Swap left and right stereo channels (optional)
- **use_sidebyside_crosseyed** (bool) – Cross-Eyed, Right eye should see left image and vice versa (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.set_working_color_space"></a>

### bpy.ops.wm.set_working_color_space(*, convert_colors=True, working_space='')

Change the working color space of all colors in this blend file

**Parameters:**

- **convert_colors** (bool) – Convert Colors in All Data-blocks, Change colors in all data-blocks to the new working space (optional)
- **working_space** (str) – Working Space, Color space to set (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.splash"></a>

### bpy.ops.wm.splash()

Open the splash screen with release info

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.splash_about"></a>

### bpy.ops.wm.splash_about()

Open a window with information about Blender

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.stl_export"></a>

### bpy.ops.wm.stl_export(*, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', ascii_format=False, use_batch=False, export_selected_objects=False, collection='', global_scale=1.0, use_scene_unit=False, forward_axis='Y', up_axis='Z', apply_modifiers=True, evaluation_mode='DAG_EVAL_RENDER', filter_glob='*.stl')

Save the scene to an STL file

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **ascii_format** (bool) – ASCII Format, Export file in ASCII format, export as binary otherwise (optional)
- **use_batch** (bool) – Batch Export, Export each object to a separate file (optional)
- **export_selected_objects** (bool) – Export Selected Objects, Export only selected objects instead of all supported objects (optional)
- **collection** (str) – Source Collection, Export only objects from this collection (and its children) (optional, never None)
- **global_scale** (float) – Scale, (in [1e-06, 1e+06], optional)
- **use_scene_unit** (bool) – Scene Unit, Apply current scene’s unit (as defined by unit scale) to exported data (optional)
- **forward_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Forward Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **up_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Up Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **apply_modifiers** (bool) – Apply Modifiers, Apply modifiers to exported meshes (optional)
- **evaluation_mode** (Literal['DAG_EVAL_RENDER', 'DAG_EVAL_VIEWPORT']) –

  Object Properties, Determines properties like object visibility, modifiers etc., where they differ for Render and Viewport (optional)

  - `DAG_EVAL_RENDER`
    Render – Export objects as they appear in render.
  - `DAG_EVAL_VIEWPORT`
    Viewport – Export objects as they appear in the viewport (Multiresolution modifiers in Sculpt Mode will not be evaluated).
- **filter_glob** (str) – Extension Filter, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.stl_import"></a>

### bpy.ops.wm.stl_import(*, filepath='', directory='', files=None, check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', global_scale=1.0, use_scene_unit=False, use_facet_normal=False, forward_axis='Y', up_axis='Z', use_mesh_validate=True, filter_glob='*.stl')

Import an STL file as an object

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **global_scale** (float) – Scale, (in [1e-06, 1e+06], optional)
- **use_scene_unit** (bool) – Scene Unit, Apply current scene’s unit (as defined by unit scale) to imported data (optional)
- **use_facet_normal** (bool) – Facet Normals, Use (import) facet normals (note that this will still give flat shading) (optional)
- **forward_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Forward Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **up_axis** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Up Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **use_mesh_validate** (bool) – Validate Mesh, Ensure the data is valid (when disabled, data may be imported which causes crashes displaying or editing) (optional)
- **filter_glob** (str) – Extension Filter, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.sysinfo"></a>

### bpy.ops.wm.sysinfo(*, filepath='')

Generate system information, saved into a text file

**Parameters:**

**filepath** (str) – filepath, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2257](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2257)

<a id="bpy.ops.wm.tool_set_by_brush_type"></a>

### bpy.ops.wm.tool_set_by_brush_type(*, brush_type='', space_type='EMPTY')

Look up the most appropriate tool for the given brush type and activate that

**Parameters:**

- **brush_type** (str) – Brush Type, Brush type identifier for which the most appropriate tool will be looked up (optional, never None)
- **space_type** (Literal['EMPTY', 'VIEW_3D', 'IMAGE_EDITOR', 'NODE_EDITOR', 'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR', 'TEXT_EDITOR', 'CONSOLE', 'INFO', 'TOPBAR', 'STATUSBAR', 'OUTLINER', 'PROPERTIES', 'FILE_BROWSER', 'SPREADSHEET', 'PREFERENCES']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2471](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2471)

<a id="bpy.ops.wm.tool_set_by_id"></a>

### bpy.ops.wm.tool_set_by_id(*, name='', cycle=False, as_fallback=False, space_type='EMPTY')

Set the tool by name (for key-maps)

**Parameters:**

- **name** (str) – Identifier, Identifier of the tool (optional, never None)
- **cycle** (bool) – Cycle, Cycle through tools in this group (optional)
- **as_fallback** (bool) – Set Fallback, Set the fallback tool instead of the primary tool (optional)
- **space_type** (Literal['EMPTY', 'VIEW_3D', 'IMAGE_EDITOR', 'NODE_EDITOR', 'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR', 'TEXT_EDITOR', 'CONSOLE', 'INFO', 'TOPBAR', 'STATUSBAR', 'OUTLINER', 'PROPERTIES', 'FILE_BROWSER', 'SPREADSHEET', 'PREFERENCES']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2380](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2380)

<a id="bpy.ops.wm.tool_set_by_index"></a>

### bpy.ops.wm.tool_set_by_index(*, index=0, cycle=False, expand=True, as_fallback=False, space_type='EMPTY')

Set the tool by index (for key-maps)

**Parameters:**

- **index** (int) – Index in Toolbar, (in [-inf, inf], optional)
- **cycle** (bool) – Cycle, Cycle through tools in this group (optional)
- **expand** (bool) – expand, Include tool subgroups (optional)
- **as_fallback** (bool) – Set Fallback, Set the fallback tool instead of the primary (optional)
- **space_type** (Literal['EMPTY', 'VIEW_3D', 'IMAGE_EDITOR', 'NODE_EDITOR', 'SEQUENCE_EDITOR', 'CLIP_EDITOR', 'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR', 'TEXT_EDITOR', 'CONSOLE', 'INFO', 'TOPBAR', 'STATUSBAR', 'OUTLINER', 'PROPERTIES', 'FILE_BROWSER', 'SPREADSHEET', 'PREFERENCES']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2430](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2430)

<a id="bpy.ops.wm.toolbar"></a>

### bpy.ops.wm.toolbar()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2538](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2538)

<a id="bpy.ops.wm.toolbar_fallback_pie"></a>

### bpy.ops.wm.toolbar_fallback_pie()

Undocumented, consider [contributing](https://developer.blender.org/).

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2562](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2562)

<a id="bpy.ops.wm.toolbar_prompt"></a>

### bpy.ops.wm.toolbar_prompt()

Leader key like functionality for accessing tools

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:2662](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L2662)

<a id="bpy.ops.wm.url_open"></a>

### bpy.ops.wm.url_open(*, url='')

Open a website in the web browser

**Parameters:**

**url** (str) – URL, URL to open (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:1085](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L1085)

<a id="bpy.ops.wm.url_open_preset"></a>

### bpy.ops.wm.url_open_preset(*, type='')

Open a preset website in the web browser

**Parameters:**

**type** (str) – Site, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/wm.py:1168](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/wm.py#L1168)

<a id="bpy.ops.wm.usd_export"></a>

### bpy.ops.wm.usd_export(*, filepath='', check_existing=True, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=True, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, display_type='DEFAULT', sort_method='', filter_glob='*.usd', selected_objects_only=False, collection='', export_animation=False, incremental_frames=0, export_hair=False, export_uvmaps=True, rename_uvmaps=True, export_mesh_colors=True, export_normals=True, export_materials=True, export_subdivision='BEST_MATCH', export_armatures=True, only_deform_bones=False, export_shapekeys=True, use_instancing=False, evaluation_mode='RENDER', generate_preview_surface=True, generate_materialx_network=False, convert_orientation=False, export_global_forward_selection='NEGATIVE_Z', export_global_up_selection='Y', export_textures_mode='NEW', overwrite_textures=False, relative_paths=True, xform_op_mode='TRS', root_prim_path='/root', export_custom_properties=True, custom_properties_namespace='userProperties', accessibility_label='', accessibility_description='', author_blender_name=True, convert_world_material=True, allow_unicode=True, export_meshes=True, export_lights=True, export_cameras=True, export_curves=True, export_points=True, export_volumes=True, triangulate_meshes=False, quad_method='SHORTEST_DIAGONAL', ngon_method='BEAUTY', usdz_downscale_size='KEEP', usdz_downscale_custom_size=128, merge_parent_xform=False, convert_scene_units='METERS', meters_per_unit=1.0)

Export current scene in a USD archive

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **filter_glob** (str) – (optional, never None)
- **selected_objects_only** (bool) – Selection Only, Only export selected objects. Unselected parents of selected objects are exported as empty transform (optional)
- **collection** (str) – Collection, (optional, never None)
- **export_animation** (bool) – Animation, Export all frames in the render frame range, rather than only the current frame (optional)
- **incremental_frames** (int) – Incremental Save, Incrementally save after the specified number of frames to reduce peak memory usage. Incremental saves can result in longer export times and potential issues with some file synchronization services. Zero disables incremental save (in [0, inf], optional)
- **export_hair** (bool) – Hair, Export hair particle systems as USD curves (optional)
- **export_uvmaps** (bool) – UV Maps, Include all mesh UV maps in the export (optional)
- **rename_uvmaps** (bool) – Rename UV Maps, Rename active render UV map to “st” to match USD conventions (optional)
- **export_mesh_colors** (bool) – Color Attributes, Include mesh color attributes in the export (optional)
- **export_normals** (bool) – Normals, Include normals of exported meshes in the export (optional)
- **export_materials** (bool) – Materials, Export viewport settings of materials as USD preview materials, and export material assignments as geometry subsets (optional)
- **export_subdivision** (Literal['IGNORE', 'TESSELLATE', 'BEST_MATCH']) –

  Subdivision, Choose how subdivision modifiers will be mapped to the USD subdivision scheme during export (optional)

  - `IGNORE`
    Ignore – Scheme = None. Export base mesh without subdivision.
  - `TESSELLATE`
    Tessellate – Scheme = None. Export subdivided mesh.
  - `BEST_MATCH`
    Best Match – Scheme = Catmull-Clark, when possible. Reverts to exporting the subdivided mesh for the Simple subdivision type.
- **export_armatures** (bool) – Armatures, Export armatures and meshes with armature modifiers as USD skeletons and skinned meshes (optional)
- **only_deform_bones** (bool) – Only Deform Bones, Only export deform bones and their parents (optional)
- **export_shapekeys** (bool) – Shape Keys, Export shape keys as USD blend shapes (optional)
- **use_instancing** (bool) – Instancing, Export instanced objects as references in USD rather than real objects (optional)
- **evaluation_mode** (Literal['RENDER', 'VIEWPORT']) –

  Use Settings for, Determines visibility of objects, modifier settings, and other areas where there are different settings for viewport and rendering (optional)

  - `RENDER`
    Render – Use Render settings for object visibility, modifier settings, etc.
  - `VIEWPORT`
    Viewport – Use Viewport settings for object visibility, modifier settings, etc.
- **generate_preview_surface** (bool) – USD Preview Surface Network, Generate an approximate USD Preview Surface shader representation of a Principled BSDF node network (optional)
- **generate_materialx_network** (bool) – MaterialX Network, Generate a MaterialX network representation of the materials (optional)
- **convert_orientation** (bool) – Convert Orientation, Convert orientation axis to a different convention to match other applications (optional)
- **export_global_forward_selection** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Forward Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **export_global_up_selection** (Literal['X', 'Y', 'Z', 'NEGATIVE_X', 'NEGATIVE_Y', 'NEGATIVE_Z']) –

  Up Axis, (optional)

  - `X`
    X – Positive X axis.
  - `Y`
    Y – Positive Y axis.
  - `Z`
    Z – Positive Z axis.
  - `NEGATIVE_X`
    -X – Negative X axis.
  - `NEGATIVE_Y`
    -Y – Negative Y axis.
  - `NEGATIVE_Z`
    -Z – Negative Z axis.
- **export_textures_mode** (Literal['KEEP', 'PRESERVE', 'NEW']) –

  Export Textures, Texture export method (optional)

  - `KEEP`
    Keep – Use original location of textures.
  - `PRESERVE`
    Preserve – Preserve file paths of textures from already imported USD files.
    Export remaining textures to a ‘textures’ folder next to the USD file.
  - `NEW`
    New Path – Export textures to a ‘textures’ folder next to the USD file.
- **overwrite_textures** (bool) – Overwrite Textures, Overwrite existing files when exporting textures (optional)
- **relative_paths** (bool) – Relative Paths, Use relative paths to reference external files (i.e. textures, volumes) in USD, otherwise use absolute paths (optional)
- **xform_op_mode** (Literal['TRS', 'TOS', 'MAT']) –

  Xform Ops, The type of transform operators to write (optional)

  - `TRS`
    Translate, Rotate, Scale – Export with translate, rotate, and scale Xform operators.
  - `TOS`
    Translate, Orient, Scale – Export with translate, orient quaternion, and scale Xform operators.
  - `MAT`
    Matrix – Export matrix operator.
- **root_prim_path** (str) – Root Prim, If set, add a transform primitive with the given path to the stage as the parent of all exported data (optional, never None)
- **export_custom_properties** (bool) – Custom Properties, Export custom properties as USD attributes (optional)
- **custom_properties_namespace** (str) – Namespace, If set, add the given namespace as a prefix to exported custom property names. This only applies to property names that do not already have a prefix (e.g., it would apply to name ‘bar’ but not ‘foo:bar’) and does not apply to blender object and data names which are always exported in the ‘userProperties:blender’ namespace (optional, never None)
- **accessibility_label** (str) – Label, Set the accessibility label for the exported stage’s default prim (optional, never None)
- **accessibility_description** (str) – Description, Set the accessibility description for the exported stage’s default prim (optional, never None)
- **author_blender_name** (bool) – Blender Names, Author USD custom attributes containing the original Blender object and object data names (optional)
- **convert_world_material** (bool) – World Dome Light, Convert the world material to a USD dome light. Currently works for simple materials, consisting of an environment texture connected to a background shader, with an optional vector multiply of the texture color (optional)
- **allow_unicode** (bool) – Allow Unicode, Preserve UTF-8 encoded characters when writing USD prim and property names (requires software utilizing USD 24.03 or greater when opening the resulting files) (optional)
- **export_meshes** (bool) – Meshes, Export all meshes (optional)
- **export_lights** (bool) – Lights, Export all lights (optional)
- **export_cameras** (bool) – Cameras, Export all cameras (optional)
- **export_curves** (bool) – Curves, Export all curves (optional)
- **export_points** (bool) – Point Clouds, Export all point clouds (optional)
- **export_volumes** (bool) – Volumes, Export all volumes (optional)
- **triangulate_meshes** (bool) – Triangulate Meshes, Triangulate meshes during export (optional)
- **quad_method** (Literal[[Modifier Triangulate Quad Method Items](bpy_types_enum_items/modifier_triangulate_quad_method_items.md#rna-enum-modifier-triangulate-quad-method-items)]) – Quad Method, Method for splitting the quads into triangles (optional)
- **ngon_method** (Literal[[Modifier Triangulate Ngon Method Items](bpy_types_enum_items/modifier_triangulate_ngon_method_items.md#rna-enum-modifier-triangulate-ngon-method-items)]) – N-gon Method, Method for splitting the n-gons into triangles (optional)
- **usdz_downscale_size** (Literal['KEEP', '256', '512', '1024', '2048', '4096', 'CUSTOM']) –

  USDZ Texture Downsampling, Choose a maximum size for all exported textures (optional)

  - `KEEP`
    Keep – Keep all current texture sizes.
  - `256`
    256 – Resize to a maximum of 256 pixels.
  - `512`
    512 – Resize to a maximum of 512 pixels.
  - `1024`
    1024 – Resize to a maximum of 1024 pixels.
  - `2048`
    2048 – Resize to a maximum of 2048 pixels.
  - `4096`
    4096 – Resize to a maximum of 4096 pixels.
  - `CUSTOM`
    Custom – Specify a custom size.
- **usdz_downscale_custom_size** (int) – USDZ Custom Downscale Size, Custom size for downscaling exported textures (in [64, 16384], optional)
- **merge_parent_xform** (bool) – Merge parent Xform, Merge USD primitives with their Xform parent if possible. USD does not allow nested UsdGeomGprims, intermediary Xform prims will be defined to keep the USD file valid when encountering object hierarchies. (optional)
- **convert_scene_units** (Literal['METERS', 'KILOMETERS', 'CENTIMETERS', 'MILLIMETERS', 'INCHES', 'FEET', 'YARDS', 'CUSTOM']) –

  Units, Set the USD Stage meters per unit to the chosen measurement, or a custom value (optional)

  - `METERS`
    Meters – Scene meters per unit to 1.0.
  - `KILOMETERS`
    Kilometers – Scene meters per unit to 1000.0.
  - `CENTIMETERS`
    Centimeters – Scene meters per unit to 0.01.
  - `MILLIMETERS`
    Millimeters – Scene meters per unit to 0.001.
  - `INCHES`
    Inches – Scene meters per unit to 0.0254.
  - `FEET`
    Feet – Scene meters per unit to 0.3048.
  - `YARDS`
    Yards – Scene meters per unit to 0.9144.
  - `CUSTOM`
    Custom – Specify a custom scene meters per unit value.
- **meters_per_unit** (float) – Meters Per Unit, Custom value for meters per unit in the USD Stage (in [0.0001, 1000], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.usd_import"></a>

### bpy.ops.wm.usd_import(*, filepath='', check_existing=False, filter_blender=False, filter_backup=False, filter_image=False, filter_movie=False, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=True, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=8, relative_path=True, display_type='DEFAULT', sort_method='', filter_glob='*.usd', scale=1.0, set_frame_range=True, import_cameras=True, import_curves=True, import_lights=True, import_materials=True, import_meshes=True, import_volumes=True, import_shapes=True, import_skeletons=True, import_blendshapes=True, import_points=True, import_subdivision=False, support_scene_instancing=True, import_visible_only=True, create_collection=False, read_mesh_uvs=True, read_mesh_colors=True, read_mesh_attributes=True, prim_path_mask='', import_guide=False, import_proxy=False, import_render=True, import_all_materials=False, import_usd_preview=True, set_material_blend=True, light_intensity_scale=1.0, mtl_purpose='MTL_FULL', mtl_name_collision_mode='MAKE_UNIQUE', import_textures_mode='IMPORT_PACK', import_textures_dir='//textures/', tex_name_collision_mode='USE_EXISTING', property_import_mode='ALL', validate_meshes=False, create_world_material=True, import_defined_only=True, merge_parent_xform=True, apply_unit_conversion_scale=True)

Import USD stage into current scene

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **check_existing** (bool) – Check Existing, Check and warn on overwriting existing files (optional)
- **filter_blender** (bool) – Filter .blend files, (optional)
- **filter_backup** (bool) – Filter backup .blend files, (optional)
- **filter_image** (bool) – Filter image files, (optional)
- **filter_movie** (bool) – Filter movie files, (optional)
- **filter_python** (bool) – Filter Python files, (optional)
- **filter_font** (bool) – Filter font files, (optional)
- **filter_sound** (bool) – Filter sound files, (optional)
- **filter_text** (bool) – Filter text files, (optional)
- **filter_archive** (bool) – Filter archive files, (optional)
- **filter_btx** (bool) – Filter btx files, (optional)
- **filter_alembic** (bool) – Filter Alembic files, (optional)
- **filter_usd** (bool) – Filter USD files, (optional)
- **filter_obj** (bool) – Filter OBJ files, (optional)
- **filter_volume** (bool) – Filter OpenVDB volume files, (optional)
- **filter_folder** (bool) – Filter folders, (optional)
- **filter_blenlib** (bool) – Filter Blender IDs, (optional)
- **filemode** (int) – File Browser Mode, The setting for the file browser mode to load a .blend file, a library or a special file (in [1, 9], optional)
- **relative_path** (bool) – Relative Path, Select the file relative to the blend file (optional)
- **display_type** (Literal['DEFAULT', 'LIST_VERTICAL', 'LIST_HORIZONTAL', 'THUMBNAIL']) –

  Display Type, (optional)

  - `DEFAULT`
    Default – Automatically determine display type for files.
  - `LIST_VERTICAL`
    Short List – Display files as short list.
  - `LIST_HORIZONTAL`
    Long List – Display files as a detailed list.
  - `THUMBNAIL`
    Thumbnails – Display files as thumbnails.
- **sort_method** (str) – File sorting mode, (optional)
- **filter_glob** (str) – (optional, never None)
- **scale** (float) – Scale, Value by which to enlarge or shrink the objects with respect to the world’s origin (in [0.0001, 1000], optional)
- **set_frame_range** (bool) – Set Frame Range, Update the scene’s start and end frame to match those of the USD archive (optional)
- **import_cameras** (bool) – Cameras, (optional)
- **import_curves** (bool) – Curves, (optional)
- **import_lights** (bool) – Lights, (optional)
- **import_materials** (bool) – Materials, (optional)
- **import_meshes** (bool) – Meshes, (optional)
- **import_volumes** (bool) – Volumes, (optional)
- **import_shapes** (bool) – USD Shapes, (optional)
- **import_skeletons** (bool) – Armatures, (optional)
- **import_blendshapes** (bool) – Shape Keys, (optional)
- **import_points** (bool) – Point Clouds, (optional)
- **import_subdivision** (bool) – Import Subdivision Scheme, Create subdivision surface modifiers based on the USD SubdivisionScheme attribute (optional)
- **support_scene_instancing** (bool) – Scene Instancing, Import USD scene graph instances as collection instances (optional)
- **import_visible_only** (bool) – Visible Primitives Only, Do not import invisible USD primitives. Only applies to primitives with a non-animated visibility attribute. Primitives with animated visibility will always be imported (optional)
- **create_collection** (bool) – Create Collection, Add all imported objects to a new collection (optional)
- **read_mesh_uvs** (bool) – UV Coordinates, Read mesh UV coordinates (optional)
- **read_mesh_colors** (bool) – Color Attributes, Read mesh color attributes (optional)
- **read_mesh_attributes** (bool) – Mesh Attributes, Read USD Primvars as mesh attributes (optional)
- **prim_path_mask** (str) – Path Mask, Import only the primitive at the given path and its descendants. Multiple paths may be specified in a list delimited by commas or semicolons (optional, never None)
- **import_guide** (bool) – Guide, Import guide geometry (optional)
- **import_proxy** (bool) – Proxy, Import proxy geometry (optional)
- **import_render** (bool) – Render, Import final render geometry (optional)
- **import_all_materials** (bool) – Import All Materials, Also import materials that are not used by any geometry. Note that when this option is false, materials referenced by geometry will still be imported (optional)
- **import_usd_preview** (bool) – Import USD Preview, Convert UsdPreviewSurface shaders to Principled BSDF shader networks (optional)
- **set_material_blend** (bool) – Set Material Blend, If the Import USD Preview option is enabled, the material blend method will automatically be set based on the shader’s opacity and opacityThreshold inputs (optional)
- **light_intensity_scale** (float) – Light Intensity Scale, Scale for the intensity of imported lights (in [0.0001, 10000], optional)
- **mtl_purpose** (Literal['MTL_ALL_PURPOSE', 'MTL_PREVIEW', 'MTL_FULL']) –

  Material Purpose, Attempt to import materials with the given purpose. If no material with this purpose is bound to the primitive, fall back on loading any other bound material (optional)

  - `MTL_ALL_PURPOSE`
    All Purpose – Attempt to import ‘allPurpose’ materials..
  - `MTL_PREVIEW`
    Preview – Attempt to import ‘preview’ materials. Load ‘allPurpose’ materials as a fallback.
  - `MTL_FULL`
    Full – Attempt to import ‘full’ materials. Load ‘allPurpose’ or ‘preview’ materials, in that order, as a fallback.
- **mtl_name_collision_mode** (Literal['MAKE_UNIQUE', 'REFERENCE_EXISTING']) –

  Material Name Collision, Behavior when the name of an imported material conflicts with an existing material (optional)

  - `MAKE_UNIQUE`
    Make Unique – Import each USD material as a unique Blender material.
  - `REFERENCE_EXISTING`
    Reference Existing – If a material with the same name already exists, reference that instead of importing.
- **import_textures_mode** (Literal['IMPORT_NONE', 'IMPORT_PACK', 'IMPORT_COPY']) –

  Import Textures, Behavior when importing textures from a USDZ archive (optional)

  - `IMPORT_NONE`
    None – Don’t import textures.
  - `IMPORT_PACK`
    Packed – Import textures as packed data.
  - `IMPORT_COPY`
    Copy – Copy files to textures directory.
- **import_textures_dir** (str) – Textures Directory, Path to the directory where imported textures will be copied (optional, never None)
- **tex_name_collision_mode** (Literal['USE_EXISTING', 'OVERWRITE']) –

  File Name Collision, Behavior when the name of an imported texture file conflicts with an existing file (optional)

  - `USE_EXISTING`
    Use Existing – If a file with the same name already exists, use that instead of copying.
  - `OVERWRITE`
    Overwrite – Overwrite existing files.
- **property_import_mode** (Literal['NONE', 'USER', 'ALL']) –

  Custom Properties, Behavior when importing USD attributes as Blender custom properties (optional)

  - `NONE`
    None – Do not import USD custom attributes.
  - `USER`
    User – Import USD attributes in the ‘userProperties’ namespace as Blender custom properties. The namespace will be stripped from the property names.
  - `ALL`
    All Custom – Import all USD custom attributes as Blender custom properties. Namespaces will be retained in the property names.
- **validate_meshes** (bool) – Validate Meshes, Ensure the data is valid (when disabled, data may be imported which causes crashes displaying or editing) (optional)
- **create_world_material** (bool) – World Dome Light, Convert the first discovered USD dome light to a world background shader (optional)
- **import_defined_only** (bool) – Defined Primitives Only, Import only defined USD primitives. When disabled this allows importing USD primitives which are not defined, such as those with an override specifier (optional)
- **merge_parent_xform** (bool) – Merge parent Xform, Allow USD primitives to merge with their Xform parent if they are the only child in the hierarchy (optional)
- **apply_unit_conversion_scale** (bool) – Apply Unit Conversion Scale, Scale the scene objects by the USD stage’s meters per unit value. This scaling is applied in addition to the value specified in the Scale option (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.window_close"></a>

### bpy.ops.wm.window_close()

Close the current window

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.window_fullscreen_toggle"></a>

### bpy.ops.wm.window_fullscreen_toggle()

Toggle the current window full-screen

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.window_new"></a>

### bpy.ops.wm.window_new()

Create a new window

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.window_new_main"></a>

### bpy.ops.wm.window_new_main()

Create a new main window with its own workspace and scene selection

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.xr_navigation_fly"></a>

### bpy.ops.wm.xr_navigation_fly(*, mode='VIEWER_FORWARD', snap_turn_threshold=0.95, lock_location_z=False, lock_direction=False, speed_frame_based=False, turn_speed_factor=0.333333, fly_speed_factor=0.333333, speed_interpolation0=(0.0, 0.0), speed_interpolation1=(1.0, 1.0), alt_mode='VIEWER_FORWARD', alt_lock_location_z=False, alt_lock_direction=False)

Move/turn relative to the VR viewer or controller

**Parameters:**

- **mode** (Literal['FORWARD', 'BACK', 'LEFT', 'RIGHT', 'UP', 'DOWN', 'TURNLEFT', 'TURNRIGHT', 'VIEWER_FORWARD', 'VIEWER_BACK', 'VIEWER_LEFT', 'VIEWER_RIGHT', 'CONTROLLER_FORWARD']) –

  Mode, Fly mode (optional)

  - `FORWARD`
    Forward – Move along navigation forward axis.
  - `BACK`
    Back – Move along navigation back axis.
  - `LEFT`
    Left – Move along navigation left axis.
  - `RIGHT`
    Right – Move along navigation right axis.
  - `UP`
    Up – Move along navigation up axis.
  - `DOWN`
    Down – Move along navigation down axis.
  - `TURNLEFT`
    Turn Left – Turn counter-clockwise around navigation up axis.
  - `TURNRIGHT`
    Turn Right – Turn clockwise around navigation up axis.
  - `VIEWER_FORWARD`
    Viewer Forward – Move along viewer’s forward axis.
  - `VIEWER_BACK`
    Viewer Back – Move along viewer’s back axis.
  - `VIEWER_LEFT`
    Viewer Left – Move along viewer’s left axis.
  - `VIEWER_RIGHT`
    Viewer Right – Move along viewer’s right axis.
  - `CONTROLLER_FORWARD`
    Controller Forward – Move along controller’s forward axis.
- **snap_turn_threshold** (float) – Snap Turn Threshold, Input state threshold when using snap turn (in [0, 1], optional)
- **lock_location_z** (bool) – Lock Elevation, Prevent changes to viewer elevation (optional)
- **lock_direction** (bool) – Lock Direction, Limit movement to viewer’s initial direction (optional)
- **speed_frame_based** (bool) – Frame Based Speed, Apply fixed movement deltas every update (optional)
- **turn_speed_factor** (float) – Turn Speed Factor, Ratio between the min and max turn speed (in [0, 1], optional)
- **fly_speed_factor** (float) – Fly Speed Factor, Ratio between the min and max fly speed (in [0, 1], optional)
- **speed_interpolation0** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Speed Interpolation 0, First cubic spline control point between min/max speeds (array of 2 items, in [0, 1], optional)
- **speed_interpolation1** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector") | Sequence[float]) – Speed Interpolation 1, Second cubic spline control point between min/max speeds (array of 2 items, in [0, 1], optional)
- **alt_mode** (Literal['FORWARD', 'BACK', 'LEFT', 'RIGHT', 'UP', 'DOWN', 'TURNLEFT', 'TURNRIGHT', 'VIEWER_FORWARD', 'VIEWER_BACK', 'VIEWER_LEFT', 'VIEWER_RIGHT', 'CONTROLLER_FORWARD']) –

  Mode (Alt), Fly mode when hands are swapped (optional)

  - `FORWARD`
    Forward – Move along navigation forward axis.
  - `BACK`
    Back – Move along navigation back axis.
  - `LEFT`
    Left – Move along navigation left axis.
  - `RIGHT`
    Right – Move along navigation right axis.
  - `UP`
    Up – Move along navigation up axis.
  - `DOWN`
    Down – Move along navigation down axis.
  - `TURNLEFT`
    Turn Left – Turn counter-clockwise around navigation up axis.
  - `TURNRIGHT`
    Turn Right – Turn clockwise around navigation up axis.
  - `VIEWER_FORWARD`
    Viewer Forward – Move along viewer’s forward axis.
  - `VIEWER_BACK`
    Viewer Back – Move along viewer’s back axis.
  - `VIEWER_LEFT`
    Viewer Left – Move along viewer’s left axis.
  - `VIEWER_RIGHT`
    Viewer Right – Move along viewer’s right axis.
  - `CONTROLLER_FORWARD`
    Controller Forward – Move along controller’s forward axis.
- **alt_lock_location_z** (bool) – Lock Elevation (Alt), When hands are swapped, prevent changes to viewer elevation (optional)
- **alt_lock_direction** (bool) – Lock Direction (Alt), When hands are swapped, limit movement to viewer’s initial direction (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.xr_navigation_grab"></a>

### bpy.ops.wm.xr_navigation_grab(*, lock_location=False, lock_location_z=False, lock_rotation=False, lock_rotation_z=False, lock_scale=False)

Navigate the VR scene by grabbing with controllers

**Parameters:**

- **lock_location** (bool) – Lock Location, Prevent changes to viewer location (optional)
- **lock_location_z** (bool) – Lock Elevation, Prevent changes to viewer elevation (optional)
- **lock_rotation** (bool) – Lock Rotation, Prevent changes to viewer rotation (optional)
- **lock_rotation_z** (bool) – Lock Up Orientation, Prevent changes to viewer up orientation (optional)
- **lock_scale** (bool) – Lock Scale, Prevent changes to viewer scale (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.xr_navigation_reset"></a>

### bpy.ops.wm.xr_navigation_reset(*, location=True, rotation=True, scale=True)

Reset VR navigation deltas relative to session base pose

**Parameters:**

- **location** (bool) – Location, Reset location deltas (optional)
- **rotation** (bool) – Rotation, Reset rotation deltas (optional)
- **scale** (bool) – Scale, Reset scale deltas (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.xr_navigation_swap_hands"></a>

### bpy.ops.wm.xr_navigation_swap_hands()

Swap VR navigation controls between left / right controllers

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.xr_navigation_teleport"></a>

### bpy.ops.wm.xr_navigation_teleport(*, selectable_only=True, force=8.5, range=0.15, ray_line_width=6.0, destination_indicator_width=0.18, hit_color=(0.4, 0.6, 0.9, 1.0), miss_color=(1.0, 0.35, 0.35, 1.0), fallback_color=(0.5, 0.45, 0.8, 1.0))

Set VR viewer location to controller raycast hit location

**Parameters:**

- **selectable_only** (bool) – Selectable Only, Only allow selectable objects to influence raycast result (optional)
- **force** (float) – Force, Velocity force controlling the teleportation arc parabola in m/s (in [0, inf], optional)
- **range** (float) – Range, Time step range controlling the teleportation arc parabola (in [0, inf], optional)
- **ray_line_width** (float) – Ray Line Width, Visual width of the teleportation ray line (in [0, inf], optional)
- **destination_indicator_width** (float) – Destination Indicator Width, Visual width of the hit destination indicator (in [0, inf], optional)
- **hit_color** (Sequence[float]) – Hit Color, Color of raycast when it succeeds (array of 4 items, in [0, 1], optional)
- **miss_color** (Sequence[float]) – Miss Color, Color of raycast when it misses (array of 4 items, in [0, 1], optional)
- **fallback_color** (Sequence[float]) – Fallback Color, Color of raycast when a fallback case succeeds (array of 4 items, in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.wm.xr_session_toggle"></a>

### bpy.ops.wm.xr_session_toggle()

Open a view for use with virtual reality headsets, or close it if already opened

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]
