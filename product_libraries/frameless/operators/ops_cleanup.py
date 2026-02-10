import bpy
import bmesh
import math
import mathutils


class hb_frameless_OT_cleanup_mesh(bpy.types.Operator):
    bl_idname = "hb_frameless.cleanup_mesh"
    bl_label = "Clean Up Mesh"
    bl_description = "Convert triangles to quads and dissolve coplanar faces to simplify mesh topology"
    bl_options = {'REGISTER', 'UNDO'}

    face_angle: bpy.props.FloatProperty(
        name="Face Angle",
        description="Maximum angle between faces to merge with Tris to Quads",
        default=math.radians(1.0),
        min=math.radians(0.1),
        max=math.radians(10.0),
        subtype='ANGLE',
    )# type: ignore

    shape_threshold: bpy.props.FloatProperty(
        name="Shape Threshold",
        description="How square the resulting quads should be (higher = more square)",
        default=0.7,
        min=0.0,
        max=1.0,
    )# type: ignore

    dissolve_angle: bpy.props.FloatProperty(
        name="Dissolve Angle",
        description="Maximum angle between faces to merge with Limited Dissolve",
        default=math.radians(1.0),
        min=math.radians(0.1),
        max=math.radians(10.0),
        subtype='ANGLE',
    )# type: ignore

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data

        before_verts = len(mesh.vertices)
        before_faces = len(mesh.polygons)

        bm = bmesh.new()
        bm.from_mesh(mesh)

        # Step 1: Tris to Quads
        bmesh.ops.join_triangles(
            bm,
            faces=bm.faces[:],
            angle_face_threshold=self.face_angle,
            angle_shape_threshold=self.shape_threshold,
        )

        # Step 2: Limited Dissolve
        bmesh.ops.dissolve_limit(
            bm,
            angle_limit=self.dissolve_angle,
            verts=bm.verts[:],
            edges=bm.edges[:],
        )

        bm.to_mesh(mesh)
        mesh.update()
        bm.free()

        after_verts = len(mesh.vertices)
        after_faces = len(mesh.polygons)

        self.report({'INFO'}, 
            f"Cleaned: {before_faces} → {after_faces} faces, "
            f"{before_verts} → {after_verts} verts")
        return {'FINISHED'}


class hb_frameless_OT_dissolve_selected(bpy.types.Operator):
    bl_idname = "hb_frameless.dissolve_selected"
    bl_label = "Dissolve Selected Faces"
    bl_description = "Dissolve interior edges of selected faces to merge coplanar triangles into clean quads/ngons"
    bl_options = {'REGISTER', 'UNDO'}

    dissolve_angle: bpy.props.FloatProperty(
        name="Dissolve Angle",
        description="Maximum angle between faces to merge",
        default=math.radians(2.0),
        min=math.radians(0.1),
        max=math.radians(15.0),
        subtype='ANGLE',
    )# type: ignore

    @classmethod
    def poll(cls, context):
        return (context.active_object 
                and context.active_object.type == 'MESH' 
                and context.active_object.mode == 'EDIT')

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)

        sel_faces = set(f for f in bm.faces if f.select)
        if not sel_faces:
            self.report({'WARNING'}, "No faces selected")
            return {'CANCELLED'}

        # Find interior edges (both adjacent faces are selected)
        interior_edges = [e for e in bm.edges 
                         if len(e.link_faces) == 2 
                         and set(e.link_faces).issubset(sel_faces)]

        # Find interior verts (all linked faces are selected)
        interior_verts = [v for v in bm.verts 
                         if v.select 
                         and all(f in sel_faces for f in v.link_faces)]

        before = len(sel_faces)

        if interior_edges or interior_verts:
            bmesh.ops.dissolve_limit(
                bm,
                angle_limit=self.dissolve_angle,
                verts=interior_verts,
                edges=interior_edges,
            )
            bmesh.update_edit_mesh(obj.data)

            after = sum(1 for f in bm.faces if f.select)
            self.report({'INFO'}, f"Dissolved: {before} → {after} faces")
        else:
            self.report({'INFO'}, "No interior edges found — faces may be floating duplicates. Try Delete Selected.")

        return {'FINISHED'}


class hb_frameless_OT_delete_floating_faces(bpy.types.Operator):
    bl_idname = "hb_frameless.delete_floating_faces"
    bl_label = "Delete Floating Faces"
    bl_description = "Delete selected faces that are disconnected from the rest of the mesh (duplicate overlapping geometry)"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object 
                and context.active_object.type == 'MESH' 
                and context.active_object.mode == 'EDIT')

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)

        sel_faces = [f for f in bm.faces if f.select]
        if not sel_faces:
            self.report({'WARNING'}, "No faces selected")
            return {'CANCELLED'}

        count = len(sel_faces)
        bmesh.ops.delete(bm, geom=sel_faces, context='FACES')
        bmesh.update_edit_mesh(obj.data)

        # Clean up loose verts left behind
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='VERTS')
            bmesh.update_edit_mesh(obj.data)

        self.report({'INFO'}, f"Deleted {count} faces")
        return {'FINISHED'}


