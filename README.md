# BlenderToMob

BlenderToMob is a modern, modular Blender add-on / extension designed for parametric cabinetry and interior design (inspired by Promob). It provides tools for walls (including curvature and custom angles), floor creation, dynamic snapping, parent insertion planes, and cabinetry layout.

## Project Structure

The project follows a modular structure to maintain clean separation of concerns:

- `blendertomob/` - Main package for the Blender extension.
  - `blender_manifest.toml` - Metadata for the Blender extension (Blender 4.2+).
  - `__init__.py` - Entry point for registering and unregistering all add-on classes.
  - `data/` - Holds Custom Properties and PropertyGroups representing entities like walls and parent planes.
  - `operators/` - Contains operators for interactive wall building, cabinetry insertion, and alignment.
  - `ui/` - Layout and rendering panels sensitive to the active object context.
  - `geometry/` - Low-level bmesh generator scripts and shader graph configurations.
  - `cutting/` - 2D nesting optimization logic (computes sheet cuts programmatically).

## Blender API Knowledge Base (RAG)

`docs/rag/` contains the full Blender 5.2 Python API reference as searchable Markdown plus curated, project-specific
guidance (patterns, 5.x compatibility, gotchas). Start at [docs/rag/README.md](docs/rag/README.md).

```bash
python3 docs/rag/tools/rag_search.py "draw handler POST_PIXEL"      # search the API reference
python3 docs/rag/tools/check_api.py                                  # check blendertomob/ against the 5.2 API
```

## Getting Started

### Packaging the Extension
To package the extension into a zip file (`blendertomob.zip`) that can be installed directly in Blender, run the helper build script from the root directory:

```bash
python3 build.py
```

### Installation
1. Open **Blender 4.2+**.
2. Go to **Edit -> Preferences -> Get Extensions**.
3. Click the gear icon in the top right and select **Install from Disk...**
4. Select the generated `blendertomob.zip` file.
5. Search for "BlenderToMob" and ensure it is activated.
6. Open the 3D Viewport sidebar (press `N`) to access the **BlenderToMob** panels.
