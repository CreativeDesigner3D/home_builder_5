<!-- source: Blender Python API reference 5.2 / gpu.capabilities.html -->

<a id="module-gpu.capabilities"></a>

# GPU Capabilities Utilities (gpu.capabilities)

This module provides access to the GPU capabilities.

<a id="gpu.capabilities.compute_shader_support_get"></a>

### gpu.capabilities.compute_shader_support_get()

Are compute shaders supported.

**Returns:**

True when supported, False when not supported.

**Return type:**

bool

<a id="gpu.capabilities.extensions_get"></a>

### gpu.capabilities.extensions_get()

Get supported extensions in the current context.

**Returns:**

Extensions.

**Return type:**

tuple[str, …]

<a id="gpu.capabilities.hdr_support_get"></a>

### gpu.capabilities.hdr_support_get()

Return whether GPU backend supports High Dynamic range for viewport.

**Returns:**

HDR support available.

**Return type:**

bool

<a id="gpu.capabilities.max_batch_indices_get"></a>

### gpu.capabilities.max_batch_indices_get()

Get maximum number of vertex array indices.

**Returns:**

Number of indices.

**Return type:**

int

<a id="gpu.capabilities.max_batch_vertices_get"></a>

### gpu.capabilities.max_batch_vertices_get()

Get maximum number of vertex array vertices.

**Returns:**

Number of vertices.

**Return type:**

int

<a id="gpu.capabilities.max_images_get"></a>

### gpu.capabilities.max_images_get()

Get maximum supported number of image units.

**Returns:**

Number of image units.

**Return type:**

int

<a id="gpu.capabilities.max_texture_layers_get"></a>

### gpu.capabilities.max_texture_layers_get()

Get maximum number of layers in texture.

**Returns:**

Number of layers.

**Return type:**

int

<a id="gpu.capabilities.max_texture_size_get"></a>

### gpu.capabilities.max_texture_size_get()

Get estimated maximum texture size to be able to handle.

**Returns:**

Texture size.

**Return type:**

int

<a id="gpu.capabilities.max_textures_frag_get"></a>

### gpu.capabilities.max_textures_frag_get()

Get maximum supported texture image units used for
accessing texture maps from the fragment shader.

**Returns:**

Texture image units.

**Return type:**

int

<a id="gpu.capabilities.max_textures_geom_get"></a>

### gpu.capabilities.max_textures_geom_get()

Get maximum supported texture image units used for
accessing texture maps from the geometry shader.

**Returns:**

Texture image units.

**Return type:**

int

<a id="gpu.capabilities.max_textures_get"></a>

### gpu.capabilities.max_textures_get()

Get maximum supported texture image units used for
accessing texture maps from the vertex shader and the
fragment processor.

**Returns:**

Texture image units.

**Return type:**

int

<a id="gpu.capabilities.max_textures_vert_get"></a>

### gpu.capabilities.max_textures_vert_get()

Get maximum supported texture image units used for
accessing texture maps from the vertex shader.

**Returns:**

Texture image units.

**Return type:**

int

<a id="gpu.capabilities.max_uniforms_frag_get"></a>

### gpu.capabilities.max_uniforms_frag_get()

Get maximum number of values held in uniform variable
storage for a fragment shader.

**Returns:**

Number of values.

**Return type:**

int

<a id="gpu.capabilities.max_uniforms_vert_get"></a>

### gpu.capabilities.max_uniforms_vert_get()

Get maximum number of values held in uniform variable
storage for a vertex shader.

**Returns:**

Number of values.

**Return type:**

int

<a id="gpu.capabilities.max_varying_floats_get"></a>

### gpu.capabilities.max_varying_floats_get()

Get maximum number of varying variables used by
vertex and fragment shaders.

**Returns:**

Number of variables.

**Return type:**

int

<a id="gpu.capabilities.max_vertex_attribs_get"></a>

### gpu.capabilities.max_vertex_attribs_get()

Get maximum number of vertex attributes accessible to
a vertex shader.

**Returns:**

Number of attributes.

**Return type:**

int

<a id="gpu.capabilities.max_work_group_count_get"></a>

### gpu.capabilities.max_work_group_count_get(index)

Get maximum number of work groups that may be dispatched to a compute shader.

**Parameters:**

**index** (int) – Index of the dimension.

**Returns:**

Maximum number of work groups for the queried dimension.

**Return type:**

int

<a id="gpu.capabilities.max_work_group_size_get"></a>

### gpu.capabilities.max_work_group_size_get(index)

Get maximum size of a work group that may be dispatched to a compute shader.

**Parameters:**

**index** (int) – Index of the dimension.

**Returns:**

Maximum size of a work group for the queried dimension.

**Return type:**

int

<a id="gpu.capabilities.shader_image_load_store_support_get"></a>

### gpu.capabilities.shader_image_load_store_support_get()

Is image load/store supported.

**Returns:**

True when supported, False when not supported.

**Return type:**

bool
