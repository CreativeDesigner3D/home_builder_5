<!-- source: Blender Python API reference 5.2 / mathutils.noise.html -->

<a id="module-mathutils.noise"></a>

# Noise Utilities (mathutils.noise)

The Blender noise module.

<a id="mathutils.noise.cell"></a>

### mathutils.noise.cell(position, /)

Returns cell noise value at the specified position.

**Parameters:**

**position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the cell noise at.

**Returns:**

The cell noise value.

**Return type:**

float

<a id="mathutils.noise.cell_vector"></a>

### mathutils.noise.cell_vector(position, /)

Returns cell noise vector at the specified position.

**Parameters:**

**position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the cell noise at.

**Returns:**

The cell noise vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="mathutils.noise.fractal"></a>

### mathutils.noise.fractal(position, H, lacunarity, octaves, /, *, noise_basis='PERLIN_ORIGINAL')

Returns the fractal Brownian motion (fBm) noise value from the noise basis at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **H** (float) – The fractal increment parameter.
- **lacunarity** (float) – The gap between successive frequencies.
- **octaves** (float) – The number of different noise frequencies used.
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.

**Returns:**

The fractal Brownian motion noise value.

**Return type:**

float

<a id="mathutils.noise.hetero_terrain"></a>

### mathutils.noise.hetero_terrain(position, H, lacunarity, octaves, offset, /, *, noise_basis='PERLIN_ORIGINAL')

Returns the heterogeneous terrain value from the noise basis at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **H** (float) – The fractal dimension of the roughest areas.
- **lacunarity** (float) – The gap between successive frequencies.
- **octaves** (float) – The number of different noise frequencies used.
- **offset** (float) – The height of the terrain above ‘sea level’.
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.

**Returns:**

The heterogeneous terrain value.

**Return type:**

float

<a id="mathutils.noise.hybrid_multi_fractal"></a>

### mathutils.noise.hybrid_multi_fractal(position, H, lacunarity, octaves, offset, gain, /, *, noise_basis='PERLIN_ORIGINAL')

Returns hybrid multifractal value from the noise basis at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **H** (float) – The fractal dimension of the roughest areas.
- **lacunarity** (float) – The gap between successive frequencies.
- **octaves** (float) – The number of different noise frequencies used.
- **offset** (float) – The height of the terrain above ‘sea level’.
- **gain** (float) – Scaling applied to the values.
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.

**Returns:**

The hybrid multifractal value.

**Return type:**

float

<a id="mathutils.noise.multi_fractal"></a>

### mathutils.noise.multi_fractal(position, H, lacunarity, octaves, /, *, noise_basis='PERLIN_ORIGINAL')

Returns multifractal noise value from the noise basis at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **H** (float) – Determines the highest fractal dimension.
- **lacunarity** (float) – The gap between successive frequencies.
- **octaves** (float) – The number of different noise frequencies used.
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.

**Returns:**

The multifractal noise value.

**Return type:**

float

<a id="mathutils.noise.noise"></a>

### mathutils.noise.noise(position, /, *, noise_basis='PERLIN_ORIGINAL')

Returns noise value from the noise basis at the position specified.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.

**Returns:**

The noise value.

**Return type:**

float

<a id="mathutils.noise.noise_vector"></a>

### mathutils.noise.noise_vector(position, /, *, noise_basis='PERLIN_ORIGINAL')

Returns the noise vector from the noise basis at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.

**Returns:**

The noise vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="mathutils.noise.random"></a>

### mathutils.noise.random()

Returns a random number in the range [0, 1).

**Returns:**

The random number.

**Return type:**

float

<a id="mathutils.noise.random_unit_vector"></a>

### mathutils.noise.random_unit_vector(*, size=3)

Returns a unit vector with random entries.

**Parameters:**

**size** (int) – The size of the vector to be produced, in the range [2, 4].

**Returns:**

The random unit vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="mathutils.noise.random_vector"></a>

### mathutils.noise.random_vector(*, size=3)

Returns a vector with random entries in the range (-1, 1).

**Parameters:**

