<!-- source: Blender Python API reference 5.2 / gpu.shader.html -->

<a id="module-gpu.shader"></a>

# GPU Shader Utilities (gpu.shader)

This module provides access to GPUShader internal functions.

Built-in shaders

All built-in shaders have the `mat4 ModelViewProjectionMatrix` uniform.

Its value must be modified using the [`gpu.matrix`](gpu.matrix.md#module-gpu.matrix "gpu.matrix") module.

> **Important:**
>
> Shader uniforms must be explicitly initialized to avoid retaining values from previous executions.

`FLAT_COLOR`
:   **Attributes:**

    vec3 pos, vec4 color

    **Uniforms:**

    none

`IMAGE`
:   **Attributes:**

    vec3 pos, vec2 texCoord

    **Uniforms:**

    sampler2D image

`IMAGE_SCENE_LINEAR_TO_REC709_SRGB`
:   **Attributes:**

    vec3 pos, vec2 texCoord

    **Uniforms:**

    sampler2D image

    **Note:**

    Expect texture to be in scene linear color space

`IMAGE_COLOR`
:   **Attributes:**

    vec3 pos, vec2 texCoord

    **Uniforms:**

    sampler2D image, vec4 color

`IMAGE_COLOR_SCENE_LINEAR_TO_REC709_SRGB`
:   **Attributes:**

    vec3 pos, vec2 texCoord

    **Uniforms:**

    sampler2D image, vec4 color

    **Note:**

    Expect texture to be in scene linear color space

`SMOOTH_COLOR`
:   **Attributes:**

    vec3 pos, vec4 color

    **Uniforms:**

    none

`UNIFORM_COLOR`
:   **Attributes:**

    vec3 pos

    **Uniforms:**

    vec4 color

`POLYLINE_FLAT_COLOR`
:   **Attributes:**

    vec3 pos, vec4 color

    **Uniforms:**

    vec2 viewportSize, float lineWidth

`POLYLINE_SMOOTH_COLOR`
:   **Attributes:**

    vec3 pos, vec4 color

    **Uniforms:**

    vec2 viewportSize, float lineWidth

`POLYLINE_UNIFORM_COLOR`
:   **Attributes:**

    vec3 pos

    **Uniforms:**

    vec2 viewportSize, float lineWidth, vec4 color

`POINT_FLAT_COLOR`
:   **Attributes:**

    vec3 pos, vec4 color

    **Uniforms:**

    float size

`POINT_UNIFORM_COLOR`
:   **Attributes:**

    vec3 pos

    **Uniforms:**

    vec4 color, float size

<a id="gpu.shader.create_from_info"></a>

### gpu.shader.create_from_info(shader_info)

Create shader from a GPUShaderCreateInfo.

**Parameters:**

**shader_info** ([`gpu.types.GPUShaderCreateInfo`](gpu.types.md#gpu.types.GPUShaderCreateInfo "gpu.types.GPUShaderCreateInfo")) – GPUShaderCreateInfo

**Returns:**

Shader object corresponding to the given shader info.

**Return type:**

[`gpu.types.GPUShader`](gpu.types.md#gpu.types.GPUShader "gpu.types.GPUShader")

<a id="gpu.shader.from_builtin"></a>

### gpu.shader.from_builtin(shader_name, *, config='DEFAULT')

Shaders that are embedded in the Blender internal code (see [Built-in shaders](#built-in-shaders)).
They all read the uniform `mat4 ModelViewProjectionMatrix`,
which can be edited by the [`gpu.matrix`](gpu.matrix.md#module-gpu.matrix "gpu.matrix") module.

You can also choose a shader configuration that uses clip_planes by setting the `CLIPPED` value to the config parameter. Note that in this case you also need to manually set the value of `mat4 ModelMatrix`.

**Parameters:**

- **shader_name** (str) – One of the builtin shader names.
- **config** (str) –

  One of these types of shader configuration:

  - `DEFAULT`
  - `CLIPPED`

**Returns:**

Shader object corresponding to the given name.

**Return type:**

[`gpu.types.GPUShader`](gpu.types.md#gpu.types.GPUShader "gpu.types.GPUShader")

<a id="gpu.shader.unbind"></a>

### gpu.shader.unbind()

Unbind the bound shader object.
