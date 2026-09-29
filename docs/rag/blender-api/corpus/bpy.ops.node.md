<!-- source: Blender Python API reference 5.2 / bpy.ops.node.html -->

<a id="module-bpy.ops.node"></a>

# Node Operators

<a id="bpy.ops.node.activate_viewer"></a>

### bpy.ops.node.activate_viewer()

Activate selected viewer node in compositor and geometry nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_closure_zone"></a>

### bpy.ops.node.add_closure_zone(*, settings=None, use_transform=False, offset=(150.0, 0.0))

Add a Closure zone

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **use_transform** (bool) – Use Transform, Start transform operator after inserting the node (optional)
- **offset** (Sequence[float]) – Offset, Offset of nodes from the cursor when added (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:857](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L857)

<a id="bpy.ops.node.add_collection"></a>

### bpy.ops.node.add_collection(*, name='', session_uid=0)

Add a collection info node to the current node editor

**Parameters:**

- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_color"></a>

### bpy.ops.node.add_color(*, color=(0.0, 0.0, 0.0, 0.0), gamma=False, has_alpha=False)

Add a color node to the current node editor

**Parameters:**

- **color** (Sequence[float]) – Color, Source color (array of 4 items, in [0, inf], optional)
- **gamma** (bool) – Gamma Corrected, The source color is gamma corrected (optional)
- **has_alpha** (bool) – Has Alpha, The source color contains an Alpha component (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_empty_group"></a>

### bpy.ops.node.add_empty_group(*, settings=None, use_transform=False)

Add a group node with an empty group

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **use_transform** (bool) – Use Transform, Start transform operator after inserting the node (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:730](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L730)

<a id="bpy.ops.node.add_foreach_geometry_element_zone"></a>

### bpy.ops.node.add_foreach_geometry_element_zone(*, settings=None, use_transform=False, offset=(150.0, 0.0))

Add a For Each Geometry Element zone that allows executing nodes e.g. for each vertex separately

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **use_transform** (bool) – Use Transform, Start transform operator after inserting the node (optional)
- **offset** (Sequence[float]) – Offset, Offset of nodes from the cursor when added (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:857](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L857)

<a id="bpy.ops.node.add_group"></a>

### bpy.ops.node.add_group(*, name='', session_uid=0, show_datablock_in_node=True)

Add an existing node group to the current node editor

**Parameters:**

- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)
- **show_datablock_in_node** (bool) – Show the data-block selector in the node, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_group_asset"></a>

### bpy.ops.node.add_group_asset(*, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='')

Add a node group asset to the active node tree

**Parameters:**

- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_group_input_node"></a>

### bpy.ops.node.add_group_input_node(*, only_selected_sockets=True, all_panel_contents=False)

Add a Group Input node with selected sockets to the current node editor

**Parameters:**