**size** (int) – The size of the vector to be produced, must be 2 or greater.

**Returns:**

The random vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="mathutils.noise.ridged_multi_fractal"></a>

### mathutils.noise.ridged_multi_fractal(position, H, lacunarity, octaves, offset, gain, /, *, noise_basis='PERLIN_ORIGINAL')

Returns ridged multifractal value from the noise basis at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **H** (float) – The fractal dimension of the roughest areas.
- **lacunarity** (float) – The gap between successive frequencies.
- **octaves** (float) – The number of different noise frequencies used.
- **offset** (float) – The height of the terrain above ‘sea level’.
- **gain** (float) – Scaling applied to the values.
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.

**Returns:**

The ridged multifractal value.

**Return type:**

float

<a id="mathutils.noise.seed_set"></a>

### mathutils.noise.seed_set(seed, /)

Sets the random seed used for random_unit_vector, random_vector, and random.

**Parameters:**

**seed** (int) – Seed used for the random generator.
When seed is zero, the current time will be used instead.

<a id="mathutils.noise.turbulence"></a>

### mathutils.noise.turbulence(position, octaves, hard, /, *, noise_basis='PERLIN_ORIGINAL', amplitude_scale=0.5, frequency_scale=2.0)

Returns the turbulence value from the noise basis at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **octaves** (int) – The number of different noise frequencies used.
- **hard** (bool) – Specifies whether returned turbulence is hard (sharp transitions) or soft (smooth transitions).
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.
- **amplitude_scale** (float) – The amplitude scaling factor.
- **frequency_scale** (float) – The frequency scaling factor.

**Returns:**

The turbulence value.

**Return type:**

float

<a id="mathutils.noise.turbulence_vector"></a>

### mathutils.noise.turbulence_vector(position, octaves, hard, /, *, noise_basis='PERLIN_ORIGINAL', amplitude_scale=0.5, frequency_scale=2.0)

Returns the turbulence vector from the noise basis at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **octaves** (int) – The number of different noise frequencies used.
- **hard** (bool) – Specifies whether returned turbulence is hard (sharp transitions) or soft (smooth transitions).
- **noise_basis** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise basis string.
- **amplitude_scale** (float) – The amplitude scaling factor.
- **frequency_scale** (float) – The frequency scaling factor.

**Returns:**

The turbulence vector.

**Return type:**

[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")

<a id="mathutils.noise.variable_lacunarity"></a>

### mathutils.noise.variable_lacunarity(position, distortion, /, *, noise_type1='PERLIN_ORIGINAL', noise_type2='PERLIN_ORIGINAL')

Returns variable lacunarity noise value, a distorted variety of noise, from noise type 1 distorted by noise type 2 at the specified position.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **distortion** (float) – The amount of distortion.
- **noise_type1** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise type string.
- **noise_type2** (Literal['BLENDER', 'PERLIN_ORIGINAL', 'PERLIN_NEW', 'VORONOI_F1', 'VORONOI_F2', 'VORONOI_F3', 'VORONOI_F4', 'VORONOI_F2F1', 'VORONOI_CRACKLE', 'CELLNOISE']) – A noise type string.

**Returns:**

The variable lacunarity noise value.

**Return type:**

float

<a id="mathutils.noise.voronoi"></a>

### mathutils.noise.voronoi(position, /, *, distance_metric='DISTANCE', exponent=2.5)

Returns a list of distances to the four closest features and their locations.

**Parameters:**

- **position** ([`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")) – The position to evaluate the selected noise function.
- **distance_metric** (Literal['DISTANCE', 'DISTANCE_SQUARED', 'MANHATTAN', 'CHEBYCHEV', 'MINKOVSKY', 'MINKOVSKY_HALF', 'MINKOVSKY_FOUR']) – A distance metric string.
- **exponent** (float) – The exponent for Minkowski distance metric.

**Returns:**

A list of distances to the four closest features and their locations.

**Return type:**

list[list[float] | list[[`mathutils.Vector`](mathutils.md#mathutils.Vector "mathutils.Vector")]]
