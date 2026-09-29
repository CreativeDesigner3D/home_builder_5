<!-- source: Blender Python API reference 5.2 / bpy.app.timers.html -->

<a id="module-bpy.app.timers"></a>

# Application Timers (bpy.app.timers)

<a id="run-a-function-in-x-seconds"></a>

## Run a Function in x Seconds

```python
import bpy

def in_5_seconds():
    print("Hello World")

bpy.app.timers.register(in_5_seconds, first_interval=5)
```

<a id="run-a-function-every-x-seconds"></a>

## Run a Function every x Seconds

```python
import bpy

def every_2_seconds():
    print("Hello World")
    return 2.0

bpy.app.timers.register(every_2_seconds)
```

<a id="run-a-function-n-times-every-x-seconds"></a>

## Run a Function n times every x seconds

```python
import bpy

counter = 0

def run_10_times():
    global counter
    counter += 1
    print(counter)
    if counter == 10:
        return None
    return 0.1

bpy.app.timers.register(run_10_times)
```

<a id="assign-parameters-to-functions"></a>

## Assign parameters to functions

```python
import bpy
import functools

def print_message(message):
    print("Message:", message)

bpy.app.timers.register(functools.partial(print_message, "Hello"), first_interval=2.0)
bpy.app.timers.register(functools.partial(print_message, "World"), first_interval=3.0)
```

<a id="bpy.app.timers.is_registered"></a>

### bpy.app.timers.is_registered(function)

Check if this function is registered as a timer.

**Parameters:**

**function** (Callable[[], float | None]) – Function to check.

**Returns:**

True when this function is registered, otherwise False.

**Return type:**

bool

<a id="bpy.app.timers.register"></a>

### bpy.app.timers.register(function, *, first_interval=0, persistent=False)

Add a new function that will be called after the specified amount of seconds.
The function gets no arguments and is expected to return either None or a float.
If `None` is returned, the timer will be unregistered.
A returned number specifies the delay until the function is called again.
`functools.partial` can be used to assign some parameters.

**Parameters:**

- **function** (Callable[[], float | None]) – The function that should called.
- **first_interval** (float) – Seconds until the callback should be called the first time.
- **persistent** (bool) – Don’t remove timer when a new file is loaded.

<a id="bpy.app.timers.unregister"></a>

### bpy.app.timers.unregister(function)

Unregister timer.

**Parameters:**

**function** (Callable[[], float | None]) – Function to unregister.
