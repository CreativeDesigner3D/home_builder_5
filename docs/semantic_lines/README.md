# Semantic Lines

Semantic Lines is an **experimental, opt-in** technical-line subsystem for
Home Builder. It is an alternative to wireframe-based edge display: it
derives intentional model edges once and provides them to viewport and render
consumers without treating Freestyle, Grease Pencil, or curve objects as the
authoritative edge model.

It is disabled by default. Enable **Show Overlay** in **Home Builder →
Semantic Edges (Experimental) → Edge Control**. The optional render pass is
also disabled until its own toggle is enabled.

## Current components

| Component | Responsibility |
| --- | --- |
| `semantic_lines/semantic_edges.py` | Extracts `SemanticEdge` records from evaluated meshes. |
| `semantic_lines/semantic_edge_overlay.py` | Projects, classifies, and draws viewport lines. |
| `semantic_lines/semantic_line_render.py` | Builds a camera-projected transparent render line pass and composites it. |
| `tests/test_semantic_edges.py` | Blender-headless unit and integration coverage. |

The `semantic_lines/` package is the module boundary. Its model, viewport,
and render layers should change together only when a feature crosses those
consumers.

## Public data contract

`SemanticEdge` is the source record. Its `uid` identifies an edge within an
authored source object; `topology_edge_index` is a current-mesh convenience,
not persistent identity. Consumers must retain `source_edge_uid`, never a
rendered segment as the model reference.

Semantic classes currently are `BOUNDARY`, `SHARP`, and `USER_MARKED`.
Coplanar triangulation edges are excluded unless the mesh has the boolean
EDGE-domain `hb_semantic_edge` attribute set for that edge.

`ProjectedEdgeSegment` is consumer-neutral 2D data. It contains the source
UID, two screen/image points, and `VISIBLE` or `HIDDEN` visibility. It stays
analytic until a viewport or render consumer rasterizes it.

## User behavior

The **Semantic Edges (Experimental)** parent panel contains all controls:

- **Edge Control** configures the viewport overlay and technical visibility.
- **Line Rendering** configures the render-camera line pass.

The shared color and line-weight controls are the source of truth. Viewport
and render multipliers are deliberately secondary calibration controls.

## Scope and non-goals

Current hidden-line classification is sampled ray testing. It is suitable for
the rectangular and low-poly interior models Home Builder primarily produces,
but it is not yet an exact analytic hidden-line solver. Vector export, edge
picking, and dimension references are planned consumers, not implemented
features.

## Upstream compatibility

The system does not modify existing wireframe, Freestyle, or Grease Pencil
Line Art architecture. It has independent scene settings and compositor nodes
prefixed `HB Semantic Lines`. A submission must preserve existing layout
rendering when the semantic overlay and render toggle are off.
