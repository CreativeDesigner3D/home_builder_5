<!-- source: Blender Python API reference 5.2 / bpy_types_enum_items/object_modifier_type_items.html -->

<a id="object-modifier-type-items"></a>

# Object Modifier Type Items

**Modify**

**GREASE_PENCIL_VERTEX_WEIGHT_PROXIMITY:**

Vertex Weight Proximity.

Generate vertex weights based on distance to object.

**Modify**

**DATA_TRANSFER:**

Data Transfer.

Transfer several types of data (vertex groups, UV maps, vertex colors, custom normals) from one mesh to another.

**MESH_CACHE:**

Mesh Cache.

Deform the mesh using an external frame-by-frame vertex transform cache.

**MESH_SEQUENCE_CACHE:**

Mesh Sequence Cache.

Deform the mesh or curve using an external mesh cache in Alembic format.

**NORMAL_EDIT:**

Normal Edit.

Modify the direction of the surface normals.

**WEIGHTED_NORMAL:**

Weighted Normal.

Modify the direction of the surface normals using a weighting method.

**UV_PROJECT:**

UV Project.

Project the UV map coordinates from the negative Z axis of another object.

**UV_WARP:**

UV Warp.

Transform the UV map using the difference between two objects.

**VERTEX_WEIGHT_EDIT:**

Vertex Weight Edit.

Modify of the weights of a vertex group.

**VERTEX_WEIGHT_MIX:**

Vertex Weight Mix.

Mix the weights of two vertex groups.

**VERTEX_WEIGHT_PROXIMITY:**

Vertex Weight Proximity.

Set the vertex group weights based on the distance to another target object.

**GREASE_PENCIL_COLOR:**

Hue/Saturation.

Change hue/saturation/value of the strokes.

**GREASE_PENCIL_TINT:**

Tint.

Tint the color of the strokes.

**GREASE_PENCIL_OPACITY:**

Opacity.

Change the opacity of the strokes.

**GREASE_PENCIL_VERTEX_WEIGHT_ANGLE:**

Vertex Weight Angle.

Generate vertex weights based on stroke angle.

**GREASE_PENCIL_TIME:**

Time Offset.

Offset keyframes.

**GREASE_PENCIL_TEXTURE:**

Texture Mapping.

Change stroke UV texture values.

**Generate**

**ARRAY:**

Array.

Create copies of the shape with offsets.

**BEVEL:**

Bevel.

Generate sloped corners by adding geometry to the mesh’s edges or vertices.

**BOOLEAN:**

Boolean.

Use another shape to cut, combine or perform a difference operation.

**BUILD:**

Build.

Cause the faces of the mesh object to appear or disappear one after the other over time.

**DECIMATE:**

Decimate.

Reduce the geometry density.

**EDGE_SPLIT:**

Edge Split.

Split away joined faces at the edges.

**NODES:**

Geometry Nodes.

**MASK:**

Mask.

Dynamically hide vertices based on a vertex group or armature.

**MIRROR:**

Mirror.

Mirror along the local X, Y and/or Z axes, over the object origin.

**MESH_TO_VOLUME:**

Mesh to Volume.

**MULTIRES:**

Multiresolution.

Subdivide the mesh in a way that allows editing the higher subdivision levels.

**REMESH:**

Remesh.

Generate new mesh topology based on the current shape.

**SCREW:**

Screw.

Lathe around an axis, treating the input mesh as a profile.

**SKIN:**

Skin.

Create a solid shape from vertices and edges, using the vertex radius to define the thickness.

**SOLIDIFY:**

Solidify.

Make the surface thick.

**SUBSURF:**

Subdivision Surface.

Split the faces into smaller parts, giving it a smoother appearance.

**TRIANGULATE:**

Triangulate.

Convert all polygons to triangles.

**VOLUME_TO_MESH:**

Volume to Mesh.

**WELD:**

Weld.

Find groups of vertices closer than dist and merge them together.

**WIREFRAME:**

Wireframe.

Convert faces into thickened edges.

**GREASE_PENCIL_ARRAY:**

Array.

Duplicate strokes into an array.

**GREASE_PENCIL_BUILD:**

Build.

Grease Pencil build modifier.

