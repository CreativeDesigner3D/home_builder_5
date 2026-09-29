<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/file_path_foreach_flag_items.html -->

<a id="file-path-foreach-flag-items"></a>

# File Path Foreach Flag Items

**SKIP_LINKED:**

Skip Linked.

Skip paths of linked IDs.

**SKIP_PACKED:**

Skip Packed.

Skip paths when their matching data is packed.

**SKIP_WEAK_REFERENCES:**

Skip Weak References.

Skip weak reference paths. Those paths are typically ‘nice to have’ extra information, but are not used as actual source of data by the current .blend file.

**SKIP_MULTIFILE:**

Skip Multi-file.

Skip paths where a single dir is used with an array of files, eg. sequence strip images or point-caches. In this case only the first file path is processed. This is needed for directory manipulation callbacks which might otherwise modify the same directory multiple times.

**RELOAD_EDITED:**

Reload Edited.

Reload data when the path is edited.

**RESOLVE_TOKEN:**

Resolve Tokens.

Resolve tokens within a virtual filepath to a single, concrete, filepath. Currently only used for UDIM tiles.

**EXPAND_TOKENS:**

Expand Tokens.

Expand template tokens in virtual file paths and invoke the callback once for each concrete file. Currently only used for UDIM tiles.

**EXPAND_SEQUENCES:**

Expand Sequences.

Expand image and volume sequences, invoking the callback once per file on disk.

**EXPAND_CACHES:**

Expand Caches.

Visit cache files, like texture cache files associated with images.
