<!-- source: Blender Python API reference 5.2 / gpu.platform.html -->

<a id="module-gpu.platform"></a>

# GPU Platform Utilities (gpu.platform)

This module provides access to GPU Platform definitions.

<a id="gpu.platform.backend_type_get"></a>

### gpu.platform.backend_type_get()

Get active GPU backend.

**Returns:**

Backend type (‘OPENGL’, ‘VULKAN’, ‘METAL’, ‘NONE’, ‘UNKNOWN’).

**Return type:**

str

<a id="gpu.platform.device_type_get"></a>

### gpu.platform.device_type_get()

Get GPU device type.

**Returns:**

Device type (‘APPLE’, ‘NVIDIA’, ‘AMD’, ‘INTEL’, ‘SOFTWARE’, ‘QUALCOMM’, ‘UNKNOWN’).

**Return type:**

str

<a id="gpu.platform.devices_get"></a>

### gpu.platform.devices_get()

Get all available GPU devices.

**Returns:**

List of `GPUDevice` objects for each device.

**Return type:**

list

<a id="gpu.platform.renderer_get"></a>

### gpu.platform.renderer_get()

Get GPU to be used for rendering.

**Returns:**

GPU name.

**Return type:**

str

<a id="gpu.platform.vendor_get"></a>

### gpu.platform.vendor_get()

Get GPU vendor.

**Returns:**

Vendor name.

**Return type:**

str

<a id="gpu.platform.version_get"></a>

### gpu.platform.version_get()

Get GPU driver version.

**Returns:**

Driver version.

**Return type:**

str