class hb_frameless_OT_rebuild_selected_faces(bpy.types.Operator):
    bl_idname = "hb_frameless.rebuild_selected_faces"
    bl_label = "Rebuild Selected Faces"
    bl_description = "Delete selected faces and replace with a single clean face using the outer boundary vertices"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.active_object 
                and context.active_object.type == 'MESH' 
                and context.active_object.mode == 'EDIT')

    def execute(self, context):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        sel_faces = [f for f in bm.faces if f.select]
        if len(sel_faces) < 2:
            self.report({'WARNING'}, "Select at least 2 faces")
            return {'CANCELLED'}

        # Get normal from first face (all should be coplanar)
        ref_normal = sel_faces[0].normal.copy()

        # Collect all vertex positions from selected faces
        vert_coords = []
        for f in sel_faces:
            for v in f.verts:
                co = v.co.copy()
                # Avoid duplicates (within tolerance)
                is_dup = False
                for existing in vert_coords:
                    if (existing - co).length < 0.0001:
                        is_dup = True
                        break
                if not is_dup:
                    vert_coords.append(co)

        if len(vert_coords) < 3:
            self.report({'WARNING'}, "Not enough unique vertices")
            return {'CANCELLED'}

        # Build 2D projection axes from the face normal
        if abs(ref_normal.z) < 0.9:
            up = mathutils.Vector((0, 0, 1))
        else:
            up = mathutils.Vector((0, 1, 0))
        axis_u = ref_normal.cross(up).normalized()
        axis_v = ref_normal.cross(axis_u).normalized()

        # Project to 2D
        center = mathutils.Vector((0, 0, 0))
        for co in vert_coords:
            center += co
        center /= len(vert_coords)

        points_2d = []
        for co in vert_coords:
            d = co - center
            u = d.dot(axis_u)
            v = d.dot(axis_v)
            points_2d.append((u, v, co))

        # Convex hull to get outer boundary in order
        hull_indices = self.convex_hull_2d([(p[0], p[1]) for p in points_2d])
        hull_coords = [points_2d[i][2] for i in hull_indices]

        # Delete all selected faces and their verts
        # First collect verts, then delete faces, then delete orphan verts
        all_verts = set()
        for f in sel_faces:
            for v in f.verts:
                all_verts.add(v)

        bmesh.ops.delete(bm, geom=sel_faces, context='FACES_ONLY')

        # Delete verts that are now loose
        loose = [v for v in all_verts if v.is_valid and not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context='VERTS')

        # Create new verts and face
        new_verts = [bm.verts.new(co) for co in hull_coords]
        bm.verts.ensure_lookup_table()

        try:
            new_face = bm.faces.new(new_verts)
            new_face.normal_update()
            # Flip if normal is opposite to original
            if new_face.normal.dot(ref_normal) < 0:
                new_face.normal_flip()
            new_face.select = True
        except ValueError as e:
            self.report({'WARNING'}, f"Could not create face: {e}")
            return {'CANCELLED'}

        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"Rebuilt {len(sel_faces)} faces → 1 clean face ({len(hull_coords)} verts)")
        return {'FINISHED'}

    def convex_hull_2d(self, points):
        """Compute convex hull of 2D points. Returns indices in CCW order."""
        n = len(points)
        if n < 3:
            return list(range(n))

        # Find leftmost point
        start = min(range(n), key=lambda i: (points[i][0], points[i][1]))

        hull = []
        current = start
        while True:
            hull.append(current)
            candidate = 0
            for i in range(1, n):
                if candidate == current:
                    candidate = i
                    continue
                cross = self.cross_2d(points[current], points[candidate], points[i])
                if cross < 0:
                    candidate = i
                elif cross == 0:
                    # Collinear — pick the farther point
                    d_cand = (points[candidate][0] - points[current][0]) ** 2 + (points[candidate][1] - points[current][1]) ** 2
                    d_i = (points[i][0] - points[current][0]) ** 2 + (points[i][1] - points[current][1]) ** 2
                    if d_i > d_cand:
                        candidate = i
            current = candidate
            if current == start:
                break

        return hull

    def cross_2d(self, o, a, b):
        """Cross product of vectors OA and OB."""
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


classes = (
    hb_frameless_OT_cleanup_mesh,
    hb_frameless_OT_dissolve_selected,
    hb_frameless_OT_delete_floating_faces,
    hb_frameless_OT_rebuild_selected_faces,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
