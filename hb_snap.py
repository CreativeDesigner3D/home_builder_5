import bpy
import math
from bpy_extras import view3d_utils
from mathutils import Vector
from mathutils.geometry import intersect_line_plane

RADIUS = 50
STEPS = 6

def get_region(context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.data:
                    return region

def event_is_pass_through(event):
    if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
        return True
    else:
        return False

#ray_cast adding the view point in the result
def ray_cast(context, depsgraph, position,region):

    #The view point of the user
    view_point = view3d_utils.region_2d_to_origin_3d(region, region.data, position)
    #The direction indicated by the mouse position from the current view
    view_vector = view3d_utils.region_2d_to_vector_3d(region, region.data, position)

    return *context.scene.ray_cast(depsgraph, view_point, view_vector), view_point

#try to find the best hit point on the scene
def best_hit(context, depsgraph, mouse_pos,region):
    
    context.view_layer.update() 
    
    #at first we raycast from the mouse position as it is
    result, location, normal, index, object, matrix, view_point = \
        ray_cast(context, depsgraph, mouse_pos,region)

    if result:
        if 'HB_CURRENT_DRAW_OBJ' not in object:
            return result, location, index, object, view_point

    #but if we are near but outside the object surface, we need to inspect around the 
    #mouse position and keep the closest location
    best_result = False
    best_location = best_index = best_object = None
    best_distance = 0

    angle = 0
    delta_angle = 2 * math.pi / STEPS
    for i in range(STEPS):
        
        pos = mouse_pos + RADIUS * Vector((math.cos(angle), math.sin(angle)))
        result, location, normal, index, object, matrix, view_point = \
            ray_cast(context, depsgraph, pos, region)
        if object and 'HB_CURRENT_DRAW_OBJ' not in object:
            if result and (best_object is None or (view_point - location).length < best_distance):
                best_distance = (view_point - location).length
                best_result = True
                best_location = location
                best_index = index
                best_object = object
        angle += delta_angle

    return best_result, best_location, best_index, best_object, view_point

def search_edge_pos(region, region3D, mouse, v1, v2, epsilon = 0.0001):
    #dichotomic search for the nearest point along an edge, compare to the mouse position
    #not optimized, but easy to write... ;)
    while (v1 - v2).length > epsilon:
        v12D = view3d_utils.location_3d_to_region_2d(region, region3D, v1)
        v22D = view3d_utils.location_3d_to_region_2d(region, region3D, v2)
        if v12D is None: return v2
        if v22D is None: return v1
        if (v12D - mouse).length < (v22D - mouse).length:
            v2 = (v1 + v2) / 2
        else:
            v1 = (v1 + v2) / 2
    return v1

def snap_to_geometry(self, context, vertices):
    #first snap to vertices
    #loop over vertices and keep the one which is closer once projected on screen
    snap_location = None
    best_distance = 0
    for co in vertices:
        co2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, co)
        if co2D is not None:
            distance = (co2D - self.mouse_pos).length
            if distance < RADIUS and (snap_location is None or distance < best_distance):
                snap_location = co
                best_distance = distance
                
    if snap_location is not None:
        self.hit_location = snap_location
        return
    
    #then, if no vertex is found, try to snap to edges
    for co1, co2 in zip(vertices[1:]+vertices[:1], vertices):
        v = search_edge_pos(self.region, self.region.data, self.mouse_pos, co1, co2)
        v2D = view3d_utils.location_3d_to_region_2d(self.region, self.region.data, v)
        if v2D is not None:
            distance = (v2D - self.mouse_pos).length
            if distance < RADIUS and (snap_location is None or distance < best_distance):
                snap_location = v
                best_distance = distance

    if snap_location is not None:
        self.hit_location = snap_location
        return

def snap_to_object(self, context, depsgraph):

    if self.hit_object.type == 'MESH':
        #the object need to be evaluated (if modifiers, for instance)
        evaluated = self.hit_object.evaluated_get(depsgraph)

        data = evaluated.data

        polygon = data.polygons[self.hit_face_index]
        matrix = evaluated.matrix_world
        
        #get evaluated vertices of the wanted polygon, in world coordinates
        vertices = [matrix @ data.vertices[i].co for i in polygon.vertices]
        
        snap_to_geometry(self, context, vertices)    

def floor_fit(v, scale):
    return math.floor(v / scale) * scale

def ceil_fit(v, scale):
    return math.ceil(v / scale) * scale

def snap_to_grid(self, context, crtl_is_pressed):

    view_point = view3d_utils.region_2d_to_origin_3d(self.region, self.region.data, self.mouse_pos)
    view_vector = view3d_utils.region_2d_to_vector_3d(self.region, self.region.data, self.mouse_pos)

    if self.region.data.is_orthographic_side_view:
        #ortho side view special case
        norm = view_vector
    else:
        #other views
        norm = Vector((0,0,1))

    #At which scale the grid is
    # (log10 is 1 for meters => 10 ** (1 - 1) = 1
    # (log10 is 0 for 10 centimeters => 10 ** (0 - 1) = 0.1
    scale = 10 ** (round(math.log10(self.region.data.view_distance)) - 1)
    #... to be improved with grid scale, subdivisions, etc.

    #here no ray cast, but intersection between the view line and the grid plane        
    max_float =1.0e+38
    co = intersect_line_plane(view_point, view_point + max_float * view_vector, (0,0,0), norm)

    if co is not None:
        self.hit_grid = True
        if crtl_is_pressed:
            #depending on the view angle, create the list of vertices for a plane around the hit point
            #which size is adapted to the view scale (view distance)
            if abs(norm.x) > 0:
                vertices = [Vector((0, floor_fit(co.y, scale), floor_fit(co.z, scale))), Vector((0, floor_fit(co.y, scale), ceil_fit(co.z, scale))), Vector((0, ceil_fit(co.y, scale), ceil_fit(co.z, scale))), Vector((0, ceil_fit(co.y, scale), floor_fit(co.z, scale)))]
            elif abs(norm.y) > 0:
                vertices = [Vector((floor_fit(co.x, scale), 0, floor_fit(co.z, scale))), Vector((floor_fit(co.x, scale), 0, ceil_fit(co.z, scale))), Vector((ceil_fit(co.x, scale), 0, ceil_fit(co.z, scale))), Vector((ceil_fit(co.x, scale), 0, floor_fit(co.z, scale)))]
            else:
                vertices = [Vector((floor_fit(co.x, scale), floor_fit(co.y, scale), 0)), Vector((floor_fit(co.x, scale), ceil_fit(co.y, scale), 0)), Vector((ceil_fit(co.x, scale), ceil_fit(co.y, scale), 0)), Vector((ceil_fit(co.x, scale), floor_fit(co.y, scale), 0))]
            #and snap on this plane
            snap_to_geometry(self, context, vertices)

        #if no snap or out of snapping, keep the co                
        if self.hit_location is None:
            self.hit_location = Vector(co)

def main(self, crtl_is_pressed, context):
    self.hit_location = None
    self.hit_grid = False
    
    depsgraph = context.evaluated_depsgraph_get()

    result, location, index, object, view_point = \
        best_hit(context, depsgraph, self.mouse_pos,self.region)
    
    self.hit_location = location
    self.hit_face_index = index
    self.hit_object = object
    self.view_point = view_point

    if result and crtl_is_pressed:
        snap_to_object(self, context, depsgraph)
    elif not result:
        snap_to_grid(self, context, crtl_is_pressed)