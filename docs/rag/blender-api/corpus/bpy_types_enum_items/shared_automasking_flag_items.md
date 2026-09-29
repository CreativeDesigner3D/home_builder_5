<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/shared_automasking_flag_items.html -->

<a id="shared-automasking-flag-items"></a>

# Shared Automasking Flag Items

**use_automasking_topology:**

Topology.

Affect only vertices connected to the active vertex under the brush.

**use_automasking_face_sets:**

Face Sets.

Affect only vertices that share face sets with the active vertex.

**use_automasking_boundary_edges:**

Mesh Boundary Auto-Masking.

Do not affect non manifold boundary edges.

**use_automasking_boundary_face_sets:**

Face Sets Boundary Automasking.

Do not affect vertices that belong to a face set boundary.

**use_automasking_cavity:**

Cavity Mask.

Do not affect vertices on peaks, based on the surface curvature.

**use_automasking_cavity_inverted:**

Inverted Cavity Mask.

Do not affect vertices within crevices, based on the surface curvature.

**use_automasking_custom_cavity_curve:**

Custom Cavity Curve.

Use custom curve.

**use_automasking_start_normal:**

Area Normal.

Affect only vertices with a similar normal to where the stroke starts.

**use_automasking_view_normal:**

View Normal.

Affect only vertices with a normal that faces the viewer.

**use_automasking_view_occlusion:**

Occlusion.

Only affect vertices that are not occluded by other faces (slower performance).