- **only_selected_sockets** (bool) – Only Selected Sockets, Include only selected sockets/panels in the added group input node (optional)
- **all_panel_contents** (bool) – All Panel Contents, Include sockets in all selected panels, even if they have a panel toggle (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_image"></a>

### bpy.ops.node.add_image(*, filepath='', directory='', files=None, hide_props_region=True, check_existing=False, filter_blender=False, filter_backup=False, filter_image=True, filter_movie=True, filter_python=False, filter_font=False, filter_sound=False, filter_text=False, filter_archive=False, filter_btx=False, filter_alembic=False, filter_usd=False, filter_obj=False, filter_volume=False, filter_folder=True, filter_blenlib=False, filemode=9, relative_path=True, show_multiview=False, use_multiview=False, display_type='DEFAULT', sort_method='', name='', session_uid=0)

Add a image/movie file as node to the current node editor

**Parameters:**

- **filepath** (str) – File Path, Path to file (optional, never None)
- **directory** (str) – Directory, Directory of the file (optional, never None)
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
- **show_multiview** (bool) – Enable Multi-View, (optional)
- **use_multiview** (bool) – Use Multi-View, (optional)
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
- **sort_method** (Literal['', 'DEFAULT', 'FILE_SORT_ALPHA', 'FILE_SORT_EXTENSION', 'FILE_SORT_TIME', 'FILE_SORT_SIZE', 'ASSET_CATALOG']) –

  File sorting mode, (optional)

  - `DEFAULT`
    Default – Automatically determine sort method for files.
  - `FILE_SORT_ALPHA`
    Name – Sort the file list alphabetically.
  - `FILE_SORT_EXTENSION`
    Extension – Sort the file list by extension/type.
  - `FILE_SORT_TIME`
    Modified Date – Sort files by modification time.
  - `FILE_SORT_SIZE`
    Size – Sort files by size.
  - `ASSET_CATALOG`
    Asset Catalog – Sort the asset list so that assets in the same catalog are kept together. Within a single catalog, assets are ordered by name. The catalogs are in order of the flattened catalog hierarchy..
- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_import_node"></a>

### bpy.ops.node.add_import_node(*, directory='', files=None)

Add an import node to the node tree

**Parameters:**

- **directory** (str) – Directory, Directory of the file (optional, never None)
- **files** (`bpy_prop_collection`[`OperatorFileListElement`] | None) – Files, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_mask"></a>

### bpy.ops.node.add_mask(*, name='', session_uid=0)

Add a mask node to the current node editor

**Parameters:**

- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_material"></a>

### bpy.ops.node.add_material(*, name='', session_uid=0)

Add a material node to the current node editor

**Parameters:**

- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_node"></a>

### bpy.ops.node.add_node(*, settings=None, use_transform=False, type='', visible_output='')

Add a node to the active tree

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **use_transform** (bool) – Use Transform, Start transform operator after inserting the node (optional)
- **type** (str) – Node Type, Node type (optional, never None)
- **visible_output** (str) – Output Name, If provided, all outputs that are named differently will be hidden (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:566](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L566)

<a id="bpy.ops.node.add_object"></a>

### bpy.ops.node.add_object(*, name='', session_uid=0)

Add an object info node to the current node editor

**Parameters:**

- **name** (str) – Name, Name of the data-block to use by the operator (optional, never None)
- **session_uid** (int) – Session UID, Session UID of the data-block to use by the operator (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_repeat_zone"></a>

### bpy.ops.node.add_repeat_zone(*, settings=None, use_transform=False, offset=(150.0, 0.0))

Add a repeat zone that allows executing nodes a dynamic number of times

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **use_transform** (bool) – Use Transform, Start transform operator after inserting the node (optional)
- **offset** (Sequence[float]) – Offset, Offset of nodes from the cursor when added (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:857](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L857)

<a id="bpy.ops.node.add_reroute"></a>

### bpy.ops.node.add_reroute(*, path=None, cursor=11)

Add a reroute node

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **cursor** (int) – Cursor, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.add_simulation_zone"></a>

### bpy.ops.node.add_simulation_zone(*, settings=None, use_transform=False, offset=(150.0, 0.0))

Add simulation zone input and output nodes to the active tree

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **use_transform** (bool) – Use Transform, Start transform operator after inserting the node (optional)
- **offset** (Sequence[float]) – Offset, Offset of nodes from the cursor when added (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:857](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L857)

<a id="bpy.ops.node.add_typed_bundle"></a>

### bpy.ops.node.add_typed_bundle(*, settings=None, use_transform=False)

Add a Combine Bundle node with a type input

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **use_transform** (bool) – Use Transform, Start transform operator after inserting the node (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:798](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L798)

<a id="bpy.ops.node.add_zone"></a>

### bpy.ops.node.add_zone(*, settings=None, use_transform=False, offset=(150.0, 0.0), input_node_type='', output_node_type='', add_default_geometry_link=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **use_transform** (bool) – Use Transform, Start transform operator after inserting the node (optional)
- **offset** (Sequence[float]) – Offset, Offset of nodes from the cursor when added (array of 2 items, in [-inf, inf], optional)
- **input_node_type** (str) – Input Node, Specifies the input node used by the created zone (optional, never None)
- **output_node_type** (str) – Output Node, Specifies the output node used by the created zone (optional, never None)
- **add_default_geometry_link** (bool) – Add Geometry Link, When enabled, create a link between geometry sockets in this zone (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:857](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L857)

<a id="bpy.ops.node.attach"></a>

### bpy.ops.node.attach()

Attach active node to a frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.backimage_fit"></a>

### bpy.ops.node.backimage_fit()

Fit the background image to the view

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.backimage_move"></a>

### bpy.ops.node.backimage_move()

Move node backdrop

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.backimage_sample"></a>

### bpy.ops.node.backimage_sample()

Use mouse to sample background image

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.backimage_zoom"></a>

### bpy.ops.node.backimage_zoom(*, factor=1.2, use_mouse_pos=True)

Zoom in/out the background image

**Parameters:**

- **factor** (float) – Factor, (in [0, 10], optional)
- **use_mouse_pos** (bool) – Use Mouse Position, Zoom to mouse position (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.bake_node_item_add"></a>

### bpy.ops.node.bake_node_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.bake_node_item_move"></a>

### bpy.ops.node.bake_node_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.bake_node_item_remove"></a>

### bpy.ops.node.bake_node_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.capture_attribute_item_add"></a>

### bpy.ops.node.capture_attribute_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.capture_attribute_item_move"></a>

### bpy.ops.node.capture_attribute_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.capture_attribute_item_remove"></a>

### bpy.ops.node.capture_attribute_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.clear_viewer_border"></a>

### bpy.ops.node.clear_viewer_border()

Clear the boundaries for viewer operations

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.clipboard_copy"></a>

### bpy.ops.node.clipboard_copy()

Copy the selected nodes to the internal clipboard

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.clipboard_paste"></a>

### bpy.ops.node.clipboard_paste(*, offset=(0.0, 0.0))

Paste nodes from the internal clipboard to the active node tree

**Parameters:**

**offset** (Sequence[float]) – Location, The 2D view location for the center of the new nodes, or unchanged if not set (array of 2 items, in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_input_item_add"></a>

### bpy.ops.node.closure_input_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_input_item_move"></a>

### bpy.ops.node.closure_input_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_input_item_remove"></a>

### bpy.ops.node.closure_input_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_output_item_add"></a>

### bpy.ops.node.closure_output_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_output_item_move"></a>

### bpy.ops.node.closure_output_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_output_item_remove"></a>

### bpy.ops.node.closure_output_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_to_list_item_add"></a>

### bpy.ops.node.closure_to_list_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_to_list_item_move"></a>

### bpy.ops.node.closure_to_list_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.closure_to_list_item_remove"></a>

### bpy.ops.node.closure_to_list_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.collapse_hide_unused_toggle"></a>

### bpy.ops.node.collapse_hide_unused_toggle()

Toggle collapsed nodes and hide unused sockets

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1123](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1123)

<a id="bpy.ops.node.combine_bundle_item_add"></a>

### bpy.ops.node.combine_bundle_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.combine_bundle_item_move"></a>

### bpy.ops.node.combine_bundle_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.combine_bundle_item_remove"></a>

### bpy.ops.node.combine_bundle_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.connect_to_output"></a>

### bpy.ops.node.connect_to_output(*, run_in_geometry_nodes=True)

Connect active node to the active output node of the node tree

**Parameters:**

**run_in_geometry_nodes** (bool) – Run in Geometry Nodes Editor, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/connect_to_output.py:251](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/connect_to_output.py#L251)

<a id="bpy.ops.node.cryptomatte_layer_add"></a>

### bpy.ops.node.cryptomatte_layer_add()

Add a new input layer to a Cryptomatte node

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.cryptomatte_layer_remove"></a>

### bpy.ops.node.cryptomatte_layer_remove()

Remove layer from a Cryptomatte node

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.deactivate_viewer"></a>

### bpy.ops.node.deactivate_viewer()

Deactivate selected viewer node in geometry nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.default_group_width_set"></a>

### bpy.ops.node.default_group_width_set()

Set the width based on the parent group node in the current context

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.delete"></a>

### bpy.ops.node.delete()

Remove selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.delete_copy_reconnect"></a>

### bpy.ops.node.delete_copy_reconnect(*, NODE_OT_clipboard_copy={}, NODE_OT_delete_reconnect={})

Copy nodes to clipboard, remove and reconnect them.

**Parameters:**

- **NODE_OT_clipboard_copy** (dict[str, Any]) – Copy to Clipboard, Copy the selected nodes to the internal clipboard (optional, [`bpy.ops.node.clipboard_copy()`](#bpy.ops.node.clipboard_copy "bpy.ops.node.clipboard_copy") keyword arguments)
- **NODE_OT_delete_reconnect** (dict[str, Any]) – Delete with Reconnect, Remove nodes and reconnect nodes as if deletion was muted (optional, [`bpy.ops.node.delete_reconnect()`](#bpy.ops.node.delete_reconnect "bpy.ops.node.delete_reconnect") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.delete_reconnect"></a>

### bpy.ops.node.delete_reconnect()

Remove nodes and reconnect nodes as if deletion was muted

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.detach"></a>

### bpy.ops.node.detach()

Detach selected nodes from parents

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.detach_translate_attach"></a>

### bpy.ops.node.detach_translate_attach(*, NODE_OT_detach={}, TRANSFORM_OT_translate={}, NODE_OT_attach={})

Detach nodes, move and attach to frame

**Parameters:**

- **NODE_OT_detach** (dict[str, Any]) – Detach Nodes, Detach selected nodes from parents (optional, [`bpy.ops.node.detach()`](#bpy.ops.node.detach "bpy.ops.node.detach") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)
- **NODE_OT_attach** (dict[str, Any]) – Attach Nodes, Attach active node to a frame (optional, [`bpy.ops.node.attach()`](#bpy.ops.node.attach "bpy.ops.node.attach") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.duplicate"></a>

### bpy.ops.node.duplicate(*, keep_inputs=False, linked=True)

Duplicate selected nodes

**Parameters:**

- **keep_inputs** (bool) – Keep Inputs, Keep the input links to duplicated nodes (optional)
- **linked** (bool) – Linked, Duplicate node but not node trees, linking to the original data (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.duplicate_compositing_modifier_node_group"></a>

### bpy.ops.node.duplicate_compositing_modifier_node_group()

Duplicate the currently assigned compositing node group.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.duplicate_compositing_node_group"></a>

### bpy.ops.node.duplicate_compositing_node_group()

Duplicate the currently assigned compositing node group.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.duplicate_move"></a>

### bpy.ops.node.duplicate_move(*, NODE_OT_duplicate={}, NODE_OT_translate_attach={})

Duplicate selected nodes and move them

**Parameters:**

- **NODE_OT_duplicate** (dict[str, Any]) – Duplicate Nodes, Duplicate selected nodes (optional, [`bpy.ops.node.duplicate()`](#bpy.ops.node.duplicate "bpy.ops.node.duplicate") keyword arguments)
- **NODE_OT_translate_attach** (dict[str, Any]) – Move and Attach, Move nodes and attach to frame (optional, [`bpy.ops.node.translate_attach()`](#bpy.ops.node.translate_attach "bpy.ops.node.translate_attach") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.duplicate_move_keep_inputs"></a>

### bpy.ops.node.duplicate_move_keep_inputs(*, NODE_OT_duplicate={}, NODE_OT_translate_attach={})

Duplicate selected nodes keeping input links and move them

**Parameters:**

- **NODE_OT_duplicate** (dict[str, Any]) – Duplicate Nodes, Duplicate selected nodes (optional, [`bpy.ops.node.duplicate()`](#bpy.ops.node.duplicate "bpy.ops.node.duplicate") keyword arguments)
- **NODE_OT_translate_attach** (dict[str, Any]) – Move and Attach, Move nodes and attach to frame (optional, [`bpy.ops.node.translate_attach()`](#bpy.ops.node.translate_attach "bpy.ops.node.translate_attach") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.duplicate_move_linked"></a>

### bpy.ops.node.duplicate_move_linked(*, NODE_OT_duplicate={}, NODE_OT_translate_attach={})

Duplicate selected nodes, but not their node trees, and move them

**Parameters:**

- **NODE_OT_duplicate** (dict[str, Any]) – Duplicate Nodes, Duplicate selected nodes (optional, [`bpy.ops.node.duplicate()`](#bpy.ops.node.duplicate "bpy.ops.node.duplicate") keyword arguments)
- **NODE_OT_translate_attach** (dict[str, Any]) – Move and Attach, Move nodes and attach to frame (optional, [`bpy.ops.node.translate_attach()`](#bpy.ops.node.translate_attach "bpy.ops.node.translate_attach") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.enum_definition_item_add"></a>

### bpy.ops.node.enum_definition_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.enum_definition_item_move"></a>

### bpy.ops.node.enum_definition_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.enum_definition_item_remove"></a>

### bpy.ops.node.enum_definition_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.evaluate_closure_input_item_add"></a>

### bpy.ops.node.evaluate_closure_input_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.evaluate_closure_input_item_move"></a>

### bpy.ops.node.evaluate_closure_input_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.evaluate_closure_input_item_remove"></a>

### bpy.ops.node.evaluate_closure_input_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.evaluate_closure_output_item_add"></a>

### bpy.ops.node.evaluate_closure_output_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.evaluate_closure_output_item_move"></a>

### bpy.ops.node.evaluate_closure_output_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.evaluate_closure_output_item_remove"></a>

### bpy.ops.node.evaluate_closure_output_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.field_to_grid_item_add"></a>

### bpy.ops.node.field_to_grid_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.field_to_grid_item_move"></a>

### bpy.ops.node.field_to_grid_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.field_to_grid_item_remove"></a>

### bpy.ops.node.field_to_grid_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.field_to_list_item_add"></a>

### bpy.ops.node.field_to_list_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.field_to_list_item_move"></a>

### bpy.ops.node.field_to_list_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.field_to_list_item_remove"></a>

### bpy.ops.node.field_to_list_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.file_output_item_add"></a>

### bpy.ops.node.file_output_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.file_output_item_move"></a>

### bpy.ops.node.file_output_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.file_output_item_remove"></a>

### bpy.ops.node.file_output_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.find_node"></a>

### bpy.ops.node.find_node()

Search for a node by name and focus and select it

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_generation_item_add"></a>

### bpy.ops.node.foreach_geometry_element_zone_generation_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_generation_item_move"></a>

### bpy.ops.node.foreach_geometry_element_zone_generation_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_generation_item_remove"></a>

### bpy.ops.node.foreach_geometry_element_zone_generation_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_input_item_add"></a>

### bpy.ops.node.foreach_geometry_element_zone_input_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_input_item_move"></a>

### bpy.ops.node.foreach_geometry_element_zone_input_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_input_item_remove"></a>

### bpy.ops.node.foreach_geometry_element_zone_input_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_main_item_add"></a>

### bpy.ops.node.foreach_geometry_element_zone_main_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_main_item_move"></a>

### bpy.ops.node.foreach_geometry_element_zone_main_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.foreach_geometry_element_zone_main_item_remove"></a>

### bpy.ops.node.foreach_geometry_element_zone_main_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.format_string_item_add"></a>

### bpy.ops.node.format_string_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.format_string_item_move"></a>

### bpy.ops.node.format_string_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.format_string_item_remove"></a>

### bpy.ops.node.format_string_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.geometry_nodes_viewer_item_add"></a>

### bpy.ops.node.geometry_nodes_viewer_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.geometry_nodes_viewer_item_move"></a>

### bpy.ops.node.geometry_nodes_viewer_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.geometry_nodes_viewer_item_remove"></a>

### bpy.ops.node.geometry_nodes_viewer_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.gltf_settings_node_operator"></a>

### bpy.ops.node.gltf_settings_node_operator()

Add a node to the active tree for glTF export

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[addons_core/io_scene_gltf2/blender/com/gltf2_blender_ui.py:34](https://projects.blender.org/blender/blender/src/branch/main/scripts/addons_core/io_scene_gltf2/blender/com/gltf2_blender_ui.py#L34)

<a id="bpy.ops.node.group_edit"></a>

### bpy.ops.node.group_edit(*, exit=False)

Edit node group

**Parameters:**

**exit** (bool) – Exit, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.group_enter_exit"></a>

### bpy.ops.node.group_enter_exit()

Enter or exit node group based on cursor location

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.group_insert"></a>

### bpy.ops.node.group_insert()

Insert selected nodes into a node group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.group_make"></a>

### bpy.ops.node.group_make()

Make group from selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.group_separate"></a>

### bpy.ops.node.group_separate(*, type='COPY')

Separate selected nodes from the node group

**Parameters:**

**type** (Literal['COPY', 'MOVE']) –

Type, (optional)

- `COPY`
  Copy – Copy to parent node tree, keep group intact.
- `MOVE`
  Move – Move to parent node tree, remove from group.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.group_ungroup"></a>

### bpy.ops.node.group_ungroup()

Ungroup selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.hide_socket_toggle"></a>

### bpy.ops.node.hide_socket_toggle()

Toggle unused node socket display

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.hide_toggle"></a>

### bpy.ops.node.hide_toggle()

Toggle collapsing of selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.index_switch_item_add"></a>

### bpy.ops.node.index_switch_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True)

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.index_switch_item_move"></a>

### bpy.ops.node.index_switch_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.index_switch_item_remove"></a>

### bpy.ops.node.index_switch_item_remove(*, index=0)

Remove active item

**Parameters:**

**index** (int) – Index, Index to remove (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.insert_offset"></a>

### bpy.ops.node.insert_offset()

Automatically offset nodes on insertion

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.interface_item_duplicate"></a>

### bpy.ops.node.interface_item_duplicate()

Add a copy of the active item to the interface

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1312](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1312)

<a id="bpy.ops.node.interface_item_make_panel_toggle"></a>

### bpy.ops.node.interface_item_make_panel_toggle()

Make the active boolean socket a toggle for its parent panel

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1391](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1391)

<a id="bpy.ops.node.interface_item_new"></a>

### bpy.ops.node.interface_item_new(*, item_type='INPUT')

Add a new item to the interface

**Parameters:**

**item_type** (Literal['INPUT', 'OUTPUT', 'PANEL']) – Item Type, Type of the item to create (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1215](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1215)

<a id="bpy.ops.node.interface_item_new_panel_toggle"></a>

### bpy.ops.node.interface_item_new_panel_toggle()

Add a checkbox to the currently selected panel

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1280](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1280)

<a id="bpy.ops.node.interface_item_remove"></a>

### bpy.ops.node.interface_item_remove()

Remove selected items from the interface

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1331](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1331)

<a id="bpy.ops.node.interface_item_unlink_panel_toggle"></a>

### bpy.ops.node.interface_item_unlink_panel_toggle()

Make the panel toggle a stand-alone socket

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1437](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1437)

<a id="bpy.ops.node.join"></a>

### bpy.ops.node.join()

Attach selected nodes to a new common frame

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.join_named"></a>

### bpy.ops.node.join_named(*, NODE_OT_join={}, WM_OT_call_panel={})

Create a new frame node around the selected nodes and name it immediately

**Parameters:**

- **NODE_OT_join** (dict[str, Any]) – Join Nodes in Frame, Attach selected nodes to a new common frame (optional, [`bpy.ops.node.join()`](#bpy.ops.node.join "bpy.ops.node.join") keyword arguments)
- **WM_OT_call_panel** (dict[str, Any]) – Call Panel, Open a predefined panel (optional, [`bpy.ops.wm.call_panel()`](bpy.ops.wm.md#bpy.ops.wm.call_panel "bpy.ops.wm.call_panel") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.join_nodes"></a>

### bpy.ops.node.join_nodes()

Merge selected group input nodes into one if possible

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.link"></a>

### bpy.ops.node.link(*, detach=False, drag_start=(0.0, 0.0), inside_padding=2.0, outside_padding=0.0, speed_ramp=1.0, max_speed=26.0, delay=0.5, zoom_influence=0.5)

Use the mouse to create a link between two nodes

**Parameters:**

- **detach** (bool) – Detach, Detach and redirect existing links (optional)
- **drag_start** (Sequence[float]) – Drag Start, The position of the mouse cursor at the start of the operation (array of 2 items, in [-6, 6], optional)
- **inside_padding** (float) – Inside Padding, Inside distance in UI units from the edge of the region within which to start panning (in [0, 100], optional)
- **outside_padding** (float) – Outside Padding, Outside distance in UI units from the edge of the region at which to stop panning (in [0, 100], optional)
- **speed_ramp** (float) – Speed Ramp, Width of the zone in UI units where speed increases with distance from the edge (in [0, 100], optional)
- **max_speed** (float) – Max Speed, Maximum speed in UI units per second (in [0, 10000], optional)
- **delay** (float) – Delay, Delay in seconds before maximum speed is reached (in [0, 10], optional)
- **zoom_influence** (float) – Zoom Influence, Influence of the zoom factor on scroll speed (in [0, 1], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.link_drag_operation_test"></a>

### bpy.ops.node.link_drag_operation_test(*, find_link_operations=False, link_operation_index=-1)

Run a node link-drag operation for testing

**Parameters:**

- **find_link_operations** (bool) – Find Link Operations, Write link operation names for the context socket the “link_operation_names” property of the node tree (optional)
- **link_operation_index** (int) – Link Operation Index, Link operation to execute on the context socket (in [-1, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.link_make"></a>

### bpy.ops.node.link_make(*, replace=False)

Make a link between selected output and input sockets

**Parameters:**

**replace** (bool) – Replace, Replace socket connections with the new links (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.link_viewer"></a>

### bpy.ops.node.link_viewer()

Link to viewer node

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.links_cut"></a>

### bpy.ops.node.links_cut(*, path=None, cursor=15)

Use the mouse to cut (remove) some links

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **cursor** (int) – Cursor, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.links_detach"></a>

### bpy.ops.node.links_detach()

Remove all links to selected nodes, and try to connect neighbor nodes together

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.links_mute"></a>

### bpy.ops.node.links_mute(*, path=None, cursor=39)

Use the mouse to mute links

**Parameters:**

- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **cursor** (int) – Cursor, (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.move_detach_links"></a>

### bpy.ops.node.move_detach_links(*, NODE_OT_links_detach={}, TRANSFORM_OT_translate={})

Move a node to detach links

**Parameters:**

- **NODE_OT_links_detach** (dict[str, Any]) – Detach Links, Remove all links to selected nodes, and try to connect neighbor nodes together (optional, [`bpy.ops.node.links_detach()`](#bpy.ops.node.links_detach "bpy.ops.node.links_detach") keyword arguments)
- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.move_detach_links_release"></a>

### bpy.ops.node.move_detach_links_release(*, NODE_OT_links_detach={}, NODE_OT_translate_attach={})

Move a node to detach links

**Parameters:**

- **NODE_OT_links_detach** (dict[str, Any]) – Detach Links, Remove all links to selected nodes, and try to connect neighbor nodes together (optional, [`bpy.ops.node.links_detach()`](#bpy.ops.node.links_detach "bpy.ops.node.links_detach") keyword arguments)
- **NODE_OT_translate_attach** (dict[str, Any]) – Move and Attach, Move nodes and attach to frame (optional, [`bpy.ops.node.translate_attach()`](#bpy.ops.node.translate_attach "bpy.ops.node.translate_attach") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.mute_toggle"></a>

### bpy.ops.node.mute_toggle()

Toggle muting of selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.new_compositing_node_group"></a>

### bpy.ops.node.new_compositing_node_group(*, name='')

Create a new compositing node group and initialize it with default nodes

**Parameters:**

**name** (str) – Name, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.new_compositor_sequencer_node_group"></a>

### bpy.ops.node.new_compositor_sequencer_node_group(*, name='Sequencer Compositor Nodes')

Create a new compositor node group for sequencer

**Parameters:**

**name** (str) – Name, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.new_geometry_node_group_assign"></a>

### bpy.ops.node.new_geometry_node_group_assign()

Create a new geometry node group and assign it to the active modifier

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/geometry_nodes.py:325](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/geometry_nodes.py#L325)

<a id="bpy.ops.node.new_geometry_node_group_tool"></a>

### bpy.ops.node.new_geometry_node_group_tool()

Create a new geometry node group for a tool

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/geometry_nodes.py:351](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/geometry_nodes.py#L351)

<a id="bpy.ops.node.new_geometry_nodes_modifier"></a>

### bpy.ops.node.new_geometry_nodes_modifier()

Create a new modifier with a new geometry node group

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/geometry_nodes.py:299](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/geometry_nodes.py#L299)

<a id="bpy.ops.node.new_node_tree"></a>

### bpy.ops.node.new_node_tree(*, type='', name='NodeTree')

Create a new node tree

**Parameters:**

- **type** (str) – Tree Type, (optional)
- **name** (str) – Name, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.node_color_preset_add"></a>

### bpy.ops.node.node_color_preset_add(*, name='', remove_name=False, remove_active=False)

Add or remove a Node Color Preset

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

<a id="bpy.ops.node.node_copy_color"></a>

### bpy.ops.node.node_copy_color()

Copy color to all selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.options_toggle"></a>

### bpy.ops.node.options_toggle()

Toggle option buttons display for selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.parent_set"></a>

### bpy.ops.node.parent_set()

Attach selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.preview_toggle"></a>

### bpy.ops.node.preview_toggle()

Toggle preview display for selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.read_viewlayers"></a>

### bpy.ops.node.read_viewlayers()

Read all render layers of all used scenes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.render_changed"></a>

### bpy.ops.node.render_changed()

Render current scene, when input node’s layer has been changed

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.repeat_zone_item_add"></a>

### bpy.ops.node.repeat_zone_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.repeat_zone_item_move"></a>

### bpy.ops.node.repeat_zone_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.repeat_zone_item_remove"></a>

### bpy.ops.node.repeat_zone_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.resize"></a>

### bpy.ops.node.resize()

Resize a node

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.sample_attribute_items_item_add"></a>

### bpy.ops.node.sample_attribute_items_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.sample_attribute_items_item_move"></a>

### bpy.ops.node.sample_attribute_items_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.sample_attribute_items_item_remove"></a>

### bpy.ops.node.sample_attribute_items_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select"></a>

### bpy.ops.node.select(*, extend=False, deselect=False, toggle=False, deselect_all=False, select_passthrough=False, location=(0, 0), socket_select=False, clear_viewer=False)

Select the node under the cursor

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **deselect** (bool) – Deselect, Remove from selection (optional)
- **toggle** (bool) – Toggle Selection, Toggle the selection (optional)
- **deselect_all** (bool) – Deselect On Nothing, Deselect all when nothing under the cursor (optional)
- **select_passthrough** (bool) – Only Select Unselected, Ignore the select action when the element is already selected (optional)
- **location** (Sequence[int]) – Location, Mouse location (array of 2 items, in [-inf, inf], optional)
- **socket_select** (bool) – Socket Select, (optional)
- **clear_viewer** (bool) – Clear Viewer, Deactivate geometry nodes viewer when clicking in empty space (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_all"></a>

### bpy.ops.node.select_all(*, action='TOGGLE')

(De)select all nodes

**Parameters:**

**action** (Literal['TOGGLE', 'SELECT', 'DESELECT', 'INVERT']) –

Action, Selection action to execute (optional)

- `TOGGLE`
  Toggle – Toggle selection for all elements.
- `SELECT`
  Select – Select all elements.
- `DESELECT`
  Deselect – Deselect all elements.
- `INVERT`
  Invert – Invert selection of all elements.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_box"></a>

### bpy.ops.node.select_box(*, tweak=False, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True, mode='SET')

Use box selection to select nodes

**Parameters:**

- **tweak** (bool) – Tweak, Only activate when mouse is not over a node (useful for tweak gesture) (optional)
- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_circle"></a>

### bpy.ops.node.select_circle(*, x=0, y=0, radius=25, wait_for_input=True, mode='SET')

Use circle selection to select nodes

**Parameters:**

- **x** (int) – X, (in [-inf, inf], optional)
- **y** (int) – Y, (in [-inf, inf], optional)
- **radius** (int) – Radius, (in [1, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_grouped"></a>

### bpy.ops.node.select_grouped(*, extend=False, type='TYPE')

Select nodes with similar properties

**Parameters:**

- **extend** (bool) – Extend, Extend selection instead of deselecting everything first (optional)
- **type** (Literal['TYPE', 'COLOR', 'PREFIX', 'SUFFIX']) – Type, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_lasso"></a>

### bpy.ops.node.select_lasso(*, tweak=False, path=None, use_smooth_stroke=False, smooth_stroke_factor=0.75, smooth_stroke_radius=35, mode='SET')

Select nodes using lasso selection

**Parameters:**

- **tweak** (bool) – Tweak, Only activate when mouse is not over a node (useful for tweak gesture) (optional)
- **path** (`bpy_prop_collection`[`OperatorMousePath`] | None) – Path, (optional)
- **use_smooth_stroke** (bool) – Stabilize Stroke, Selection lags behind mouse and follows a smoother path (optional)
- **smooth_stroke_factor** (float) – Smooth Stroke Factor, Higher values give a smoother stroke (in [0.5, 0.99], optional)
- **smooth_stroke_radius** (int) – Smooth Stroke Radius, Minimum distance from last point before selection continues (in [10, 200], optional)
- **mode** (Literal['SET', 'ADD', 'SUB']) –

  Mode, (optional)

  - `SET`
    Set – Set a new selection.
  - `ADD`
    Extend – Extend existing selection.
  - `SUB`
    Subtract – Subtract existing selection.

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_link_viewer"></a>

### bpy.ops.node.select_link_viewer(*, NODE_OT_select={}, NODE_OT_link_viewer={})

Select node and link it to a viewer node

**Parameters:**

- **NODE_OT_select** (dict[str, Any]) – Select, Select the node under the cursor (optional, [`bpy.ops.node.select()`](#bpy.ops.node.select "bpy.ops.node.select") keyword arguments)
- **NODE_OT_link_viewer** (dict[str, Any]) – Link to Viewer Node, Link to viewer node (optional, [`bpy.ops.node.link_viewer()`](#bpy.ops.node.link_viewer "bpy.ops.node.link_viewer") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_linked_from"></a>

### bpy.ops.node.select_linked_from()

Select nodes linked from the selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_linked_to"></a>

### bpy.ops.node.select_linked_to()

Select nodes linked to the selected ones

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.select_same_type_step"></a>

### bpy.ops.node.select_same_type_step(*, prev=False)

Activate and view same node type, step by step

**Parameters:**

**prev** (bool) – Previous, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.separate_bundle_item_add"></a>

### bpy.ops.node.separate_bundle_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.separate_bundle_item_move"></a>

### bpy.ops.node.separate_bundle_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.separate_bundle_item_remove"></a>

### bpy.ops.node.separate_bundle_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.shader_script_update"></a>

### bpy.ops.node.shader_script_update()

Update shader script node with new sockets and options from the script

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.simulation_zone_item_add"></a>

### bpy.ops.node.simulation_zone_item_add(*, node_identifier=0, show_dialog=False, init_from_active=True, socket_type='FLOAT', item_name='')

Add item below active item

**Parameters:**

- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)
- **show_dialog** (bool) – Show Dialog, Show a dialog to edit the initial properties (optional)
- **init_from_active** (bool) – Init from Active, Instead of using the provided name or type, copy the state of the active item (optional)
- **socket_type** (Literal[[Node Socket Data Type Items](bpy_types_enum_items/node_socket_data_type_items.md#rna-enum-node-socket-data-type-items)]) – Socket Type, Type of the new socket item (optional)
- **item_name** (str) – Item Name, Name of the new socket item (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.simulation_zone_item_move"></a>

### bpy.ops.node.simulation_zone_item_move(*, direction='UP', node_identifier=0)

Move active item

**Parameters:**

- **direction** (Literal['UP', 'DOWN']) – Direction, Move direction (optional)
- **node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.simulation_zone_item_remove"></a>

### bpy.ops.node.simulation_zone_item_remove(*, node_identifier=0)

Remove active item

**Parameters:**

**node_identifier** (int) – Node Identifier, Optional identifier of the node to operate on (in [0, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.sockets_sync"></a>

### bpy.ops.node.sockets_sync(*, node_name='')

Update sockets to match what is actually used

**Parameters:**

**node_name** (str) – Node Name, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.swap_empty_group"></a>

### bpy.ops.node.swap_empty_group(*, settings=None)

Replace active node with an empty group

**Parameters:**

**settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:766](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L766)

<a id="bpy.ops.node.swap_group_asset"></a>

### bpy.ops.node.swap_group_asset(*, asset_library_type='LOCAL', asset_library_identifier='', relative_asset_identifier='')

Swap selected nodes with the specified node group asset

**Parameters:**

- **asset_library_type** (Literal[[Asset Library Type Items](bpy_types_enum_items/asset_library_type_items.md#rna-enum-asset-library-type-items)]) – Asset Library Type, (optional)
- **asset_library_identifier** (str) – Asset Library Identifier, (optional, never None)
- **relative_asset_identifier** (str) – Relative Asset Identifier, (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.swap_node"></a>

### bpy.ops.node.swap_node(*, settings=None, type='', visible_output='')

Replace the selected nodes with the specified type

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **type** (str) – Node Type, Node type (optional, never None)
- **visible_output** (str) – Output Name, If provided, all outputs that are named differently will be hidden (optional, never None)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:645](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L645)

<a id="bpy.ops.node.swap_typed_bundle"></a>

### bpy.ops.node.swap_typed_bundle(*, settings=None)

Swap existing node with a Combine Bundle node with a type input

**Parameters:**

**settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:811](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L811)

<a id="bpy.ops.node.swap_zone"></a>

### bpy.ops.node.swap_zone(*, settings=None, offset=(150.0, 0.0), input_node_type='', output_node_type='', add_default_geometry_link=False)

Undocumented, consider [contributing](https://developer.blender.org/).

**Parameters:**

- **settings** (`bpy_prop_collection`[`NodeSetting`] | None) – Settings, Settings to be applied on the newly created node (optional)
- **offset** (Sequence[float]) – Offset, Offset of nodes from the cursor when added (array of 2 items, in [-inf, inf], optional)
- **input_node_type** (str) – Input Node, Specifies the input node used by the created zone (optional, never None)
- **output_node_type** (str) – Output Node, Specifies the output node used by the created zone (optional, never None)
- **add_default_geometry_link** (bool) – Add Geometry Link, When enabled, create a link between geometry sockets in this zone (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:975](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L975)

<a id="bpy.ops.node.test_inlining_shader_nodes"></a>

### bpy.ops.node.test_inlining_shader_nodes()

Create a new inlined shader node tree as is consumed by renderers

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.toggle_viewer"></a>

### bpy.ops.node.toggle_viewer()

Toggle selected viewer node in compositor and geometry nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.translate_attach"></a>

### bpy.ops.node.translate_attach(*, TRANSFORM_OT_translate={}, NODE_OT_attach={})

Move nodes and attach to frame

**Parameters:**

- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)
- **NODE_OT_attach** (dict[str, Any]) – Attach Nodes, Attach active node to a frame (optional, [`bpy.ops.node.attach()`](#bpy.ops.node.attach "bpy.ops.node.attach") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.translate_attach_remove_on_cancel"></a>

### bpy.ops.node.translate_attach_remove_on_cancel(*, TRANSFORM_OT_translate={}, NODE_OT_attach={})

Move nodes and attach to frame

**Parameters:**

- **TRANSFORM_OT_translate** (dict[str, Any]) – Move, Move selected items (optional, [`bpy.ops.transform.translate()`](bpy.ops.transform.md#bpy.ops.transform.translate "bpy.ops.transform.translate") keyword arguments)
- **NODE_OT_attach** (dict[str, Any]) – Attach Nodes, Attach active node to a frame (optional, [`bpy.ops.node.attach()`](#bpy.ops.node.attach "bpy.ops.node.attach") keyword arguments)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.tree_path_parent"></a>

### bpy.ops.node.tree_path_parent(*, parent_tree_index=0)

Go to parent node tree

**Parameters:**

**parent_tree_index** (int) – Parent Index, Parent index in context path (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1159](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1159)

<a id="bpy.ops.node.view_all"></a>

### bpy.ops.node.view_all()

Resize view so you can see all nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.view_selected"></a>

### bpy.ops.node.view_selected()

Resize view so you can see selected nodes

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.viewer_border"></a>

### bpy.ops.node.viewer_border(*, xmin=0, xmax=0, ymin=0, ymax=0, wait_for_input=True)

Set the boundaries for viewer operations (Not implemented)

**Parameters:**

- **xmin** (int) – X Min, (in [-inf, inf], optional)
- **xmax** (int) – X Max, (in [-inf, inf], optional)
- **ymin** (int) – Y Min, (in [-inf, inf], optional)
- **ymax** (int) – Y Max, (in [-inf, inf], optional)
- **wait_for_input** (bool) – Wait for Input, (optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

<a id="bpy.ops.node.viewer_shortcut_get"></a>

### bpy.ops.node.viewer_shortcut_get(*, viewer_index=0)

Toggle a specific viewer node using 1,2,..,9 keys

**Parameters:**

**viewer_index** (int) – Viewer Index, Index corresponding to the shortcut, e.g. number key 1 corresponds to index 1 etc.. (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1551](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1551)

<a id="bpy.ops.node.viewer_shortcut_set"></a>

### bpy.ops.node.viewer_shortcut_set(*, viewer_index=0)

Create a viewer shortcut for the selected node by pressing ctrl+1,2,..9

**Parameters:**

**viewer_index** (int) – Viewer Index, Index corresponding to the shortcut, e.g. number key 1 corresponds to index 1 etc.. (in [-inf, inf], optional)

**Returns:**

Result of the operator call.

**Return type:**

set[Literal[[Operator Return Items](bpy_types_enum_items/operator_return_items.md#rna-enum-operator-return-items)]]

**File:**

[startup/bl_operators/node.py:1491](https://projects.blender.org/blender/blender/src/branch/main/scripts/startup/bl_operators/node.py#L1491)