**GREASE_PENCIL_LENGTH:**

Length.

Grease Pencil length modifier.

**LINEART:**

Line Art.

Generate Line Art from scene geometries.

**GREASE_PENCIL_MIRROR:**

Mirror.

Duplicate strokes like a mirror.

**GREASE_PENCIL_MULTIPLY:**

Multiple Strokes.

Generate multiple strokes around original strokes.

**GREASE_PENCIL_SIMPLIFY:**

Simplify.

Simplify stroke reducing number of points.

**GREASE_PENCIL_SUBDIV:**

Subdivide.

Grease Pencil subdivide modifier.

**GREASE_PENCIL_ENVELOPE:**

Envelope.

Create an envelope shape.

**GREASE_PENCIL_OUTLINE:**

Outline.

Convert stroke to outline.

**Deform**

**ARMATURE:**

Armature.

Deform the shape using an armature object.

**CAST:**

Cast.

Shift the shape towards a predefined primitive.

**CURVE:**

Curve.

Bend the mesh using a curve object.

**DISPLACE:**

Displace.

Offset vertices based on a texture.

**HOOK:**

Hook.

Deform specific points using another object.

**LAPLACIANDEFORM:**

Laplacian Deform.

Deform based a series of anchor points.

**LATTICE:**

Lattice.

Deform using the shape of a lattice object.

**MESH_DEFORM:**

Mesh Deform.

Deform using a different mesh, which acts as a deformation cage.

**SHRINKWRAP:**

Shrinkwrap.

Project the shape onto another object.

**SIMPLE_DEFORM:**

Simple Deform.

Deform the shape by twisting, bending, tapering or stretching.

**SMOOTH:**

Smooth.

Smooth the mesh by flattening the angles between adjacent faces.

**CORRECTIVE_SMOOTH:**

Smooth Corrective.

Smooth the mesh while still preserving the volume.

**LAPLACIANSMOOTH:**

Smooth Laplacian.

Reduce the noise on a mesh surface with minimal changes to its shape.

**SURFACE_DEFORM:**

Surface Deform.

Transfer motion from another mesh.

**WARP:**

Warp.

Warp parts of a mesh to a new location in a very flexible way thanks to 2 specified objects.

**WAVE:**

Wave.

Adds a ripple-like motion to an object’s geometry.

**VOLUME_DISPLACE:**

Volume Displace.

Deform volume based on noise or other vector fields.

**GREASE_PENCIL_HOOK:**

Hook.

Deform stroke points using objects.

**GREASE_PENCIL_NOISE:**

Noise.

Generate noise wobble in Grease Pencil strokes.

**GREASE_PENCIL_OFFSET:**

Offset.

Change stroke location, rotation, or scale.

**GREASE_PENCIL_SMOOTH:**

Smooth.

Smooth Grease Pencil strokes.

**GREASE_PENCIL_THICKNESS:**

Thickness.

Change stroke thickness.

**GREASE_PENCIL_LATTICE:**

Lattice.

Deform strokes using a lattice object.

**GREASE_PENCIL_DASH:**

Dot Dash.

Generate dot-dash styled strokes.

**GREASE_PENCIL_ARMATURE:**

Armature.

Deform stroke points using armature object.

**GREASE_PENCIL_SHRINKWRAP:**

Shrinkwrap.

Project the shape onto another object.

**Physics**

**CLOTH:**

Cloth.

Physic simulation for cloth.

**COLLISION:**

Collision.

For colliders participating in physics simulation, control which level in the modifier stack is used as the collision surface.

**DYNAMIC_PAINT:**

Dynamic Paint.

Turn objects into paint canvases and brushes, creating color attributes, image sequences, or displacement.

**EXPLODE:**

Explode.

Break apart the mesh faces and let them follow particles.

**FLUID:**

Fluid.

Physics simulation for fluids, like water, oil and smoke.

**OCEAN:**

Ocean.

Generate a moving ocean surface.

**PARTICLE_INSTANCE:**

Particle Instance.

Duplicate mesh at the location of particles.

**PARTICLE_SYSTEM:**

Particle System.

Spawn particles from the shape.

**SOFT_BODY:**

Soft Body.

Simulate soft deformable objects.

**SURFACE:**

Surface.
