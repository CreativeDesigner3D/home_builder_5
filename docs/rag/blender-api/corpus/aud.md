<!-- source: Blender Python API reference 5.2 / aud.html -->

<a id="module-aud"></a>

# Audio System (aud)

Audaspace (pronounced “outer space”) is a high level audio library.

<a id="basic-sound-playback"></a>

## Basic Sound Playback

This script shows how to use the classes: [`Device`](#aud.Device "aud.Device"), [`Sound`](#aud.Sound "aud.Sound") and
[`Handle`](#aud.Handle "aud.Handle").

```python
import aud

device = aud.Device()
# Load sound file (it can be a video file with audio).
sound = aud.Sound('music.ogg')

# Play the audio, this return a handle to control play/pause.
handle = device.play(sound)
# If the audio is not too big and will be used often you can buffer it.
sound_buffered = aud.Sound.cache(sound)
handle_buffered = device.play(sound_buffered)

# Stop the sounds (otherwise they play until their ends).
handle.stop()
handle_buffered.stop()
```

<a id="aud.AP_LOCATION"></a>

### aud.AP_LOCATION

Constant value 3

**Type:**

int

<a id="aud.AP_ORIENTATION"></a>

### aud.AP_ORIENTATION

Constant value 4

**Type:**

int

<a id="aud.AP_PANNING"></a>

### aud.AP_PANNING

Constant value 1

**Type:**

int

<a id="aud.AP_PITCH"></a>

### aud.AP_PITCH

Constant value 2

**Type:**

int

<a id="aud.AP_PITCH_SCALE"></a>

### aud.AP_PITCH_SCALE

Constant value 6

**Type:**

int

<a id="aud.AP_TIME_STRETCH"></a>

### aud.AP_TIME_STRETCH

Constant value 5

**Type:**

int

<a id="aud.AP_VOLUME"></a>

### aud.AP_VOLUME

Constant value 0

**Type:**

int

<a id="aud.CHANNELS_INVALID"></a>

### aud.CHANNELS_INVALID

Constant value 0

**Type:**

int

<a id="aud.CHANNELS_MONO"></a>

### aud.CHANNELS_MONO

Constant value 1

**Type:**

int

<a id="aud.CHANNELS_STEREO"></a>

### aud.CHANNELS_STEREO

Constant value 2

**Type:**

int

<a id="aud.CHANNELS_STEREO_LFE"></a>

### aud.CHANNELS_STEREO_LFE

Constant value 3

**Type:**

int

<a id="aud.CHANNELS_SURROUND4"></a>

### aud.CHANNELS_SURROUND4

Constant value 4

**Type:**

int

<a id="aud.CHANNELS_SURROUND5"></a>

### aud.CHANNELS_SURROUND5

Constant value 5

**Type:**

int

<a id="aud.CHANNELS_SURROUND51"></a>

### aud.CHANNELS_SURROUND51

Constant value 6

**Type:**

int

<a id="aud.CHANNELS_SURROUND61"></a>

### aud.CHANNELS_SURROUND61

Constant value 7

**Type:**

int

<a id="aud.CHANNELS_SURROUND71"></a>

### aud.CHANNELS_SURROUND71

Constant value 8

**Type:**

int

<a id="aud.CODEC_AAC"></a>

### aud.CODEC_AAC

Constant value 1

**Type:**

int

<a id="aud.CODEC_AC3"></a>

### aud.CODEC_AC3

Constant value 2

**Type:**

int

<a id="aud.CODEC_FLAC"></a>

### aud.CODEC_FLAC

Constant value 3

**Type:**

int

<a id="aud.CODEC_INVALID"></a>

### aud.CODEC_INVALID

Constant value 0

**Type:**

int

<a id="aud.CODEC_MP2"></a>

### aud.CODEC_MP2

Constant value 4

**Type:**

int

<a id="aud.CODEC_MP3"></a>

### aud.CODEC_MP3

Constant value 5

**Type:**

int

<a id="aud.CODEC_OPUS"></a>

### aud.CODEC_OPUS

Constant value 8

**Type:**

int

<a id="aud.CODEC_PCM"></a>

### aud.CODEC_PCM

Constant value 6

**Type:**

int

<a id="aud.CODEC_VORBIS"></a>

### aud.CODEC_VORBIS

Constant value 7

**Type:**

int

<a id="aud.CONTAINER_AAC"></a>

### aud.CONTAINER_AAC

Constant value 8

**Type:**

int

<a id="aud.CONTAINER_AC3"></a>

### aud.CONTAINER_AC3

Constant value 1

**Type:**

int

<a id="aud.CONTAINER_FLAC"></a>

### aud.CONTAINER_FLAC

Constant value 2

**Type:**

int

<a id="aud.CONTAINER_INVALID"></a>

### aud.CONTAINER_INVALID

Constant value 0

**Type:**

int

<a id="aud.CONTAINER_MATROSKA"></a>

### aud.CONTAINER_MATROSKA

Constant value 3

**Type:**

int

<a id="aud.CONTAINER_MP2"></a>

### aud.CONTAINER_MP2

Constant value 4

**Type:**

int

<a id="aud.CONTAINER_MP3"></a>

### aud.CONTAINER_MP3

Constant value 5

**Type:**

int

<a id="aud.CONTAINER_OGG"></a>

### aud.CONTAINER_OGG

Constant value 6

**Type:**

int

<a id="aud.CONTAINER_WAV"></a>

### aud.CONTAINER_WAV

Constant value 7

**Type:**

int

<a id="aud.DISTANCE_MODEL_EXPONENT"></a>

### aud.DISTANCE_MODEL_EXPONENT

Constant value 5

**Type:**

int

<a id="aud.DISTANCE_MODEL_EXPONENT_CLAMPED"></a>

### aud.DISTANCE_MODEL_EXPONENT_CLAMPED

Constant value 6

**Type:**

int

<a id="aud.DISTANCE_MODEL_INVALID"></a>

### aud.DISTANCE_MODEL_INVALID

Constant value 0

**Type:**

int

<a id="aud.DISTANCE_MODEL_INVERSE"></a>

### aud.DISTANCE_MODEL_INVERSE

Constant value 1

**Type:**

int

<a id="aud.DISTANCE_MODEL_INVERSE_CLAMPED"></a>

### aud.DISTANCE_MODEL_INVERSE_CLAMPED

Constant value 2

**Type:**

int

<a id="aud.DISTANCE_MODEL_LINEAR"></a>

### aud.DISTANCE_MODEL_LINEAR

Constant value 3

**Type:**

int

<a id="aud.DISTANCE_MODEL_LINEAR_CLAMPED"></a>

### aud.DISTANCE_MODEL_LINEAR_CLAMPED

Constant value 4

**Type:**

int

<a id="aud.FORMAT_FLOAT32"></a>

### aud.FORMAT_FLOAT32

Constant value 36

**Type:**

int

<a id="aud.FORMAT_FLOAT64"></a>

### aud.FORMAT_FLOAT64

Constant value 40

**Type:**

int

<a id="aud.FORMAT_INVALID"></a>

### aud.FORMAT_INVALID

Constant value 0

**Type:**

int

<a id="aud.FORMAT_S16"></a>

### aud.FORMAT_S16

Constant value 18

**Type:**

int

<a id="aud.FORMAT_S24"></a>

### aud.FORMAT_S24

Constant value 19

**Type:**

int

<a id="aud.FORMAT_S32"></a>

### aud.FORMAT_S32

Constant value 20

**Type:**

int

<a id="aud.FORMAT_U8"></a>

### aud.FORMAT_U8

Constant value 1

**Type:**

int

<a id="aud.RATE_11025"></a>

### aud.RATE_11025

Constant value 11025

**Type:**

int

<a id="aud.RATE_16000"></a>

### aud.RATE_16000

Constant value 16000

**Type:**

int

<a id="aud.RATE_192000"></a>

### aud.RATE_192000

Constant value 192000

**Type:**

int

<a id="aud.RATE_22050"></a>

### aud.RATE_22050

Constant value 22050

**Type:**

int

<a id="aud.RATE_32000"></a>

### aud.RATE_32000

Constant value 32000

**Type:**

int

<a id="aud.RATE_44100"></a>

### aud.RATE_44100

Constant value 44100

**Type:**

int

<a id="aud.RATE_48000"></a>

### aud.RATE_48000

Constant value 48000

**Type:**

int

<a id="aud.RATE_8000"></a>

### aud.RATE_8000

Constant value 8000

**Type:**

int

<a id="aud.RATE_88200"></a>

### aud.RATE_88200

Constant value 88200

**Type:**

int

<a id="aud.RATE_96000"></a>

### aud.RATE_96000

Constant value 96000

**Type:**

int

<a id="aud.RATE_INVALID"></a>

### aud.RATE_INVALID

Constant value 0

**Type:**

int

<a id="aud.STATUS_INVALID"></a>

### aud.STATUS_INVALID

Constant value 0

**Type:**

int

<a id="aud.STATUS_PAUSED"></a>

### aud.STATUS_PAUSED

Constant value 2

**Type:**

int

<a id="aud.STATUS_PLAYING"></a>

### aud.STATUS_PLAYING

Constant value 1

**Type:**

int

<a id="aud.STATUS_STOPPED"></a>

### aud.STATUS_STOPPED

Constant value 3

**Type:**

int

<a id="aud.STRETCHER_QUALITY_CONSISTENT"></a>

### aud.STRETCHER_QUALITY_CONSISTENT

Constant value 2

**Type:**

int

<a id="aud.STRETCHER_QUALITY_FAST"></a>

### aud.STRETCHER_QUALITY_FAST

Constant value 1

**Type:**

int

<a id="aud.STRETCHER_QUALITY_HIGH"></a>

### aud.STRETCHER_QUALITY_HIGH

Constant value 0

**Type:**

int

<a id="aud.AnimateableProperty"></a>

### class aud.AnimateableProperty(count, value=0.0, /)

An AnimateableProperty object stores an array of float values for animating sound properties (e.g. pan, volume, pitch-scale).

**Parameters:**

- **count** (int) – The number of float values to store per frame.
- **value** (float) – The initial value for all elements.

<a id="aud.AnimateableProperty.read"></a>

#### aud.AnimateableProperty.read(position)

Reads the properties value at the given position.

**Parameters:**

**position** (float) – The position in the animation in frames.

**Returns:**

A numpy array of values representing the properties value.

**Return type:**

`numpy.ndarray`

<a id="aud.AnimateableProperty.readSingle"></a>

#### aud.AnimateableProperty.readSingle(position)

Reads the properties value at the given position, assuming there is exactly one value.

**Parameters:**

**position** (float) – The position in the animation in frames.

**Returns:**

The value at that position.

**Return type:**

float

<a id="aud.AnimateableProperty.write"></a>

#### aud.AnimateableProperty.write(data[, position])

Writes the properties value.

If position is also given, the property is marked animated and
the values are written starting at position.

**Parameters:**

- **data** (numpy.ndarray) – numpy array of float32 values.
- **position** (int) – The starting position in frames.

<a id="aud.AnimateableProperty.writeConstantRange"></a>

#### aud.AnimateableProperty.writeConstantRange(data, position_start, position_end)

Fills the properties frame range with a constant value and marks it animated.

**Parameters:**

- **data** (numpy.ndarray) – numpy array of float values representing the constant value.
- **position_start** (int) – The start position in frames.
- **position_end** (int) – The end position in frames.

<a id="aud.AnimateableProperty.animated"></a>

#### aud.AnimateableProperty.animated

Whether the property is animated.

<a id="aud.AnimateableProperty.count"></a>

#### aud.AnimateableProperty.count

The count of floats for a property.

<a id="aud.Device"></a>

### class aud.Device(type='', rate=48000.0, channels=2, format=36, buffer_size=1024, name='')

Device objects represent an audio output backend like OpenAL or SDL, but might also represent a file output or RAM buffer output.

**Parameters:**

- **type** (string) – The device type. An empty string means the default device.
- **rate** (double) – The sample rate in Hz.
- **channels** (int) – The number of channels.
- **format** (int) – The sample format.
- **buffer_size** (int) – The size of the audio buffer in samples.
- **name** (string) – The name of the device.

<a id="aud.Device.lock"></a>

#### aud.Device.lock()

Locks the device so that it’s guaranteed, that no samples are
read from the streams until [`unlock()`](#aud.Device.unlock "aud.Device.unlock") is called.
This is useful if you want to do start/stop/pause/resume some
sounds at the same time.

> **Note:**
>
> The device has to be unlocked as often as locked to be
> able to continue playback.

> **Warning:**
>
> Make sure the time between locking and unlocking is
> as short as possible to avoid clicks.

<a id="aud.Device.play"></a>

#### aud.Device.play(sound, keep=False)

Plays a sound.

**Parameters:**

- **sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound to play.
- **keep** (bool) – See [`Handle.keep`](#aud.Handle.keep "aud.Handle.keep").

**Returns:**

The playback handle with which playback can be
controlled with.

**Return type:**

[`Handle`](#aud.Handle "aud.Handle")

<a id="aud.Device.stopAll"></a>

#### aud.Device.stopAll()

Stops all playing and paused sounds.

<a id="aud.Device.unlock"></a>

#### aud.Device.unlock()

Unlocks the device after a lock call, see [`lock()`](#aud.Device.lock "aud.Device.lock") for
details.

<a id="aud.Device.channels"></a>

#### aud.Device.channels

The channel count of the device.

<a id="aud.Device.distance_model"></a>

#### aud.Device.distance_model

The distance model of the device.

> **See also:**
>
> [OpenAL Documentation](https://www.openal.org/documentation/)

<a id="aud.Device.doppler_factor"></a>

#### aud.Device.doppler_factor

The doppler factor of the device.
This factor is a scaling factor for the velocity vectors in doppler calculation. So a value bigger than 1 will exaggerate the effect as it raises the velocity.

<a id="aud.Device.format"></a>

#### aud.Device.format

The native sample format of the device.

<a id="aud.Device.listener_location"></a>

#### aud.Device.listener_location

The listeners’s location in 3D space, a 3D tuple of floats.

<a id="aud.Device.listener_orientation"></a>

#### aud.Device.listener_orientation

The listener’s orientation in 3D space as quaternion, a 4 float tuple.

<a id="aud.Device.listener_velocity"></a>

#### aud.Device.listener_velocity

The listener’s velocity in 3D space, a 3D tuple of floats.

<a id="aud.Device.rate"></a>

#### aud.Device.rate

The sampling rate of the device in Hz.

<a id="aud.Device.speed_of_sound"></a>

#### aud.Device.speed_of_sound

The speed of sound of the device.
The speed of sound in air is typically 343.3 m/s.

<a id="aud.Device.volume"></a>

#### aud.Device.volume

The overall volume of the device.

<a id="aud.DynamicMusic"></a>

### class aud.DynamicMusic(device, /)

The DynamicMusic object allows to play music depending on a current scene, scene changes are managed by the class, with the possibility of custom transitions.
The default transition is a crossfade effect, and the default scene is silent and has id 0.

**Parameters:**

**device** ([`Device`](#aud.Device "aud.Device")) – The device that will be used to play sounds.

<a id="aud.DynamicMusic.addScene"></a>

#### aud.DynamicMusic.addScene(scene)

Adds a new scene.

**Parameters:**

**scene** ([`Sound`](#aud.Sound "aud.Sound")) – The scene sound.

**Returns:**

The new scene id.

**Return type:**

int

<a id="aud.DynamicMusic.addTransition"></a>

#### aud.DynamicMusic.addTransition(ini, end, transition)

Adds a new scene.

**Parameters:**

- **ini** (int) – the initial scene foor the transition.
- **end** (int) – The final scene for the transition.
- **transition** ([`Sound`](#aud.Sound "aud.Sound")) – The transition sound.

**Returns:**

false if the ini or end scenes don’t exist, true otherwise.

**Return type:**

bool

<a id="aud.DynamicMusic.pause"></a>

#### aud.DynamicMusic.pause()

Pauses playback of the scene.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.DynamicMusic.resume"></a>

#### aud.DynamicMusic.resume()

Resumes playback of the scene.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.DynamicMusic.stop"></a>

#### aud.DynamicMusic.stop()

Stops playback of the scene.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.DynamicMusic.fadeTime"></a>

#### aud.DynamicMusic.fadeTime

The length in seconds of the crossfade transition

<a id="aud.DynamicMusic.position"></a>

#### aud.DynamicMusic.position

The playback position of the scene in seconds.

<a id="aud.DynamicMusic.scene"></a>

#### aud.DynamicMusic.scene

The current scene

<a id="aud.DynamicMusic.status"></a>

#### aud.DynamicMusic.status

Whether the scene is playing, paused or stopped (=invalid).

<a id="aud.DynamicMusic.volume"></a>

#### aud.DynamicMusic.volume

The volume of the scene.

<a id="aud.HRTF"></a>

### class aud.HRTF

An HRTF object represents a set of head related transfer functions as impulse responses. It’s used for binaural sound.

<a id="aud.HRTF.loadLeftHrtfSet"></a>

#### aud.HRTF.loadLeftHrtfSet(extension, directory)

Loads all HRTFs from a directory.

**Parameters:**

- **extension** (string) – The file extension of the hrtfs.
- **directory** – The path to where the HRTF files are located.

**Returns:**

The loaded [`HRTF`](#aud.HRTF "aud.HRTF") object.

**Return type:**

[`HRTF`](#aud.HRTF "aud.HRTF")

<a id="aud.HRTF.loadRightHrtfSet"></a>

#### aud.HRTF.loadRightHrtfSet(extension, directory)

Loads all HRTFs from a directory.

**Parameters:**

- **extension** (string) – The file extension of the hrtfs.
- **directory** – The path to where the HRTF files are located.

**Returns:**

The loaded [`HRTF`](#aud.HRTF "aud.HRTF") object.

**Return type:**

[`HRTF`](#aud.HRTF "aud.HRTF")

<a id="aud.HRTF.addImpulseResponseFromSound"></a>

#### aud.HRTF.addImpulseResponseFromSound(sound, azimuth, elevation)

Adds a new hrtf to the HRTF object

**Parameters:**

- **sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound that contains the hrtf.
- **azimuth** (float) – The azimuth angle of the hrtf.
- **elevation** (float) – The elevation angle of the hrtf.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.Handle"></a>

### class aud.Handle

Handle objects are playback handles that can be used to control playback of a sound. If a sound is played back multiple times then there are as many handles.

<a id="aud.Handle.pause"></a>

#### aud.Handle.pause()

Pauses playback.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.Handle.resume"></a>

#### aud.Handle.resume()

Resumes playback.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.Handle.stop"></a>

#### aud.Handle.stop()

Stops playback.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

> **Note:**
>
> This makes the handle invalid.

<a id="aud.Handle.attenuation"></a>

#### aud.Handle.attenuation

This factor is used for distance based attenuation of the source.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.Handle.cone_angle_inner"></a>

#### aud.Handle.cone_angle_inner

The opening angle of the inner cone of the source. If the cone values of a source are set there are two (audible) cones with the apex at the [`location`](#aud.Handle.location "aud.Handle.location") of the source and with infinite height, heading in the direction of the source’s [`orientation`](#aud.Handle.orientation "aud.Handle.orientation").
In the inner cone the volume is normal. Outside the outer cone the volume will be [`cone_volume_outer`](#aud.Handle.cone_volume_outer "aud.Handle.cone_volume_outer") and in the area between the volume will be interpolated linearly.

<a id="aud.Handle.cone_angle_outer"></a>

#### aud.Handle.cone_angle_outer

The opening angle of the outer cone of the source.

> **See also:**
>
> [`cone_angle_inner`](#aud.Handle.cone_angle_inner "aud.Handle.cone_angle_inner")

<a id="aud.Handle.cone_volume_outer"></a>

#### aud.Handle.cone_volume_outer

The volume outside the outer cone of the source.

> **See also:**
>
> [`cone_angle_inner`](#aud.Handle.cone_angle_inner "aud.Handle.cone_angle_inner")

<a id="aud.Handle.distance_maximum"></a>

#### aud.Handle.distance_maximum

The maximum distance of the source.
If the listener is further away the source volume will be 0.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.Handle.distance_reference"></a>

#### aud.Handle.distance_reference

The reference distance of the source.
At this distance the volume will be exactly [`volume`](#aud.Handle.volume "aud.Handle.volume").

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.Handle.keep"></a>

#### aud.Handle.keep

Whether the sound should be kept paused in the device when its end is reached.
This can be used to seek the sound to some position and start playback again.

> **Warning:**
>
> If this is set to true and you forget stopping this equals a memory leak as the handle exists until the device is destroyed.

<a id="aud.Handle.location"></a>

#### aud.Handle.location

The source’s location in 3D space, a 3D tuple of floats.

<a id="aud.Handle.loop_count"></a>

#### aud.Handle.loop_count

The (remaining) loop count of the sound. A negative value indicates infinity.

<a id="aud.Handle.orientation"></a>

#### aud.Handle.orientation

The source’s orientation in 3D space as quaternion, a 4 float tuple.

<a id="aud.Handle.pitch"></a>

#### aud.Handle.pitch

The pitch of the sound.

<a id="aud.Handle.position"></a>

#### aud.Handle.position

The playback position of the sound in seconds.

<a id="aud.Handle.relative"></a>

#### aud.Handle.relative

Whether the source’s location, velocity and orientation is relative or absolute to the listener.

<a id="aud.Handle.status"></a>

#### aud.Handle.status

Whether the sound is playing, paused or stopped (=invalid).

<a id="aud.Handle.velocity"></a>

#### aud.Handle.velocity

The source’s velocity in 3D space, a 3D tuple of floats.

<a id="aud.Handle.volume"></a>

#### aud.Handle.volume

The volume of the sound.

<a id="aud.Handle.volume_maximum"></a>

#### aud.Handle.volume_maximum

The maximum volume of the source.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.Handle.volume_minimum"></a>

#### aud.Handle.volume_minimum

The minimum volume of the source.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.ImpulseResponse"></a>

### class aud.ImpulseResponse(sound, /)

An ImpulseResponse object represents a filter with which to convolve a sound.

**Parameters:**

**sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound to use as the impulse response.

<a id="aud.PlaybackManager"></a>

### class aud.PlaybackManager(device, /)

A PlaybackManager object allows to easily control groups of sounds organized in categories.

**Parameters:**

**device** ([`Device`](#aud.Device "aud.Device")) – The device that will be used to play sounds.

<a id="aud.PlaybackManager.addCategory"></a>

#### aud.PlaybackManager.addCategory(volume)

Adds a category with a custom volume.

**Parameters:**

**volume** (float) – The volume for ther new category.

**Returns:**

The key of the new category.

**Return type:**

int

<a id="aud.PlaybackManager.clean"></a>

#### aud.PlaybackManager.clean()

Cleans all the invalid and finished sound from the playback manager.

<a id="aud.PlaybackManager.getVolume"></a>

#### aud.PlaybackManager.getVolume(catKey)

Retrieves the volume of a category.

**Parameters:**

**catKey** (int) – the key of the category.

**Returns:**

The volume of the category.

**Return type:**

float

<a id="aud.PlaybackManager.pause"></a>

#### aud.PlaybackManager.pause(catKey)

Pauses playback of the category.

**Parameters:**

**catKey** (int) – the key of the category.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.PlaybackManager.play"></a>

#### aud.PlaybackManager.play(sound, catKey)

Plays a sound through the playback manager and assigns it to a category.

**Parameters:**

- **sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound to play.
- **catKey** (int) – the key of the category in which the sound will be added,
  if it doesn’t exist, a new one will be created.

**Returns:**

The playback handle with which playback can be controlled with.

**Return type:**

[`Handle`](#aud.Handle "aud.Handle")

<a id="aud.PlaybackManager.resume"></a>

#### aud.PlaybackManager.resume(catKey)

Resumes playback of the catgory.

**Parameters:**

**catKey** (int) – the key of the category.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.PlaybackManager.setVolume"></a>

#### aud.PlaybackManager.setVolume(volume, catKey)

Changes the volume of a category.

**Parameters:**

- **volume** (float) – the new volume value.
- **catKey** (int) – the key of the category.

**Returns:**

Whether the action succeeded.

**Return type:**

int

<a id="aud.PlaybackManager.stop"></a>

#### aud.PlaybackManager.stop(catKey)

Stops playback of the category.

**Parameters:**

**catKey** (int) – the key of the category.

**Returns:**

Whether the action succeeded.

**Return type:**

bool

<a id="aud.Sequence"></a>

### class aud.Sequence(channels=2, rate=48000.0, fps=30.0, muted=False)

This sound represents sequenced entries to play a sound sequence.

**Parameters:**

- **channels** (int) – The number of channels.
- **rate** (double) – The sample rate in Hz.
- **fps** (float) – The frames per second of the sequence.
- **muted** (bool) – Whether the sequence is muted.

<a id="aud.Sequence.add"></a>

#### aud.Sequence.add()

Adds a new entry to the sequence.

**Parameters:**

- **sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound this entry should play.
- **begin** (double) – The start time.
- **end** (double) – The end time or a negative value if determined by the sound.
- **skip** (double) – How much seconds should be skipped at the beginning.

**Returns:**

The entry added.

**Return type:**

[`SequenceEntry`](#aud.SequenceEntry "aud.SequenceEntry")

<a id="aud.Sequence.remove"></a>

#### aud.Sequence.remove()

Removes an entry from the sequence.

**Parameters:**

**entry** ([`SequenceEntry`](#aud.SequenceEntry "aud.SequenceEntry")) – The entry to remove.

<a id="aud.Sequence.setAnimationData"></a>

#### aud.Sequence.setAnimationData()

Writes animation data to a sequence.

**Parameters:**

- **type** (int) – The type of animation data.
- **frame** (int) – The frame this data is for.
- **data** (sequence of float) – The data to write.
- **animated** (bool) – Whether the attribute is animated.

<a id="aud.Sequence.channels"></a>

#### aud.Sequence.channels

The channel count of the sequence.

<a id="aud.Sequence.distance_model"></a>

#### aud.Sequence.distance_model

The distance model of the sequence.

> **See also:**
>
> [OpenAL Documentation](https://www.openal.org/documentation/)

<a id="aud.Sequence.doppler_factor"></a>

#### aud.Sequence.doppler_factor

The doppler factor of the sequence.
This factor is a scaling factor for the velocity vectors in doppler calculation. So a value bigger than 1 will exaggerate the effect as it raises the velocity.

<a id="aud.Sequence.fps"></a>

#### aud.Sequence.fps

The listeners’s location in 3D space, a 3D tuple of floats.

<a id="aud.Sequence.muted"></a>

#### aud.Sequence.muted

Whether the whole sequence is muted.

<a id="aud.Sequence.rate"></a>

#### aud.Sequence.rate

The sampling rate of the sequence in Hz.

<a id="aud.Sequence.speed_of_sound"></a>

#### aud.Sequence.speed_of_sound

The speed of sound of the sequence.
The speed of sound in air is typically 343.3 m/s.

<a id="aud.SequenceEntry"></a>

### class aud.SequenceEntry

SequenceEntry objects represent an entry of a sequenced sound.

<a id="aud.SequenceEntry.move"></a>

#### aud.SequenceEntry.move()

Moves the entry.

**Parameters:**

- **begin** (double) – The new start time.
- **end** (double) – The new end time or a negative value if unknown.
- **skip** (double) – How many seconds to skip at the beginning.

<a id="aud.SequenceEntry.setAnimationData"></a>

#### aud.SequenceEntry.setAnimationData()

Writes animation data to a sequenced entry.

**Parameters:**

- **type** (int) – The type of animation data.
- **frame** (int) – The frame this data is for.
- **data** (sequence of float) – The data to write.
- **animated** (bool) – Whether the attribute is animated.

<a id="aud.SequenceEntry.attenuation"></a>

#### aud.SequenceEntry.attenuation

This factor is used for distance based attenuation of the source.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.SequenceEntry.cone_angle_inner"></a>

#### aud.SequenceEntry.cone_angle_inner

The opening angle of the inner cone of the source. If the cone values of a source are set there are two (audible) cones with the apex at the `location` of the source and with infinite height, heading in the direction of the source’s `orientation`.
In the inner cone the volume is normal. Outside the outer cone the volume will be [`cone_volume_outer`](#aud.SequenceEntry.cone_volume_outer "aud.SequenceEntry.cone_volume_outer") and in the area between the volume will be interpolated linearly.

<a id="aud.SequenceEntry.cone_angle_outer"></a>

#### aud.SequenceEntry.cone_angle_outer

The opening angle of the outer cone of the source.

> **See also:**
>
> [`cone_angle_inner`](#aud.SequenceEntry.cone_angle_inner "aud.SequenceEntry.cone_angle_inner")

<a id="aud.SequenceEntry.cone_volume_outer"></a>

#### aud.SequenceEntry.cone_volume_outer

The volume outside the outer cone of the source.

> **See also:**
>
> [`cone_angle_inner`](#aud.SequenceEntry.cone_angle_inner "aud.SequenceEntry.cone_angle_inner")

<a id="aud.SequenceEntry.distance_maximum"></a>

#### aud.SequenceEntry.distance_maximum

The maximum distance of the source.
If the listener is further away the source volume will be 0.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.SequenceEntry.distance_reference"></a>

#### aud.SequenceEntry.distance_reference

The reference distance of the source.
At this distance the volume will be exactly `volume`.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.SequenceEntry.muted"></a>

#### aud.SequenceEntry.muted

Whether the entry is muted.

<a id="aud.SequenceEntry.relative"></a>

#### aud.SequenceEntry.relative

Whether the source’s location, velocity and orientation is relative or absolute to the listener.

<a id="aud.SequenceEntry.sound"></a>

#### aud.SequenceEntry.sound

The sound the entry is representing and will be played in the sequence.

<a id="aud.SequenceEntry.volume_maximum"></a>

#### aud.SequenceEntry.volume_maximum

The maximum volume of the source.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.SequenceEntry.volume_minimum"></a>

#### aud.SequenceEntry.volume_minimum

The minimum volume of the source.

> **See also:**
>
> [`Device.distance_model`](#aud.Device.distance_model "aud.Device.distance_model")

<a id="aud.Sound"></a>

### class aud.Sound(filename, stream=0)

Sound objects are immutable and represent a sound that can be played simultaneously multiple times. They are called factories because they create reader objects internally that are used for playback.

**Parameters:**

- **filename** (string) – Path of the file.
- **stream** (int) – The index of the audio stream within the file if it
  contains multiple audio streams, 0 by default.

<a id="aud.Sound.buffer"></a>

#### classmethod aud.Sound.buffer(data, rate)

Creates a sound from a data buffer.

**Parameters:**

- **data** (`numpy.ndarray`) – The data as two dimensional numpy array.
- **rate** (double) – The sample rate.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.file"></a>

#### classmethod aud.Sound.file(filename)

Creates a sound object of a sound file.

**Parameters:**

**filename** (string) – Path of the file.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Warning:**
>
> If the file doesn’t exist or can’t be read you will
> not get an exception immediately, but when you try to start
> playback of that sound.

<a id="aud.Sound.list"></a>

#### classmethod aud.Sound.list()

Creates an empty sound list that can contain several sounds.

**Parameters:**

**random** (int) – whether the playback will be random or not.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.sawtooth"></a>

#### classmethod aud.Sound.sawtooth(frequency, rate=48000)

Creates a sawtooth sound which plays a sawtooth wave.

**Parameters:**

- **frequency** (float) – The frequency of the sawtooth wave in Hz.
- **rate** (int) – The sampling rate in Hz. It’s recommended to set this
  value to the playback device’s sampling rate to avoid resampling.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.silence"></a>

#### classmethod aud.Sound.silence(rate=48000)

Creates a silence sound which plays simple silence.

**Parameters:**

**rate** (int) – The sampling rate in Hz. It’s recommended to set this
value to the playback device’s sampling rate to avoid resampling.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.sine"></a>

#### classmethod aud.Sound.sine(frequency, rate=48000)

Creates a sine sound which plays a sine wave.

**Parameters:**

- **frequency** (float) – The frequency of the sine wave in Hz.
- **rate** (int) – The sampling rate in Hz. It’s recommended to set this
  value to the playback device’s sampling rate to avoid resampling.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.square"></a>

#### classmethod aud.Sound.square(frequency, rate=48000)

Creates a square sound which plays a square wave.

**Parameters:**

- **frequency** (float) – The frequency of the square wave in Hz.
- **rate** (int) – The sampling rate in Hz. It’s recommended to set this
  value to the playback device’s sampling rate to avoid resampling.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.triangle"></a>

#### classmethod aud.Sound.triangle(frequency, rate=48000)

Creates a triangle sound which plays a triangle wave.

**Parameters:**

- **frequency** (float) – The frequency of the triangle wave in Hz.
- **rate** (int) – The sampling rate in Hz. It’s recommended to set this
  value to the playback device’s sampling rate to avoid resampling.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.ADSR"></a>

#### aud.Sound.ADSR(attack, decay, sustain, release)

Attack-Decay-Sustain-Release envelopes the volume of a sound.
Note: there is currently no way to trigger the release with this API.

**Parameters:**

- **attack** (float) – The attack time in seconds.
- **decay** (float) – The decay time in seconds.
- **sustain** (float) – The sustain level.
- **release** (float) – The release level.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.accumulate"></a>

#### aud.Sound.accumulate(additive=False)

Accumulates a sound by summing over positive input
differences thus generating a monotonic sigal.
If additivity is set to true negative input differences get added too,
but positive ones with a factor of two.

Note that with additivity the signal is not monotonic anymore.

**Parameters:**

**additive** – Whether the accumulation should be additive or not.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.addSound"></a>

#### aud.Sound.addSound(sound)

Adds a new sound to a sound list.

**Parameters:**

**sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound that will be added to the list.

> **Note:**
>
> You can only add a sound to a sound list.

<a id="aud.Sound.animateableTimeStretchPitchScale"></a>

#### aud.Sound.animateableTimeStretchPitchScale(fps[, time_stretch, pitch_scale, quality, preserve_formant])

Applies time-stretching and pitch-scaling to the sound.

**Parameters:**

- **fps** (float) – The FPS of the animation system.
- **time_stretch** (float or `AnimateablePropertyP`) – The factor by which to stretch or compress time.
- **pitch_scale** (float or `AnimateablePropertyP`
  :arg quality: Rubberband stretcher quality (STRETCHER_QUALITY_*).) – The factor by which to adjust the pitch.
- **preserve_formant** (bool) – Whether to preserve the vocal formants during pitch-shifting.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.binaural"></a>

#### aud.Sound.binaural()

Creates a binaural sound using another sound as source. The original sound must be mono

**Parameters:**

- **hrtfs** – An HRTF set.
- **source** ([`Source`](#aud.Source "aud.Source")) – An object representing the source position of the sound.
- **threadPool** ([`ThreadPool`](#aud.ThreadPool "aud.ThreadPool")) – A thread pool used to parallelize convolution.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.cache"></a>

#### aud.Sound.cache()

Caches a sound into RAM.

This saves CPU usage needed for decoding and file access if the
underlying sound reads from a file on the harddisk,
but it consumes a lot of memory.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> Only known-length factories can be buffered.

> **Warning:**
>
> Raw PCM data needs a lot of space, only buffer
> short factories.

<a id="aud.Sound.convolver"></a>

#### aud.Sound.convolver()

Creates a sound that will apply convolution to another sound.

**Parameters:**

- **impulseResponse** ([`ImpulseResponse`](#aud.ImpulseResponse "aud.ImpulseResponse")) – The filter with which convolve the sound.
- **threadPool** ([`ThreadPool`](#aud.ThreadPool "aud.ThreadPool")) – A thread pool used to parallelize convolution.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.data"></a>

#### aud.Sound.data()

Retrieves the data of the sound as numpy array.

**Returns:**

A two dimensional numpy float array.

**Return type:**

`numpy.ndarray`

> **Note:**
>
> Best efficiency with cached sounds.

<a id="aud.Sound.delay"></a>

#### aud.Sound.delay(time)

Delays by playing adding silence in front of the other sound’s data.

**Parameters:**

**time** (float) – How many seconds of silence should be added before the sound.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.Echo"></a>

#### aud.Sound.Echo(delay, feedback, mix)

Adds Echo effect to the sound.

**Parameters:**

- **delay** (float) – The delay time in seconds.
- **feedback** (float) – The feedback amount (0.0 to 1.0).
- **mix** (float) – The wet/dry mix (0.0 to 1.0).
- **reset_buffer** (bool) – Whether to reset the delay buffer on seek.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.envelope"></a>

#### aud.Sound.envelope(attack, release, threshold, arthreshold)

Delays by playing adding silence in front of the other sound’s data.

**Parameters:**

- **attack** (float) – The attack factor.
- **release** (float) – The release factor.
- **threshold** (float) – The general threshold value.
- **arthreshold** (float) – The attack/release threshold value.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.fadein"></a>

#### aud.Sound.fadein(start, length)

Fades a sound in by raising the volume linearly in the given
time interval.

**Parameters:**

- **start** (float) – Time in seconds when the fading should start.
- **length** (float) – Time in seconds how long the fading should last.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> Before the fade starts it plays silence.

<a id="aud.Sound.fadeout"></a>

#### aud.Sound.fadeout(start, length)

Fades a sound in by lowering the volume linearly in the given
time interval.

**Parameters:**

- **start** (float) – Time in seconds when the fading should start.
- **length** (float) – Time in seconds how long the fading should last.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> After the fade this sound plays silence, so that
> the length of the sound is not altered.

<a id="aud.Sound.filter"></a>

#### aud.Sound.filter(b, a=(1,))

Filters a sound with the supplied IIR filter coefficients.
Without the second parameter you’ll get a FIR filter.

If the first value of the a sequence is 0,
it will be set to 1 automatically.
If the first value of the a sequence is neither 0 nor 1, all
filter coefficients will be scaled by this value so that it is 1
in the end, you don’t have to scale yourself.

**Parameters:**

- **b** (sequence of float) – The nominator filter coefficients.
- **a** (sequence of float) – The denominator filter coefficients.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.highpass"></a>

#### aud.Sound.highpass(frequency, Q=0.5)

Creates a second order highpass filter based on the transfer
function \(H(s) = s^2 / (s^2 + s/Q + 1)\)

**Parameters:**

- **frequency** (float) – The cut off trequency of the highpass.
- **Q** (float) – Q factor of the lowpass.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.join"></a>

#### aud.Sound.join(sound)

Plays two factories in sequence.

**Parameters:**

**sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound to play second.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> The two factories have to have the same specifications
> (channels and samplerate).

<a id="aud.Sound.limit"></a>

#### aud.Sound.limit(start, end)

Limits a sound within a specific start and end time.

**Parameters:**

- **start** (float) – Start time in seconds.
- **end** (float) – End time in seconds.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.loop"></a>

#### aud.Sound.loop(count)

Loops a sound.

**Parameters:**

**count** (integer) – How often the sound should be looped.
Negative values mean endlessly.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> This is a filter function, you might consider using
> [`Handle.loop_count`](#aud.Handle.loop_count "aud.Handle.loop_count") instead.

<a id="aud.Sound.lowpass"></a>

#### aud.Sound.lowpass(frequency, Q=0.5)

Creates a second order lowpass filter based on the transfer function \(H(s) = 1 / (s^2 + s/Q + 1)\)

**Parameters:**

- **frequency** (float) – The cut off trequency of the lowpass.
- **Q** (float) – Q factor of the lowpass.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.mix"></a>

#### aud.Sound.mix(sound)

Mixes two factories.

**Parameters:**

**sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound to mix over the other.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> The two factories have to have the same specifications
> (channels and samplerate).

<a id="aud.Sound.modulate"></a>

#### aud.Sound.modulate(sound)

Modulates two factories.

**Parameters:**

**sound** ([`Sound`](#aud.Sound "aud.Sound")) – The sound to modulate over the other.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> The two factories have to have the same specifications
> (channels and samplerate).

<a id="aud.Sound.mutable"></a>

#### aud.Sound.mutable()

Creates a sound that will be restarted when sought backwards.
If the original sound is a sound list, the playing sound can change.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.pingpong"></a>

#### aud.Sound.pingpong()

Plays a sound forward and then backward.
This is like joining a sound with its reverse.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.pitch"></a>

#### aud.Sound.pitch(factor)

Changes the pitch of a sound with a specific factor.

**Parameters:**

**factor** (float) – The factor to change the pitch with.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> This is done by changing the sample rate of the
> underlying sound, which has to be an integer, so the factor
> value rounded and the factor may not be 100 % accurate.

> **Note:**
>
> This is a filter function, you might consider using
> [`Handle.pitch`](#aud.Handle.pitch "aud.Handle.pitch") instead.

<a id="aud.Sound.rechannel"></a>

#### aud.Sound.rechannel(channels)

Rechannels the sound.

**Parameters:**

**channels** (int) – The new channel configuration.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.resample"></a>

#### aud.Sound.resample(rate, quality)

Resamples the sound.

**Parameters:**

- **rate** (double) – The new sample rate.
- **quality** (int) – Resampler performance vs quality choice (0=fastest, 3=slowest).

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.reverse"></a>

#### aud.Sound.reverse()

Plays a sound reversed.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> The sound has to have a finite length and has to be seekable.
> It’s recommended to use this only with factories with
> fast and accurate seeking, which is not true for encoded audio
> files, such ones should be buffered using [`cache()`](#aud.Sound.cache "aud.Sound.cache") before
> being played reversed.

> **Warning:**
>
> If seeking is not accurate in the underlying sound
> you’ll likely hear skips/jumps/cracks.

<a id="aud.Sound.sum"></a>

#### aud.Sound.sum()

Sums the samples of a sound.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.threshold"></a>

#### aud.Sound.threshold(threshold=0)

Makes a threshold wave out of an audio wave by setting all samples
with a amplitude >= threshold to 1, all <= -threshold to -1 and
all between to 0.

**Parameters:**

**threshold** (float) – Threshold value over which an amplitude counts
non-zero.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.timeStretchPitchScale"></a>

#### aud.Sound.timeStretchPitchScale(time_stretch, pitch_scale, quality, preserve_formant)

Applies time-stretching and pitch-scaling to the sound.

**Parameters:**

- **time_stretch** (float) – The factor by which to stretch or compress time.
- **pitch_scale** (float) – The factor by which to adjust the pitch.
- **quality** (int) – Rubberband stretcher quality (STRETCHER_QUALITY_*).
- **preserve_formant** (bool) – Whether to preserve the vocal formants during pitch-shifting.

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

<a id="aud.Sound.volume"></a>

#### aud.Sound.volume(volume)

Changes the volume of a sound.

**Parameters:**

**volume** (float) – The new volume..

**Returns:**

The created [`Sound`](#aud.Sound "aud.Sound") object.

**Return type:**

[`Sound`](#aud.Sound "aud.Sound")

> **Note:**
>
> Should be in the range [0, 1] to avoid clipping.

> **Note:**
>
> This is a filter function, you might consider using
> [`Handle.volume`](#aud.Handle.volume "aud.Handle.volume") instead.

<a id="aud.Sound.write"></a>

#### aud.Sound.write(filename, rate, channels, format, container, codec, bitrate, buffersize)

Writes the sound to a file.

**Parameters:**

- **filename** (string) – The path to write to.
- **rate** (int) – The sample rate to write with.
- **channels** (int) – The number of channels to write with.
- **format** (int) – The sample format to write with.
- **container** (int) – The container format for the file.
- **codec** (int) – The codec to use in the file.
- **bitrate** (int) – The bitrate to write with.
- **buffersize** (int) – The size of the writing buffer.

<a id="aud.Sound.length"></a>

#### aud.Sound.length

The sample specification of the sound as a tuple with rate and channel count.

<a id="aud.Sound.specs"></a>

#### aud.Sound.specs

The sample specification of the sound as a tuple with rate and channel count.

<a id="aud.Source"></a>

### class aud.Source(azimuth, elevation, distance, /)

The source object represents the source position of a binaural sound.

**Parameters:**

- **azimuth** (float) – The azimuth angle in degrees.
- **elevation** (float) – The elevation angle in degrees.
- **distance** (float) – The distance of the source.

<a id="aud.Source.azimuth"></a>

#### aud.Source.azimuth

The azimuth angle.

<a id="aud.Source.distance"></a>

#### aud.Source.distance

The distance value. 0 is min, 1 is max.

<a id="aud.Source.elevation"></a>

#### aud.Source.elevation

The elevation angle.

<a id="aud.ThreadPool"></a>

### class aud.ThreadPool(nThreads, /)

A ThreadPool is used to parallelize convolution efficiently.

**Parameters:**

**nThreads** (int) – The number of threads in the pool.

<a id="aud.error"></a>

### class aud.error
