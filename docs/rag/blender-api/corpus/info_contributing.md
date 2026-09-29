<!-- source: Blender Python API reference 5.2 / info_contributing.html -->

<a id="contribute-documentation"></a>

# Contribute Documentation

This guide covers how to contribute to Blender’s Python API documentation,
including writing examples, formatting documentation, and building the docs locally.

<a id="setting-up-your-environment"></a>

## Setting Up Your Environment

<a id="prerequisites"></a>

### Prerequisites

Before you can build the documentation, you need:

Blender Source Code
:   Clone the Blender repository following the
    [official build instructions](https://developer.blender.org/docs/handbook/building_blender/).

Python Environment *(optional)*
:   Set up a Python [virtual environment](https://docs.python.org/3/library/venv.html).

<a id="installing-documentation-requirements"></a>

### Installing Documentation Requirements

Typically, you would set up a virtual environment and install the packages listed in
`doc/python_api/requirements.txt`. However, the only hard requirement is Sphinx,
which you can install directly:

```bash
pip install -r doc/python_api/requirements.txt
```

<a id="building-the-documentation"></a>

### Building the Documentation

Once you have the requirements installed, you can build the documentation:

```bash
# From the Blender source root
make doc_py
```

You can then open `doc/python_api/sphinx-out/index.html` in your browser.

<a id="modifying-api-documentation"></a>

## Modifying API Documentation

API documentation is automatically generated from Blender’s source code, meaning that
class descriptions, method signatures, etc., are defined either within C/C++ files
(via `PyDoc_STRVAR`) or as standard doc-strings in Python files.

**To modify API class or method descriptions:**

1. Locate the relevant source file in the Blender repository.
2. Find the relevant doc-string either inside `PyDoc_STRVAR(...)` for the Python C/API
   or as a standard doc-string in a Python file.
3. Edit using **reStructuredText** formatting.
4. Rebuild the Python API docs with `make doc_py` to regenerate the pages.

<a id="adding-example-code-snippets"></a>

## Adding Example Code Snippets

Code examples are a crucial part of the API documentation. They help users
understand how to use various classes, functions, and modules, appearing
above the API reference for each one.

<a id="example-file-naming-convention"></a>

### Example File Naming Convention

Examples can be included as standalone script files instead of inlining
code-blocks in the doc-string. Create a file matching the naming conventions
below, and it will be included automatically.

Example files are located in `doc/python_api/examples/` and are matched by filename:

- `module.N.py` matches a module (e.g., `gpu.0.py`).
- `module.ClassName.N.py` matches a class (e.g., `bpy.types.Operator.0.py`).
- `module.ClassName.method.N.py` matches a method (e.g., `bpy.types.Operator.invoke.0.py`).
- `module.ClassName.attribute.N.py` matches an attribute (e.g., `bpy.types.Scene.frame_start.0.py`).
- `module.member.N.py` matches a module member (e.g., `bpy.context.object.0.py`).

Multiple examples are supported, where `N` allows them to be ordered sequentially.

<a id="example-file-structure"></a>

### Example File Structure

For each example, it is often useful to include a description explaining what the code demonstrates.
To support this, the doc-string at the start of the file is extracted and displayed above the code example.
The doc-string content will be formatted as reStructuredText.

Each example file should follow this structure:

```python
"""
Example Title
+++++++++++++

A description of what this example demonstrates.
This doc-string appears above the code in the documentation.

You can use **reStructuredText** formatting here, for example:

- *Italic* text with single asterisks
- **Bold** text with double asterisks
- ``inline code`` with double backticks
- :class:`bpy.types.Operator` to link to API classes
- Links to `external resources <https://www.blender.org/>`__

.. note::

   You can use this to highlight important information.

Everything after this doc-string is included as code.
"""
import bpy

# Example code goes here
print("This is an example")
```

<a id="important-notes"></a>

#### Important Notes

- The file must start with triple double-quotes `"""` (single-quoted doc-strings aren’t recognized).
- Use section header underlines with `+` characters for the title.
- Everything after the doc-string is included as code in the documentation.
- To add additional code-blocks with text in between, add new files.

<a id="best-practices-for-documentation"></a>

## Best Practices for Documentation

<a id="writing-good-examples"></a>

### Writing Good Examples

- **Keep it simple**: Focus on demonstrating one concept at a time.
- **Make it runnable**: Examples should work when pasted into Blender’s Python console or text editor.
- **Use comments**: Comment thoroughly, assuming readers are new to the APIs and concepts being demonstrated.

<a id="style-guidelines"></a>

### Style Guidelines

For documentation, we aim for high-quality technical writing. Refer to these
style guides from the User Manual for markup and conventions:

- [Markup Guide](https://docs.blender.org/manual/en/latest/contribute/manual/guides/markup_guide.html)
- [Writing Guide](https://docs.blender.org/manual/en/latest/contribute/manual/guides/writing_guide.html)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html)

<a id="testing-your-changes"></a>

## Testing Your Changes

After adding or modifying documentation, rebuild the docs (see
[Building the Documentation](#building-the-documentation)) and check for any warnings about broken links,
missing references, or formatting issues. Preview the generated HTML files
in your browser to verify they look correct.

<a id="contributing-your-changes"></a>

## Contributing Your Changes

Once you’ve added or improved documentation,
follow Blender’s [contribution guidelines](https://developer.blender.org/docs/handbook/contributing/)
to create a pull request.
