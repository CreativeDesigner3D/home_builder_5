<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/asset_import_method_items.html -->

<a id="asset-import-method-items"></a>

# Asset Import Method Items

**LINK:**

Link.

Import the assets as linked data-block.

**APPEND:**

Append.

Import the assets as copied data-block, with no link to the original asset data-block.

**APPEND_REUSE:**

Append (Reuse Data).

Import the assets as copied data-block while avoiding multiple copies of nested, typically heavy data. For example the textures of a material asset, or the mesh of an object asset, don’t have to be copied every time this asset is imported. The instances of the asset share the data instead..

**PACK:**

Pack.

Import the asset as linked data-block, and pack it in the current file (ensures that it remains unchanged in case the library data is modified, is not available anymore, etc.).
