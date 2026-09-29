<!-- source: Blender Python API reference 5.2 / gpu.compute.html -->

<a id="module-gpu.compute"></a>

# GPU Compute Utilities (gpu.compute)

This module provides access to the global GPU compute functions.

<a id="gpu.compute.dispatch"></a>

### gpu.compute.dispatch(shader, groups_x_len, groups_y_len, groups_z_len)

Dispatches GPU compute.

**Parameters:**

- **shader** ([`gpu.types.GPUShader`](gpu.types.md#gpu.types.GPUShader "gpu.types.GPUShader")) – The shader that you want to dispatch.
- **groups_x_len** (int) – Int for group x length:
- **groups_y_len** (int) – Int for group y length:
- **groups_z_len** (int) – Int for group z length:
