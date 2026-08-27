"""Semantic model-edge extraction for Home Builder technical drawings.

This is deliberately the *source* layer only.  It identifies the useful
edges of an evaluated Blender mesh, keeps a stable Home Builder identity for
the owning object, and returns neutral records that a later projector,
visibility solver, viewport overlay, and drawing exporter can share.

Faces are evidence for classification, not line candidates: an edge that is
only an internal coplanar tessellation diagonal is omitted by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians
from typing import Iterable, Optional, Tuple
from uuid import uuid4

from mathutils import Vector


SOURCE_UID_PROPERTY = "HB_SEMANTIC_SOURCE_UID"
USER_MARKED_ATTRIBUTE = "hb_semantic_edge"

EDGE_BOUNDARY = "BOUNDARY"
EDGE_SHARP = "SHARP"
EDGE_USER_MARKED = "USER_MARKED"

Point3 = Tuple[float, float, float]


@dataclass(frozen=True)
class SemanticEdge:
    """One intentional line candidate, expressed in world space.

    ``topology_edge_index`` is useful while a mesh is current, but is not
    persistent identity.  ``uid`` is stable for the source object and its
    canonical endpoint topology reference; callers must recreate edge
    references after a topology change.
    """

    uid: str
    source_object_uid: str
    source_object_name: str
    topology_edge_index: int
    topology_vertices: Tuple[int, int]
    start: Point3
    end: Point3
    edge_class: str
    adjacent_faces: Tuple[int, ...]


@dataclass(frozen=True)
class EdgeExtractionOptions:
    """Policy for the first semantic edge extractor.

    A user-marked edge always survives classification.  Boundary edges and
    edges with an angle at or above ``sharp_angle_degrees`` are candidates.
    """

    sharp_angle_degrees: float = 30.0
    include_boundary: bool = True
    include_sharp: bool = True
    include_user_marked: bool = True
    include_loose: bool = True


def ensure_source_uid(obj) -> str:
    """Return Home Builder's persistent UID for an authored object.

    The object, rather than its evaluated copy, owns this identifier.  This
    is intentionally the only extraction-time write and lets downstream
    systems retain a meaningful reference as evaluated meshes are rebuilt.
    """
    uid = obj.get(SOURCE_UID_PROPERTY)
    if not uid:
        uid = str(uuid4())
        obj[SOURCE_UID_PROPERTY] = uid
    return str(uid)


def extract_semantic_edges(obj, depsgraph=None,
                           options: Optional[EdgeExtractionOptions] = None
                           ) -> Tuple[SemanticEdge, ...]:
    """Extract semantic edges from ``obj``'s evaluated mesh.

    ``obj`` must be a mesh object.  Supplying a depsgraph includes Geometry
    Nodes and modifiers; omit it for direct mesh tests or authored meshes.
    This function has no viewport, camera, or rendering dependency.
    """
    if obj.type != 'MESH':
        return ()

    options = options or EdgeExtractionOptions()
    source_uid = ensure_source_uid(obj)
    evaluated = obj.evaluated_get(depsgraph) if depsgraph is not None else obj
    mesh = evaluated.data
    if mesh is None:
        return ()

    edge_faces = _edge_face_map(mesh)
    threshold_cos = cos(radians(options.sharp_angle_degrees))
    result = []
    for edge in mesh.edges:
        edge_index = edge.index
        faces = edge_faces[edge_index]
        user_marked = _edge_is_user_marked(mesh, edge_index)
        edge_class = _classify_edge(mesh, faces, threshold_cos, user_marked,
                                    options)
        if edge_class is None:
            continue

        v0, v1 = sorted(edge.vertices[:])
        start = _world_point(evaluated.matrix_world, mesh.vertices[v0].co)
        end = _world_point(evaluated.matrix_world, mesh.vertices[v1].co)
        uid = f"{source_uid}:{v0}:{v1}"
        result.append(SemanticEdge(
            uid=uid,
            source_object_uid=source_uid,
            source_object_name=obj.name,
            topology_edge_index=edge_index,
            topology_vertices=(v0, v1),
            start=start,
            end=end,
            edge_class=edge_class,
            adjacent_faces=tuple(faces),
        ))
    return tuple(result)


def _edge_face_map(mesh) -> Tuple[Tuple[int, ...], ...]:
    """Map each mesh edge to adjacent polygon indices without BMesh."""
    by_key = {tuple(sorted(edge.vertices[:])): edge.index for edge in mesh.edges}
    faces = [[] for _edge in mesh.edges]
    for polygon in mesh.polygons:
        vertices = polygon.vertices[:]
        for index, vertex in enumerate(vertices):
            key = tuple(sorted((vertex, vertices[(index + 1) % len(vertices)])))
            edge_index = by_key.get(key)
            if edge_index is not None:
                faces[edge_index].append(polygon.index)
    return tuple(tuple(face_indices) for face_indices in faces)


def _classify_edge(mesh, faces: Iterable[int], threshold_cos: float,
                   user_marked: bool, options: EdgeExtractionOptions) -> Optional[str]:
    faces = tuple(faces)
    if user_marked and options.include_user_marked:
        return EDGE_USER_MARKED
    if len(faces) == 0:
        return EDGE_BOUNDARY if options.include_loose else None
    if len(faces) == 1:
        return EDGE_BOUNDARY if options.include_boundary else None
    if not options.include_sharp:
        return None

    # Manifold meshes normally have two adjacent polygons.  With non-manifold
    # edges, any materially differing normal makes the edge intentional.
    normals = [mesh.polygons[index].normal.normalized() for index in faces]
    first = normals[0]
    if any(first.dot(normal) < threshold_cos for normal in normals[1:]):
        return EDGE_SHARP
    return None


def _edge_is_user_marked(mesh, edge_index: int) -> bool:
    """Read the optional boolean EDGE-domain authoring attribute safely."""
    attribute = mesh.attributes.get(USER_MARKED_ATTRIBUTE)
    if attribute is None or attribute.domain != 'EDGE':
        return False
    try:
        return bool(attribute.data[edge_index].value)
    except (AttributeError, IndexError):
        return False


def _world_point(matrix, coordinate: Vector) -> Point3:
    point = matrix @ coordinate
    return (float(point.x), float(point.y), float(point.z))
