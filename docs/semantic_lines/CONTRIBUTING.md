# Semantic Lines Contribution Conventions

## Design rules

1. Extract semantic edges once; do not add a separate edge-discovery path for
   viewport, rendering, drafting, or picking.
2. Faces and triangles are visibility evidence only. Internal tessellation
   must not become visible technical linework by accident.
3. Keep geometry in model/world space and projected edges in 2D space. Do not
   persist raster pixels as geometry or measurement data.
4. New consumers accept `SemanticEdge` or `ProjectedEdgeSegment`; they must
   not depend on a particular viewport or compositor implementation.
5. Preserve existing Home Builder wireframe, Line Art, and Freestyle behavior
   unless the user explicitly enables Semantic Lines.

## Visibility conventions

- Use scale-aware self-occlusion tolerances.
- Split at visibility transitions. For sampled changes at an edge endpoint,
  snap the transition to the endpoint so solid strokes do not overdraw a
  hidden corner.
- Suppress a hidden line only when visible collinear segments cover its entire
  projected length. Do not suppress merely nearby or partially overlapping
  linework.
- Keep dash generation in screen/image space so it is independent of mesh
  segmentation.

## UI and settings conventions

- Add user controls under **Semantic Edges (Experimental)** as a child panel.
- Put shared visual controls in **Edge Control**. A consumer may add an
  explicitly named multiplier for calibration, but must not introduce an
  unrelated duplicate color or base-weight setting.
- Scene properties use the `hb_semantic_edge_` or `hb_semantic_render_`
  prefix. Blender data blocks and compositor nodes use the `HB Semantic`
  prefix.

## Tests and verification

Run:

```bat
scripts\run_tests.cmd
```

Every semantic feature needs a Blender-headless test. At minimum cover a
box, coplanar triangulation, sharp fold, marked edge, visibility-run boundary,
and the render pass when applicable. Add a visual regression fixture before
changing line style, dashing, or visibility semantics.

Before upstream review, rebuild the portable extension with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_dev_extension.ps1
```

Then check both an orthographic isometric viewport and an F12 layout render.
