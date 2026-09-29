<!-- source: Blender Python API reference 5.2 / bpy_extras.asset_utils.html -->

<a id="module-bpy_extras.asset_utils"></a>

# bpy_extras submodule (bpy_extras.asset_utils)

Helpers for asset management tasks.

<a id="bpy_extras.asset_utils.AssetBrowserPanel"></a>

### class bpy_extras.asset_utils.AssetBrowserPanel

Mixin class for panels that should only show in the asset browser.

<a id="bpy_extras.asset_utils.AssetBrowserPanel.asset_browser_panel_poll"></a>

#### classmethod bpy_extras.asset_utils.AssetBrowserPanel.asset_browser_panel_poll(context)

Check if the panel should be shown in the asset browser.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

True when the panel should be visible.

**Return type:**

bool

<a id="bpy_extras.asset_utils.AssetBrowserPanel.poll"></a>

#### classmethod bpy_extras.asset_utils.AssetBrowserPanel.poll(context)

Poll for asset browser visibility.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

True when the panel should be visible.

**Return type:**

bool

<a id="bpy_extras.asset_utils.AssetMetaDataPanel"></a>

### class bpy_extras.asset_utils.AssetMetaDataPanel

Mixin class for panels that display asset metadata in the asset browser.

<a id="bpy_extras.asset_utils.AssetMetaDataPanel.poll"></a>

#### classmethod bpy_extras.asset_utils.AssetMetaDataPanel.poll(context)

Poll for asset browser with active asset metadata.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

True when the asset browser has active asset data.

**Return type:**

bool

<a id="bpy_extras.asset_utils.SpaceAssetInfo"></a>

### class bpy_extras.asset_utils.SpaceAssetInfo

Utility class for checking if a space is an asset browser.

<a id="bpy_extras.asset_utils.SpaceAssetInfo.is_asset_browser"></a>

#### classmethod bpy_extras.asset_utils.SpaceAssetInfo.is_asset_browser(space_data)

Check if the given space is an asset browser.

**Parameters:**

**space_data** ([`bpy.types.Space`](bpy.types.Space.md#bpy.types.Space "bpy.types.Space")) – The space to check.

**Returns:**

True when the space is an asset browser.

**Return type:**

bool

<a id="bpy_extras.asset_utils.SpaceAssetInfo.is_asset_browser_poll"></a>

#### classmethod bpy_extras.asset_utils.SpaceAssetInfo.is_asset_browser_poll(context)

Poll whether the active space is an asset browser.

**Parameters:**

**context** ([`bpy.types.Context`](bpy.types.Context.md#bpy.types.Context "bpy.types.Context")) – The context.

**Returns:**

True when the active space is an asset browser.

**Return type:**

bool
