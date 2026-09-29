<!-- source: Blender Python API reference 5.2 / bpy.types.BlendDataPathMeta.html -->

<a id="blenddatapathmeta"></a>

# BlendDataPathMeta

<a id="bpy.types.BlendDataPathMeta"></a>

### class bpy.types.BlendDataPathMeta

Metadata about a file path visited by [`bpy.types.BlendData.file_path_foreach`](bpy.types.BlendData.md#bpy.types.BlendData.file_path_foreach "bpy.types.BlendData.file_path_foreach").

<a id="bpy.types.BlendDataPathMeta.is_cache"></a>

#### bpy.types.BlendDataPathMeta.is_cache

True when the path is a cache file, like the image texture cache. These paths can not be edited.

**Type:**

bool

<a id="bpy.types.BlendDataPathMeta.is_expanded"></a>

#### bpy.types.BlendDataPathMeta.is_expanded

True when the path was expanded from a UDIM tile or sequence frame. These paths can not be edited.

**Type:**

bool

<a id="bpy.types.BlendDataPathMeta.is_readonly"></a>

#### bpy.types.BlendDataPathMeta.is_readonly

True when the path is read-only and can not be edited.

**Type:**

bool
